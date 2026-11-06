# Desain Sistem (System Design Specification)

Dokumentasi lengkap perancangan sistem Fase 2 (System Design) terbagi menjadi 3 dokumen terperinci:

1. **[Arsitektur Sistem (`docs/02-design/architecture.md`)](./02-design/architecture.md)**:
   - Diagram topologi monolitik modular terpadu (FastAPI + Gradio).
   - Diagram urutan (*sequence diagrams*) untuk inferensi single dan batch.
   - Kebijakan privasi *zero-raw-text logging* dan strategi pencegahan DoS.
   - Strategi concurrency & mitigasi blocking event loop ASGI.

2. **[Spesifikasi API (`docs/02-design/api-spec.md`)](./02-design/api-spec.md)**:
   - Skema lengkap data Pydantic masukan dan keluaran (`JobPosting`, `PredictionResult`, `BatchPredictResponse`, dll.).
   - Spesifikasi endpoint (`GET /health`, `GET /api/v1/model-info`, `POST /api/v1/predict`, `POST /api/v1/predict/batch`).
   - Formula penetapan tingkat risiko berjenjang 3 level.
   - Contoh pemanggilan konkret menggunakan perintah `curl`.

3. **[Rancangan Antarmuka Pengguna (`docs/02-design/ui-design.md`)](./02-design/ui-design.md)**:
   - Rancangan antarmuka Gradio 3 tab (Cek Satu Lowongan, Cek Banyak CSV, Tentang Model).
   - Wireframe visual ASCII untuk setiap tab.
   - Standar aksesibilitas warna + teks eksplisit ramah buta warna.
   - Alur pengunduhan berkas CSV hasil batch.
