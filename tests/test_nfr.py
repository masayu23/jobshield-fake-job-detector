import io
import logging
import time

import sklearn
from fastapi.testclient import TestClient

from detector import config
from detector.api import app
from detector.model_loader import get_model_service

client = TestClient(app)


def test_nfr_01_single_inference_latency_under_1_second():
    """NFR-01: Latensi prediksi tunggal harus < 1.0 detik pada CPU."""
    posting = {
        "title": "Senior Solutions Architect",
        "company_profile": "Global enterprise cloud consulting company with 2000+ consultants.",
        "description": (
            "Lead technical architecture discovery sessions with Fortune 500 clients. Design resilient "
            "multi-region cloud infrastructure using AWS, Azure, and Terraform. Mentor junior architects."
        ),
        "requirements": "10+ years IT experience, AWS Certified Solutions Architect Professional.",
        "benefits": "Competitive compensation, annual bonus, comprehensive health coverage.",
        "location": "US, NY, New York",
        "employment_type": "Full-time",
        "has_company_logo": 1,
        "has_questions": 1,
    }

    # Warmup
    client.post("/api/v1/predict", json=posting)

    # Benchmark 5 requests and measure average latency
    latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        resp = client.post("/api/v1/predict", json=posting)
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        latencies.append(elapsed)

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 1.0, f"Average latency too high: {avg_latency:.4f}s"
    assert max(latencies) < 1.0, f"Max latency exceeded 1.0s: {max(latencies):.4f}s"


def test_nfr_01_batch_500_latency_under_15_seconds():
    """NFR-01: Latensi inferensi batch 500 baris harus < 15.0 detik."""
    items = [
        {
            "title": f"Software Engineer Tier {i}",
            "description": f"Design and maintain microservice component #{i} using Python.",
            "location": "US, CA, San Francisco",
        }
        for i in range(500)
    ]

    t0 = time.perf_counter()
    resp = client.post("/api/v1/predict/batch", json={"items": items})
    elapsed = time.perf_counter() - t0

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 500
    assert len(data["results"]) == 500
    assert elapsed < 15.0, f"Batch 500 latency exceeded 15.0s: {elapsed:.2f}s"


def test_nfr_02_validation_title_length_limit():
    """NFR-02: Title > 500 karakter ditolak dengan 422."""
    payload = {
        "title": "A" * 501,
        "description": "Valid description within limit.",
    }
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_nfr_02_validation_text_length_limit():
    """NFR-02: Text field > 20000 karakter ditolak dengan 422."""
    payload = {
        "title": "Valid Title",
        "description": "B" * (config.MAX_TEXT_LEN + 1),
    }
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_nfr_02_validation_batch_size_limit():
    """NFR-02: Batch > 500 item ditolak dengan 422."""
    items = [
        {"title": f"Job {i}", "description": "Desc"}
        for i in range(501)
    ]
    resp = client.post("/api/v1/predict/batch", json={"items": items})
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data


def test_nfr_02_validation_csv_size_limit():
    """NFR-02: Berkas CSV > 5 MB ditolak dengan 422."""
    # Generate CSV payload slightly exceeding 5 MB
    large_csv = io.BytesIO()
    large_csv.write(b"title,description\n")
    chunk = b"Engineer," + (b"x" * 1024) + b"\n"
    for _ in range(5200):  # ~5.3 MB
        large_csv.write(chunk)
    large_csv.seek(0)

    resp = client.post(
        "/api/v1/predict/batch",
        files={"file": ("oversized.csv", large_csv, "text/csv")},
    )
    assert resp.status_code == 422
    assert "5 MB" in resp.json()["detail"]


def test_nfr_03_zero_raw_text_logging(caplog):
    """NFR-03: Zero raw-text logging — teks lowongan dilarang keras masuk ke log."""
    secret_marker = "TOP_SECRET_PROPRIETARY_UNRELEASED_PRODUCT_INFO_987654321"
    payload = {
        "title": f"Role with {secret_marker}",
        "description": f"Confidential job description containing {secret_marker} that must never be logged.",
        "company_profile": f"Company profile with {secret_marker}",
    }

    with caplog.at_level(logging.INFO, logger="detector.access"):
        resp = client.post("/api/v1/predict", json=payload)
        assert resp.status_code == 200

    # Ensure metadata is logged
    assert "method=POST" in caplog.text
    assert "path=/api/v1/predict" in caplog.text
    assert "status=200" in caplog.text

    # Strict assertion: secret marker text must NOT exist anywhere in log messages
    assert secret_marker not in caplog.text


def test_nfr_04_scikit_learn_reproducibility():
    """NFR-04: Runtime scikit-learn version matches metadata or is compatible 1.9.x."""
    svc = get_model_service()
    info = svc.model_info()
    expected_version = info.get("sklearn_version", "1.9.1")
    actual_version = sklearn.__version__
    assert actual_version == expected_version, (
        f"Version mismatch: runtime is {actual_version}, model was exported with {expected_version}"
    )


def test_nfr_07_xss_and_injection_input_handled_cleanly():
    """NFR-07: Payload yang mengandung script/HTML tag diproses secara aman tanpa eksekusi."""
    payload = {
        "title": "<script>alert('XSS')</script> Backend Lead",
        "description": "<img src=x onerror=alert(1)> Build reliable services; DROP TABLE jobs; --",
        "company_profile": "<svg/onload=alert('hello')>",
    }
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["prediksi"] in ("ASLI", "PALSU")
    assert 0.0 <= data["probabilitas_palsu"] <= 1.0
