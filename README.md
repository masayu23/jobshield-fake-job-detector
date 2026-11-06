# Fake Job Detector — Sistem Cerdas Deteksi Lowongan Kerja Palsu

Aplikasi web (FastAPI + Gradio) yang mendeteksi lowongan kerja palsu menggunakan model Logistic Regression terlatih (F1 ≈ 0,86, ROC-AUC ≈ 0,99).

> ⚠️ **Peringatan:** Model dilatih pada teks **bahasa Inggris**. Lowongan berbahasa Indonesia dapat menghasilkan prediksi yang kurang akurat.

---

## Daftar Isi
1. [Quickstart (Docker)](#quickstart-docker)
2. [Quickstart (Lokal)](#quickstart-lokal)
3. [Contoh Perintah curl](#contoh-perintah-curl)
4. [Endpoint API](#endpoint-api)
5. [Antarmuka Web (UI)](#antarmuka-web-ui)
6. [Struktur Proyek](#struktur-proyek)
7. [Alur Kerja Waterfall](#alur-kerja-waterfall)
8. [Memakai Agen Coding](#memakai-agen-coding)

---

## Quickstart (Docker)

```bash
# 1. Build image
make docker-build
# atau: docker build -t fake-job-detector:latest .

# 2. Jalankan container (port 8000)
make docker-run
# atau: docker run --rm -p 8000:8000 fake-job-detector:latest
```

Setelah container berjalan:
- **API:** http://localhost:8000
- **Docs (Swagger):** http://localhost:8000/docs
- **UI (Gradio):** http://localhost:8000/ui

---

## Quickstart (Lokal)

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn detector.api:app --app-dir src --host 0.0.0.0 --port 8000

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn detector.api:app --app-dir src --host 0.0.0.0 --port 8000
```

Perintah `make` yang tersedia:

| Perintah | Keterangan |
|---|---|
| `make install` | Install dependensi dev (`requirements-dev.txt`) |
| `make test` | Jalankan seluruh test suite dengan coverage |
| `make lint` | Periksa kode dengan ruff |
| `make run` | Jalankan server lokal (port 8000, reload aktif) |
| `make docker-build` | Build Docker image |
| `make docker-run` | Jalankan Docker container di port 8000 |

---

## Contoh Perintah curl

### 1. Health check

```bash
curl http://localhost:8000/health
```

Respons yang diharapkan:
```json
{"status": "ok", "model_loaded": true, "version": "1.0.0"}
```

---

### 2. Informasi model

```bash
curl http://localhost:8000/api/v1/model-info
```

Respons contoh:
```json
{
  "model_name": "A. Logistic Regression",
  "sklearn_version": "1.9.1",
  "threshold": 0.7827,
  "metrics": {
    "Accuracy": 0.9875,
    "F1 (palsu)": 0.8625,
    "ROC-AUC": 0.9934
  },
  "warnings": ["Model dilatih pada teks bahasa Inggris."]
}
```

---

### 3. Prediksi satu lowongan (JSON)

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Data Entry Clerk — Work From Home",
    "description": "Earn $500/day! No experience needed. Send your bank details to register.",
    "company_profile": "",
    "requirements": "",
    "benefits": "Unlimited income"
  }'
```

Respons contoh:
```json
{
  "is_fake": true,
  "probability_fake": 0.923,
  "label": "PALSU",
  "threshold_used": 0.7827,
  "warnings": ["Model dilatih pada teks bahasa Inggris."]
}
```

---

### 4. Prediksi banyak lowongan (JSON batch)

```bash
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Software Engineer",
        "description": "Join our team to build scalable backend systems.",
        "company_profile": "Tech startup in Silicon Valley.",
        "requirements": "3+ years Python experience.",
        "benefits": "Health insurance, remote work"
      },
      {
        "title": "Secret Agent Needed",
        "description": "Make $1000/day from home! Just pay a small registration fee.",
        "company_profile": "",
        "requirements": "",
        "benefits": ""
      }
    ]
  }'
```

Respons contoh:
```json
{
  "results": [
    {"is_fake": false, "probability_fake": 0.041, "label": "ASLI", "threshold_used": 0.7827, "warnings": ["Model dilatih pada teks bahasa Inggris."]},
    {"is_fake": true,  "probability_fake": 0.961, "label": "PALSU", "threshold_used": 0.7827, "warnings": ["Model dilatih pada teks bahasa Inggris."]}
  ],
  "count": 2,
  "warnings": ["Model dilatih pada teks bahasa Inggris."]
}
```

---

### 5. Prediksi batch via CSV (upload file)

```bash
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -F "file=@jobs.csv"
```

> File CSV harus memiliki header kolom yang sesuai dengan field model (misalnya `title`, `description`, `company_profile`, dst.). Ukuran maksimum 5 MB, maksimum 500 baris per request.

---

## Endpoint API

| Method | Path | Keterangan |
|---|---|---|
| `GET` | `/health` | Status server & model |
| `GET` | `/api/v1/model-info` | Metadata model (versi, metrik, threshold) |
| `POST` | `/api/v1/predict` | Prediksi satu lowongan (JSON) |
| `POST` | `/api/v1/predict/batch` | Prediksi banyak lowongan (JSON atau CSV upload) |
| `GET` | `/docs` | Swagger UI interaktif |
| `GET` | `/ui` | Antarmuka Gradio |

Lihat spesifikasi lengkap di [`docs/02-design/api-spec.md`](docs/02-design/api-spec.md).

---

## Antarmuka Web (UI)

Buka http://localhost:8000/ui — antarmuka Gradio dengan tiga tab:

1. **Cek Satu Lowongan** — isi form field, klik Analisis, lihat label ASLI/PALSU + probabilitas.
2. **Cek Banyak (CSV)** — upload file CSV, unduh hasil prediksi.
3. **Tentang Model** — informasi model, metrik evaluasi, dan peringatan.

---

## Struktur Proyek

```
fake-job-detector/
├── AGENTS.md              # instruksi untuk agen coding (Codex, opencode)
├── GEMINI.md              # instruksi untuk Antigravity → mengarah ke AGENTS.md
├── Dockerfile             # image produksi (python:3.11-slim, non-root user)
├── Makefile               # perintah umum (install, test, lint, run, docker-*)
├── requirements.txt       # dependensi runtime (scikit-learn==1.9.1 wajib)
├── requirements-dev.txt   # dependensi dev (pytest, ruff, httpx, dsb.)
├── docs/                  # dokumen per fase Waterfall (01 s.d. 06) + PHASE_STATUS.md
├── models/
│   ├── current/           # MODEL AKTIF: joblib + fake_job_utils.py + metadata
│   └── archive/           # versi model lama
├── notebooks/             # notebook Colab pelatihan model
├── src/
│   └── detector/
│       ├── api.py         # FastAPI app + Gradio mount
│       ├── config.py      # konfigurasi via env var
│       ├── model_loader.py# singleton ModelService
│       ├── schemas.py     # Pydantic v2 schemas
│       └── ui.py          # Gradio Blocks UI
└── tests/                 # pytest — 58 test, coverage 92%
```

---

## Alur Kerja Waterfall

| Fase | Folder dokumen | Output utama | Status |
|---|---|---|---|
| 1. Requirements | `docs/01-requirements/` | SRS (FR & NFR) | ✅ Lulus |
| 2. Design | `docs/02-design/` | Arsitektur, API spec, UI design | ✅ Lulus |
| 3. Implementation | `docs/03-implementation/` | Kode `src/` (T-01 s.d. T-09) | ✅ Lulus |
| 4. Testing | `docs/04-testing/` | Laporan uji, coverage 92% | ✅ Lulus |
| 5. Deployment | `docs/05-deployment/` | Docker + panduan rilis | 🔄 Aktif |
| 6. Maintenance | `docs/06-maintenance/` | Monitoring, retraining | ⏳ Terkunci |

Status detail ada di [`docs/PHASE_STATUS.md`](docs/PHASE_STATUS.md).

---

## Memakai Agen Coding

- **Codex / opencode**: jalankan di root proyek; keduanya membaca `AGENTS.md`. Tempel isi `prompts/phase-N-*.md`.
- **Antigravity**: membaca `GEMINI.md` (sudah mengarah ke `AGENTS.md`). Tempel prompt fase yang sama.
- Kerjakan **satu fase per sesi**; minta agen memperbarui `docs/PHASE_STATUS.md` di akhir sesi.
