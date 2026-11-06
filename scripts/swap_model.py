#!/usr/bin/env python3
"""Script pemeliharaan untuk memvalidasi dan menukar (swap) model aktif.

Alur kerja:
1. Memeriksa keberadaan file artefak di direktori model baru.
2. Memuat bundle joblib, metadata, dan utilitas.
3. Memvalidasi kompatibilitas kolom fitur (raw_columns).
4. Menjalankan uji asap (smoke test) prediksi sampel data asli dan palsu.
5. Jika lulus dan bukan --dry-run:
   - Mengarsipkan model lama di models/archive/<timestamp>/
   - Menyalin file model baru ke models/current/
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("swap_model")

REQUIRED_FILES = [
    "fake_job_detector.joblib",
    "model_metadata.json",
    "fake_job_utils.py",
    "requirements.txt",
]

EXPECTED_RAW_COLUMNS = [
    "title",
    "location",
    "department",
    "salary_range",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "telecommuting",
    "has_company_logo",
    "has_questions",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function",
]


class ModelValidationError(Exception):
    """Kesalahan validasi paket model baru."""


def validate_model_package(source_dir: Path) -> dict[str, Any]:
    """Validasi artefak model baru secara komprehensif.

    Mengembalikan kamus ringkasan hasil validasi jika berhasil.
    Melempar ModelValidationError jika ditemukan kegagalan validasi.
    """
    if not source_dir.is_dir():
        raise ModelValidationError(f"Direktori sumber tidak ditemukan: {source_dir}")

    # 1. Periksa kelengkapan file
    for filename in REQUIRED_FILES:
        file_path = source_dir / filename
        if not file_path.is_file():
            raise ModelValidationError(f"File wajib tidak ditemukan di direktori model: {filename}")

    # 2. Validasi model_metadata.json
    meta_path = source_dir / "model_metadata.json"
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ModelValidationError(f"Gagal membaca atau mem-parse model_metadata.json: {e}") from e

    if not isinstance(metadata, dict):
        raise ModelValidationError("model_metadata.json harus berupa objek JSON (dict).")

    for key in ("threshold", "model_name", "raw_columns"):
        if key not in metadata:
            raise ModelValidationError(f"Key wajib '{key}' tidak ada di model_metadata.json.")

    meta_threshold = metadata.get("threshold")
    if not isinstance(meta_threshold, (int, float)) or not (0.0 < meta_threshold < 1.0):
        raise ModelValidationError(f"Nilai threshold pada metadata tidak valid: {meta_threshold}")

    meta_raw_cols = metadata.get("raw_columns")
    if set(meta_raw_cols) != set(EXPECTED_RAW_COLUMNS):
        diff = set(EXPECTED_RAW_COLUMNS).symmetric_difference(set(meta_raw_cols))
        raise ModelValidationError(
            f"Kolom raw_columns pada metadata tidak cocok dengan spesifikasi fitur. Selisih: {diff}"
        )

    # 3. Import modul fake_job_utils dari direktori sumber
    utils_path = source_dir / "fake_job_utils.py"
    try:
        spec = importlib.util.spec_from_file_location("fake_job_utils", utils_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Tidak dapat membuat modul spec untuk {utils_path}")
        new_utils = importlib.util.module_from_spec(spec)
        sys.modules["fake_job_utils"] = new_utils
        spec.loader.exec_module(new_utils)
    except Exception as e:
        raise ModelValidationError(f"Gagal mengimpor fake_job_utils.py: {e}") from e

    # 4. Muat bundle joblib
    joblib_path = source_dir / "fake_job_detector.joblib"
    try:
        bundle = joblib.load(joblib_path)
    except Exception as e:
        raise ModelValidationError(f"Gagal memuat artefak joblib: {e}") from e

    if not isinstance(bundle, dict):
        raise ModelValidationError("Bundle joblib harus berupa dictionary.")

    for k in ("model", "threshold", "raw_columns", "model_name"):
        if k not in bundle:
            raise ModelValidationError(f"Key wajib '{k}' tidak ditemukan dalam bundle joblib.")

    bundle_cols = bundle["raw_columns"]
    if set(bundle_cols) != set(EXPECTED_RAW_COLUMNS):
        diff = set(EXPECTED_RAW_COLUMNS).symmetric_difference(set(bundle_cols))
        raise ModelValidationError(
            f"Kolom raw_columns dalam bundle joblib tidak cocok dengan spesifikasi fitur. Selisih: {diff}"
        )

    bundle_thr = bundle["threshold"]
    if not isinstance(bundle_thr, (int, float)) or not (0.0 < bundle_thr < 1.0):
        raise ModelValidationError(f"Nilai threshold bundle joblib tidak valid: {bundle_thr}")

    # 5. Uji asap (smoke test) inferensi
    legit_sample = {
        "title": "Senior Python Backend Engineer",
        "company_profile": "Reputable tech firm building cloud infrastructure for enterprises.",
        "description": "Develop and maintain high performance microservices using Python and PostgreSQL.",
        "requirements": "5+ years of experience with distributed systems and relational databases.",
        "benefits": "Competitive salary, health insurance, annual retreat, remote work options.",
        "location": "US, CA, San Francisco",
        "department": "Engineering",
        "salary_range": "120000-160000",
        "telecommuting": 1,
        "has_company_logo": 1,
        "has_questions": 1,
        "employment_type": "Full-time",
        "required_experience": "Mid-Senior level",
        "required_education": "Bachelor's Degree",
        "industry": "Information Technology and Services",
        "function": "Engineering",
    }

    scam_sample = {
        "title": "Data Entry Specialist - Earn $5000 Weekly Fast!",
        "company_profile": "",
        "description": "Urgent hire! No experience required. Send bank account details and deposit fee.",
        "requirements": "Must have computer and WhatsApp.",
        "benefits": "Make quick cash from home unlimited earnings guaranteed.",
        "location": "US",
        "department": "",
        "salary_range": "100000-250000",
        "telecommuting": 1,
        "has_company_logo": 0,
        "has_questions": 0,
        "employment_type": "Part-time",
        "required_experience": "Not Applicable",
        "required_education": "Unspecified",
        "industry": "",
        "function": "",
    }

    test_df = pd.DataFrame([legit_sample, scam_sample])
    try:
        pred_df = new_utils.predict_postings(bundle, test_df)
    except Exception as e:
        raise ModelValidationError(f"Smoke test inferensi gagal dieksekusi: {e}") from e

    expected_cols = {"probabilitas_palsu", "prediksi", "tingkat_risiko"}
    if not expected_cols.issubset(pred_df.columns):
        raise ModelValidationError(
            f"Output inferensi tidak memiliki kolom yang diharapkan: {expected_cols - set(pred_df.columns)}"
        )

    legit_prob = float(pred_df.iloc[0]["probabilitas_palsu"])
    scam_prob = float(pred_df.iloc[1]["probabilitas_palsu"])

    if not (0.0 <= legit_prob <= 1.0 and 0.0 <= scam_prob <= 1.0):
        raise ModelValidationError(f"Probabilitas inferensi di luar rentang [0, 1]: {legit_prob}, {scam_prob}")

    if scam_prob <= legit_prob:
        logger.warning(
            "Peringatan: sampel scam tidak memperoleh probabilitas lebih tinggi daripada legit "
            f"(legit: {legit_prob}, scam: {scam_prob})."
        )

    # Uji inferensi dengan field opsional kosong
    empty_df = pd.DataFrame([{"title": "Minimal Job Posting", "description": "Just a short job description."}])
    try:
        new_utils.predict_postings(bundle, empty_df)
    except Exception as e:
        raise ModelValidationError(f"Smoke test dengan kolom kosong gagal: {e}") from e

    logger.info("Validasi model baru BERHASIL.")
    logger.info("  Nama model: %s", bundle.get("model_name"))
    logger.info("  Threshold : %s", bundle_thr)
    logger.info("  Probabilitas legit: %.4f | scam: %.4f", legit_prob, scam_prob)

    return {
        "model_name": bundle.get("model_name"),
        "threshold": bundle_thr,
        "legit_prob": legit_prob,
        "scam_prob": scam_prob,
        "metadata": metadata,
    }


def swap_model(
    source_dir: Path,
    current_dir: Path,
    archive_dir: Path,
    dry_run: bool = False,
    backup_tag: str | None = None,
) -> Path | None:
    """Validasi model baru dan lakukan penukaran dengan model aktif jika valid.

    Mengembalikan path folder arsip jika penukaran dilakukan, atau None jika dry-run.
    """
    logger.info("Memulai validasi paket model dari: %s", source_dir)
    validate_model_package(source_dir)

    if dry_run:
        logger.info("[DRY RUN] Validasi sukses. Tidak ada file yang dipindahkan atau diubah.")
        return None

    # Siapkan direktori target
    current_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    # 1. Arsipkan model lama jika ada isinya
    archived_to: Path | None = None
    existing_files = [f for f in current_dir.iterdir() if f.is_file() and f.name in REQUIRED_FILES]
    if existing_files:
        tag = backup_tag or datetime.now().strftime("%Y%m%d_%H%M%S")
        target_archive = archive_dir / tag
        target_archive.mkdir(parents=True, exist_ok=True)
        for f in existing_files:
            dest = target_archive / f.name
            shutil.copy2(f, dest)
        # Salin juga model_metadata.json dan requirements.txt jika ada
        for extra in ["model_metadata.json", "requirements.txt"]:
            src_extra = current_dir / extra
            if src_extra.is_file() and not (target_archive / extra).exists():
                shutil.copy2(src_extra, target_archive / extra)
        archived_to = target_archive
        logger.info("Model lama berhasil diarsipkan ke: %s", target_archive)
    else:
        logger.info("Tidak ada file model lama di %s untuk diarsipkan.", current_dir)

    # 2. Pasang model baru ke current_dir
    for filename in REQUIRED_FILES:
        src_file = source_dir / filename
        dest_file = current_dir / filename
        shutil.copy2(src_file, dest_file)
        logger.info("Menyalin: %s -> %s", filename, dest_file)

    logger.info("Penukaran model selesai. Model aktif baru kini terpasang di %s", current_dir)
    return archived_to


def main(argv: list[str] | None = None) -> int:
    """Entry point CLI untuk swap_model."""
    parser = argparse.ArgumentParser(
        description="Validasi dan ganti model aktif (models/current/) dengan model baru secara aman."
    )
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Direktori berisi artefak model baru (joblib, metadata, utils, requirements).",
    )
    parser.add_argument(
        "--current-dir",
        type=Path,
        default=Path("models/current"),
        help="Direktori model aktif (default: models/current).",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("models/archive"),
        help="Direktori arsip model lama (default: models/archive).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Jalankan seluruh proses validasi tanpa melakukan perubahan file.",
    )
    parser.add_argument(
        "--backup-tag",
        type=str,
        default=None,
        help="Nama kustom untuk folder arsip (default: timestamp YYYYMMDD_HHMMSS).",
    )

    args = parser.parse_args(argv)

    try:
        swap_model(
            source_dir=args.source_dir,
            current_dir=args.current_dir,
            archive_dir=args.archive_dir,
            dry_run=args.dry_run,
            backup_tag=args.backup_tag,
        )
        return 0
    except ModelValidationError as err:
        logger.error("VALIDASI GAGAL: %s", err)
        return 1
    except Exception:
        logger.exception("Terjadi kesalahan tidak terduga saat swap model.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
