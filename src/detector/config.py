import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Folder model aktif; dapat diganti lewat env var MODEL_DIR
MODEL_DIR = Path(os.getenv("MODEL_DIR", ROOT / "models" / "current"))
MODEL_FILE = os.getenv("MODEL_FILE", "fake_job_detector.joblib")
MAX_BATCH = int(os.getenv("MAX_BATCH", "500"))
MAX_TEXT_LEN = int(os.getenv("MAX_TEXT_LEN", "20000"))
MAX_CSV_SIZE = int(os.getenv("MAX_CSV_SIZE", str(5 * 1024 * 1024)))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Konfigurasi Asisten AI Gemini (CR-2026-11-05-03)
# PENTING: Set env var GEMINI_API_KEY di Render.com / .env lokal, jangan hardcode di sini!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

LANGUAGE_WARNING = "Model dilatih pada teks bahasa Inggris; hasil adalah indikasi, bukan keputusan final."
