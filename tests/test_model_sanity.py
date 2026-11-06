import pandas as pd
import pytest

from detector.model_loader import get_model_service


@pytest.fixture
def model_service():
    return get_model_service()


def test_model_sanity_legitimate_software_engineer(model_service):
    posting = {
        "title": "Senior Backend Software Engineer",
        "company_profile": (
            "CloudScale Technologies is an established SaaS provider with 300 employees across "
            "Europe and North America. We provide enterprise observability solutions."
        ),
        "description": (
            "We are seeking an experienced Backend Engineer to design, build, and optimize scalable "
            "REST APIs and asynchronous event processing systems in Python and Go. You will collaborate "
            "with a cross-functional squad of product managers, QA specialists, and frontend engineers."
        ),
        "requirements": (
            "5+ years of software development experience with Python or Go. Experience with PostgreSQL, "
            "Docker, and Kubernetes. Strong understanding of distributed systems and clean architecture."
        ),
        "benefits": (
            "Competitive salary ($140k - $170k), comprehensive health/dental/vision insurance, 401(k) "
            "matching up to 5%, annual professional development budget ($2,000), and 25 days paid time off."
        ),
        "location": "US, CA, San Francisco",
        "employment_type": "Full-time",
        "required_experience": "Mid-Senior level",
        "required_education": "Bachelor's Degree",
        "industry": "Information Technology and Services",
        "function": "Engineering",
        "telecommuting": 0,
        "has_company_logo": 1,
        "has_questions": 1,
    }
    result = model_service.predict_one(posting)
    assert result["prediksi"] == "ASLI"
    assert result["tingkat_risiko"] == "RENDAH"
    assert result["probabilitas_palsu"] < (result["threshold"] / 2)


def test_model_sanity_legitimate_healthcare_nurse(model_service):
    posting = {
        "title": "Registered Nurse - Intensive Care Unit",
        "company_profile": (
            "Memorial General Hospital has served the greater Chicago community for over 75 years, "
            "providing compassionate patient-centered healthcare across 400 acute care beds."
        ),
        "description": (
            "Assess patient health problems, implement nursing care plans, and maintain medical records. "
            "Provide clinical guidance in intensive care unit environment."
        ),
        "requirements": "Active RN license in the state of Illinois, BSN preferred. BLS and ACLS certification.",
        "benefits": "Medical benefits, retirement pension, shift differentials, tuition reimbursement.",
        "location": "US, IL, Chicago",
        "employment_type": "Full-time",
        "industry": "Hospital & Health Care",
        "has_company_logo": 1,
        "has_questions": 1,
    }
    result = model_service.predict_one(posting)
    assert result["prediksi"] == "ASLI"
    assert result["tingkat_risiko"] == "RENDAH"


def test_model_sanity_blatant_scam_urgent_whatsapp_money(model_service):
    scam = {
        "title": "URGENT HIRING!!! WORK FROM HOME EARN $5000 WEEKLY GUARANTEED!!!",
        "company_profile": "",
        "description": (
            "No skills or experience required! Anyone can do this simple job! Start today and receive "
            "instant payout daily! Send your personal bank account details, copy of ID, and an initial "
            "registration processing fee of $150 via MoneyGram or WhatsApp to start immediately! "
            "Contact Mrs. Johnson on WhatsApp at +1-999-555-0199 now! Limited slots available!!!"
        ),
        "requirements": "Must have phone, internet, and WhatsApp. No education required.",
        "benefits": "Instant cash, work whenever you want, make thousands of dollars easily.",
        "location": "US",
        "employment_type": "Part-time",
        "telecommuting": 1,
        "has_company_logo": 0,
        "has_questions": 0,
    }
    result = model_service.predict_one(scam)
    assert result["prediksi"] == "PALSU"
    assert result["tingkat_risiko"] == "TINGGI"
    assert result["probabilitas_palsu"] >= result["threshold"]


def test_model_sanity_scam_scores_dramatically_higher_than_legit(model_service):
    legit = model_service.predict_one({
        "title": "Senior Product Manager",
        "company_profile": "Datadog is a monitoring service for cloud-scale applications.",
        "description": "Drive product roadmap for infrastructure monitoring products.",
        "requirements": "5+ years of B2B SaaS product management experience.",
        "has_company_logo": 1,
        "has_questions": 1,
    })
    scam = model_service.predict_one({
        "title": "Package Reshipment Agent - Earn $4000/week from Home!",
        "company_profile": "",
        "description": "Receive luxury packages at home and reship them overseas. We send you cashier checks.",
        "has_company_logo": 0,
        "has_questions": 0,
    })
    assert scam["probabilitas_palsu"] > 0.60
    assert legit["probabilitas_palsu"] < 0.20
    assert scam["probabilitas_palsu"] - legit["probabilitas_palsu"] > 0.40


def test_model_sanity_minimal_columns_does_not_crash(model_service):
    # Only title and description provided
    minimal = {"title": "Junior Data Analyst", "description": "Write SQL queries and build dashboards in PowerBI."}
    result = model_service.predict_one(minimal)
    assert result["prediksi"] in ("ASLI", "PALSU")
    assert 0.0 <= result["probabilitas_palsu"] <= 1.0
    assert result["tingkat_risiko"] in ("RENDAH", "WASPADA", "TINGGI")


def test_model_sanity_special_characters_and_html_tokens(model_service):
    messy_text = {
        "title": "Web Developer &amp; Designer &lt;Frontend&gt;",
        "description": (
            "We need a developer who knows <b>HTML5</b>, CSS3, &amp; JavaScript. "
            "Apply at #URL_12345# or contact #EMAIL_67890# or call #PHONE_112233#. "
            "Salary: $95,000 - $110,000/year! Great company!!!"
        ),
        "location": "US, NY, New York",
        "has_company_logo": 1,
        "has_questions": 1,
    }
    result = model_service.predict_one(messy_text)
    assert result["prediksi"] in ("ASLI", "PALSU")
    assert not pd.isna(result["probabilitas_palsu"])


def test_model_sanity_batch_ordering_preserved(model_service):
    jobs = [
        {"title": "Legit Engineer 1", "description": "Standard engineering role at software firm.", "has_company_logo": 1},
        {"title": "Scam Job 2", "description": "Send bank account fee to start work instantly!", "has_company_logo": 0},
        {"title": "Legit Accountant 3", "description": "Maintain general ledger and GAAP accounting.", "has_company_logo": 1},
    ]
    df = pd.DataFrame(jobs)
    out = model_service.predict_dataframe(df)

    assert len(out) == 3
    assert list(out.index) == [0, 1, 2]
    for i, job in enumerate(jobs):
        single_res = model_service.predict_one(job)
        assert out.iloc[i]["probabilitas_palsu"] == single_res["probabilitas_palsu"]
        assert out.iloc[i]["prediksi"] == single_res["prediksi"]
        assert out.iloc[i]["tingkat_risiko"] == single_res["tingkat_risiko"]


def test_model_sanity_deterministic_inference(model_service):
    posting = {
        "title": "DevOps Engineer",
        "description": "Manage Terraform infrastructure, AWS VPCs, and CI/CD pipelines in GitHub Actions.",
        "location": "US, WA, Seattle",
        "has_company_logo": 1,
    }
    res1 = model_service.predict_one(posting)
    res2 = model_service.predict_one(posting)
    assert res1["probabilitas_palsu"] == res2["probabilitas_palsu"]
    assert res1["prediksi"] == res2["prediksi"]
    assert res1["tingkat_risiko"] == res2["tingkat_risiko"]
