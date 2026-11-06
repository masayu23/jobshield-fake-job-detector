# Rancangan Antarmuka Pengguna (UI Design) — Fase 2 (System Design)
**Proyek:** Sistem Cerdas Deteksi Penipuan Lowongan Kerja Palsu (Fake Job Detector)  
**Dokumen:** `docs/02-design/ui-design.md`  
**Versi:** 1.0  
**Status:** Siap Ditinjau (Phase 2 Review)  
**Teknologi UI:** Gradio 4+ (Blocks API) di-mount langsung pada FastAPI di rute `/ui`  
**Bahasa UI:** Bahasa Indonesia (Baku, Informatif, dan Aksesibel)  
**Acuan SRS:** `docs/01-requirements/SRS.md` (FR-01, FR-02, FR-07, FR-08, FR-09, FR-10, NFR-08)  

---

## 1. Prinsip Desain & Aksesibilitas (*Accessibility First*)

1. **Aksesibilitas Buta Warna (NFR-08):** Indikator risiko tidak pernah mengandalkan warna semata. Setiap status selalu memadukan:
   - Warna latar/bingkai (Hijau / Kuning / Merah).
   - Ikon visual emoji/simbol (✅ / ⚠️ / 🚨).
   - Teks label status eksplisit ("ASLI - Risiko Rendah", "ASLI - Waspada", "PALSU - Risiko Tinggi").
2. **Kejelasan Penafian (FR-07):** Peringatan bahwa model dilatih pada teks berbahasa Inggris dan merupakan alat bantu skrining ditampilkan secara permanen pada header aplikasi.
3. **Pemisahan Tingkat Kompleksitas (FR-01):** Formulir input membedakan antara bidang utama wajib (`title`, `description`) dengan 14 bidang opsional yang dikelompokkan rapi dalam *collapsible accordion* agar antarmuka tetap bersih dan tidak membebani pengguna baru.
4. **Pencegahan Error Pengguna:** Validasi interaktif pada browser sebelum data dikirim ke backend.

---

## 2. Tata Letak Global (*Global Layout Structure*)

Halaman antarmuka web `/ui` memiliki struktur tata letak Modern SaaS terpusat:
- **Header Global:** Top brand bar JobShield dengan badge status dan deskripsi sistem.
- **Peringatan & Penafian Transparansi:** Banner resmi mengenai batasan bahasa dan fungsi skrining awal.
- **Tab Navigasi Utama (5 Bagian):**
  - **Tab 1: 🏠 Beranda (*Home & Overview*):** Hero CTA, 3 kartu fitur interaktif, alur kerja 3 langkah.
  - **Tab 2: 🔎 Cek Lowongan (*Single Job Inspection*):** Form terstruktur (wajib & opsional accordion), lencana risiko, skor model, ambang batas, saran tindakan, dan panduan verifikasi mandiri.
  - **Tab 3: 📂 Cek Banyak (CSV) (*Batch CSV Analysis*):** Dropzone berkas, ringkasan KPI, pratinjau tabel, dan ekspor CSV beranotasi dengan perlindungan Formula Injection.
  - **Tab 4: 🛡️ Pusat Edukasi (*Anti-Scam Education & Safety*):** 5 modul edukasi modus scam di Indonesia, checklist interaktif sebelum melamar, dan FAQ.
  - **Tab 5: ℹ️ Tentang JobShield (*System Transparency & Verified Privacy*):** Penjelasan cara kerja bahasa awam, batasan model, transparansi privasi stateless (*Zero Raw-Text Logging*), dan detail teknis metrik hold-out.
- **Footer Global:** Tautan status sistem, batasan AI, dan hak akses.

---

## 3. Detail Rancangan per Tab

---

### 3.1 Header Global & Penafian (FR-07)
```
+----------------------------------------------------------------------------------------------------+
|  🔍 FAKE JOB DETECTOR — Sistem Cerdas Deteksi Penipuan Lowongan Kerja                              |
|  Skrining keamanan lowongan kerja daring berbasis Machine Learning & Natural Language Processing    |
+----------------------------------------------------------------------------------------------------+
|  ⚠️ PERINGATAN & PENAFIAN RESMI (DISCLAIMER):                                                      |
|  • Model AI dilatih khusus pada korpus teks lowongan kerja berbahasa Inggris.                       |
|  • Hasil deteksi adalah indikasi potensi risiko (skrining awal), BUKAN vonis mutlak atau bukti     |
|    hukum. Jangan gunakan sebagai satu-satunya dasar untuk menolak pelamar atau menuduh perusahaan. |
+----------------------------------------------------------------------------------------------------+
```

---

### 3.2 Tab 1: "Cek Satu Lowongan" (FR-01, FR-02, FR-07, FR-10)

Tab ini ditujukan bagi pencari kerja perorangan yang ingin menguji satu lowongan kerja secara mendalam.

#### Komponen Antarmuka:
1. **Tombol Preset Cepat (FR-10):**
   - `[ 📋 Muat Contoh Lowongan Sah ]`: Mengisi form otomatis dengan lowongan "Senior Software Engineer" (Acme Systems).
   - `[ ⚠️ Muat Contoh Lowongan Penipuan ]`: Mengisi form otomatis dengan lowongan "Earn $5000/week WhatsApp registration fee".
   - `[ 🔄 Bersihkan Formulir ]`: Mengosongkan seluruh kolom masukan.
2. **Bagian Wajib (Mandatory Fields):**
   - **Judul Lowongan (`title`):** Textbox baris tunggal, placeholder: *"Contoh: Senior Python Backend Engineer"* (Wajib, maks 500 karakter).
   - **Deskripsi Pekerjaan (`description`):** Textarea multibaris (minimal 6 baris), placeholder: *"Tempelkan isi deskripsi pekerjaan lengkap di sini..."* (Wajib, maks 20.000 karakter).
3. **Bagian Tambahan (Collapsible Accordion — "Informasi Tambahan (Opsional)"):**
   - `company_profile`: Textarea, profil singkat perusahaan (maks 20.000 karakter).
   - `requirements`: Textarea, kualifikasi/syarat pelamar (maks 20.000 karakter).
   - `benefits`: Textarea, fasilitas/tunjangan kerja (maks 20.000 karakter).
   - `location`: Textbox, format: *"US, CA, San Francisco"* atau *"Indonesia, Jakarta"*.
   - `department`: Textbox, departemen/divisi kerja.
   - `salary_range`: Textbox, kisaran gaji (mis. *"50000-80000"*).
   - `employment_type`: Dropdown (`Full-time`, `Part-time`, `Contract`, `Temporary`, `Other`).
   - `required_experience`: Dropdown (`Entry level`, `Mid-Senior level`, `Associate`, `Director`, `Executive`, `Not Applicable`).
   - `required_education`: Dropdown (`Bachelor's Degree`, `Master's Degree`, `High School or equivalent`, `Unspecified`).
   - `industry`: Textbox, sektor industri perusahaan.
   - `function`: Textbox, fungsi posisi kerja.
   - Opsi Biner (Checkbox / Toggle):
     - `telecommuting`: ☑️ Bekerja Jarak Jauh / Remote (WFH)
     - `has_company_logo`: ☑️ Memiliki Logo Perusahaan Resmi
     - `has_questions`: ☑️ Terdapat Pertanyaan Penyaring Tambahan
4. **Tombol Aksi Utama:**
   - `[ 🚀 PERIKSA KEAMANAN LOWONGAN ]` (Tombol primer, aksen kontras).
5. **Panel Hasil Prediksi (Output Card):**
   - **Lencana Hasil & Tingkat Risiko (FR-02, NFR-08):**
     - Kasus $P < \frac{\text{thr}}{2}$: Kartu Hijau $\rightarrow$ **`✅ ASLI (Risiko Rendah)`**
     - Kasus $\frac{\text{thr}}{2} \le P < \text{thr}$: Kartu Kuning $\rightarrow$ **`⚠️ ASLI (Waspada / Perlu Verifikasi Tambahan)`**
     - Kasus $P \ge \text{thr}$: Kartu Merah $\rightarrow$ **`🚨 PALSU (Risiko Tinggi - Potensi Penipuan)`**
   - **Indikator Probabilitas Penipuan:** Progress bar persentase (mis. `4.12%` atau `89.24%`).
   - **Informasi Threshold Model:** Teks keterbukaan ambang batas (mis. *"Ambang Batas Keputusan: 78.27%"*).
   - **Kotak Rekomendasi & Tindakan Pencegahan:**
     - Jika PALSU/TINGGI: *"Waspada! Model mendeteksi pola penipuan yang kuat. Jangan pernah mentransfer uang, membayar biaya seragam/administrasi, atau mengirimkan data perbankan sensitif."*
     - Jika WASPADA: *"Perhatian! Meskipun belum melampaui ambang batas penipuan, lowongan ini memiliki elemen yang kurang lengkap atau mencurigakan. Pastikan untuk memverifikasi situs resmi perusahaan."*
     - Jika RENDAH: *"Profil lowongan konsisten dengan pola lowongan sah."*

#### Wireframe ASCII Tab 1:
```
+----------------------------------------------------------------------------------------------------+
| [Tab 1: Cek Satu Lowongan] | [Tab 2: Cek Banyak (CSV)] | [Tab 3: Tentang Model]                    |
+----------------------------------------------------------------------------------------------------+
|  Contoh Demo: [ 📋 Contoh Sah ]  [ ⚠️ Contoh Penipuan ]  [ 🔄 Bersihkan ]                          |
|                                                                                                    |
|  KOLOM INPUT LOWONGAN                           |  HASIL ANALISIS KEAMANAN                         |
|  ---------------------------------------------  |  ----------------------------------------------  |
|  Judul Pekerjaan (* Wajib)                      |  +--------------------------------------------+  |
|  [ Senior Software Engineer                  ]  |  | 🚨 PALSU (Risiko Tinggi - Potensi Scam)   |  |
|                                                 |  +--------------------------------------------+  |
|  Deskripsi Lowongan (* Wajib)                   |                                                  |
|  +-------------------------------------------+  |  Probabilitas Penipuan: [ 89.24% ]               |
|  | No experience needed! Earn $5000/week...  |  |  Ambang Batas Model:    [ 78.27% ]               |
|  | Contact WhatsApp immediately...           |  |                                                  |
|  +-------------------------------------------+  |  Rekomendasi Tindakan:                           |
|                                                 |  • JANGAN mengirim uang untuk biaya registrasi.  |
|  ▶ Detail Tambahan (Klik untuk Membuka)         |  • JANGAN memberikan data pribadi sensitif.      |
|    - Profil Perusahaan: [...]                   |  • Laporkan lowongan ini ke pihak berwenang.     |
|    - Lokasi:            [...]                   |                                                  |
|    - Gaji / Tipe Kerja: [...]                   |  Model: A. Logistic Regression (v1.0.0)          |
|    [ ] WFH   [x] Ada Logo   [ ] Ada Pertanyaan  |                                                  |
|                                                 |                                                  |
|  [ 🚀 PERIKSA KEAMANAN LOWONGAN ]               |                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### 3.3 Tab 2: "Cek Banyak (CSV)" (FR-04, FR-08)

Tab ini dirancang untuk analis bursa kerja atau auditor yang menguji puluhan hingga ratusan lowongan kerja sekaligus.

#### Komponen Antarmuka:
1. **Panduan & Unduh Template:**
   - Teks instruksi: *"Unggah berkas CSV berisi data lowongan (maksimal 500 baris, ukuran berkas $\le 5$ MB). Kolom `title` dan `description` wajib ada pada berkas CSV."*
   - Tautan `[ 📥 Unduh Berkas Contoh Template CSV ]` (berisi contoh header 16 kolom).
2. **Widget Unggah Berkas (`gr.File`):**
   - Area drag-and-drop berkas `.csv`.
3. **Tombol Eksekusi:**
   - `[ ⚙️ ANALISIS SELURUH LOWONGAN ]`
4. **Ringkasan Metrik Batch (KPI Summary Cards):**
   - Total Dianalisis (mis. `120 Lowongan`)
   - Risiko Rendah / Sah (mis. `108` - Kartu Hijau)
   - Waspada (mis. `5` - Kartu Kuning)
   - Risiko Tinggi / Palsu (mis. `7` - Kartu Merah)
5. **Pratinjau Tabel Interaktif (`gr.Dataframe`):**
   - Menampilkan baris data asli yang telah diperkaya 3 kolom hasil:
     - `prediksi` (`ASLI` / `PALSU`)
     - `probabilitas_palsu` (mis. `0.9123`)
     - `tingkat_risiko` (`TINGGI` / `WASPADA` / `RENDAH`)
6. **Ekspor & Unduhan (FR-08):**
   - Tombol `[ 📥 UNDUH HASIL LENGKAP (.CSV) ]` yang menghasilkan berkas CSV terunduh secara instan ke komputer pengguna.

#### Wireframe ASCII Tab 2:
```
+----------------------------------------------------------------------------------------------------+
| [Tab 1: Cek Satu Lowongan] | [Tab 2: Cek Banyak (CSV)] | [Tab 3: Tentang Model]                    |
+----------------------------------------------------------------------------------------------------+
|  1. Unggah Berkas Lowongan (Format .CSV, Maks 500 baris / 5 MB)                                    |
|     +----------------------------------------------------------------------------------------+     |
|     |  📁 Tarik & Lepas Berkas CSV di sini atau Klik untuk Memilih Berkas                    |     |
|     +----------------------------------------------------------------------------------------+     |
|     [ 📥 Unduh Template CSV ]   [ ⚙️ ANALISIS SELURUH LOWONGAN ]                                   |
|                                                                                                    |
|  2. Ringkasan Hasil Analisis Batch:                                                                |
|     [ Total: 150 Lowongan ]  [ ✅ Rendah: 135 ]  [ ⚠️ Waspada: 5 ]  [ 🚨 Tinggi (Palsu): 10 ]     |
|                                                                                                    |
|  3. Tabel Pratinjau Hasil:                                                                         |
|     +-------+--------------------------+----------+--------------------+----------------+          |
|     | Baris | Judul Lowongan           | Prediksi | Probabilitas Palsu | Tingkat Risiko |          |
|     +-------+--------------------------+----------+--------------------+----------------+          |
|     | 1     | Senior Data Engineer     | ASLI     | 0.0312             | RENDAH         |          |
|     | 2     | Online Data Entry Scam   | PALSU    | 0.9412             | TINGGI         |          |
|     | 3     | Customer Support Officer | ASLI     | 0.4210             | WASPADA        |          |
|     +-------+--------------------------+----------+--------------------+----------------+          |
|                                                                                                    |
|  4. Unduh Berkas CSV Beranotasi:                                                                   |
|     [ 📥 UNDUH HASIL LENGKAP (.CSV) ]                                                              |
+----------------------------------------------------------------------------------------------------+
```

---

### 3.4 Tab 3: "Tentang Model & Informasi Sistem" (FR-05, FR-07)

Tab ini menyediakan transparansi penuh mengenai model AI yang digunakan, performa empirisnya, dan batasan teknologinya.

#### Komponen Antarmuka:
1. **Kartu Spesifikasi Model:**
   - Nama Algoritma: `A. Logistic Regression (scikit-learn Pipeline)`
   - Waktu Pelatihan: `2026-11-04`
   - Versi scikit-learn: `1.9.1`
   - Nilai Ambang Batas (*Optimal Decision Threshold*): `0.7827`
2. **Tabel Metrik Performa Empiris (Evaluasi Data Hold-out):**
   - Akurasi Keseluruhan: `98.75%`
   - Presisi Kelas Penipuan: `92.62%` (Tingkat False Positive sangat rendah)
   - Recall Kelas Penipuan: `80.70%`
   - F1-Score Kelas Penipuan: `86.25%`
   - Area Under ROC (ROC-AUC): `0.9934`
   - Precision-Recall AUC (PR-AUC): `0.9400`
3. **Penjelasan 16 Fitur Masukan:**
   - Ringkasan bagaimana teks diproses melalui `TfidfVectorizer`, metadata kategorikal di-encode, dan fitur numerik linguistik (kapitalisasi, tanda seru, ada/tidaknya profil perusahaan) digabungkan.
4. **Kebijakan Privasi & Keamanan Data (NFR-03):**
   - Penjelasan bahwa sistem ini murni *stateless*; teks lowongan kerja pengguna tidak pernah disimpan ke basis data dan tidak pernah ditulis ke berkas log server.

---

## 4. Penanganan Kesalahan & Validasi Sisi Klien (*Client-Side Feedback*)

1. **Judul / Deskripsi Kosong:**
   - Jika pengguna menekan tombol "Periksa" tanpa mengisi judul atau deskripsi, UI menampilkan notifikasi peringatan (*Gradio Info/Warning Toast*): *"Mohon isi Judul dan Deskripsi lowongan terlebih dahulu."* tanpa melakukan request sia-sia ke backend.
2. **Format Berkas CSV Rusak:**
   - Jika berkas CSV tidak memiliki kolom `title` atau `description`, antarmuka menampilkan pesan error deskriptif yang meminta pengguna menyesuaikan header berkas dengan template yang disediakan.
3. **Model Tidak Siap (503):**
   - Jika layanan model sedang tidak aktif, UI menampilkan status banner merah: *"Layanan klasifikasi sedang tidak tersedia. Silakan hubungi administrator sistem."*

---

## 5. Matriks Pemenuhan Kebutuhan SRS pada UI Design
- **FR-01:** Form lengkap 16 atribut pada Tab 1 (Subbab 3.2).
- **FR-02:** Visualisasi risiko 3 level (Hijau/Kuning/Merah + Teks eksplisit + Probabilitas) (Subbab 3.2).
- **FR-07:** Penafian resmi bahasa Inggris pada Header permanen (Subbab 3.1).
- **FR-08:** Tabel pratinjau dan tombol unduh berkas CSV teranotasi pada Tab 2 (Subbab 3.3).
- **FR-09:** Antarmuka di-mount pada path `/ui` via FastAPI (Bagian 2).
- **FR-10:** Tombol preset demonstrasi lowongan sah & palsu siap klik (Subbab 3.2).
- **NFR-08:** Aksesibilitas warna + teks eksplisit ramah buta warna di seluruh kartu status risiko (Bagian 1).
