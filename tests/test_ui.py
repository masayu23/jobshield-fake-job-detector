import os
import tempfile
from unittest.mock import MagicMock, patch

import gradio as gr
import pandas as pd
from fastapi.testclient import TestClient

from detector.api import app
from detector.ui import (
    analyze_batch_csv,
    analyze_single_job,
    create_template_csv,
    create_ui,
    evaluate_checklist,
    sanitize_csv_cell,
    sanitize_dataframe_for_csv,
)

client = TestClient(app)


def test_create_ui_returns_blocks():
    ui = create_ui()
    assert isinstance(ui, gr.Blocks)


def test_ui_route_mounted_on_fastapi():
    response = client.get("/ui")
    # Gradio mount returns 200 or redirect to /ui/
    assert response.status_code in (200, 307, 308)


def test_analyze_single_job_legit():
    badge, proba, thr, saran = analyze_single_job(
        title="Senior Software Engineer",
        description="Develop backend services in Python and Go.",
        company_profile="Acme Systems is a 200-person tech company.",
        requirements="5+ years experience.",
        benefits="Health insurance, 401k.",
        location="US, CA, San Francisco",
        department="Engineering",
        salary_range="120000-150000",
        employment_type="Full-time",
        required_experience="Mid-Senior level",
        required_education="Bachelor's Degree",
        industry="Technology",
        function="Engineering",
        telecommuting=False,
        has_company_logo=True,
        has_questions=True,
    )
    assert "ASLI" in badge
    assert "RENDAH" in badge
    assert "%" in proba
    assert "%" in thr
    assert "INDIKASI AMAN" in saran


def test_analyze_single_job_scam():
    badge, proba, _thr, saran = analyze_single_job(
        title="Work From Home - $5000 Weekly Guaranteed!",
        description="No experience needed! Send bank details and registration fee on WhatsApp immediately!",
        company_profile="",
        requirements="",
        benefits="",
        location="US",
        department="",
        salary_range="",
        employment_type="Part-time",
        required_experience="",
        required_education="",
        industry="",
        function="",
        telecommuting=True,
        has_company_logo=False,
        has_questions=False,
    )
    assert "PALSU" in badge
    assert "TINGGI" in badge
    assert "%" in proba
    assert "PERHATIAN KERAS" in saran


def test_analyze_single_job_waspada():
    mock_svc = MagicMock()
    mock_svc.threshold = 0.78
    mock_svc.predict_one.return_value = {
        "prediksi": "ASLI",
        "probabilitas_palsu": 0.50,
        "tingkat_risiko": "WASPADA",
        "threshold": 0.78,
        "model": "Mock Model",
        "warnings": [],
    }
    with patch("detector.ui.get_model_service", return_value=mock_svc):
        badge, proba, _thr, saran = analyze_single_job(
            title="Accountant Staff",
            description="Manage bookkeeping and taxes.",
            company_profile="",
            requirements="Finance degree.",
            benefits="",
            location="US, NY",
            department="Finance",
            salary_range="",
            employment_type="Full-time",
            required_experience="Entry level",
            required_education="Bachelor's Degree",
            industry="Accounting",
            function="Finance",
            telecommuting=False,
            has_company_logo=False,
            has_questions=False,
        )
    assert "ASLI" in badge
    assert "WASPADA" in badge
    assert "50.00%" in proba
    assert "CATATAN WASPADA" in saran


def test_analyze_single_job_empty_validation():
    badge, proba, _thr, _saran = analyze_single_job(
        title="",
        description="",
        company_profile="",
        requirements="",
        benefits="",
        location="",
        department="",
        salary_range="",
        employment_type="",
        required_experience="",
        required_education="",
        industry="",
        function="",
        telecommuting=False,
        has_company_logo=False,
        has_questions=False,
    )
    assert "PERINGATAN VALIDASI" in badge
    assert proba == "0.00%"


def test_analyze_batch_csv_success():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "jobs.csv")
    df = pd.DataFrame(
        [
            {"title": "Software Engineer", "description": "Backend API development."},
            {"title": "Scam Job $5000", "description": "Send bank fee on WhatsApp immediately!"},
        ]
    )
    df.to_csv(csv_file, index=False)

    summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert "Total Lowongan Dianalisis" in summary
    assert out_df is not None
    assert len(out_df) == 2
    assert "prediksi" in out_df.columns
    assert "probabilitas_palsu" in out_df.columns
    assert "tingkat_risiko" in out_df.columns
    assert out_csv is not None
    assert os.path.exists(out_csv)


def test_analyze_batch_csv_missing_columns():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "bad.csv")
    df = pd.DataFrame([{"notes": "just notes"}])
    df.to_csv(csv_file, index=False)

    summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert "wajib memuat kolom 'title' dan 'description'" in summary
    assert out_df is None
    assert out_csv is None


def test_analyze_batch_csv_empty_and_none():
    summary, out_df, _out_csv = analyze_batch_csv(None)
    assert "Mohon unggah berkas CSV" in summary
    assert out_df is None


def test_analyze_batch_csv_file_not_found():
    summary, out_df, out_csv = analyze_batch_csv("non_existent_file.csv")
    assert "tidak valid atau tidak ditemukan" in summary
    assert out_df is None
    assert out_csv is None


def test_analyze_batch_csv_empty_dataframe():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "empty.csv")
    with open(csv_file, "w") as f:
        f.write("title,description\n")

    summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert "Berkas CSV kosong" in summary
    assert out_df is None
    assert out_csv is None


def test_analyze_batch_csv_oversize():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "large.csv")
    with open(csv_file, "wb") as f:
        f.write(b"0" * (6 * 1024 * 1024))  # 6 MB > 5 MB limit

    summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert "melebihi batas maksimal" in summary
    assert out_df is None
    assert out_csv is None


def test_analyze_batch_csv_over_max_batch():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "over_batch.csv")
    rows = [{"title": f"Title {i}", "description": f"Desc {i}"} for i in range(505)]
    pd.DataFrame(rows).to_csv(csv_file, index=False)

    summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert "melebihi batas maksimal 500 baris" in summary
    assert out_df is None
    assert out_csv is None


def test_create_template_csv():
    template_path = create_template_csv()
    assert os.path.exists(template_path)
    df = pd.read_csv(template_path)
    assert "title" in df.columns
    assert "description" in df.columns
    assert len(df) == 1


def test_sanitize_csv_cell():
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-123") == "'-123"
    assert sanitize_csv_cell("@SUM(A1:A5)") == "'@SUM(A1:A5)"
    assert sanitize_csv_cell("\tTab") == "'\tTab"
    assert sanitize_csv_cell("\rReturn") == "'\rReturn"
    assert sanitize_csv_cell("Normal Title") == "Normal Title"
    assert sanitize_csv_cell(123) == 123


def test_sanitize_dataframe_for_csv():
    df = pd.DataFrame(
        {
            "title": ["=cmd", "Normal Title"],
            "amount": [10, 20],
        }
    )
    clean_df = sanitize_dataframe_for_csv(df)
    assert clean_df["title"].iloc[0] == "'=cmd"
    assert clean_df["title"].iloc[1] == "Normal Title"
    assert clean_df["amount"].iloc[0] == 10


def test_analyze_batch_csv_formula_injection_sanitization():
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, "injection.csv")
    df = pd.DataFrame(
        [
            {"title": "=cmd|' /C calc'!A0", "description": "+2+2"},
        ]
    )
    df.to_csv(csv_file, index=False)

    _summary, out_df, out_csv = analyze_batch_csv(csv_file)
    assert out_df is not None
    assert out_csv is not None

    exported_df = pd.read_csv(out_csv)
    # Tanda petik tunggal mencegah formula execution
    assert exported_df["title"].iloc[0].startswith("'=")
    assert exported_df["description"].iloc[0].startswith("'+")


def test_evaluate_checklist():
    out_all = evaluate_checklist(True, True, True, True, True, True)
    assert "6/6 (Sangat Baik)" in out_all

    out_four = evaluate_checklist(True, True, True, True, False, False)
    assert "4/6 (Cukup" in out_four

    out_low = evaluate_checklist(True, False, False, False, False, False)
    assert "1/6 (Waspada Tinggi)" in out_low
