# SRS — Software Requirements Specification
**Proyek:** Sistem Cerdas Deteksi Penipuan Lowongan Kerja Palsu (Fake Job Detector)  
**Dokumen:** `docs/01-requirements/SRS.md`  
**Versi:** 1.0 (Disetujui / Approved)  
**Status:** Disetujui Pemilik Proyek (Phase 1 Gate Passed - 2026-11-04)  
**Metodologi:** Waterfall SDLC (Fase 1: Kebutuhan / Requirements Analysis)  

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen
Dokumen Software Requirements Specification (SRS) ini mendefinisikan seluruh kebutuhan fungsional, kebutuhan non-fungsional, batasan arsitektur, dan kriteria penerimaan untuk pengembangan sistem **Fake Job Detector**. Dokumen ini menjadi acuan tunggal (*single source of truth*) bagi fase perancangan (*System Design*), implementasi (*Implementation*), pengujian (*Testing*), penerapan (*Deployment*), dan pemeliharaan (*Maintenance*).

### 1.2 Latar Belakang & Pernyataan Masalah
Penipuan lowongan kerja daring (*fake job scam*) kian marak dan merugikan para pencari kerja, baik secara finansial maupun pencurian identitas pribadi. Lowongan palsu seringkali menyerupai lowongan asli namun memiliki pola linguistik, struktural, atau metadata tertentu (misalnya minimnya profil perusahaan, janji kompensasi tidak realistis, atau tidak adanya logo perusahaan). Proyek ini memanfaatkan model *Machine Learning* terlatih (pipeline scikit-learn Logistic Regression) untuk mendeteksi lowongan palsu secara otomatis, cepat, dan terukur.

### 1.3 Batasan Legal & Penafian (*Disclaimer*)
1. Sistem ini adalah **alat bantu skrining risiko** (*decision support tool*), bukan penentu legalitas mutlak.
2. Prediksi model berupa probabilitas dan label indikatif; hasil prediksi tidak boleh menjadi satu-satunya dasar untuk menuduh organisasi secara hukum atau menolak pelamar secara sepihak.
3. Penafian resmi wajib ditampilkan pada antarmuka pengguna (UI) dan seluruh keluaran REST API:  
   > *"Model dilatih pada teks lowongan kerja berbahasa Inggris; hasil adalah indikasi potensi risiko, bukan keputusan final atau bukti hukum."*

---

## 2. Ruang Lingkup Sistem

### 2.1 Lingkup Pekerjaan (*In-Scope*)
1. **Pemuatan & Pelayanan Model ML**: Mengintegrasikan pipeline model terlatih (`models/current/fake_job_detector.joblib`, `fake_job_utils.py`, `model_metadata.json`) menggunakan modul singleton `ModelService` (`src/detector/model_loader.py`) tanpa melatih ulang (*no runtime retraining*).
2. **REST API (FastAPI)**:
   - Endpoint kesehatan sistem (`GET /health`).
   - Endpoint informasi & metadata model (`GET /api/v1/model-info`).
   - Endpoint prediksi lowongan tunggal berbasis JSON (`POST /api/v1/predict`).
   - Endpoint prediksi sekumpulan lowongan (batch) via JSON payload atau unggah file CSV (`POST /api/v1/predict/batch`).
3. **Antarmuka Pengguna Web (Gradio)**:
   - Antarmuka web ramah pengguna yang di-mount pada path `/ui` di dalam proses FastAPI yang sama.
   - Tab 1: "Cek Satu Lowongan" (analisis detail dengan visualisasi lencana risiko dan probabilitas).
   - Tab 2: "Cek Banyak (CSV)" (unggah CSV, tabel hasil deteksi, dan unduh CSV beranotasi risiko).
   - Tab 3: "Tentang Model" (ringkasan arsitektur model, metrik evaluasi hold-out, threshold, dan keterbatasan).
   - Contoh preset siap pakai (1 lowongan sah dan 1 lowongan penipuan) untuk demonstrasi instan.
4. **Validasi & Keamanan Input**:
   - Skema Pydantic ketat dengan sanitasi karakter dan batasan panjang teks untuk mitigasi serangan Denial of Service (DoS).
   - Penolakan berkas dan entri yang melebihi kuota batch maksimal.
5. **Kebijakan Privasi Ketat (*Zero Raw-Text Logging*)**:
   - Teks mentah lowongan dilarang keras dituliskan ke dalam log sistem atau berkas audit.
   - Log hanya mencatat ID transaksi, stempel waktu, latensi, probabilitas, label prediksi, dan tingkat risiko.
6. **Kontainerisasi & Lingkungan Mandiri**:
   - Berkas `Dockerfile` mandiri untuk build dan eksekusi aplikasi menggunakan Docker dengan hak akses non-root.

### 2.2 Di Luar Ruang Lingkup (*Out-of-Scope*)
1. Pelatihan ulang model (*retraining*) otomatis dalam aplikasi backend (retraining hanya dilakukan terpisah di `notebooks/`).
2. Sistem autentikasi pengguna, manajemen hak akses (RBAC), atau pendaftaran akun (aplikasi bersifat publik/stateless v1.0).
3. Basis data relasional permanen untuk menyimpan riwayat input lowongan pengguna (v1.0 beroperasi stateless demi privasi).
4. Web scraping otomatis ke situs lowongan kerja pihak ketiga (LinkedIn, Indeed, Jobstreet).
5. Verifikasi legalitas entitas perusahaan ke lembaga legal/pemerintah (misal Kemenkumham/AHU).
6. Dukungan pemrosesan bahasa alami multibahasa di luar bahasa Inggris pada v1.0 (dataset pelatihan hanya bahasa Inggris).

---

## 3. Karakteristik Pengguna & Skenario Penggunaan (*Actors & Use Cases*)

### 3.1 Aktor Sistem
1. **Pencari Kerja (*Job Seeker*)**: Pengguna umum non-teknis yang menempelkan teks lowongan kerja yang mereka temukan ke formulir web untuk mengecek tingkat keamanannya.
2. **Auditor / Analis Rekrutmen (*Job Board Auditor*)**: Pengguna profesional yang memiliki daftar lowongan kerja dalam format CSV dan ingin melakukan skrining massal sekaligus mengunduh laporannya.
3. **Pengembang / Sistem Klien (*External Integrator / API Consumer*)**: Aplikasi atau layanan eksternal yang mengonsumsi endpoint REST API untuk mengotomatisasi pipeline deteksi lowongan kerja.
4. **Administrator / DevOps Engineer**: Pengelola infrastruktur yang memantau ketersediaan sistem via health check probe dan memastikan kompatibilitas dependency model.

### 3.2 Diagram Use Case Ringkas
```
+-------------------------------------------------------------+
|                     Fake Job Detector                       |
|                                                             |
|   (Pencari Kerja) ────► [ UC-01: Analisis Lowongan Tunggal ]|
|                                     │                       |
|   (Auditor)       ────► [ UC-02: Analisis Batch CSV ]       |
|                                     │                       |
|   (Auditor)       ────► [ UC-03: Unduh Hasil Batch CSV ]    |
|                                     │                       |
|   (Integrator)    ────► [ UC-04: Prediksi via REST API ]    |
|                                     │                       |
|   (DevOps/Admin)  ────► [ UC-05: Monitor Health & Info ]    |
|                                                             |
+-------------------------------------------------------------+
```

---

## 4. Kebutuhan Fungsional (*Functional Requirements*)

| ID | Nama Kebutuhan | Deskripsi & Spesifikasi Alur | Masukan / Keluaran | Prioritas |
|---|---|---|---|---|
| **FR-01** | Formulir Input Lowongan Tunggal (Web UI) | Sistem menyediakan formulir web interaktif pada tab "Cek Satu Lowongan" di `/ui`. Formulir mencakup input teks untuk 16 atribut fitur raw model, dengan penataan terstruktur (bidang utama di atas, bidang pelengkap di accordion/bagian opsional). | **Masukan:** Data teks & opsi lowongan.<br>**Keluaran:** Tampilan form responsif & tombol "Periksa Lowongan". | **Wajib (Must)** |
| **FR-02** | Klasifikasi & Penentuan Tingkat Risiko | Sistem menghitung probabilitas penipuan (`probabilitas_palsu` $\in [0, 1]$), membandingkannya terhadap ambang batas dinamis (`threshold` dari model bundle), dan mengklasifikasikan ke dalam label serta tingkat risiko:<br>1. $P \ge \text{threshold}$: Label `PALSU`, Risiko `TINGGI`<br>2. $\frac{\text{threshold}}{2} \le P < \text{threshold}$: Label `ASLI`, Risiko `WASPADA`<br>3. $P < \frac{\text{threshold}}{2}$: Label `ASLI`, Risiko `RENDAH` | **Masukan:** Objek data lowongan.<br>**Keluaran:** Tuple `(prediksi, probabilitas_palsu, tingkat_risiko)`. | **Wajib (Must)** |
| **FR-03** | REST API Prediksi Tunggal | Sistem menyediakan endpoint `POST /api/v1/predict` yang menerima payload JSON lowongan tunggal dan mengembalikan hasil evaluasi model secara terstruktur. | **Masukan:** JSON `JobPosting`<br>**Keluaran:** HTTP 200 JSON `{prediksi, probabilitas_palsu, tingkat_risiko, threshold, model, warnings}`. | **Wajib (Must)** |
| **FR-04** | REST API Prediksi Batch | Sistem menyediakan endpoint `POST /api/v1/predict/batch` yang menerima array lowongan via JSON `{ "items": [...] }` atau berkas CSV via `multipart/form-data` (maksimal 500 baris). | **Masukan:** JSON batch atau berkas CSV.<br>**Keluaran:** HTTP 200 JSON `{count, results: [{index, prediksi, probabilitas_palsu, tingkat_risiko}, ...]}`. | **Wajib (Must)** |
| **FR-05** | REST API Informasi Model & Status Layanan | Sistem menyediakan:<br>1. `GET /health`: Pemeriksaan liveness & readiness (`status: ok`, `model_loaded: true`).<br>2. `GET /api/v1/model-info`: Menyajikan metadata model lengkap (nama model, threshold, versi scikit-learn, metrik hold-out & CV, tanggal rilis). | **Masukan:** HTTP GET.<br>**Keluaran:** HTTP 200 JSON health/model-info. | **Wajib (Must)** |
| **FR-06** | Aturan Validasi Input & Nilai Bawaan (*Defaulting*) | 1. Field `title` dan `description` **wajib diisi** dan tidak boleh hanya berisi spasi kosong.<br>2. Field teks lainnya opsional; jika tidak disertakan, sistem mengisinya dengan string kosong (`""`) atau `np.nan`.<br>3. Field biner (`telecommuting`, `has_company_logo`, `has_questions`) bertipe integer `0` atau `1` (default: `0`).<br>4. Atribut `job_id` dan `fraudulent` jika ada pada input/CSV diabaikan dan tidak dimasukkan ke dalam fitur prediksi. | **Masukan:** Payload request.<br>**Keluaran:** Objek tervalidasi atau HTTP 422 Unprocessable Entity dengan rincian error. | **Wajib (Must)** |
| **FR-07** | Peringatan Bahasa & Penafian (*Disclaimer*) | Sistem wajib menampilkan pesan penafian bahasa Inggris dan batasan prediksi pada:<br>1. Header halaman web UI `/ui`.<br>2. Field `warnings` pada setiap respons JSON API prediksi. | **Keluaran:** Teks penafian standar bahasa Indonesia. | **Wajib (Must)** |
| **FR-08** | Analisis Batch & Ekspor CSV (Web UI) | Pada tab "Cek Banyak (CSV)", pengguna dapat mengunggah berkas CSV lowongan, melihat tabel cuplikan hasil klasifikasi di layar, dan mengunduh berkas CSV lengkap yang telah diperkaya dengan kolom hasil (`prediksi`, `probabilitas_palsu`, `tingkat_risiko`). | **Masukan:** Berkas `.csv`.<br>**Keluaran:** Tabel interaktif & tautan/tombol unduh berkas CSV hasil. | **Penting (Should)** |
| **FR-09** | Mounting Web UI pada FastAPI | Seluruh antarmuka Gradio UI di-mount langsung pada routing `/ui` di aplikasi FastAPI utama sehingga sistem berjalan dalam satu proses server uvicorn terpadu. Dokumentasi API interaktif tersedia di `/docs` (Swagger UI). | **Keluaran:** Akses web terpadu port 8000. | **Wajib (Must)** |
| **FR-10** | Contoh Preset Lowongan Demonstrasi | UI menyediakan minimal 2 tombol contoh siap pakai (*presets*):<br>1. **Contoh Sah**: Profil jelas, benefit realistis, logo tersedia, pertanyaan screening aktif.<br>2. **Contoh Penipuan**: Judul mencolok ("Work From Home $5000/week!"), permintaan data bank/WhatsApp, tanpa profil perusahaan. | **Masukan:** Tombol klik preset.<br>**Keluaran:** Form terisi otomatis dengan data contoh. | **Penting (Should)** |

---

## 5. Kebutuhan Non-Fungsional (*Non-Functional Requirements*)

| ID | Kategori | Kebutuhan & Spesifikasi Kuantitatif | Metode Pengukuran | Prioritas |
|---|---|---|---|---|
| **NFR-01** | Kinerja & Latensi | Model ML dimuat hanya sekali ke memori saat startup aplikasi (Singleton Pattern).<br>1. Latensi respons prediksi tunggal: $\le 1{,}0$ detik per permintaan pada CPU standar (2 core / 4 GB RAM).<br>2. Latensi batch 500 baris: $\le 15{,}0$ detik. | Pengujian benchmark otomatis via pytest & locust/timer. | **Wajib (Must)** |
| **NFR-02** | Validasi & Batas Beban (*DoS Prevention*) | 1. Panjang maksimal string `title`: 500 karakter.<br>2. Panjang maksimal string kolom teks (`description`, `company_profile`, `requirements`, `benefits`, dsb.): 20.000 karakter per kolom.<br>3. Ukuran batch maksimal: 500 baris lowongan per request.<br>4. Ukuran berkas CSV maksimal: 5 MB.<br>Pelanggaran aturan mengembalikan HTTP 422 secara instan tanpa membebani model. | Unit test validasi skema Pydantic & boundary testing. | **Wajib (Must)** |
| **NFR-03** | Privasi Data (*Zero Raw-Text Logging*) | Demi perlindungan privasi dan kerahasiaan data (selaras dengan prinsip UU PDP / GDPR):<br>1. Teks mentah lowongan, profil perusahaan, maupun informasi kontak dilarang keras ditulis ke dalam berkas log aplikasi, console, atau stack trace.<br>2. Log hanya mencatat: ID request, stempel waktu, kode status HTTP, waktu pemrosesan, probabilitas prediksi, dan label risiko. | Audit log dan pengujian unit logging capture. | **Wajib (Must)** |
| **NFR-04** | Reprodusibilitas Lingkungan Model | Versi runtime pustaka Machine Learning harus terkunci dan identik dengan metadata pelatihan Colab:<br>- `scikit-learn==1.9.1`<br>- `joblib>=1.3.0`<br>- `pandas>=2.0.0`<br>- `numpy>=1.24.0`<br>Pemuatan model wajib melalui `ModelService` (`src/detector/model_loader.py`) bersama modul pendamping `fake_job_utils.py`. | Smoke test model `test_model_loads_and_has_threshold`. | **Wajib (Must)** |
| **NFR-05** | Kualitas Kode & Cakupan Uji (*Code Quality & Test Coverage*) | 1. Test coverage minimum 80% pada seluruh berkas di direktori `src/detector/`.<br>2. Bebas dari kesalahan linter (PEP 8, flake8/ruff).<br>3. Menggunakan type hints lengkap pada fungsi dan signature endpoint. | `pytest --cov=src` dan `make lint`. | **Wajib (Must)** |
| **NFR-06** | Kontainerisasi & Portabilitas | Sistem dapat dibangun dan dijalankan secara portabel melalui Docker:<br>1. `docker build -t fake-job-detector .`<br>2. `docker run -d -p 8000:8000 fake-job-detector`<br>Image berbasis `python:3.11-slim`, berjalan menggunakan pengguna non-root (*security hardening*), dan lulus smoke test kontainer. | Eksekusi build & run container Docker. | **Wajib (Must)** |
| **NFR-07** | Keamanan Aplikasi (*Application Security*) | 1. Model deserialization (`joblib.load`) hanya dilakukan terhadap berkas lokal terkonfigurasi di `MODEL_DIR`, dilarang memuat artefak dari input pengguna.<br>2. Sanitasi HTML pada antarmuka pengguna untuk mencegah Cross-Site Scripting (XSS).<br>3. Seluruh error unhandled (500) dibungkus rapi tanpa membocorkan trace internal sistem ke klien. | Security code review & dynamic error injection testing. | **Wajib (Must)** |
| **NFR-08** | Aksesibilitas & Kejelasan UI | Seluruh indikator risiko visual wajib mengombinasikan warna dan teks eksplisit (tidak mengandalkan warna semata demi mendukung pengguna dengan keterbatasan penglihatan warna):<br>- Hijau + Teks "ASLI (Risiko Rendah)"<br>- Kuning + Teks "ASLI (Waspada / Perlu Verifikasi Tambahan)"<br>- Merah + Teks "PALSU (Risiko Tinggi)"<br>Seluruh label UI menggunakan Bahasa Indonesia yang baku dan komunikatif. | Review kepatuhan pedoman aksesibilitas UI. | **Penting (Should)** |

---

## 6. Spesifikasi Kontrak Data & Transformasi Fitur

### 6.1 Daftar Kolom Mentah (*Raw Feature Columns*)
Berdasarkan artefak model aktif (`models/current/model_metadata.json`), model mengharapkan tepat 16 atribut masukan berikut:

| # | Nama Kolom | Tipe Data | Kategori Fitur | Deskripsi | Aturan Default Jika Kosong |
|---|---|---|---|---|---|
| 1 | `title` | String | Teks | Judul posisi pekerjaan | **Wajib diisi** (Maks 500 char) |
| 2 | `description` | String | Teks | Uraian tugas & deskripsi lowongan | **Wajib diisi** (Maks 20.000 char) |
| 3 | `company_profile` | String | Teks | Profil / latar belakang perusahaan | Kosong (`""` / `np.nan`) |
| 4 | `requirements` | String | Teks | Syarat kualifikasi pelamar | Kosong (`""` / `np.nan`) |
| 5 | `benefits` | String | Teks | Fasilitas & benefit yang ditawarkan | Kosong (`""` / `np.nan`) |
| 6 | `location` | String | Metadata | Lokasi (format rekomendasi: `Negara, Provinsi, Kota`) | Kosong (`"UNKNOWN"`) |
| 7 | `department` | String | Metadata | Departemen / divisi kerja | Kosong (`np.nan`) |
| 8 | `salary_range` | String | Metadata | Kisaran gaji (mis. `50000-80000`) | Kosong (`np.nan`) |
| 9 | `employment_type` | String | Kategorikal | Jenis kerja (mis. `Full-time`, `Part-time`, `Contract`) | Kosong (`"unknown"`) |
| 10 | `required_experience` | String | Kategorikal | Pengalaman (mis. `Entry level`, `Mid-Senior level`) | Kosong (`"unknown"`) |
| 11 | `required_education` | String | Kategorikal | Pendidikan (mis. `Bachelor's Degree`, `High School`) | Kosong (`"unknown"`) |
| 12 | `industry` | String | Kategorikal | Sektor industri (mis. `Information Technology`) | Kosong (`"unknown"`) |
| 13 | `function` | String | Kategorikal | Fungsi pekerjaan (mis. `Engineering`, `Sales`) | Kosong (`"unknown"`) |
| 14 | `telecommuting` | Integer (0/1) | Biner | Kebijakan kerja jarak jauh / WFH | Default `0` |
| 15 | `has_company_logo` | Integer (0/1) | Biner | Apakah profil memuat logo perusahaan | Default `0` |
| 16 | `has_questions` | Integer (0/1) | Biner | Apakah ada pertanyaan penyaring tambahan | Default `0` |

### 6.2 Aturan Kolom Terlarang (*Prohibited Columns*)
- `fraudulent`: Target ground-truth. Dilarang keras menjadi input inferensi.
- `job_id`: Identifier database. Dilarang diproses sebagai fitur inferensi (hanya diizinkan sebagai referensi tracking baris jika ada di file batch CSV).

---

## 7. Kriteria Penerimaan Model (*Model Acceptance Baseline*)
Model yang digunakan adalah model hasil pelatihan Google Colab yang telah disetujui pada Fase 0:
- **Arsitektur Model:** Pipeline TF-IDF (TfidfVectorizer) + Categorical Encoder + Numerical Feature Union + scikit-learn `LogisticRegression`.
- **Ambang Batas (*Decision Threshold*):** Dinamis dari bundle model, saat ini tercatat bernilai $\approx 0{,}7827$.
- **Performa Evaluasi (*Hold-out Test Set*):**
  - Akurasi: $\ge 0{,}98$ ($0{,}9875$)
  - Presisi Kelas Palsu: $\ge 0{,}90$ ($0{,}9262$)
  - Recall Kelas Palsu: $\ge 0{,}75$ ($0{,}8070$)
  - F1-Score Kelas Palsu: $\ge 0{,}85$ ($0{,}8625$)
  - ROC-AUC: $\ge 0{,}98$ ($0{,}9934$)
  - PR-AUC: $\ge 0{,}90$ ($0{,}9400$)

---

## 8. Asumsi, Ketergantungan, & Batasan Sistem

1. **Asumsi Korpus & Bahasa:** Seluruh model representasi teks (TF-IDF vocabulary) dilatih menggunakan dataset EMSCAD berbahasa Inggris. Sistem mengasumsikan input berupa teks bahasa Inggris agar hasil inferensi akurat.
2. **Ketergantungan Serialisasi Sklearn:** Model `.joblib` sangat sensitif terhadap versi library. Aplikasi bergantung secara mutlak pada `scikit-learn==1.9.1`.
3. **Stateless Architecture:** Sistem tidak menyimpan data masukan lowongan ke basis data persisten. Hasil analisis batch hanya tersedia pada sesi peramban pengguna saat pengunduhan CSV berlangsung.
4. **Alokasi Sumber Daya:** Aplikasi ditargetkan berjalan pada lingkungan server tunggal (minimal 1 vCPU, 2 GB RAM).

---

## 9. Analisis Risiko & Strategi Mitigasi

| Risiko | Dampak | Probabilitas | Strategi Mitigasi |
|---|---|---|---|
| **R-01: False Positive** (Lowongan asli dinyatakan PALSU) | Tinggi: Reputasi perusahaan dirugikan atau pelamar membatalkan lamaran yang sah. | Rendah | Menggunakan threshold optimal ($0{,}7827$) dengan presisi tinggi ($92{,}6\%$), menyediakan kategori risiko menengah `WASPADA`, serta menyertakan penafian legal bahwa hasil bukan keputusan mutlak. |
| **R-02: Input Berbahasa Indonesia** | Sedang: Skor tidak reliabel karena TF-IDF tidak mengenali kosakata Indonesia. | Tinggi | Menampilkan peringatan mencolok di header UI dan response API bahwa model dievaluasi untuk teks bahasa Inggris. |
| **R-03: Serangan DoS Payload Besar** | Tinggi: Server kehabisan memori atau CPU throttling saat parsing payload raksasa. | Sedang | Membatasi ukuran teks (`title` $\le 500$, teks $\le 20.000$ karakter), membatasi batch maksimal 500 baris, dan membatasi ukuran berkas CSV $\le 5$ MB melalui validasi Pydantic / middleware FastAPI. |
| **R-04: Kebocoran Data Privasi pada Log** | Tinggi: Pelanggaran privasi data pelamar atau data internal perusahaan. | Rendah | Melarang keras logging teks mentah lowongan (`NFR-03`), hanya mencatat metadata operasional dan ID permintaan. |
| **R-05: Inkompatibilitas Runtime Model** | Kritis: Aplikasi gagal start (503 / ImportError pada unpickling). | Rendah | Mengunci dependensi pada `requirements.txt` dan mengisolasi eksekusi dalam image Docker berbasis versi Python dan scikit-learn yang identik. |

---

## 10. Matriks Keterlacakan Kebutuhan (*Traceability Matrix*)

| ID Kebutuhan | Nama Kebutuhan | Dokumen Desain (Fase 2) | Implementasi (Fase 3) | Rencana Pengujian (Fase 4) |
|---|---|---|---|---|
| **FR-01** | Formulir Lowongan Tunggal Web | `02-design/ui-design.md` (§3.2 Form Tab 1) | [x] `src/detector/ui.py` (T-08) | `test-plan.md` (UT-01, UT-02, UT-03) |
| **FR-02** | Klasifikasi & Tingkat Risiko | `02-design/api-spec.md` (§4 Formula Risiko), `architecture.md` (§3.1) | [x] `src/detector/model_loader.py` (T-01, T-04) | `tests/test_model_loader.py`, `tests/test_model_sanity.py` |
| **FR-03** | REST API Prediksi Tunggal | `02-design/api-spec.md` (§3.3 POST /predict) | [x] `src/detector/api.py` (T-04) | `tests/test_api.py` |
| **FR-04** | REST API Prediksi Batch | `02-design/api-spec.md` (§3.4 & §3.5 Batch JSON & CSV) | [x] `src/detector/api.py` (T-05) | `tests/test_api.py`, `tests/test_nfr.py` |
| **FR-05** | API Info Model & Health | `02-design/api-spec.md` (§3.1 /health, §3.2 /model-info) | [x] `src/detector/api.py` (T-03) | `tests/test_api.py` |
| **FR-06** | Aturan Validasi & Defaulting | `02-design/api-spec.md` (§2.1 Skema JobPosting) | [x] `src/detector/schemas.py` (T-02) | `tests/test_schemas.py` |
| **FR-07** | Peringatan Bahasa & Penafian | `02-design/ui-design.md` (§3.1), `api-spec.md` (§2.2) | [x] `src/detector/config.py`, `ui.py`, `api.py` (T-04, T-08) | `tests/test_api.py`, `test-plan.md` (UT-01) |
| **FR-08** | Analisis Batch & Ekspor CSV (UI) | `02-design/ui-design.md` (§3.3 Tab 2 Ekspor CSV) | [x] `src/detector/ui.py` (T-08) | `test-plan.md` (UT-04) |
| **FR-09** | Gradio Mounted on FastAPI | `02-design/architecture.md` (§1 Topologi Terpadu) | [x] `src/detector/api.py` (T-08) | `tests/test_api.py` |
| **FR-10** | Preset Contoh Lowongan | `02-design/ui-design.md` (§3.2 Tombol Preset Demo) | [x] `src/detector/ui.py` (T-08) | `test-plan.md` (UT-01, UT-02) |
| **NFR-01** | Kinerja & Latensi | `02-design/architecture.md` (§5 Kinerja & Concurrency) | [x] `src/detector/model_loader.py` (T-06) | `tests/test_nfr.py` |
| **NFR-02** | Validasi & Batas Beban | `02-design/architecture.md` (§4.2), `api-spec.md` (§2.1) | [x] `src/detector/schemas.py`, `config.py` (T-02) | `tests/test_schemas.py`, `tests/test_nfr.py` |
| **NFR-03** | Privasi Data (No Raw Logging) | `02-design/architecture.md` (§4.1 Zero-Text Logging) | [x] `src/detector/api.py` (T-07) | `tests/test_nfr.py` |
| **NFR-04** | Reprodusibilitas Lingkungan | `02-design/architecture.md` (§2 & §7 Runtime Lock) | [x] `requirements.txt`, `model_loader.py` (T-01) | `tests/test_model_loader.py` |
| **NFR-05** | Kualitas Kode & Coverage | `02-design/architecture.md` (§2 Modularitas Paket) | [x] Seluruh `src/detector/` (T-01 s/d T-09) | `pytest --cov=src` |
| **NFR-06** | Kontainerisasi Docker | `02-design/architecture.md` (§1 & §7 Containerization) | [x] `Dockerfile` | Smoke test kontainer Docker |
| **NFR-07** | Keamanan Aplikasi | `02-design/architecture.md` (§4.3 Deserialisasi Aman) | [x] `src/detector/api.py`, `ui.py` | Security review & error injection tests |
| **NFR-08** | Aksesibilitas UI | `02-design/ui-design.md` (§1 & §3.2 Aksesibilitas) | [x] `src/detector/ui.py` (T-08) | UI inspection checklist |

---

## 11. Kriteria Penyelesaian (*Definition of Done*) — Fase 1

Fase 1 (Requirements Analysis) dinyatakan selesai jika dan hanya jika:
- [x] Seluruh kebutuhan fungsional (FR-01 s/d FR-10) dan non-fungsional (NFR-01 s/d NFR-08) telah dirumuskan secara terukur, konsisten, dan bebas ambiguitas.
- [x] Kontrak input 16 fitur mentah selaras dengan metadata model dan `fake_job_utils.py`.
- [x] Pertanyaan terbuka dan asumsi konservatif terdokumentasi di `docs/OPEN_QUESTIONS.md`.
- [x] Matriks keterlacakan (Section 10) terisi penuh menghubungkan kebutuhan ke fase berikutnya.
- [x] Dokumen SRS dan usulan asumsi telah ditinjau dan **disetujui secara eksplisit oleh Pemilik Proyek**.
- [x] Gate Fase 1 dicentang pada `docs/PHASE_STATUS.md` setelah persetujuan pemilik proyek diterima.
