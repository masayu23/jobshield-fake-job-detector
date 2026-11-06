import html
import re
import numpy as np
import pandas as pd

TEXT_PARTS = ["title", "company_profile", "description", "requirements", "benefits"]
CAT_COLS = ["country", "employment_type", "required_experience",
            "required_education", "function", "industry"]
NUM_COLS = ["len_title", "len_profile", "len_desc", "len_req", "len_benefits",
            "n_exclaim", "caps_ratio", "n_url", "n_email", "n_phone", "n_dollar",
            "has_salary", "has_department", "no_profile", "no_req", "no_benefits",
            "telecommuting", "has_company_logo", "has_questions"]
TEXT_COL = "text"

# Kolom mentah yang diterima model saat inferensi (kolom yang tidak diisi dianggap kosong)
RAW_COLUMNS = ["title", "location", "department", "salary_range", "company_profile",
               "description", "requirements", "benefits", "telecommuting",
               "has_company_logo", "has_questions", "employment_type",
               "required_experience", "required_education", "industry", "function"]


def _s(x):
    return x if isinstance(x, str) else ""


def _clean_text(s):
    s = html.unescape(_s(s))
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"#URL_[A-Za-z0-9]+#", " urltoken ", s)
    s = re.sub(r"#EMAIL_[A-Za-z0-9]+#", " emailtoken ", s)
    s = re.sub(r"#PHONE_[A-Za-z0-9]+#", " phonetoken ", s)
    s = re.sub(r"(?<=[a-z0-9\.\,\)\!])(?=[A-Z][a-z])", " ", s)   # pisahkan kalimat yang menempel
    s = re.sub(r"[^A-Za-z0-9\s\$\!]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def prepare_features(df):
    # Mengubah data lowongan mentah (DataFrame) menjadi tabel fitur siap model.
    d = df.copy()
    for c in RAW_COLUMNS:
        if c not in d.columns:
            d[c] = np.nan

    raw_all = d[TEXT_PARTS].apply(lambda col: col.map(_s)).agg(" ".join, axis=1)
    out = pd.DataFrame(index=d.index)
    out[TEXT_COL] = d[TEXT_PARTS].apply(lambda col: col.map(_clean_text)).agg(" ".join, axis=1)

    country = d["location"].map(lambda x: _s(x).split(",")[0].strip().upper() or "UNKNOWN")
    out["country"] = country
    for c in CAT_COLS[1:]:
        out[c] = d[c].fillna("unknown").astype(str)

    out["len_title"] = np.log1p(d["title"].map(lambda x: len(_s(x))))
    out["len_profile"] = np.log1p(d["company_profile"].map(lambda x: len(_s(x))))
    out["len_desc"] = np.log1p(d["description"].map(lambda x: len(_s(x))))
    out["len_req"] = np.log1p(d["requirements"].map(lambda x: len(_s(x))))
    out["len_benefits"] = np.log1p(d["benefits"].map(lambda x: len(_s(x))))
    out["n_exclaim"] = raw_all.str.count("!")
    out["caps_ratio"] = raw_all.map(lambda t: sum(ch.isupper() for ch in t) / max(len(t), 1))
    out["n_url"] = raw_all.str.count(r"#URL_")
    out["n_email"] = raw_all.str.count(r"#EMAIL_")
    out["n_phone"] = raw_all.str.count(r"#PHONE_")
    out["n_dollar"] = raw_all.str.count(r"\$")
    out["has_salary"] = d["salary_range"].notna().astype(int)
    out["has_department"] = d["department"].notna().astype(int)
    out["no_profile"] = (d["company_profile"].map(lambda x: len(_s(x))) == 0).astype(int)
    out["no_req"] = (d["requirements"].map(lambda x: len(_s(x))) == 0).astype(int)
    out["no_benefits"] = (d["benefits"].map(lambda x: len(_s(x))) == 0).astype(int)
    for c in ["telecommuting", "has_company_logo", "has_questions"]:
        out[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).astype(int)
    return out


def predict_postings(bundle, df):
    # Memprediksi sekumpulan lowongan. bundle = hasil joblib.load("fake_job_detector.joblib")
    proba = bundle["model"].predict_proba(df)[:, 1]
    thr = bundle["threshold"]
    res = pd.DataFrame({"probabilitas_palsu": proba.round(4)}, index=df.index)
    res["prediksi"] = np.where(proba >= thr, "PALSU", "ASLI")
    res["tingkat_risiko"] = np.select(
        [proba >= thr, proba >= thr / 2], ["TINGGI", "WASPADA"], default="RENDAH")
    return res
