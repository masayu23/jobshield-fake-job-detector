from unittest.mock import patch

from fastapi.testclient import TestClient

from detector.api import app
from detector.model_loader import ModelNotAvailable

client = TestClient(app)


def test_health_check_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["version"] == "1.0.0"


def test_model_info_ok():
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "Logistic Regression" in data["model_name"]
    assert 0.0 < data["threshold"] < 1.0
    assert "title" in data["raw_columns"]
    assert "description" in data["raw_columns"]
    assert data["sklearn_version"] == "1.9.1"
    assert "Accuracy" in data["metrics_test_holdout"]


def test_health_and_model_info_unavailable():
    with patch("detector.api.get_model_service", side_effect=ModelNotAvailable("Model file missing")):
        res_health = client.get("/health")
        assert res_health.status_code == 503
        data_health = res_health.json()
        assert data_health["status"] == "degraded"
        assert data_health["model_loaded"] is False

        res_info = client.get("/api/v1/model-info")
        assert res_info.status_code == 503
        assert "Model tidak tersedia" in res_info.json()["detail"]


def test_predict_single_legit_job():
    payload = {
        "title": "Senior Software Engineer",
        "company_profile": "Acme Systems is a 200-person software company building logistics tools.",
        "description": "Design and maintain backend services in Python and Go with a team of eight engineers.",
        "requirements": "5+ years of experience, BSc in Computer Science, PostgreSQL and AWS.",
        "benefits": "Health insurance, paid leave.",
        "location": "US, CA, San Francisco",
        "employment_type": "Full-time",
        "has_company_logo": 1,
        "has_questions": 1,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediksi"] == "ASLI"
    assert data["tingkat_risiko"] == "RENDAH"
    assert data["probabilitas_palsu"] < 0.5
    assert len(data["warnings"]) > 0


def test_predict_single_scam_job():
    payload = {
        "title": "Work From Home - Earn $5000 Weekly!!!",
        "description": "No experience needed! Send your bank details and a small registration fee to start now. Contact us on WhatsApp!!!",
        "location": "US",
        "employment_type": "Part-time",
        "has_company_logo": 0,
        "has_questions": 0,
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediksi"] == "PALSU"
    assert data["tingkat_risiko"] == "TINGGI"
    assert data["probabilitas_palsu"] > 0.5


def test_predict_single_validation_error():
    # Missing title
    response = client.post("/api/v1/predict", json={"description": "No title provided"})
    assert response.status_code == 422


def test_predict_single_model_unavailable():
    with patch("detector.api.get_model_service", side_effect=ModelNotAvailable("Model file missing")):
        response = client.post(
            "/api/v1/predict",
            json={"title": "Engineer", "description": "Backend API engineer"},
        )
        assert response.status_code == 503
        assert "Model tidak tersedia" in response.json()["detail"]


def test_predict_batch_json_success():
    payload = {
        "items": [
            {
                "title": "Senior Software Engineer",
                "description": "Design and maintain backend microservices.",
                "company_profile": "Acme Systems.",
            },
            {
                "title": "Work From Home - $5000 weekly guaranteed!",
                "description": "No experience needed! Send bank details on WhatsApp immediately!",
            },
        ]
    }
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["index"] == 0
    assert data["results"][1]["index"] == 1
    # Scam posting has higher probability
    assert data["results"][1]["probabilitas_palsu"] > data["results"][0]["probabilitas_palsu"]


def test_predict_batch_json_empty_or_too_large():
    # Empty items
    res_empty = client.post("/api/v1/predict/batch", json={"items": []})
    assert res_empty.status_code == 422

    # Over 500 items
    too_many = [{"title": f"Job {i}", "description": f"Desc {i}"} for i in range(501)]
    res_large = client.post("/api/v1/predict/batch", json={"items": too_many})
    assert res_large.status_code == 422


def test_predict_batch_csv_success():
    csv_content = (
        "title,description,company_profile,location\n"
        "Data Engineer,Build analytics pipelines in Python,Acme Corp,\"US, NY, New York\"\n"
        "Earn Money Fast,Send WhatsApp message for registration fee,,US\n"
    )
    files = {"file": ("test_jobs.csv", csv_content.encode("utf-8"), "text/csv")}
    response = client.post("/api/v1/predict/batch", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2


def test_predict_batch_csv_missing_columns():
    csv_bad = "job_id,company_profile\n1,Acme Corp\n"
    files = {"file": ("bad_jobs.csv", csv_bad.encode("utf-8"), "text/csv")}
    response = client.post("/api/v1/predict/batch", files=files)
    assert response.status_code == 422
    assert "title" in response.json()["detail"]


def test_predict_batch_csv_empty():
    files = {"file": ("empty.csv", b"", "text/csv")}
    response = client.post("/api/v1/predict/batch", files=files)
    assert response.status_code == 422


def test_predict_batch_csv_over_500_rows():
    header = "title,description\n"
    rows = "".join(f"Title {i},Description {i}\n" for i in range(505))
    large_csv = (header + rows).encode("utf-8")
    files = {"file": ("too_large.csv", large_csv, "text/csv")}
    response = client.post("/api/v1/predict/batch", files=files)
    assert response.status_code == 422
    assert "melebihi batas maksimal" in response.json()["detail"]


def test_structured_validation_error_format():
    # Calling predict with invalid JSON body triggers RequestValidationError
    response = client.post("/api/v1/predict", json={"title": 123})
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "timestamp" in data
    assert isinstance(data["detail"], list)


def test_structured_model_not_ready_error_format():
    with patch("detector.api.get_model_service", side_effect=ModelNotAvailable("Model file missing")):
        response = client.post(
            "/api/v1/predict",
            json={"title": "Engineer", "description": "Backend API engineer"},
        )
        assert response.status_code == 503
        data = response.json()
        assert data["code"] == "MODEL_NOT_READY"
        assert "timestamp" in data


def test_privacy_safe_logging_never_logs_raw_text(caplog):
    import logging

    secret_raw_text = "CONFIDENTIAL_APPLICANT_SECRET_DATA_XYZ_98765"
    payload = {
        "title": "Confidential Role",
        "description": secret_raw_text,
    }

    with caplog.at_level(logging.INFO, logger="detector.access"):
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    # Check that access logger logged metadata
    assert "method=POST" in caplog.text
    assert "path=/api/v1/predict" in caplog.text
    assert "status=200" in caplog.text
    assert "request_id=" in caplog.text

    # CRITICAL (NFR-03): Raw text MUST NEVER appear in any log message
    assert secret_raw_text not in caplog.text


def test_frontend_routes_served():
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "JobShield" in res_root.text

    res_app = client.get("/app")
    assert res_app.status_code == 200
    assert "JobShield" in res_app.text


def test_assistant_chat_without_api_key_returns_knowledge_base():
    payload = {
        "messages": [
            {"role": "user", "content": "Saya disuruh beli tiket travel ke Bali oleh panitia tes kerja."}
        ],
        "job_context": {"title": "Staff Admin", "prediksi": "PALSU", "probabilitas_palsu": 0.89},
    }
    with patch("detector.config.GEMINI_API_KEY", ""):
        response = client.post("/api/v1/assistant/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_live_gemini"] is False
        assert "Tiket Travel Bodong" in data["reply"]
        assert "Staff Admin" in data["reply"]


def test_assistant_chat_with_mocked_gemini_api():
    from unittest.mock import AsyncMock, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Panggilan tes ini memiliki ciri penipuan berkedok travel rekanan."}]
                }
            }
        ]
    }

    payload = {
        "messages": [{"role": "user", "content": "Apakah email dari hrd-pertamina@gmail.com asli?"}],
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        response = client.post(
            "/api/v1/assistant/chat",
            json=payload,
            headers={"X-Gemini-API-Key": "dummy-test-key-12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_live_gemini"] is True
        assert "ciri penipuan" in data["reply"]


def test_assistant_chat_validation_error():
    # Empty messages list should trigger 422
    response = client.post("/api/v1/assistant/chat", json={"messages": []})
    assert response.status_code == 422


def test_assistant_chat_fallback_scenarios():
    with patch("detector.config.GEMINI_API_KEY", ""):
        # Telegram deposit scenario
        resp_tele = client.post(
            "/api/v1/assistant/chat",
            json={"messages": [{"role": "user", "content": "Saya ditawari tugas freelance Telegram like subscribe"}]},
        )
        assert resp_tele.status_code == 200
        assert "Telegram" in resp_tele.json()["reply"]

        # KTP phishing scenario
        resp_ktp = client.post(
            "/api/v1/assistant/chat",
            json={"messages": [{"role": "user", "content": "Apakah boleh kirim foto KTP dan buku tabungan?"}]},
        )
        assert resp_ktp.status_code == 200
        assert "Data Pribadi" in resp_ktp.json()["reply"]

        # General greeting scenario
        resp_gen = client.post(
            "/api/v1/assistant/chat",
            json={"messages": [{"role": "user", "content": "Halo apa kabar?"}]},
        )
        assert resp_gen.status_code == 200
        assert "JobShield Security Advisor" in resp_gen.json()["reply"]


def test_assistant_chat_gemini_api_error_graceful_fallback():
    from unittest.mock import AsyncMock, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.json.return_value = {"error": {"message": "API key not valid"}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        response = client.post(
            "/api/v1/assistant/chat",
            json={"messages": [{"role": "user", "content": "Wawancara kerja di hotel bayar uang seragam"}]},
            headers={"X-Gemini-API-Key": "invalid-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_live_gemini"] is False
        assert "API key not valid" in data["reply"]





