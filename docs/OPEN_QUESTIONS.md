# Pertanyaan Terbuka (Open Questions) — Fase 1 (Requirements)

Dokumen ini mencatat hal-hal ambigu atau keputusan produk yang memerlukan konfirmasi dari Pemilik Proyek.
Sesuai aturan Waterfall pada `AGENTS.md`: jika ada ambiguitas, sistem mengadopsi **asumsi paling konservatif** agar tidak mengarang fitur atau membengkakkan cakupan (*scope creep*).

---

### OQ-01: Dukungan Bahasa Teks Lowongan
* **Pertanyaan:** Apakah sistem perlu mendukung lowongan berbahasa Indonesia pada versi 1.0?
* **Konteks:** Model Machine Learning saat ini (pipeline TF-IDF + Logistic Regression pada `models/current/`) dilatih secara eksklusif menggunakan korpus lowongan kerja berbahasa Inggris (dataset EMSCAD).
* **Asumsi Konservatif yang Diambil:**
  - Versi 1.0 **hanya mendukung inferensi teks bahasa Inggris**.
  - Sistem menampilkan peringatan (*disclaimer*) eksplisit di UI (`/ui`) dan respons API (`warnings` array): *"Model dilatih pada teks bahasa Inggris; hasil adalah indikasi, bukan keputusan final."*
  - Dukungan multibahasa / bahasa Indonesia dicatat sebagai *future improvement* pada Fase 6 (Maintenance) yang membutuhkan dataset lokal dan/atau fine-tuning model representasi teks (seperti IndoBERT).
* **Status:** Menunggu konfirmasi pemilik proyek.

---

### OQ-02: Kebijakan Penyimpanan Riwayat Prediksi & Privasi
* **Pertanyaan:** Apakah hasil prediksi dan teks lowongan perlu disimpan ke dalam database riwayat (*history*)? Jika ya, bagaimana kebijakan privasinya?
* **Konteks:** Menyimpan teks lowongan pengguna dapat memicu isu kepatuhan privasi (UU Pelindungan Data Pribadi / GDPR) jika teks mengandung identitas pribadi pelamar/rekruter, serta membutuhkan infrastruktur database persisten (PostgreSQL/SQLite).
* **Asumsi Konservatif yang Diambil:**
  - Versi 1.0 beroperasi secara **murni stateless** (tanpa database penyimpanan lowongan pengguna).
  - Teks mentah lowongan **dilarang keras** ditulis ke log aplikasi (`NFR-03`). Log hanya mencatat ID transaksi, stempel waktu, status HTTP, durasi pemrosesan, probabilitas, dan label prediksi.
  - Untuk pengguna batch CSV di UI, hasil anotasi dapat diunduh langsung (*client-side download*) saat sesi browser berlangsung tanpa disimpan di server.
* **Status:** Menunggu konfirmasi pemilik proyek.

---

### OQ-03: Penentuan Target Pengguna Utama & Fokus UI
* **Pertanyaan:** Siapa target pengguna utama: pencari kerja perorangan atau admin/auditor portal lowongan?
* **Konteks:** Mempengaruhi prioritas tata letak UI dan optimalisasi fitur.
* **Asumsi Konservatif yang Diambil:**
  - Sistem melayani **kedua profil pengguna** dengan pemisahan saluran yang jelas:
    1. **Pencari Kerja Perorangan:** Dilayani via antarmuka web tab "Cek Satu Lowongan" (`/ui`) dengan form interaktif dan lencana risiko visual.
    2. **Auditor / Analis Bursa Kerja:** Dilayani via tab "Cek Banyak (CSV)" (`/ui`) dan REST API terprogram (`/api/v1/predict/batch`).
* **Status:** Menunggu konfirmasi pemilik proyek.

---

### OQ-04: Penanganan Kolom Ekstra / Tidak Dikenal pada Berkas Batch CSV
* **Pertanyaan:** Bagaimana sistem bersikap jika berkas CSV yang diunggah pengguna memuat kolom-kolom tambahan di luar 16 kolom fitur model (misalnya kolom `job_id`, `posted_date`, `url`, `notes`)?
* **Konteks:** Pengguna batch seringkali mengunggah dataset ekspor mentah yang memuat ID pelacak internal mereka.
* **Asumsi Konservatif yang Diambil:**
  - Kolom ekstra yang tidak dikenal atau kolom terlarang (`job_id`, `fraudulent`) **diabaikan dari ekstraksi fitur model**, namun kolom asli dipertahankan dalam berkas hasil unduhan CSV sehingga pengguna tidak kehilangan metadata pelacak mereka.
  - Baris dengan format rusak / non-parsable ditandai dengan error pada baris tersebut tanpa menggagalkan pemrosesan seluruh baris lain dalam batch.
* **Status:** Menunggu konfirmasi pemilik proyek.

---

### OQ-05: Batas Kuota Batch & Ukuran File CSV
* **Pertanyaan:** Apakah batas maksimal 500 baris dan ukuran berkas 5 MB per panggilan batch sudah mencukupi kebutuhan operasional?
* **Konteks:** Pembatasan diperlukan untuk mencegah kehabisan memori (*out of memory*) dan menjaga waktu respons server tetap di bawah 15 detik pada spesifikasi kontainer standar.
* **Asumsi Konservatif yang Diambil:**
  - Menetapkan batas tegas: maksimal 500 baris per panggilan batch dan ukuran berkas CSV maksimal 5 MB. Permintaan melebihi batas ini ditolak dengan kode status HTTP 422 (*Unprocessable Entity*).
* **Status:** Menunggu konfirmasi pemilik proyek.

---

### OQ-06: Arsitektur Navigasi Multi-Halaman pada Gradio UI
* **Pertanyaan:** Bagaimana navigasi antar-halaman (Beranda, Cek Lowongan, Cek CSV, Pusat Edukasi, Tentang) diimplementasikan di Gradio agar mulus tanpa *page reload* dan tanpa dependensi framework tambahan?
* **Konteks:** Gradio menjalankan aplikasi sebagai Single Page Application (SPA). Komponen `gr.Tabs` adalah mekanisme standar bawaan Gradio untuk navigasi multi-bagian tanpa merusak state sesi pengguna atau memicu reload halaman penuh.
* **Asumsi Konservatif yang Diambil:**
  - Menggunakan top-level `gr.Tabs` dengan styling tab modern/pills terpadu (5 tab: 🏠 Beranda, 🔎 Cek Lowongan, 📂 Cek Banyak (CSV), 🛡️ Pusat Edukasi, ℹ️ Tentang JobShield).
  - Tautan Call-to-Action (CTA) di halaman Beranda disediakan sebagai panduan aksi yang jelas menuju tab Cek Lowongan dan Pusat Edukasi tanpa membuat tautan anchor mati.
* **Status:** Menunggu konfirmasi pemilik proyek (CR-2026-11-05-01).

---

### OQ-07: Pencegahan CSV Formula Injection (CSV Injection / Formula Injection)
* **Pertanyaan:** Apakah berkas CSV beranotasi hasil analisis batch perlu disanitasi terhadap potensi CSV Formula Injection saat diekspor untuk diunduh pengguna?
* **Konteks:** Jika pengguna mengunggah teks lowongan yang diawali dengan `=`, `+`, `-`, atau `@`, aplikasi spreadsheet (Excel / Google Sheets) dapat mengeksekusinya sebagai formula saat dibuka oleh pengguna akhir.
* **Asumsi Konservatif yang Diambil:**
  - Menerapkan sanitasi defensif pada pembuatan file CSV hasil unduhan: menambahkan prefix tanda petik tunggal (`'`) jika nilai sel teks diawali dengan karakter formula (`=`, `+`, `-`, `@`, `\t`, `\r`).
  - Kolom asli dan struktur tabel tetap utuh.
* **Status:** Menunggu konfirmasi pemilik proyek (CR-2026-11-05-01).

---

### OQ-08: Panduan Verifikasi Interaktif & Kepatuhan Privasi Pusat Edukasi
* **Pertanyaan:** Apakah checklist interaktif sebelum melamar di Pusat Edukasi memerlukan penyimpanan status ke backend atau inferensi AI?
* **Konteks:** Pengguna membutuhkan alat bantu cepat untuk mengecek kewajaran lowongan secara mandiri sebelum melamar.
* **Asumsi Konservatif yang Diambil:**
  - Checklist beroperasi secara murni di sisi antarmuka pengguna (stateless di sesi browser).
  - Tidak ada data pribadi pelamar yang dikirim ke server, disimpan ke basis data, maupun diproses oleh model Machine Learning.
  - Teks modul edukasi disesuaikan dengan pola-pola penipuan rekrutmen aktual di Indonesia (permintaan uang seragam, travel agen fiktif, tugas like/deposit online, WhatsApp recruiter fiktif).
* **Status:** Menunggu konfirmasi pemilik proyek (CR-2026-11-05-01).
