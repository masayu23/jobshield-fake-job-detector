import io
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

import gradio as gr
import httpx
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from . import config
from .model_loader import ModelNotAvailable, get_model_service
from .schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    BatchItemResult,
    BatchPredictJsonRequest,
    BatchPredictResponse,
    HealthResponse,
    JobPosting,
    ModelInfoResponse,
    PredictionResult,
)
from .ui import create_ui


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context: memuat model sekali saat startup (NFR-01)."""
    try:
        svc = get_model_service()
        _ = svc.threshold
    except (ModelNotAvailable, RuntimeError, OSError):
        pass
    yield


logger = logging.getLogger("detector.access")
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

app = FastAPI(
    title="Fake Job Detector API",
    description="Sistem Cerdas Deteksi Penipuan Lowongan Kerja Palsu",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def privacy_safe_logging_middleware(request: Request, call_next):
    """Logging middleware yang aman privasi: tidak pernah mencatat teks mentah (NFR-03)."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(ModelNotAvailable)
async def model_not_available_handler(request: Request, exc: ModelNotAvailable):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": f"Model tidak tersedia: {exc}",
            "code": "MODEL_NOT_READY",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "code": "VALIDATION_ERROR",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.get("/health", response_model=HealthResponse, tags=["Sistem"])
def health_check():
    """Health check endpoint: memeriksa ketersediaan sistem dan kesiapan model."""
    try:
        svc = get_model_service()
        _ = svc.threshold
        return HealthResponse(status="ok", model_loaded=True, version="1.0.0")
    except (ModelNotAvailable, RuntimeError, OSError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "model_loaded": False, "version": "1.0.0"},
        )


@app.get("/api/v1/model-info", response_model=ModelInfoResponse, tags=["Model"])
def get_model_info():
    """Mengembalikan metadata model, metrik hold-out, threshold, dan versi library."""
    svc = get_model_service()
    info = svc.model_info()
    return ModelInfoResponse(
        model_name=info.get("model_name", "Unknown Model"),
        threshold=float(info.get("threshold", svc.threshold)),
        raw_columns=list(info.get("raw_columns", svc.raw_columns)),
        metrics_test_holdout=info.get("metrics_test_holdout"),
        metrics_cv=info.get("metrics_cv"),
        refit_on_all_data=info.get("refit_on_all_data"),
        sklearn_version=info.get("sklearn_version"),
        created_at=info.get("created_at"),
    )


@app.post(
    "/api/v1/predict",
    response_model=PredictionResult,
    tags=["Prediksi"],
    summary="Prediksi satu lowongan kerja",
)
def predict_single(posting: JobPosting):
    """Mengevaluasi satu lowongan kerja dan mengembalikan probabilitas, label, dan tingkat risiko."""
    svc = get_model_service()
    result = svc.predict_one(posting.to_raw_dict())
    return PredictionResult(**result)


def _execute_batch_predictions(postings: list[JobPosting]) -> BatchPredictResponse:
    svc = get_model_service()
    records = [p.to_raw_dict() for p in postings]
    df = pd.DataFrame(records)
    preds = svc.predict_dataframe(df)
    results = [
        BatchItemResult(
            index=i,
            prediksi=str(row["prediksi"]),
            probabilitas_palsu=float(row["probabilitas_palsu"]),
            tingkat_risiko=str(row["tingkat_risiko"]),
        )
        for i, (_, row) in enumerate(preds.iterrows())
    ]
    return BatchPredictResponse(
        count=len(results),
        results=results,
        threshold=svc.threshold,
        model=svc.bundle["model_name"],
        warnings=[config.LANGUAGE_WARNING],
    )


@app.post(
    "/api/v1/predict/batch",
    response_model=BatchPredictResponse,
    tags=["Prediksi"],
    summary="Prediksi sekumpulan lowongan kerja (JSON atau CSV multipart)",
)
async def predict_batch(request: Request):
    """Mengevaluasi banyak lowongan kerja via JSON array atau unggahan berkas CSV (maks 500 baris)."""
    content_type = request.headers.get("content-type", "").lower()
    postings: list[JobPosting] = []

    if "multipart/form-data" in content_type:
        form = await request.form()
        file_obj = form.get("file")
        if file_obj is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Field 'file' wajib disertakan pada form multipart",
            )
        contents = await file_obj.read()  # type: ignore[union-attr]
        if len(contents) > config.MAX_CSV_SIZE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ukuran berkas CSV melebihi batas maksimal {config.MAX_CSV_SIZE // (1024 * 1024)} MB",
            )
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            text = contents.decode("latin-1", errors="replace")

        try:
            df_csv = pd.read_csv(io.StringIO(text))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Berkas CSV tidak valid atau gagal di-parse: {e}",
            ) from e

        if df_csv.empty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Berkas CSV kosong (0 baris)",
            )
        if len(df_csv) > config.MAX_BATCH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Jumlah baris ({len(df_csv)}) melebihi batas maksimal {config.MAX_BATCH} baris",
            )
        if "title" not in df_csv.columns or "description" not in df_csv.columns:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Berkas CSV wajib memuat kolom 'title' dan 'description'",
            )

        records = df_csv.where(pd.notna(df_csv), None).to_dict(orient="records")
        for i, row in enumerate(records):
            try:
                postings.append(JobPosting.model_validate(row))
            except ValidationError as ve:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validasi gagal pada baris CSV {i + 1}: {ve.errors()}",
                ) from ve
    else:
        try:
            body = await request.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Format JSON tidak valid: {e}",
            ) from e

        try:
            req_data = BatchPredictJsonRequest.model_validate(body)
            postings = req_data.items
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ve.errors(),
            ) from ve

    return _execute_batch_predictions(postings)


def _generate_knowledge_base_fallback(query: str, job_context: dict | None) -> str:
    """Fallback cerdas berbasis basis pengetahuan JobShield saat API Key Gemini belum dipasang."""
    q_lower = query.lower()
    context_note = ""
    if job_context and job_context.get("title"):
        context_note = (
            f"\n\n*Konteks Lowongan Terpilih:* **{job_context.get('title')}** "
            f"(Probabilitas: {job_context.get('probabilitas_palsu', '-')}, "
            f"Status: {job_context.get('prediksi', '-')})."
        )

    if any(k in q_lower for k in ["travel", "tiket", "pesawat", "hotel", "rekanan"]):
        return (
            "🚨 **Peringatan Modus Tiket Travel Bodong:**\n\n"
            "Jika Anda menerima surat panggilan tes di luar kota dan diwajibkan membeli tiket melalui biro perjalanan tertentu "
            "dengan janji uang diganti (reimburse), **100% INI ADALAH PENIPUAN!**\n\n"
            "**Tindakan Anda:**\n"
            "1. Jangan pernah transfer uang sepeser pun ke rekening travel tersebut.\n"
            "2. Hubungi kantor pusat perusahaan melalui nomor telepon resmi yang terdaftar di Google Maps atau situs web resminya.\n"
            "3. Laporkan nomor rekening penipu ke kanal resmi [patrolisiber.id](https://patrolisiber.id)."
            f"{context_note}"
        )
    elif any(k in q_lower for k in ["biaya", "bayar", "transfer", "seragam", "uang", "psikotes", "mcu"]):
        return (
            "⚠️ **Aturan Emas Rekrutmen Kerja:**\n\n"
            "Perusahaan bonafide dan sah **TIDAK PERNAH memungut biaya apa pun** dalam proses rekrutmen—baik untuk biaya tes psikotes, "
            "biaya seragam, modul pelatihan, maupun cek medis (MCU).\n\n"
            "Jika ada pungutan dengan dalih apa pun, segera hentikan komunikasi karena itu adalah indikasi kuat pemerasan rekrutmen palsu."
            f"{context_note}"
        )
    elif any(k in q_lower for k in ["telegram", "freelance", "like", "subscribe", "deposit", "misi", "tugas"]):
        return (
            "🛑 **Waspada Modus Scam Freelance Telegram / Like & Subscribe:**\n\n"
            "Modus ini berawal dari tawaran tugas mudah (follow IG, like video YouTube, review barang) yang diberi komisi kecil Rp 20rb - Rp 50rb di awal. "
            "Namun setelah Anda percaya, pelaku akan meminta 'deposit' jutaan rupiah untuk tugas VIP dengan janji keuntungan berlipat. Uang tersebut tidak akan pernah bisa ditarik kembali!\n\n"
            "**Saran Taktis:** Jangan pernah mentransfer dana deposit untuk pekerjaan paruh waktu."
            f"{context_note}"
        )
    elif any(k in q_lower for k in ["ktp", "rekening", "pinjol", "selfie", "buku tabungan", "data"]):
        return (
            "🔒 **Lindungi Data Pribadi Anda:**\n\n"
            "Waspadalah jika pemberi kerja meminta foto KTP tampak depan, selfie memegang KTP, foto buku tabungan, atau data ibu kandung "
            "sebelum ada penawaran kerja resmi (Offering Letter) dan kontrak kerja yang sah.\n\n"
            "Data ini sering disalahgunakan sindikat penipu untuk membobol rekening atau mengajukan pinjaman online (pinjol) ilegal atas nama Anda."
            f"{context_note}"
        )
    else:
        return (
            "Halo! Saya **JobShield Security Advisor** (Asisten Keamanan Karir). 🛡️\n\n"
            "Saya siap membantu Anda memverifikasi keabsahan tawaran kerja, memeriksa surat panggilan, dan mengenali modus penipuan rekrutmen.\n\n"
            "**Tips Verifikasi Cepat:**\n"
            "- Pastikan domain email pengirim menggunakan email korporat resmi (`@nama-perusahaan.com`), bukan webmail gratisan (@gmail, @yahoo).\n"
            "- Jangan pernah mentransfer uang untuk alasan apa pun (tiket, seragam, modul tes).\n"
            "- Periksa apakah lowongan tersebut benar-benar tercantum di laman karier resmi perusahaan.\n\n"
            "*Catatan: Anda dapat memasukkan Google Gemini API Key pada bilah atas untuk mengaktifkan penalaran interaktif Gemini 1.5 Flash secara langsung!*"
            f"{context_note}"
        )


@app.post(
    "/api/v1/assistant/chat",
    response_model=AssistantChatResponse,
    tags=["Asisten AI"],
    summary="Konsultasi interaktif dengan Asisten AI Gemini",
)
async def chat_with_gemini(
    chat_req: AssistantChatRequest,
    x_gemini_api_key: str | None = Header(default=None, alias="X-Gemini-API-Key"),
):
    """Berkomunikasi dengan Asisten AI Gemini untuk konsultasi keamanan rekrutmen dan analisis penipuan."""
    api_key = (x_gemini_api_key or config.GEMINI_API_KEY).strip()
    latest_message = chat_req.messages[-1].content

    # Jika API Key belum tersedia, gunakan respons cerdas basis pengetahuan JobShield
    if not api_key:
        fallback_reply = _generate_knowledge_base_fallback(
            latest_message, chat_req.job_context
        )
        return AssistantChatResponse(
            reply=fallback_reply,
            model="JobShield Knowledge Base (Offline Advisor)",
            is_live_gemini=False,
        )

    # Format percakapan untuk Google Gemini API
    system_instruction = (
        "Kamu adalah JobShield AI Assistant, seorang pakar keamanan siber, anti-fraud, "
        "dan konsultan perlindungan pencari kerja profesional di Indonesia. "
        "Tugasmu adalah menganalisis indikasi penipuan lowongan kerja, mengidentifikasi modus operandi "
        "(tiket travel bodong, tes berbayar, rekrutmen palsu atas nama BUMN/korporasi ternama, phishing identitas KTP/rekening, "
        "dan tugas deposit Telegram), serta memberikan saran pencegahan yang taktis, ramah, dan solutif. "
        "Format jawabanmu dalam Markdown yang terstruktur, jelas, dan mudah dipahami."
    )

    if chat_req.job_context:
        ctx_title = chat_req.job_context.get("title", "")
        ctx_pred = chat_req.job_context.get("prediksi", "")
        ctx_prob = chat_req.job_context.get("probabilitas_palsu", "")
        system_instruction += (
            f"\n\n[KONTEKS LOWONGAN SAAT INI]: Judul: '{ctx_title}', "
            f"Hasil AI ML: {ctx_pred} (Probabilitas Penipuan: {ctx_prob}). "
            "Gunakan konteks ini jika pengguna bertanya tentang lowongan tersebut."
        )

    contents = []
    for msg in chat_req.messages:
        role = "model" if msg.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg.content}]})

    gemini_payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent"
        f"?key={api_key}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=gemini_payload)

        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return AssistantChatResponse(
                        reply=parts[0]["text"],
                        model=config.GEMINI_MODEL,
                        is_live_gemini=True,
                    )
            return AssistantChatResponse(
                reply="Asisten Gemini tidak menghasilkan respons untuk pertanyaan ini. Silakan ulangi dengan pertanyaan berbeda.",
                model=config.GEMINI_MODEL,
                is_live_gemini=True,
            )
        else:
            err_msg = f"HTTP {resp.status_code}"
            try:
                err_data = resp.json()
                err_msg = err_data.get("error", {}).get("message", err_msg)
            except (ValueError, KeyError, TypeError):
                logger.debug("Failed to decode JSON error from Gemini API")

            fallback_reply = _generate_knowledge_base_fallback(
                latest_message, chat_req.job_context
            )
            return AssistantChatResponse(
                reply=f"⚠️ *Catatan: Layanan Gemini API merespons dengan kendala ({err_msg}). Berikut panduan dari basis pengetahuan JobShield:*\n\n{fallback_reply}",
                model=f"{config.GEMINI_MODEL} (Fallback)",
                is_live_gemini=False,
            )
    except (httpx.HTTPError, OSError, ValueError) as e:
        logger.warning("Gemini Assistant error: %s", e)
        fallback_reply = _generate_knowledge_base_fallback(
            latest_message, chat_req.job_context
        )
        return AssistantChatResponse(
            reply=f"⚠️ *Koneksi ke Gemini API tidak dapat terhubung. Menggunakan respons penasihat JobShield:*\n\n{fallback_reply}",
            model="JobShield Knowledge Base (Fallback)",
            is_live_gemini=False,
        )





# Mount Gradio UI pada path /ui (FR-09)
app = gr.mount_gradio_app(app, create_ui(), path="/ui")

# Frontend React SPA static mounting (CR-2026-11-05-02)
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists() and (_frontend_dist / "index.html").exists():
    if (_frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="frontend_assets")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        return FileResponse(str(_frontend_dist / "index.html"))

    @app.get("/app", include_in_schema=False)
    def serve_frontend_app():
        return FileResponse(str(_frontend_dist / "index.html"))
