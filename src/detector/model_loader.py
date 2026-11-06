# Pemuat model (SUDAH JADI). Semua prediksi di aplikasi harus lewat ModelService.
import json
import sys
from functools import lru_cache
from typing import Any

import joblib
import pandas as pd

from . import config


class ModelNotAvailable(RuntimeError):
    pass


class ModelService:
    def __init__(self, model_dir=None, model_file=None):
        self.model_dir = config.MODEL_DIR if model_dir is None else model_dir
        self.model_path = self.model_dir / (model_file or config.MODEL_FILE)
        if not self.model_path.exists():
            raise ModelNotAvailable(f"File model tidak ditemukan: {self.model_path}")
        # fake_job_utils harus dapat di-import saat joblib.load (ada di folder model)
        if str(self.model_dir) not in sys.path:
            sys.path.insert(0, str(self.model_dir))
        import fake_job_utils
        self._utils = fake_job_utils
        self.bundle = joblib.load(self.model_path)

    @property
    def threshold(self) -> float:
        return float(self.bundle["threshold"])

    @property
    def raw_columns(self) -> list:
        return list(self.bundle["raw_columns"])

    def predict_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # Kolom: probabilitas_palsu, prediksi (ASLI/PALSU), tingkat_risiko (RENDAH/WASPADA/TINGGI)
        return self._utils.predict_postings(self.bundle, df)

    def predict_one(self, posting: dict) -> dict:
        res = self.predict_dataframe(pd.DataFrame([posting])).iloc[0]
        return {
            "prediksi": str(res["prediksi"]),
            "probabilitas_palsu": float(res["probabilitas_palsu"]),
            "tingkat_risiko": str(res["tingkat_risiko"]),
            "threshold": self.threshold,
            "model": self.bundle["model_name"],
            "warnings": [config.LANGUAGE_WARNING],
        }

    def model_info(self) -> dict[str, Any]:
        meta_path = self.model_dir / "model_metadata.json"
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return {k: v for k, v in self.bundle.items() if k != "model"}


@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    return ModelService()
