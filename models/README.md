# Paket Deploy - Deteksi Lowongan Kerja Palsu
Model: A. Logistic Regression | Threshold: 0.7869

## Cara pakai (Python)
    import joblib, pandas as pd
    import fake_job_utils
    from fake_job_utils import predict_postings
    bundle = joblib.load("fake_job_detector.joblib")
    df = pd.DataFrame([{"title": "...", "description": "...", "company_profile": "..."}])
    print(predict_postings(bundle, df))

## Jalankan demo web
    pip install -r requirements.txt
    python app.py
