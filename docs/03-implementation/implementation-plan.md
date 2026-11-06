# Rencana Implementasi — Fase 3
Kerjakan berurutan. Centang per tugas; tiap tugas harus punya test.

| ID | Tugas | Requirement | File | Status |
|---|---|---|---|---|
| T-01 | Verifikasi loader & smoke test hijau | NFR-04 | `src/detector/model_loader.py`, `tests/test_model_loader.py` | [x] (disediakan) |
| T-02 | Skema Pydantic `JobPosting`, `PredictionResult`, `BatchRequest/Response` + batas panjang | FR-06, NFR-02 | `schemas.py` | [x] |
| T-03 | `GET /health`, `GET /api/v1/model-info` | FR-05 | `api.py` | [x] |
| T-04 | `POST /api/v1/predict` | FR-02, FR-03, FR-07 | `api.py` | [x] |
| T-05 | `POST /api/v1/predict/batch` (JSON & CSV, maks 500) | FR-04, NFR-02 | `api.py` | [x] |
| T-06 | Startup: muat model sekali; error handler 503/422 | NFR-01 | `api.py` | [x] |
| T-07 | Logging tanpa teks mentah | NFR-03 | `api.py` | [x] |
| T-08 | UI Gradio 3 tab, di-mount di `/ui` | FR-01, FR-02, FR-07, FR-08 | `ui.py` | [x] |
| T-09 | Perbarui matriks keterlacakan di SRS | semua | `docs/01-requirements/SRS.md` | [x] |

## Definition of Done — Fase 3
- [x] Semua tugas T-01…T-09 dicentang
- [x] `make test` hijau, coverage ≥ 80%, `make lint` bersih
- [x] `make run` → `/docs` dan `/ui` dapat dibuka
- [x] Gate fase 3 dicentang
