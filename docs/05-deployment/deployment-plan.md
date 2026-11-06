# Rencana Deployment — Fase 5

## Artefak rilis
- Image Docker (`Dockerfile` di root) berisi `src/` + `models/current/`.
- Variabel lingkungan: `MODEL_DIR` (default `/app/models/current`), `MAX_BATCH` (500), `LOG_LEVEL` (INFO).
- Base image: `python:3.11-slim` dengan user non-root `appuser`.
- Entry-point: `uvicorn detector.api:app --app-dir src --host 0.0.0.0 --port 8000`

## Langkah deploy

### Lokal
```bash
# Install dependensi
pip install -r requirements.txt

# Jalankan server
uvicorn detector.api:app --app-dir src --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Build image
docker build -t fake-job-detector:latest .
# atau: make docker-build

# Jalankan container
docker run --rm -p 8000:8000 fake-job-detector:latest
# atau: make docker-run
```

Setelah berjalan, verifikasi:
```bash
curl http://localhost:8000/health
# → {"status":"ok","model_loaded":true,"version":"1.0.0"}
```

### Cloud (opsional)
Deploy ke Hugging Face Spaces (Docker), Render, Railway, atau VPS — gunakan image yang sama, expose port 8000.

## Catatan versi
- Python: 3.11-slim (cocok dengan lingkungan dev)
- scikit-learn: **1.9.1** (harus sama dengan `models/current/model_metadata.json`)
- Gradio: dipasang via `requirements.txt`

## Checklist rilis

- [x] Versi scikit-learn di image = `models/current/model_metadata.json` (1.9.1 — dikunci di `requirements.txt`)
- [x] Image berjalan sebagai user non-root (`appuser` via `useradd`, `USER appuser` di Dockerfile)
- [x] `README.md` berisi cara menjalankan & contoh `curl` (5 contoh: health, model-info, predict, batch JSON, batch CSV)
- [x] Tag rilis `v1.0.0` + catatan rilis (tag git annotated `v1.0.0`)
- [x] Gate fase 5 dicentang (Disetujui pemilik proyek pada 2026-11-04)

## Hasil verifikasi (2026-11-04)

| Pemeriksaan | Hasil |
|---|---|
| `make lint` / `ruff check src tests` | ✅ All checks passed |
| `make test` / pytest (58 test) | ✅ 58 passed, coverage 92% |
| Docker build | ⚠️ Docker Desktop tidak terpasang di mesin pengembang — perintah `docker build` tidak dieksekusi secara lokal. Dockerfile telah direview dan dinilai benar secara sintaksis dan logis. |
| Docker smoke test `GET /health` | ⚠️ Tidak dapat diverifikasi tanpa Docker (lihat atas). `/health` endpoint diverifikasi melalui pytest (`tests/test_api.py`) — mengembalikan `{"status":"ok","model_loaded":true}`. |

> **Catatan:** Jika Docker tersedia, jalankan `make docker-build && make docker-run` lalu `curl http://localhost:8000/health` untuk verifikasi penuh.
