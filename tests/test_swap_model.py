import json
import shutil
import sys
from pathlib import Path

import joblib
import pytest

# Ensure repo root is on sys.path so scripts can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.swap_model import (
    EXPECTED_RAW_COLUMNS,
    ModelValidationError,
    main,
    swap_model,
    validate_model_package,
)

CURRENT_MODELS_DIR = REPO_ROOT / "models" / "current"


def test_validate_real_current_model():
    """Model aktif saat ini di models/current/ harus lulus validasi."""
    res = validate_model_package(CURRENT_MODELS_DIR)
    assert res["model_name"] == "A. Logistic Regression"
    assert 0.0 < res["threshold"] < 1.0
    assert 0.0 <= res["legit_prob"] <= 1.0
    assert 0.0 <= res["scam_prob"] <= 1.0


def test_validate_missing_source_dir(tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    with pytest.raises(ModelValidationError, match="Direktori sumber tidak ditemukan"):
        validate_model_package(missing_dir)


def test_validate_missing_required_files(tmp_path):
    # Buat direktori kosong
    with pytest.raises(ModelValidationError, match="File wajib tidak ditemukan"):
        validate_model_package(tmp_path)

    # Tambahkan sebagian file tapi kurang
    (tmp_path / "fake_job_detector.joblib").write_text("dummy")
    with pytest.raises(ModelValidationError, match="File wajib tidak ditemukan"):
        validate_model_package(tmp_path)


def test_validate_invalid_metadata(tmp_path):
    # Copy all files from CURRENT_MODELS_DIR first
    for f in CURRENT_MODELS_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, tmp_path / f.name)

    # 1. Broken JSON
    (tmp_path / "model_metadata.json").write_text("{corrupt-json")
    with pytest.raises(ModelValidationError, match="Gagal membaca atau mem-parse"):
        validate_model_package(tmp_path)

    # 2. Non-dict JSON
    (tmp_path / "model_metadata.json").write_text("[1, 2, 3]")
    with pytest.raises(ModelValidationError, match="harus berupa objek JSON"):
        validate_model_package(tmp_path)

    # 3. Missing keys
    (tmp_path / "model_metadata.json").write_text(json.dumps({"threshold": 0.5}))
    with pytest.raises(ModelValidationError, match="Key wajib 'model_name' tidak ada"):
        validate_model_package(tmp_path)

    # 4. Invalid threshold
    (tmp_path / "model_metadata.json").write_text(
        json.dumps({
            "model_name": "Test",
            "threshold": 1.5,
            "raw_columns": EXPECTED_RAW_COLUMNS,
        })
    )
    with pytest.raises(ModelValidationError, match="Nilai threshold pada metadata tidak valid"):
        validate_model_package(tmp_path)

    # 5. Mismatched raw columns in metadata
    (tmp_path / "model_metadata.json").write_text(
        json.dumps({
            "model_name": "Test",
            "threshold": 0.7,
            "raw_columns": ["title", "wrong_column"],
        })
    )
    with pytest.raises(ModelValidationError, match="Kolom raw_columns pada metadata tidak cocok"):
        validate_model_package(tmp_path)


def test_validate_invalid_joblib_bundle(tmp_path):
    for f in CURRENT_MODELS_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, tmp_path / f.name)

    # 1. Corrupt joblib file
    (tmp_path / "fake_job_detector.joblib").write_bytes(b"not-a-joblib-file")
    with pytest.raises(ModelValidationError, match="Gagal memuat artefak joblib"):
        validate_model_package(tmp_path)

    # 2. Joblib containing non-dict
    joblib.dump(["not", "a", "dict"], tmp_path / "fake_job_detector.joblib")
    with pytest.raises(ModelValidationError, match="Bundle joblib harus berupa dictionary"):
        validate_model_package(tmp_path)

    # 3. Joblib missing keys
    joblib.dump({"threshold": 0.5}, tmp_path / "fake_job_detector.joblib")
    with pytest.raises(ModelValidationError, match="Key wajib 'model' tidak ditemukan"):
        validate_model_package(tmp_path)


class DummyClassifier:
    def predict_proba(self, df):
        import numpy as np
        return np.array([[0.9, 0.1], [0.1, 0.9]])


def test_validate_bundle_mismatched_columns_or_threshold(tmp_path):
    for f in CURRENT_MODELS_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, tmp_path / f.name)

    # 1. Mismatched columns in bundle
    bad_bundle = {
        "model": DummyClassifier(),
        "threshold": 0.78,
        "raw_columns": ["title", "description"],
        "model_name": "Dummy Model",
    }
    joblib.dump(bad_bundle, tmp_path / "fake_job_detector.joblib")
    with pytest.raises(ModelValidationError, match="Kolom raw_columns dalam bundle joblib tidak cocok"):
        validate_model_package(tmp_path)

    # 2. Invalid threshold in bundle
    bad_bundle["raw_columns"] = EXPECTED_RAW_COLUMNS
    bad_bundle["threshold"] = -0.5
    joblib.dump(bad_bundle, tmp_path / "fake_job_detector.joblib")
    with pytest.raises(ModelValidationError, match="Nilai threshold bundle joblib tidak valid"):
        validate_model_package(tmp_path)


def test_swap_model_dry_run(tmp_path):
    current_dir = tmp_path / "current"
    archive_dir = tmp_path / "archive"
    current_dir.mkdir()
    archive_dir.mkdir()

    # Create dummy initial file in current
    dummy_file = current_dir / "fake_job_detector.joblib"
    dummy_file.write_text("old_model")

    result = swap_model(
        source_dir=CURRENT_MODELS_DIR,
        current_dir=current_dir,
        archive_dir=archive_dir,
        dry_run=True,
    )

    assert result is None
    # Current dir should not have been updated
    assert dummy_file.read_text() == "old_model"
    # Archive should be empty
    assert list(archive_dir.iterdir()) == []


def test_swap_model_success_with_archiving(tmp_path):
    source_dir = tmp_path / "new_model"
    source_dir.mkdir()
    for f in CURRENT_MODELS_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, source_dir / f.name)

    current_dir = tmp_path / "current"
    archive_dir = tmp_path / "archive"
    current_dir.mkdir()
    archive_dir.mkdir()

    # Set up existing old model in current
    for f in ["fake_job_detector.joblib", "model_metadata.json", "fake_job_utils.py", "requirements.txt"]:
        (current_dir / f).write_text(f"old_{f}")

    archived_to = swap_model(
        source_dir=source_dir,
        current_dir=current_dir,
        archive_dir=archive_dir,
        dry_run=False,
        backup_tag="backup_v1",
    )

    assert archived_to is not None
    assert archived_to == archive_dir / "backup_v1"
    assert (archived_to / "fake_job_detector.joblib").read_text() == "old_fake_job_detector.joblib"

    # Verify current dir now has the new model files
    assert (current_dir / "fake_job_detector.joblib").stat().st_size > 100000
    assert (current_dir / "model_metadata.json").is_file()


def test_swap_model_empty_current_dir(tmp_path):
    current_dir = tmp_path / "current"
    archive_dir = tmp_path / "archive"

    archived_to = swap_model(
        source_dir=CURRENT_MODELS_DIR,
        current_dir=current_dir,
        archive_dir=archive_dir,
        dry_run=False,
    )

    # Since current was empty, nothing archived
    assert archived_to is None
    assert (current_dir / "fake_job_detector.joblib").is_file()


def test_cli_main_success_and_failure(tmp_path):
    # 1. Success with --dry-run
    ret = main([str(CURRENT_MODELS_DIR), "--dry-run"])
    assert ret == 0

    # 2. Failure with invalid dir
    ret = main([str(tmp_path / "non_existent")])
    assert ret == 1
