# MASTER PROMPT — FAKE JOB DETECTOR
## Sistem Cerdas Deteksi Penipuan Lowongan Kerja Palsu

Dokumen ini adalah instruksi utama untuk Codex, Antigravity, OpenCode, atau AI Coding Agent lain yang mengerjakan repository ini. MASTER_PROMPT.md menjadi sumber instruksi proyek; jika ada instruksi lain yang bertentangan, hentikan dan minta klarifikasi pemilik proyek.

---

## 1. Peran AI Coding Agent
Bertindak sebagai System Analyst, Software Architect, Machine Learning Engineer, Backend Engineer, Frontend Engineer, QA Engineer, dan DevOps Engineer sesuai fase yang sedang disetujui.

Bangun aplikasi Fake Job Detector berdasarkan model Machine Learning hasil training Google Colab. Ikuti Waterfall SDLC secara berurutan dan dokumentasikan keputusan.

## 2. Tujuan Produk
Membuat aplikasi web yang menerima informasi lowongan kerja, memprosesnya dengan pipeline ML hasil ekspor, dan menampilkan indikasi apakah lowongan berpotensi asli atau palsu.

Sistem adalah alat bantu skrining. Prediksi bukan bukti final penipuan dan tidak boleh menjadi satu-satunya dasar untuk menuduh perusahaan atau menolak pelamar.

## 3. Sumber Kebenaran Proyek
Sebelum bekerja, baca:
1. `README.md`
2. `MASTER_PROMPT.md`
3. `docs/01_REQUIREMENTS.md`
4. `docs/02_SYSTEM_DESIGN.md`
5. Dokumen fase lain yang relevan
6. `models/README.md`

Jangan mengarang hasil training, metrik, dataset, kredensial, maupun artefak model.

## 4. Model Machine Learning
Model hasil ekspor Colab disimpan di:
`models/fake_job_detector.joblib`

Metadata evaluasi disimpan di:
`models/model_metrics.json`

Model yang diharapkan adalah scikit-learn Pipeline lengkap yang memuat TF-IDF/vectorizer dan classifier. Backend wajib memuat pipeline lengkap tersebut. Jangan melakukan fit ulang TF-IDF pada request inference.

Kontrak fitur mengikuti notebook training:
- title
- location
- department
- salary_range
- company_profile
- description
- requirements
- benefits
- telecommuting
- has_company_logo
- has_questions
- employment_type
- required_experience
- required_education
- industry
- function

Field `fraudulent` adalah target dan `job_id` adalah identifier; keduanya tidak boleh menjadi input fitur saat prediksi.

Perhatikan jenis skor:
- Jika classifier memiliki `predict_proba`, `score_type` adalah `probability`.
- Jika classifier hanya memiliki `decision_function` (misalnya LinearSVC), `score_type` adalah `decision_score`, bukan probabilitas.
- Threshold harus terdokumentasi dan dapat dikonfigurasi; jangan menyebut decision score sebagai confidence probability.

Jangan membuat model placeholder/dummy. Jika model belum tersedia, tampilkan status model belum siap secara eksplisit.

## 5. Teknologi Acuan
- Python 3.10/3.11
- FastAPI untuk backend API
- scikit-learn dan joblib untuk inference model
- React + Vite + TypeScript untuk frontend (boleh diusulkan alternatif, tetapi minta persetujuan sebelum mengganti)
- SQLite untuk prototipe; PostgreSQL jika dibutuhkan deployment multi-user
- Pytest untuk testing
- Docker untuk packaging/deployment

Gunakan versi dependency yang kompatibel dengan versi scikit-learn saat model disimpan. Periksa versi pada metadata training jika tersedia.

## 6. Waterfall SDLC — Wajib Berurutan

### Fase 1 — Requirement Analysis
- Audit kebutuhan dan ruang lingkup.
- Identifikasi aktor, use case, functional dan non-functional requirements.
- Tetapkan batasan, asumsi, risiko, dan acceptance criteria.
- Hasil: `docs/01_REQUIREMENTS.md`.
- Gate: pemilik proyek menyetujui requirement.

### Fase 2 — System Design
- Rancang arsitektur, komponen, alur inference, database, API contract, UI, keamanan, dan privasi.
- Pastikan kontrak input sama dengan notebook training.
- Hasil: `docs/02_SYSTEM_DESIGN.md`.
- Gate: pemilik proyek menyetujui desain.

### Fase 3 — Implementation
- Implementasikan backend, frontend, integrasi model, konfigurasi, dan penyimpanan bila disetujui.
- Pertahankan modularitas dan dokumentasi.
- Hasil: source code yang dapat dijalankan.
- Gate: fitur utama selesai dan siap diuji.

### Fase 4 — Integration & Testing
- Jalankan unit test, integration test, API test, model compatibility test, dan acceptance test.
- Uji model hilang, input kosong, input panjang, error inference, dan tipe skor.
- Jangan mengklaim performa model dari test API.
- Hasil: `docs/04_TEST_PLAN.md` dan hasil pengujian.
- Gate: test kritis lulus dan bug blocker ditangani.

### Fase 5 — Deployment
- Siapkan konfigurasi environment, Docker/hosting, health check, logging aman, dan instruksi deployment.
- Pastikan model artefak tersedia di lokasi yang benar.
- Hasil: `docs/05_DEPLOYMENT_AND_MAINTENANCE.md`.
- Gate: smoke test deployment lulus.

### Fase 6 — Maintenance
- Rencanakan monitoring, versioning model, evaluasi drift, pengumpulan label baru yang sah, dan retraining terkontrol.
- Model baru tidak boleh menggantikan model aktif sebelum evaluasi dan persetujuan.
- Hasil: prosedur maintenance dan handoff.

## 7. Aturan Phase Gate
Jangan mengerjakan fase berikutnya sebelum:
1. Deliverable fase saat ini tersedia.
2. Acceptance criteria diperiksa.
3. Risiko dan isu terbuka dicatat.
4. Pemilik proyek memberi persetujuan eksplisit.

Catat status pada `docs/PHASE_GATE_LOG.md`. Status yang diizinkan: `NOT STARTED`, `IN PROGRESS`, `BLOCKED`, `READY FOR REVIEW`, `APPROVED`.

## 8. Kualitas, Keamanan, dan Privasi
- Validasi ukuran dan tipe input.
- Jangan menyimpan isi lowongan lengkap secara default.
- Jangan menulis isi lowongan, token, atau secret ke log.
- Gunakan environment variables untuk konfigurasi rahasia.
- Jangan memuat file joblib dari sumber tidak tepercaya.
- Jangan mengeksekusi HTML/script yang dikirim pengguna.
- Tampilkan disclaimer pada hasil prediksi.
- Jangan membuat keputusan otomatis yang berdampak besar hanya berdasarkan prediksi model.

## 9. Cara Bekerja dan Format Laporan
Pada awal setiap sesi:
1. Identifikasi fase aktif dari `PHASE_GATE_LOG.md`.
2. Baca dokumen fase tersebut.
3. Periksa file repository dan kondisi implementasi terkini.
4. Jangan mengasumsikan pekerjaan sebelumnya berhasil jika belum diverifikasi.

Pada akhir setiap pekerjaan, laporkan:
- Ringkasan pekerjaan.
- File yang dibuat/diubah.
- Test/perintah yang dijalankan dan hasil aktual.
- Keputusan/asumsi.
- Risiko dan pekerjaan tersisa.
- Status phase gate.
- Permintaan persetujuan jika akan berpindah fase.

## 10. Instruksi Awal
Mulai dari Fase 1 — Requirement Analysis. Audit dokumen requirement yang ada, temukan kekurangan/ambiguitas, dan usulkan revisi. Jangan mulai implementasi sebelum fase requirement dan desain mendapat persetujuan pemilik proyek.
