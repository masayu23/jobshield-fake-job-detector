# Spesifikasi API — Fase 2 (System Design)
**Proyek:** Sistem Cerdas Deteksi Penipuan Lowongan Kerja Palsu (Fake Job Detector)  
**Dokumen:** `docs/02-design/api-spec.md`  
**Versi:** 1.0  
**Status:** Siap Ditinjau (Phase 2 Review)  
**Base Path:** `/api/v1` (Endpoint Health Check di `/health`)  
**Format Standar:** JSON (`application/json`) dan Multipart Form untuk Unggah Berkas (`multipart/form-data`)  
**Dokumentasi Otomatis:** Swagger UI interaktif tersedia di `/docs` dan ReDoc di `/redoc`  

---

## 1. Aturan Umum & Header HTTP

### 1.1 Header Permintaan (*Request Headers*)
- `Content-Type: application/json` untuk seluruh endpoint JSON.
- `Content-Type: multipart/form-data` untuk endpoint unggah berkas CSV batch.
- `Accept: application/json`

### 1.2 Format Respon Galat Standar
Seluruh respon galat (4xx dan 5xx) mengikuti skema terpadu berikut:
```json
{
  "detail": "Keterangan penyebab error yang dapat dibaca manusia",
  "code": "VALIDATION_ERROR | MODEL_NOT_READY | PAYLOAD_TOO_LARGE | INTERNAL_ERROR",
  "timestamp": "2026-11-04T20:30:00Z"
}
```

---

## 2. Skema Data Pydantic (*Data Models*)

### 2.1 Skema Masukan: `JobPosting`
Mewakili data satu lowongan kerja yang akan dievaluasi oleh model:

```python
class JobPosting(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Judul posisi pekerjaan (wajib diisi)",
        example="Senior Software Engineer"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Deskripsi pekerjaan lengkap (wajib diisi)",
        example="We are seeking an experienced Python developer to build scalable backend APIs."
    )
    company_profile: Optional[str] = Field(
        default="",
        max_length=20000,
        description="Profil atau latar belakang singkat perusahaan",
        example="Acme Corp is a leading technology company with 500+ employees globally."
    )
    requirements: Optional[str] = Field(
        default="",
        max_length=20000,
        description="Persyaratan kualifikasi dan keahlian pelamar",
        example="5+ years of Python, experience with FastAPI, PostgreSQL, and Docker."
    )
    benefits: Optional[str] = Field(
        default="",
        max_length=20000,
        description="Fasilitas dan tunjangan yang ditawarkan",
        example="Health insurance, 401(k) matching, flexible working hours."
    )
    location: Optional[str] = Field(
        default="",
        max_length=500,
        description="Lokasi kerja (rekomendasi: Negara, Provinsi, Kota)",
        example="US, CA, San Francisco"
    )
    department: Optional[str] = Field(
        default="",
        max_length=500,
        description="Divisi atau departemen pekerjaan",
        example="Engineering"
    )
    salary_range: Optional[str] = Field(
        default="",
        max_length=100,
        description="Kisaran gaji yang ditawarkan",
        example="120000-150000"
    )
    employment_type: Optional[str] = Field(
        default="",
        max_length=100,
        description="Jenis pekerjaan (Full-time, Part-time, Contract, dll.)",
        example="Full-time"
    )
    required_experience: Optional[str] = Field(
        default="",
        max_length=100,
        description="Tingkat pengalaman yang dibutuhkan",
        example="Mid-Senior level"
    )
    required_education: Optional[str] = Field(
        default="",
        max_length=100,
        description="Kualifikasi pendidikan minimum",
        example="Bachelor's Degree"
    )
    industry: Optional[str] = Field(
        default="",
        max_length=500,
        description="Sektor industri perusahaan",
        example="Information Technology and Services"
    )
    function: Optional[str] = Field(
        default="",
        max_length=500,
        description="Fungsi peran pekerjaan",
        example="Engineering"
    )
    telecommuting: Optional[int] = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika remote/WFH, 0 jika on-site",
        example=0
    )
    has_company_logo: Optional[int] = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika memiliki logo perusahaan, 0 jika tidak",
        example=1
    )
    has_questions: Optional[int] = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika ada pertanyaan screening lamaran, 0 jika tidak",
        example=1
    )
```

### 2.2 Skema Keluaran: `PredictionResult`
```python
class PredictionResult(BaseModel):
    prediksi: Literal["ASLI", "PALSU"] = Field(
        ...,
        description="Keputusan biner klasifikasi model berdasarkan ambang batas"
    )
    probabilitas_palsu: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilitas lowongan bersifat penipuan (0.0000 - 1.0000)"
    )
    tingkat_risiko: Literal["RENDAH", "WASPADA", "TINGGI"] = Field(
        ...,
        description="Tingkat risiko berjenjang sistem deteksi"
    )
    threshold: float = Field(
        ...,
        description="Ambang batas keputusan aktif yang dimuat dari bundle model"
    )
    model: str = Field(
        ...,
        description="Nama algoritma dan versi model yang melayani prediksi"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Daftar peringatan bahasa dan penafian resmi"
    )
```

### 2.3 Skema Permintaan & Respon Batch
```python
class BatchPredictJsonRequest(BaseModel):
    items: list[JobPosting] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Daftar lowongan kerja yang akan dianalisis (maks 500 entri)"
    )

class BatchItemResult(BaseModel):
    index: int = Field(..., description="Nomor urut lowongan pada request (0-indexed)")
    prediksi: Literal["ASLI", "PALSU"]
    probabilitas_palsu: float
    tingkat_risiko: Literal["RENDAH", "WASPADA", "TINGGI"]

class BatchPredictResponse(BaseModel):
    count: int = Field(..., description="Total lowongan yang berhasil dianalisis")
    results: list[BatchItemResult] = Field(..., description="Hasil prediksi per baris lowongan")
    threshold: float
    model: str
    warnings: list[str]
```

### 2.4 Skema Info Model & Status Kesehatan
```python
class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    model_loaded: bool
    version: str

class ModelInfoResponse(BaseModel):
    model_name: str
    threshold: float
    raw_columns: list[str]
    metrics_test_holdout: dict[str, float]
    metrics_cv: dict[str, float]
    refit_on_all_data: bool
    sklearn_version: str
    created_at: str
```

---

## 3. Spesifikasi Endpoint Terperinci

---

### 3.1 `GET /health`
* **Tujuan:** Pemeriksaan ketersediaan sistem (*liveness & readiness probe*).
* **Autentikasi:** Bebas (Publik).
* **Respon Sukses (HTTP 200):**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```
* **Respon Degradasi (HTTP 503):** Jika model gagal dimuat saat startup.
```json
{
  "status": "degraded",
  "model_loaded": false,
  "version": "1.0.0"
}
```

---

### 3.2 `GET /api/v1/model-info`
* **Tujuan:** Menyajikan metadata teknis model, metrik evaluasi historis Colab, dan versi library runtime.
* **Respon Sukses (HTTP 200):**
```json
{
  "model_name": "A. Logistic Regression",
  "threshold": 0.7827271690741614,
  "raw_columns": [
    "title", "location", "department", "salary_range", "company_profile",
    "description", "requirements", "benefits", "telecommuting",
    "has_company_logo", "has_questions", "employment_type",
    "required_experience", "required_education", "industry", "function"
  ],
  "metrics_test_holdout": {
    "Accuracy": 0.9875,
    "Precision": 0.9262,
    "Recall": 0.807,
    "F1 (palsu)": 0.8625,
    "F1 @thr 0.5": 0.8466,
    "ROC-AUC": 0.9934,
    "PR-AUC": 0.94,
    "Threshold": 0.7827
  },
  "metrics_cv": {
    "PR-AUC": 0.9086,
    "ROC-AUC": 0.9888,
    "Precision": 0.9109,
    "Recall": 0.7912,
    "F1 (palsu)": 0.8469,
    "Threshold": 0.7827,
    "Waktu (dtk)": 100.4007
  },
  "refit_on_all_data": true,
  "sklearn_version": "1.9.1",
  "created_at": "2026-11-04T18:01:32"
}
```

---

### 3.3 `POST /api/v1/predict`
* **Tujuan:** Melakukan prediksi klasifikasi pada satu entitas lowongan kerja.
* **Payload Masukan (JSON):**
```json
{
  "title": "Senior Software Engineer",
  "description": "Develop and maintain high performance backend microservices in Python and PostgreSQL.",
  "company_profile": "Acme Systems is an established enterprise software company with over 500 team members.",
  "requirements": "5+ years of software engineering experience, BS in Computer Science, proficiency in FastAPI and Docker.",
  "benefits": "Competitive compensation, comprehensive healthcare coverage, 401(k), annual learning budget.",
  "location": "US, CA, San Francisco",
  "employment_type": "Full-time",
  "has_company_logo": 1,
  "has_questions": 1,
  "telecommuting": 0
}
```
* **Respon Sukses (HTTP 200) — Lowongan Asli:**
```json
{
  "prediksi": "ASLI",
  "probabilitas_palsu": 0.0412,
  "tingkat_risiko": "RENDAH",
  "threshold": 0.7827,
  "model": "A. Logistic Regression",
  "warnings": [
    "Model dilatih pada teks bahasa Inggris; hasil adalah indikasi, bukan keputusan final."
  ]
}
```
* **Respon Sukses (HTTP 200) — Lowongan Penipuan:**
```json
{
  "prediksi": "PALSU",
  "probabilitas_palsu": 0.8924,
  "tingkat_risiko": "TINGGI",
  "threshold": 0.7827,
  "model": "A. Logistic Regression",
  "warnings": [
    "Model dilatih pada teks bahasa Inggris; hasil adalah indikasi, bukan keputusan final."
  ]
}
```
* **Respon Validasi Gagal (HTTP 422):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

### 3.4 `POST /api/v1/predict/batch` (Format JSON Array)
* **Tujuan:** Menganalisis sekumpulan lowongan kerja sekaligus via JSON payload (1 s.d. 500 entri).
* **Payload Masukan (JSON):**
```json
{
  "items": [
    {
      "title": "Data Entry Specialist",
      "description": "Urgent hire! No experience required! Earn $5000 weekly from home. Contact WhatsApp immediately.",
      "location": "US"
    },
    {
      "title": "Backend Python Developer",
      "description": "Building microservices with FastAPI and Kubernetes.",
      "company_profile": "Tech Solutions Inc. provides enterprise cloud solutions."
    }
  ]
}
```
* **Respon Sukses (HTTP 200):**
```json
{
  "count": 2,
  "results": [
    {
      "index": 0,
      "prediksi": "PALSU",
      "probabilitas_palsu": 0.8845,
      "tingkat_risiko": "TINGGI"
    },
    {
      "index": 1,
      "prediksi": "ASLI",
      "probabilitas_palsu": 0.0521,
      "tingkat_risiko": "RENDAH"
    }
  ],
  "threshold": 0.7827,
  "model": "A. Logistic Regression",
  "warnings": [
    "Model dilatih pada teks bahasa Inggris; hasil adalah indikasi, bukan keputusan final."
  ]
}
```

---

### 3.5 `POST /api/v1/predict/batch` (Format Berkas CSV Multipart)
* **Tujuan:** Menganalisis batch melalui unggahan berkas file `.csv` langsung.
* **Header:** `Content-Type: multipart/form-data`
* **Form Field:** `file` (File binary CSV, maks 500 baris, ukuran berkas $\le 5$ MB).
* **Kolom CSV yang Diharapkan:** Sesuai nama atribut pada `JobPosting` (kolom `title` dan `description` wajib ada pada header CSV).
* **Respon Sukses (HTTP 200):** Format JSON identik dengan Subbab 3.4 di atas.

---

## 4. Logika Perhitungan Tingkat Risiko (*Risk Level Formula*)

Model mengembalikan nilai probabilitas kelas palsu $P = P(\text{fraudulent}=1) \in [0.0, 1.0]$.
Tingkat risiko dan label klasifikasi ditetapkan secara deterministik:

$$\text{prediksi} = \begin{cases} \text{"PALSU"}, & \text{jika } P \ge \text{threshold} \\ \text{"ASLI"}, & \text{jika } P < \text{threshold} \end{cases}$$

$$\text{tingkat\_risiko} = \begin{cases} \text{"TINGGI"}, & \text{jika } P \ge \text{threshold} \\ \text{"WASPADA"}, & \text{jika } \frac{\text{threshold}}{2} \le P < \text{threshold} \\ \text{"RENDAH"}, & \text{jika } P < \frac{\text{threshold}}{2} \end{cases}$$

*Catatan: Nilai `threshold` bersifat dinamis dan diambil langsung dari `bundle["threshold"]` (pada model aktif saat ini bernilai $\approx 0{,}7827$). Nilai $\frac{\text{threshold}}{2} \approx 0{,}3914$.*

---

## 5. Contoh Pemanggilan Konkret (*curl Examples*)

### 5.1 Cek Kesehatan Layanan
```bash
curl -X GET "http://localhost:8000/health" \
     -H "Accept: application/json"
```

### 5.2 Ambil Informasi & Metrik Model
```bash
curl -X GET "http://localhost:8000/api/v1/model-info" \
     -H "Accept: application/json"
```

### 5.3 Prediksi Lowongan Tunggal (Lowongan Sah)
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Senior Backend Developer",
       "company_profile": "Acme Cloud Services is a reputable infrastructure provider with 300 staff members.",
       "description": "Design and maintain high-throughput REST APIs and event-driven data pipelines using Python and Kafka.",
       "requirements": "BSc in Computer Science, 5+ years experience with microservices architecture.",
       "benefits": "Medical, dental, vision insurance, annual bonus, paid time off.",
       "location": "US, CA, San Francisco",
       "employment_type": "Full-time",
       "has_company_logo": 1,
       "has_questions": 1
     }'
```

### 5.4 Prediksi Lowongan Tunggal (Lowongan Penipuan)
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "URGENT HIRING: Work From Home Data Entry Assistant! Earn $5000/Week!",
       "description": "No experience needed! Start making money today from anywhere! Send a small registration fee and your bank details on WhatsApp to begin immediately!",
       "location": "US",
       "employment_type": "Part-time",
       "has_company_logo": 0,
       "has_questions": 0
     }'
```

### 5.5 Prediksi Batch via JSON Array
```bash
curl -X POST "http://localhost:8000/api/v1/predict/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "items": [
         {
           "title": "Software Engineer",
           "description": "Build modern web applications with Python and React."
         },
         {
           "title": "Easy Cash Online Worker",
           "description": "Transfer funds and receive commission immediately. Contact WhatsApp now!"
         }
       ]
     }'
```

### 5.6 Prediksi Batch via Unggah Berkas CSV
```bash
curl -X POST "http://localhost:8000/api/v1/predict/batch" \
     -H "Accept: application/json" \
     -F "file=@sample_jobs.csv;type=text/csv"
```

### 5.7 Uji Validasi Galat (Title Kosong $\rightarrow$ HTTP 422)
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Missing title field to test validation."
     }'
```

---

## 6. Matriks Pemenuhan Kebutuhan SRS pada API
- **FR-02:** Terpenuhi pada kalkulasi `prediksi`, `probabilitas_palsu`, dan `tingkat_risiko` (Subbab 2.2 & Bagian 4).
- **FR-03:** Terpenuhi pada endpoint `POST /api/v1/predict` (Subbab 3.3).
- **FR-04:** Terpenuhi pada endpoint `POST /api/v1/predict/batch` JSON & CSV (Subbab 3.4 & 3.5).
- **FR-05:** Terpenuhi pada endpoint `GET /health` & `GET /api/v1/model-info` (Subbab 3.1 & 3.2).
- **FR-06:** Terpenuhi pada validasi Pydantic `JobPosting` (Subbab 2.1).
- **FR-07:** Terpenuhi pada array `warnings` di seluruh response (Subbab 2.2 & 2.3).
- **NFR-02:** Terpenuhi pada `min_length`, `max_length`, batas 500 item batch, dan batas 5 MB file CSV.
