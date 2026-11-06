from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from . import config


class JobPosting(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Judul posisi pekerjaan (wajib diisi)",
        examples=["Senior Software Engineer"],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=config.MAX_TEXT_LEN,
        description="Deskripsi pekerjaan lengkap (wajib diisi)",
        examples=["We are seeking an experienced Python developer to build scalable backend APIs."],
    )
    company_profile: str | None = Field(
        default="",
        max_length=config.MAX_TEXT_LEN,
        description="Profil atau latar belakang singkat perusahaan",
        examples=["Acme Corp is a leading technology company."],
    )
    requirements: str | None = Field(
        default="",
        max_length=config.MAX_TEXT_LEN,
        description="Persyaratan kualifikasi dan keahlian pelamar",
        examples=["5+ years of Python, FastAPI, PostgreSQL."],
    )
    benefits: str | None = Field(
        default="",
        max_length=config.MAX_TEXT_LEN,
        description="Fasilitas dan tunjangan yang ditawarkan",
        examples=["Health insurance, flexible working hours."],
    )
    location: str | None = Field(
        default="",
        max_length=500,
        description="Lokasi kerja (rekomendasi: Negara, Provinsi, Kota)",
        examples=["US, CA, San Francisco"],
    )
    department: str | None = Field(
        default="",
        max_length=500,
        description="Divisi atau departemen pekerjaan",
        examples=["Engineering"],
    )
    salary_range: str | None = Field(
        default="",
        max_length=100,
        description="Kisaran gaji yang ditawarkan",
        examples=["100000-140000"],
    )
    employment_type: str | None = Field(
        default="",
        max_length=100,
        description="Jenis pekerjaan (Full-time, Part-time, Contract, dll.)",
        examples=["Full-time"],
    )
    required_experience: str | None = Field(
        default="",
        max_length=100,
        description="Tingkat pengalaman yang dibutuhkan",
        examples=["Mid-Senior level"],
    )
    required_education: str | None = Field(
        default="",
        max_length=100,
        description="Kualifikasi pendidikan minimum",
        examples=["Bachelor's Degree"],
    )
    industry: str | None = Field(
        default="",
        max_length=500,
        description="Sektor industri perusahaan",
        examples=["Information Technology"],
    )
    function: str | None = Field(
        default="",
        max_length=500,
        description="Fungsi peran pekerjaan",
        examples=["Engineering"],
    )
    telecommuting: int | None = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika remote/WFH, 0 jika on-site",
        examples=[0],
    )
    has_company_logo: int | None = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika memiliki logo perusahaan, 0 jika tidak",
        examples=[1],
    )
    has_questions: int | None = Field(
        default=0,
        ge=0,
        le=1,
        description="Biner: 1 jika ada pertanyaan screening lamaran, 0 jika tidak",
        examples=[1],
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def validate_non_whitespace(cls, v: Any) -> str:
        if isinstance(v, str):
            s = v.strip()
            if not s:
                raise ValueError("Nilai tidak boleh kosong atau hanya berupa spasi")
            return v
        if v is None:
            raise ValueError("Field wajib diisi")
        return str(v)

    @field_validator(
        "company_profile",
        "requirements",
        "benefits",
        "location",
        "department",
        "salary_range",
        "employment_type",
        "required_experience",
        "required_education",
        "industry",
        "function",
        mode="before",
    )
    @classmethod
    def default_none_to_empty_str(cls, v: Any) -> str:
        if v is None:
            return ""
        return str(v)

    @field_validator("telecommuting", "has_company_logo", "has_questions", mode="before")
    @classmethod
    def default_binary(cls, v: Any) -> int:
        if v is None or v == "":
            return 0
        try:
            val = int(v)
            if val in (0, 1):
                return val
        except (ValueError, TypeError):
            pass
        raise ValueError("Field biner harus bernilai 0 atau 1")

    def to_raw_dict(self) -> dict[str, Any]:
        """Konversi ke dict kolom mentah yang diterima model."""
        return {
            "title": self.title,
            "location": self.location or "",
            "department": self.department or "",
            "salary_range": self.salary_range or "",
            "company_profile": self.company_profile or "",
            "description": self.description,
            "requirements": self.requirements or "",
            "benefits": self.benefits or "",
            "telecommuting": self.telecommuting,
            "has_company_logo": self.has_company_logo,
            "has_questions": self.has_questions,
            "employment_type": self.employment_type or "",
            "required_experience": self.required_experience or "",
            "required_education": self.required_education or "",
            "industry": self.industry or "",
            "function": self.function or "",
        }


class PredictionResult(BaseModel):
    prediksi: Literal["ASLI", "PALSU"] = Field(
        ...,
        description="Keputusan biner klasifikasi model berdasarkan ambang batas",
    )
    probabilitas_palsu: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilitas lowongan bersifat penipuan (0.0000 - 1.0000)",
    )
    tingkat_risiko: Literal["RENDAH", "WASPADA", "TINGGI"] = Field(
        ...,
        description="Tingkat risiko berjenjang sistem deteksi",
    )
    threshold: float = Field(
        ...,
        description="Ambang batas keputusan aktif dari model bundle",
    )
    model: str = Field(
        ...,
        description="Nama algoritma dan versi model",
    )
    warnings: list[str] = Field(
        default_factory=lambda: [config.LANGUAGE_WARNING],
        description="Daftar peringatan bahasa dan penafian resmi",
    )


class BatchPredictJsonRequest(BaseModel):
    items: list[JobPosting] = Field(
        ...,
        min_length=1,
        max_length=config.MAX_BATCH,
        description=f"Daftar lowongan kerja yang akan dianalisis (maksimal {config.MAX_BATCH} entri)",
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
    warnings: list[str] = Field(
        default_factory=lambda: [config.LANGUAGE_WARNING],
        description="Daftar peringatan bahasa dan penafian resmi",
    )


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    model_loaded: bool
    version: str = "1.0.0"


class ModelInfoResponse(BaseModel):
    model_name: str
    threshold: float
    raw_columns: list[str]
    metrics_test_holdout: dict[str, Any] | None = None
    metrics_cv: dict[str, Any] | None = None
    refit_on_all_data: bool | None = None
    sklearn_version: str | None = None
    created_at: str | None = None


# Skema Percakapan Asisten AI Gemini (CR-2026-11-05-03)
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Peran pengirim pesan")
    content: str = Field(..., min_length=1, max_length=10000, description="Isi teks percakapan")


class AssistantChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50, description="Riwayat pesan")
    job_context: dict[str, Any] | None = Field(default=None, description="Konteks lowongan (opsional)")


class AssistantChatResponse(BaseModel):
    reply: str
    model: str
    is_live_gemini: bool = Field(default=True, description="True jika dijawab langsung via Gemini API")
