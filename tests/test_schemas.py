import pytest
from pydantic import ValidationError

from detector import config
from detector.schemas import (
    BatchItemResult,
    BatchPredictJsonRequest,
    BatchPredictResponse,
    HealthResponse,
    JobPosting,
    ModelInfoResponse,
    PredictionResult,
)


def test_job_posting_minimal_valid():
    job = JobPosting(title="Software Engineer", description="Develop backend APIs")
    assert job.title == "Software Engineer"
    assert job.description == "Develop backend APIs"
    assert job.company_profile == ""
    assert job.telecommuting == 0
    assert job.has_company_logo == 0
    assert job.has_questions == 0


def test_job_posting_all_fields_valid():
    job = JobPosting(
        title="Fullstack Developer",
        description="Build fullstack applications",
        company_profile="Tech Innovators",
        requirements="Python, React",
        benefits="Health, 401k",
        location="US, NY, New York",
        department="Engineering",
        salary_range="100000-130000",
        employment_type="Full-time",
        required_experience="Mid-Senior level",
        required_education="Bachelor's Degree",
        industry="Technology",
        function="Information Technology",
        telecommuting=1,
        has_company_logo=1,
        has_questions=1,
    )
    raw = job.to_raw_dict()
    assert len(raw) == 16
    assert raw["title"] == "Fullstack Developer"
    assert raw["telecommuting"] == 1
    assert raw["location"] == "US, NY, New York"


def test_job_posting_empty_or_whitespace_title_fails():
    with pytest.raises(ValidationError):
        JobPosting(title="", description="Valid description")

    with pytest.raises(ValidationError):
        JobPosting(title="   ", description="Valid description")


def test_job_posting_empty_or_whitespace_desc_fails():
    with pytest.raises(ValidationError):
        JobPosting(title="Valid title", description="")

    with pytest.raises(ValidationError):
        JobPosting(title="Valid title", description="   \n\t  ")


def test_job_posting_title_too_long():
    long_title = "A" * 501
    with pytest.raises(ValidationError):
        JobPosting(title=long_title, description="Valid description")


def test_job_posting_text_exceeds_max_len():
    long_desc = "A" * (config.MAX_TEXT_LEN + 1)
    with pytest.raises(ValidationError):
        JobPosting(title="Valid title", description=long_desc)


def test_job_posting_binary_field_validation():
    job = JobPosting(title="Job", description="Desc", telecommuting="1")
    assert job.telecommuting == 1

    job2 = JobPosting(title="Job", description="Desc", telecommuting=None)
    assert job2.telecommuting == 0

    with pytest.raises(ValidationError):
        JobPosting(title="Job", description="Desc", telecommuting=5)


def test_job_posting_extra_fields_ignored():
    job = JobPosting(
        title="Job",
        description="Desc",
        job_id=12345,
        fraudulent=1,
        unexpected_key="ignore_me",
    )
    raw = job.to_raw_dict()
    assert "job_id" not in raw
    assert "fraudulent" not in raw


def test_batch_request_validation():
    # Empty list should fail
    with pytest.raises(ValidationError):
        BatchPredictJsonRequest(items=[])

    # Valid items
    single = JobPosting(title="Job 1", description="Desc 1")
    req = BatchPredictJsonRequest(items=[single])
    assert len(req.items) == 1

    # Over 500 items should fail
    too_many = [JobPosting(title=f"Job {i}", description=f"Desc {i}") for i in range(501)]
    with pytest.raises(ValidationError):
        BatchPredictJsonRequest(items=too_many)


def test_prediction_result_and_batch_response():
    res = PredictionResult(
        prediksi="PALSU",
        probabilitas_palsu=0.885,
        tingkat_risiko="TINGGI",
        threshold=0.7827,
        model="A. Logistic Regression",
    )
    assert res.prediksi == "PALSU"
    assert config.LANGUAGE_WARNING in res.warnings

    batch_resp = BatchPredictResponse(
        count=1,
        results=[
            BatchItemResult(
                index=0,
                prediksi="PALSU",
                probabilitas_palsu=0.885,
                tingkat_risiko="TINGGI",
            )
        ],
        threshold=0.7827,
        model="A. Logistic Regression",
    )
    assert batch_resp.count == 1
    assert len(batch_resp.results) == 1


def test_health_and_model_info_response():
    h = HealthResponse(status="ok", model_loaded=True)
    assert h.status == "ok"
    assert h.model_loaded is True

    m = ModelInfoResponse(
        model_name="A. Logistic Regression",
        threshold=0.7827,
        raw_columns=["title", "description"],
        metrics_test_holdout={"Accuracy": 0.98},
    )
    assert m.model_name == "A. Logistic Regression"
    assert m.threshold == 0.7827
