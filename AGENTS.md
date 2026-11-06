# AGENTS.md — Fake Job Detector

Kamu adalah agen coding yang membangun sistem deteksi lowongan kerja palsu di sekitar model ML yang **sudah jadi**.
Proyek ini memakai **Waterfall**. Baca aturan ini sebelum mengubah apa pun.

## Aturan Waterfall (WAJIB)
1. Baca `docs/PHASE_STATUS.md`. Kerjakan hanya **fase aktif** (yang pertama belum dicentang gate-nya).
2. Dilarang melompat fase atau menulis kode fitur yang belum ada di SRS (`docs/01-requirements/SRS.md`).
3. Dilarang mengubah dokumen fase yang sudah lulus gate, kecuali lewat entri di `docs/CHANGE_LOG.md` (alasan + dampak).
4. Setiap fase selesai ketika semua item *Definition of Done* di dokumennya terpenuhi; lalu centang gate di `docs/PHASE_STATUS.md` dan tulis ringkasan 3–5 baris.
5. Jika ada ambiguitas pada requirement: catat di `docs/OPEN_QUESTIONS.md` dan lanjutkan dengan asumsi paling konservatif — jangan mengarang fitur.

## Model AI (jangan dilatih ulang di sini)
- Artefak model ada di `models/current/`: `fake_job_detector.joblib`, `fake_job_utils.py`, `model_metadata.json`, `requirements.txt`.
- Model adalah scikit-learn Pipeline: input = DataFrame berkolom mentah (`RAW_COLUMNS`), output `predict_proba`.
- Gunakan `src/detector/model_loader.py` (sudah jadi) — jangan memuat joblib di tempat lain. `fake_job_utils` harus dapat di-import saat memuat model (loader sudah menambahkan `models/current` ke `sys.path`).
- Threshold keputusan ada di bundle (`threshold`); jangan di-hardcode.
- Pelatihan/evaluasi ulang model dilakukan di `notebooks/`, bukan di `src/`. Model baru ditaruh di `models/current/` dan yang lama dipindah ke `models/archive/<tanggal>/`.
- Model dilatih pada teks **bahasa Inggris**; tampilkan peringatan ini di UI dan respons API (`warnings`).

## Stack
Python 3.10+, FastAPI (API), Gradio (UI, di-mount di `/ui`), pytest, Docker. Tidak menambah dependensi besar tanpa mencatatnya di `docs/02-design/architecture.md`.

## Perintah
- `make install` · `make test` · `make run` (uvicorn, port 8000) · `make lint` · `make docker-build`

## Gaya kode
- Type hints, docstring singkat, tanpa side-effect saat import. Konfigurasi lewat `src/detector/config.py` (env var), bukan hardcode.
- Jangan menyimpan teks lowongan mentah ke log (privasi); log hanya id permintaan, probabilitas, dan label.
- Tiap fitur baru wajib punya test di `tests/`. Jangan menurunkan coverage di bawah 80% pada `src/`.

## Definition of Done umum
Test hijau (`make test`), lint bersih, dokumen fase aktif ter-update, `docs/PHASE_STATUS.md` ter-update.
