import pandas as pd
import pytest

from detector.model_loader import ModelNotAvailable, ModelService, get_model_service


def test_model_loads_and_has_threshold():
    svc = get_model_service()
    assert 0.0 < svc.threshold < 1.0
    assert "description" in svc.raw_columns


def test_legit_posting_low_risk():
    res = get_model_service().predict_one({
        "title": "Senior Software Engineer",
        "company_profile": "Acme Systems is a 200-person software company building logistics tools.",
        "description": "Design and maintain backend services in Python and Go with a team of eight engineers.",
        "requirements": "5+ years of experience, BSc in Computer Science, PostgreSQL and AWS.",
        "benefits": "Health insurance, paid leave.",
        "location": "US, CA, San Francisco", "employment_type": "Full-time",
        "has_company_logo": 1, "has_questions": 1})
    assert res["prediksi"] == "ASLI"
    assert res["tingkat_risiko"] == "RENDAH"


def test_scam_pattern_scores_higher_than_legit():
    # Uji relatif (tidak bergantung pada threshold) agar tetap valid setelah model diganti
    svc = get_model_service()
    legit = svc.predict_one({
        "title": "Senior Software Engineer",
        "company_profile": "Acme Systems is a 200-person software company building logistics tools.",
        "description": "Design and maintain backend services in Python and Go with a team of eight engineers.",
        "requirements": "5+ years of experience, BSc in Computer Science.",
        "location": "US, CA, San Francisco", "employment_type": "Full-time",
        "has_company_logo": 1, "has_questions": 1})
    scam = svc.predict_one({
        "title": "Work From Home - Earn $5000 Weekly!!!",
        "description": "No experience needed! Send your bank details and a small registration fee to start now. "
                       "Contact us on WhatsApp!!!",
        "location": "US", "employment_type": "Part-time", "has_company_logo": 0, "has_questions": 0})
    assert scam["probabilitas_palsu"] > 0.5 > legit["probabilitas_palsu"]


def test_missing_optional_columns_do_not_crash():
    df = pd.DataFrame([{"title": "Data entry", "description": "Simple data entry job."}])
    out = get_model_service().predict_dataframe(df)
    assert len(out) == 1


def test_missing_model_raises(tmp_path):
    with pytest.raises(ModelNotAvailable):
        ModelService(model_dir=tmp_path)
