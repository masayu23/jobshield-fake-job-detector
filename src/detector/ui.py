import html
import os
import tempfile
from typing import Any

import gradio as gr
import pandas as pd

from . import config
from .model_loader import get_model_service


def sanitize_csv_cell(val: Any) -> Any:
    """Mencegah serangan CSV Formula Injection (Excel / Google Sheets execution).

    Menyisipkan prefix tanda petik tunggal jika nilai teks diawali karakter formula.
    """
    if isinstance(val, str) and len(val) > 0 and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def sanitize_dataframe_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Membersihkan dataframe dari potensi formula injection sebelum diekspor ke CSV."""
    clean_df = df.copy()
    for col in clean_df.columns:
        clean_df[col] = clean_df[col].apply(sanitize_csv_cell)
    return clean_df


def analyze_single_job(
    title: str,
    description: str,
    company_profile: str,
    requirements: str,
    benefits: str,
    location: str,
    department: str,
    salary_range: str,
    employment_type: str,
    required_experience: str,
    required_education: str,
    industry: str,
    function: str,
    telecommuting: bool,
    has_company_logo: bool,
    has_questions: bool,
) -> tuple[str, str, str, str]:
    """Handler analisis satu lowongan kerja pada UI Gradio."""
    if not title or not title.strip() or not description or not description.strip():
        badge_err = (
            "<div style='background-color: #fee2e2; color: #991b1b; padding: 16px 20px; "
            "border-radius: 12px; font-weight: 700; border-left: 6px solid #dc2626;'>"
            "⚠️ PERINGATAN VALIDASI: Judul lowongan dan Deskripsi pekerjaan wajib diisi."
            "</div>"
        )
        return (
            badge_err,
            "0.00%",
            "-",
            "Silakan lengkapi judul dan deskripsi lowongan kerja untuk memulai pemeriksaan.",
        )

    posting = {
        "title": title.strip(),
        "description": description.strip(),
        "company_profile": (company_profile or "").strip(),
        "requirements": (requirements or "").strip(),
        "benefits": (benefits or "").strip(),
        "location": (location or "").strip(),
        "department": (department or "").strip(),
        "salary_range": (salary_range or "").strip(),
        "employment_type": employment_type or "",
        "required_experience": required_experience or "",
        "required_education": required_education or "",
        "industry": (industry or "").strip(),
        "function": (function or "").strip(),
        "telecommuting": 1 if telecommuting else 0,
        "has_company_logo": 1 if has_company_logo else 0,
        "has_questions": 1 if has_questions else 0,
    }

    svc = get_model_service()
    res = svc.predict_one(posting)

    proba = res["probabilitas_palsu"]
    risiko = res["tingkat_risiko"]
    thr = res["threshold"]

    # Aksesibilitas NFR-08: Padukan warna latar + teks eksplisit + ikon
    if risiko == "TINGGI":
        badge = (
            "<div style='background-color: #fee2e2; color: #991b1b; padding: 18px 22px; "
            "border-radius: 14px; font-weight: 800; font-size: 1.18rem; border-left: 8px solid #dc2626; "
            "box-shadow: 0 4px 12px rgba(220, 38, 38, 0.12);'>"
            "🚨 PALSU — Tingkat Risiko: TINGGI (Potensi Penipuan Kuat)"
            "</div>"
        )
        saran = (
            "⚠️ **PERHATIAN KERAS:** Model mendeteksi karakteristik linguistik dan struktur yang "
            "sangat mirip dengan pola lowongan penipuan.\n\n"
            "#### 🛑 Tindakan Pencegahan Segera:\n"
            "1. **JANGAN PERNAH mentransfer uang** untuk biaya pendaftaran, seragam, pelatihan, formulir, atau akomodasi/tiket travel.\n"
            "2. **JANGAN membagikan informasi perbankan sensitif**, nomor rekening, foto KTP/selfie identitas, OTP, PIN, atau kata sandi.\n"
            "3. **Waspadai kontak perekrut** yang hanya menggunakan WhatsApp, akun Telegram anonim, atau alamat email gratisan (Gmail, Yahoo).\n"
            "4. **Periksa situs resmi korporat** dan hubungi saluran resmi perusahaan yang ditemukan secara independen.\n\n"
            "---\n"
            "### 📋 Panduan Verifikasi Mandiri (Bukan Temuan AI)\n"
            "*Pemeriksaan manual berikut disarankan bagi pelamar untuk memastikan validitas:*\n"
            "- [ ] Apakah perusahaan memiliki kantor fisik yang terdaftar jelas di peta digital/portal resmi?\n"
            "- [ ] Apakah alamat email pengirim menggunakan domain resmi perusahaan (bukan webmail publik)?\n"
            "- [ ] Apakah tahapan wawancara masuk akal dan dilakukan secara profesional?"
        )
    elif risiko == "WASPADA":
        badge = (
            "<div style='background-color: #fef3c7; color: #92400e; padding: 18px 22px; "
            "border-radius: 14px; font-weight: 800; font-size: 1.18rem; border-left: 8px solid #f59e0b; "
            "box-shadow: 0 4px 12px rgba(245, 158, 11, 0.12);'>"
            "⚠️ ASLI — Tingkat Risiko: WASPADA (Perlu Verifikasi Lanjutan)"
            "</div>"
        )
        saran = (
            "ℹ️ **CATATAN WASPADA:** Meskipun skor belum melampaui ambang batas klasifikasi penipuan, "
            "lowongan ini memiliki sejumlah elemen yang kurang lengkap atau patut dicermati (seperti profil "
            "perusahaan minim atau kompensasi tidak lazim).\n\n"
            "#### 🔍 Tindakan Verifikasi yang Disarankan:\n"
            "1. **Buka laman karier resmi** pada situs perusahaan terkait untuk memeriksa apakah lowongan ini benar-benar dibuka.\n"
            "2. **Pastikan proses rekrutmen tidak meminta pungutan biaya apa pun** di tahapan seleksi berikutnya.\n"
            "3. **Konfirmasikan ke bagian HRD** melalui nomor kontak telepon kantor resmi perusahaan.\n\n"
            "---\n"
            "### 📋 Panduan Verifikasi Mandiri (Bukan Temuan AI)\n"
            "- [ ] Verifikasi keabsahan profil perusahaan di LinkedIn atau kanal industri kredibel.\n"
            "- [ ] Pastikan tidak ada desakan untuk segera menandatangani dokumen atau mengirim data rahasia."
        )
    else:
        badge = (
            "<div style='background-color: #d1fae5; color: #065f46; padding: 18px 22px; "
            "border-radius: 14px; font-weight: 800; font-size: 1.18rem; border-left: 8px solid #10b981; "
            "box-shadow: 0 4px 12px rgba(16, 185, 129, 0.12);'>"
            "✅ ASLI — Tingkat Risiko: RENDAH (Konsisten dengan Lowongan Sah)"
            "</div>"
        )
        saran = (
            "✔️ **INDIKASI AMAN:** Karakteristik linguistik, susunan deskripsi, dan metadata lowongan kerja "
            "ini konsisten dengan profil lowongan kerja yang sah dan wajar pada data latih.\n\n"
            "#### 🛡️ Tetap Waspada Sebagai Pelamar Cerdas:\n"
            "Meskipun hasil skrining awal menunjukkan risiko rendah, selalu terapkan prinsip kehati-hatian: "
            "perusahaan profesional tidak akan meminta biaya rekrutmen dan tidak akan meminta OTP/PIN atau kata sandi.\n\n"
            "---\n"
            "### 📋 Panduan Verifikasi Mandiri (Bukan Temuan AI)\n"
            "- [ ] Pastikan lamaran dikirimkan melalui portal resmi perusahaan atau bursa kerja terpercaya.\n"
            "- [ ] Jangan pernah meminjamkan akun perbankan atau melakukan transaksi uji coba atas nama perusahaan."
        )

    proba_text = f"{proba * 100:.2f}%"
    thr_text = f"{thr * 100:.2f}%"

    return badge, proba_text, thr_text, saran


def analyze_batch_csv(file_obj) -> tuple[str, pd.DataFrame | None, str | None]:
    """Handler analisis kumpulan lowongan melalui berkas CSV dengan sanitasi formula injection."""
    if file_obj is None:
        return "⚠️ Mohon unggah berkas CSV terlebih dahulu.", None, None

    file_path = file_obj if isinstance(file_obj, str) else getattr(file_obj, "name", "")
    if not file_path or not os.path.exists(file_path):
        return "⚠️ Berkas CSV tidak valid atau tidak ditemukan.", None, None

    if os.path.getsize(file_path) > config.MAX_CSV_SIZE:
        max_mb = config.MAX_CSV_SIZE // (1024 * 1024)
        return f"⚠️ Ukuran berkas CSV melebihi batas maksimal {max_mb} MB.", None, None

    try:
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")
    except (ValueError, pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as e:
        safe_msg = html.escape(str(e))
        return f"⚠️ Gagal membaca berkas CSV: {safe_msg}", None, None

    if df.empty:
        return "⚠️ Berkas CSV kosong (0 baris data).", None, None

    if len(df) > config.MAX_BATCH:
        return (
            f"⚠️ Jumlah baris dalam berkas CSV ({len(df)}) melebihi batas maksimal {config.MAX_BATCH} baris.",
            None,
            None,
        )

    if "title" not in df.columns or "description" not in df.columns:
        return "⚠️ Berkas CSV wajib memuat kolom 'title' dan 'description'.", None, None

    svc = get_model_service()
    preds = svc.predict_dataframe(df)

    result_df = df.copy()
    result_df["prediksi"] = preds["prediksi"]
    result_df["probabilitas_palsu"] = preds["probabilitas_palsu"]
    result_df["tingkat_risiko"] = preds["tingkat_risiko"]

    total = len(result_df)
    n_rendah = int((result_df["tingkat_risiko"] == "RENDAH").sum())
    n_waspada = int((result_df["tingkat_risiko"] == "WASPADA").sum())
    n_tinggi = int((result_df["tingkat_risiko"] == "TINGGI").sum())

    pct_rendah = (n_rendah / total * 100) if total > 0 else 0
    pct_waspada = (n_waspada / total * 100) if total > 0 else 0
    pct_tinggi = (n_tinggi / total * 100) if total > 0 else 0

    summary_md = (
        f"### 📊 Ringkasan Hasil Analisis Batch\n\n"
        f"• **Total Lowongan Dianalisis:** `{total}` baris  \n"
        f"• **✅ Risiko Rendah (Sah):** `{n_rendah}` lowongan ({pct_rendah:.1f}%)  \n"
        f"• **⚠️ Risiko Waspada:** `{n_waspada}` lowongan ({pct_waspada:.1f}%)  \n"
        f"• **🚨 Risiko Tinggi (Palsu):** `{n_tinggi}` lowongan ({pct_tinggi:.1f}%)  \n\n"
        f"> 🛡️ *Catatan Keamanan: Berkas CSV hasil unduhan telah disanitasi dari karakter pemicu Formula Injection.*"
    )

    # Simpan hasil dengan sanitasi Formula Injection (OQ-07)
    temp_dir = tempfile.mkdtemp()
    out_csv_path = os.path.join(temp_dir, "hasil_analisis_lowongan.csv")
    safe_export_df = sanitize_dataframe_for_csv(result_df)
    safe_export_df.to_csv(out_csv_path, index=False)

    return summary_md, result_df, out_csv_path


def create_template_csv() -> str:
    """Membuat berkas CSV template untuk diunduh pengguna."""
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, "template_lowongan.csv")
    sample_df = pd.DataFrame(
        [
            {
                "title": "Software Engineer",
                "description": "Design and build backend APIs in Python.",
                "company_profile": "Acme Corp is a software company.",
                "requirements": "3+ years Python experience.",
                "benefits": "Health insurance, paid leave.",
                "location": "US, CA, San Francisco",
                "department": "Engineering",
                "salary_range": "90000-120000",
                "employment_type": "Full-time",
                "required_experience": "Mid-Senior level",
                "required_education": "Bachelor's Degree",
                "industry": "Information Technology",
                "function": "Engineering",
                "telecommuting": 0,
                "has_company_logo": 1,
                "has_questions": 1,
            }
        ]
    )
    sample_df.to_csv(path, index=False)
    return path


def evaluate_checklist(c1: bool, c2: bool, c3: bool, c4: bool, c5: bool, c6: bool) -> str:
    """Evaluasi mandiri checklist sebelum melamar di Pusat Edukasi (client-side assistance)."""
    checks = [c1, c2, c3, c4, c5, c6]
    checked_count = sum(bool(c) for c in checks)

    if checked_count == 6:
        return (
            "<div style='background-color: #d1fae5; color: #065f46; padding: 16px 20px; "
            "border-radius: 12px; font-weight: 700; border-left: 6px solid #10b981;'>"
            "🎉 <b>Skor Pemeriksaan Mandiri: 6/6 (Sangat Baik)</b><br>"
            "Semua indikator kewajaran dasar telah terverifikasi. Tetap jaga kerahasiaan OTP, PIN, dan kata sandi Anda."
            "</div>"
        )
    if checked_count >= 4:
        return (
            f"<div style='background-color: #fef3c7; color: #92400e; padding: 16px 20px; "
            f"border-radius: 12px; font-weight: 700; border-left: 6px solid #f59e0b;'>"
            f"⚠️ <b>Skor Pemeriksaan Mandiri: {checked_count}/6 (Cukup / Perlu Verifikasi Tambahan)</b><br>"
            f"Beberapa poin penting belum terverifikasi. Telusuri saluran resmi perusahaan sebelum mengirim data sensitif."
            f"</div>"
        )
    return (
        f"<div style='background-color: #fee2e2; color: #991b1b; padding: 16px 20px; "
        f"border-radius: 12px; font-weight: 700; border-left: 6px solid #dc2626;'>"
        f"🚨 <b>Skor Pemeriksaan Mandiri: {checked_count}/6 (Waspada Tinggi)</b><br>"
        f"Banyak indikator kewajaran belum terpenuhi. Jangan pernah mentransfer uang atau menyerahkan identitas sensitif."
        f"</div>"
    )


def create_ui() -> gr.Blocks:
    """Membangun antarmuka pengguna web JobShield berstandar Modern SaaS 5 Tab."""
    svc = get_model_service()
    info = svc.model_info()

    model_name = info.get("model_name", "Logistic Regression Pipeline")
    threshold = float(info.get("threshold", svc.threshold))
    metrics_holdout = info.get("metrics_test_holdout", {})

    theme_css = """
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --js-navy: #14213d;
        --js-royal: #2457d6;
        --js-royal-hover: #1d4ed8;
        --js-accent: #3b82f6;
        --js-bg: #f5f7fb;
        --js-surface: #ffffff;
        --js-border: #e2e8f0;
        --js-muted: #64748b;
        --js-heading: #0f172a;
    }

    body, .gradio-container {
        font-family: 'DM Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--js-bg) !important;
        color: #1e293b !important;
    }

    .gradio-container {
        max-width: 1240px !important;
        margin: 0 auto !important;
        padding: 12px 18px 48px !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--js-navy) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* Top Brand Navigation Bar */
    .js-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 22px;
        background: #ffffff;
        border: 1px solid var(--js-border);
        border-radius: 16px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(20, 33, 61, 0.03);
    }
    .js-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 1.25rem;
        color: var(--js-navy);
        letter-spacing: -0.03em;
    }
    .js-brand-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        background: #eff4fe;
        color: var(--js-royal);
        border-radius: 6px;
        border: 1px solid #dbeafe;
    }

    /* Hero Section */
    .js-hero {
        background: linear-gradient(135deg, #101c38 0%, #193f9e 60%, #2457d6 100%);
        color: #ffffff;
        padding: 44px 44px;
        border-radius: 24px;
        margin-bottom: 22px;
        box-shadow: 0 16px 36px rgba(20, 33, 61, 0.15);
        position: relative;
        overflow: hidden;
    }
    .js-hero .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-size: 0.75rem;
        font-weight: 700;
        color: #93c5fd;
        margin-bottom: 12px;
        display: inline-block;
    }
    .js-hero h1 {
        color: #ffffff !important;
        font-size: clamp(1.85rem, 3.8vw, 2.75rem);
        line-height: 1.18;
        margin: 0 0 14px 0;
    }
    .js-hero p {
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.65;
        max-width: 780px;
        margin: 0;
    }

    /* Notice & Disclaimer Banner */
    .js-disclaimer {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        border-left: 5px solid #f59e0b;
        border-radius: 12px;
        padding: 13px 18px;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-bottom: 20px;
    }

    /* SaaS Cards */
    .js-card {
        background: #ffffff !important;
        border: 1px solid var(--js-border) !important;
        border-radius: 18px !important;
        padding: 22px !important;
        box-shadow: 0 4px 16px rgba(20, 33, 61, 0.03) !important;
        transition: all 0.2s ease;
    }

    /* Feature Cards (Beranda) */
    .js-feature-card {
        background: #ffffff;
        border: 1px solid var(--js-border);
        border-radius: 18px;
        padding: 24px 20px;
        box-shadow: 0 4px 14px rgba(20, 33, 61, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .js-feature-icon {
        font-size: 2rem;
        margin-bottom: 12px;
        display: inline-block;
    }
    .js-feature-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.15rem;
    }
    .js-feature-card p {
        color: var(--js-muted);
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0 0 16px 0;
        flex-grow: 1;
    }

    /* Step Workflow */
    .js-step {
        display: flex;
        gap: 16px;
        align-items: flex-start;
        padding: 16px 18px;
        background: #ffffff;
        border: 1px solid var(--js-border);
        border-radius: 14px;
        margin-bottom: 12px;
    }
    .js-step-num {
        background: #eff4fe;
        color: var(--js-royal);
        font-weight: 800;
        font-size: 1.1rem;
        min-width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #dbeafe;
    }
    .js-step-text h4 {
        margin: 0 0 4px 0;
        font-size: 1rem;
    }
    .js-step-text p {
        margin: 0;
        color: var(--js-muted);
        font-size: 0.88rem;
        line-height: 1.5;
    }

    /* Education Cards */
    .js-edu-module {
        background: #ffffff;
        border: 1px solid var(--js-border);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(20, 33, 61, 0.02);
    }
    .js-edu-module h3 {
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1.18rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Gradio Tabs Styling */
    .tabs {
        border-bottom: 1px solid var(--js-border) !important;
        gap: 8px !important;
        margin-bottom: 18px !important;
    }
    button[role=tab] {
        font-family: 'DM Sans', sans-serif !important;
        border-radius: 10px 10px 0 0 !important;
        border: 1px solid transparent !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 18px !important;
        color: var(--js-muted) !important;
        transition: all 0.15s ease !important;
    }
    button[role=tab]:hover {
        color: var(--js-navy) !important;
        background: #f1f5f9 !important;
    }
    button[role=tab][aria-selected=true] {
        background: #ffffff !important;
        color: var(--js-royal) !important;
        border-color: var(--js-border) var(--js-border) #ffffff !important;
        box-shadow: 0 -3px 0 var(--js-royal) inset !important;
    }

    /* Form Controls */
    input, textarea, select {
        border-radius: 10px !important;
        border: 1px solid var(--js-border) !important;
        font-family: inherit !important;
    }
    input:focus, textarea:focus {
        border-color: var(--js-royal) !important;
        box-shadow: 0 0 0 3px rgba(36, 87, 214, 0.12) !important;
    }
    label span {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 0.9rem !important;
    }

    /* Buttons */
    .gr-button-primary {
        background: var(--js-royal) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 11px 22px !important;
        box-shadow: 0 4px 14px rgba(36, 87, 214, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    .gr-button-primary:hover {
        background: var(--js-royal-hover) !important;
        box-shadow: 0 6px 18px rgba(36, 87, 214, 0.3) !important;
        transform: translateY(-1px);
    }
    .gr-button-secondary {
        background: #ffffff !important;
        color: #334155 !important;
        border: 1px solid var(--js-border) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    .gr-button-secondary:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
    }

    /* Footer */
    .js-footer {
        margin-top: 40px;
        padding: 24px 18px;
        border-top: 1px solid var(--js-border);
        text-align: center;
        color: var(--js-muted);
        font-size: 0.86rem;
        line-height: 1.6;
    }

    @media (max-width: 768px) {
        .js-hero {
            padding: 30px 22px;
            border-radius: 18px;
        }
        .gradio-container {
            padding: 10px 12px 32px !important;
        }
    }
    """

    with gr.Blocks(
        title="JobShield — Deteksi Cerdas Lowongan Kerja Palsu",
        css=theme_css,
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
    ) as ui:
        # Top Header / Brand Bar
        gr.HTML(
            "<header class='js-topbar'>"
            "<div class='js-brand'>🛡️ JobShield <span class='js-brand-badge'>AI Detection & Safety</span></div>"
            "<div style='font-size:0.85rem; color:#64748b; font-weight:500;'>"
            "Sistem Cerdas Skrining Lowongan Kerja Daring"
            "</div>"
            "</header>"
        )

        # Global Disclaimer Banner
        gr.HTML(
            "<div class='js-disclaimer'>⚠️ <b>Pemberitahuan Transparansi:</b> "
            f"{config.LANGUAGE_WARNING} Sistem ini berfungsi sebagai instrumen skrining awal indikasi risiko, "
            "bukan jaminan keaslian lowongan kerja atau vonis hukum final. Selalu lakukan verifikasi mandiri "
            "sebelum menyerahkan data pribadi atau membuat keputusan melamar.</div>"
        )

        with gr.Tabs() as main_tabs:
            # =========================================================================
            # TAB 1: BERANDA
            # =========================================================================
            with gr.Tab("🏠  Beranda", id="tab_home"):
                gr.HTML(
                    "<section class='js-hero'>"
                    "<div class='eyebrow'>JOBSHIELD · SMART CYBERSECURITY FOR JOB SEEKERS</div>"
                    "<h1>Periksa Lowongan Kerja Sebelum Terlambat.</h1>"
                    "<p>Lindungi diri Anda dari modus penipuan rekrutmen, pungutan biaya ilegal, "
                    "dan pencurian identitas. JobShield menggunakan kecerdasan buatan untuk menganalisis "
                    "indikasi risiko lowongan kerja secara cepat, objektif, dan transparan.</p>"
                    "</section>"
                )

                # Call-To-Action Row
                with gr.Row():
                    btn_cta_single = gr.Button(
                        "🔎 Periksa Satu Lowongan Sekarang", variant="primary", scale=2
                    )
                    btn_cta_edu = gr.Button(
                        "🛡️ Pelajari Modus Penipuan (Pusat Edukasi)", variant="secondary", scale=2
                    )

                gr.HTML("<div style='height: 18px;'></div>")

                # Three Feature Cards
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML(
                            "<div class='js-feature-card'>"
                            "<div>"
                            "<span class='js-feature-icon'>📝</span>"
                            "<h3>Cek Satu Lowongan</h3>"
                            "<p>Analisis mendalam terhadap deskripsi, profil perusahaan, kompensasi, "
                            "dan 16 parameter fitur lowongan kerja.</p>"
                            "</div>"
                            "</div>"
                        )
                        btn_goto_single = gr.Button("Mulai Cek Lowongan →", variant="secondary")

                    with gr.Column(scale=1):
                        gr.HTML(
                            "<div class='js-feature-card'>"
                            "<div>"
                            "<span class='js-feature-icon'>📂</span>"
                            "<h3>Analisis CSV Massal</h3>"
                            "<p>Unggah berkas CSV hingga 500 lowongan sekaligus. Dapatkan rangkuman risiko "
                            "dan ekspor data yang aman dari formula injection.</p>"
                            "</div>"
                            "</div>"
                        )
                        btn_goto_batch = gr.Button("Mulai Analisis CSV →", variant="secondary")

                    with gr.Column(scale=1):
                        gr.HTML(
                            "<div class='js-feature-card'>"
                            "<div>"
                            "<span class='js-feature-icon'>🛡️</span>"
                            "<h3>Pusat Edukasi Anti-Scam</h3>"
                            "<p>Panduan komprehensif mengenali modus penipuan di Indonesia, checklist sebelum "
                            "melamar, dan langkah pelaporan resmi.</p>"
                            "</div>"
                            "</div>"
                        )
                        btn_goto_edu = gr.Button("Buka Pusat Edukasi →", variant="secondary")

                gr.HTML("<div style='height: 24px;'></div>")

                # 3-Step Workflow
                gr.HTML(
                    "<div class='js-card'>"
                    "<h3>Cara Kerja JobShield dalam 3 Langkah Sederhana</h3>"
                    "<div class='js-step'>"
                    "<div class='js-step-num'>1</div>"
                    "<div class='js-step-text'>"
                    "<h4>Masukkan Informasi Lowongan</h4>"
                    "<p>Tempelkan judul dan deskripsi lowongan kerja yang Anda temukan di internet atau unggah file CSV.</p>"
                    "</div>"
                    "</div>"
                    "<div class='js-step'>"
                    "<div class='js-step-num'>2</div>"
                    "<div class='js-step-text'>"
                    "<h4>Evaluasi Kecerdasan Buatan</h4>"
                    "<p>Model Machine Learning mengevaluasi pola tekstual, struktur linguistik, dan kelengkapan profil organisasi.</p>"
                    "</div>"
                    "</div>"
                    "<div class='js-step'>"
                    "<div class='js-step-num'>3</div>"
                    "<div class='js-step-text'>"
                    "<h4>Dapatkan Skor Risiko & Panduan Tindakan</h4>"
                    "<p>Lihat indikasi risiko (Rendah / Waspada / Tinggi) serta panduan verifikasi mandiri sebelum melamar.</p>"
                    "</div>"
                    "</div>"
                    "</div>"
                )

                # Navigasi tab interaktif dari Beranda
                btn_cta_single.click(lambda: gr.Tabs(selected="tab_single"), outputs=main_tabs)
                btn_cta_edu.click(lambda: gr.Tabs(selected="tab_edu"), outputs=main_tabs)
                btn_goto_single.click(lambda: gr.Tabs(selected="tab_single"), outputs=main_tabs)
                btn_goto_batch.click(lambda: gr.Tabs(selected="tab_batch"), outputs=main_tabs)
                btn_goto_edu.click(lambda: gr.Tabs(selected="tab_edu"), outputs=main_tabs)

            # =========================================================================
            # TAB 2: CEK SATU LOWONGAN
            # =========================================================================
            with gr.Tab("🔎  Cek Lowongan", id="tab_single"):
                gr.Markdown(
                    "### 🔎 Pemeriksaan Keamanan Lowongan Tunggal\n"
                    "Masukkan rincian informasi lowongan kerja untuk mendapatkan evaluasi risiko berbasis model kecerdasan buatan."
                )

                # Demo Presets
                with gr.Row():
                    btn_demo_legit = gr.Button("📋 Muat Contoh Lowongan Sah", variant="secondary")
                    btn_demo_scam = gr.Button("⚠️ Muat Contoh Lowongan Penipuan", variant="secondary")
                    btn_clear = gr.Button("🔄 Bersihkan Formulir", variant="secondary")

                with gr.Row():
                    # Input Form Column
                    with gr.Column(scale=3, elem_classes=["js-card"]):
                        gr.Markdown("#### Formulir Data Lowongan")
                        inp_title = gr.Textbox(
                            label="Judul Lowongan Kerja (Wajib)",
                            placeholder="Contoh: Senior Python Backend Developer",
                            max_lines=2,
                        )
                        inp_desc = gr.Textbox(
                            label="Deskripsi Lowongan Lengkap (Wajib)",
                            placeholder="Tempelkan seluruh uraian pekerjaan, tanggung jawab, dan kualifikasi di sini...",
                            lines=8,
                        )

                        with gr.Accordion("Detail Tambahan (Opsional — untuk Akurasi Optimal)", open=False):
                            inp_profile = gr.Textbox(
                                label="Profil Perusahaan (Company Profile)",
                                placeholder="Profil, visi, atau latar belakang singkat perusahaan...",
                                lines=3,
                            )
                            inp_req = gr.Textbox(
                                label="Persyaratan Pelamar (Requirements)",
                                placeholder="Syarat keahlian, kualifikasi teknis, atau pengalaman...",
                                lines=3,
                            )
                            inp_benefits = gr.Textbox(
                                label="Fasilitas & Tunjangan (Benefits)",
                                placeholder="Asuransi kesehatan, tunjangan cuti, opsi kerja, dll...",
                                lines=2,
                            )

                            with gr.Row():
                                inp_loc = gr.Textbox(label="Lokasi Kerja", placeholder="Contoh: US, CA, San Francisco atau Jakarta")
                                inp_dept = gr.Textbox(label="Departemen / Divisi", placeholder="Engineering")
                                inp_salary = gr.Textbox(label="Kisaran Gaji", placeholder="80000-110000")

                            with gr.Row():
                                inp_emp_type = gr.Dropdown(
                                    label="Jenis Pekerjaan",
                                    choices=["", "Full-time", "Part-time", "Contract", "Temporary", "Other"],
                                    value="",
                                )
                                inp_exp = gr.Dropdown(
                                    label="Tingkat Pengalaman",
                                    choices=[
                                        "",
                                        "Entry level",
                                        "Mid-Senior level",
                                        "Associate",
                                        "Director",
                                        "Executive",
                                        "Not Applicable",
                                    ],
                                    value="",
                                )
                                inp_edu = gr.Dropdown(
                                    label="Pendidikan Minimum",
                                    choices=[
                                        "",
                                        "Bachelor's Degree",
                                        "Master's Degree",
                                        "High School or equivalent",
                                        "Unspecified",
                                    ],
                                    value="",
                                )

                            with gr.Row():
                                inp_ind = gr.Textbox(label="Sektor Industri", placeholder="Information Technology")
                                inp_func = gr.Textbox(label="Fungsi Pekerjaan", placeholder="Engineering")

                            with gr.Row():
                                inp_tele = gr.Checkbox(label="Bekerja Jarak Jauh (Remote / WFH)", value=False)
                                inp_logo = gr.Checkbox(label="Memiliki Logo Perusahaan", value=False)
                                inp_q = gr.Checkbox(label="Ada Pertanyaan Screening", value=False)

                        btn_submit = gr.Button("🚀 PERIKSA KEAMANAN LOWONGAN", variant="primary")

                    # Output Column
                    with gr.Column(scale=2, elem_classes=["js-card"]):
                        gr.Markdown("#### Hasil Analisis Keamanan")
                        out_badge = gr.HTML(
                            value=(
                                "<div style='background-color: #f8fafc; color: #64748b; padding: 18px; "
                                "border-radius: 12px; font-weight: 600; border: 1px dashed #cbd5e1;'>"
                                "ℹ️ Formulir siap. Tekan tombol <b>Periksa Keamanan Lowongan</b> untuk memulai evaluasi."
                                "</div>"
                            )
                        )
                        with gr.Row():
                            out_proba = gr.Textbox(
                                label="Skor Model / Probabilitas Keluaran Model",
                                value="-",
                                interactive=False,
                            )
                            out_threshold = gr.Textbox(
                                label="Ambang Batas Keputusan (*Threshold*)",
                                value=f"{threshold * 100:.2f}%",
                                interactive=False,
                            )
                        out_saran = gr.Markdown("Panduan tindak lanjut dan rekomendasi keamanan akan muncul di sini.")

                all_inputs = [
                    inp_title,
                    inp_desc,
                    inp_profile,
                    inp_req,
                    inp_benefits,
                    inp_loc,
                    inp_dept,
                    inp_salary,
                    inp_emp_type,
                    inp_exp,
                    inp_edu,
                    inp_ind,
                    inp_func,
                    inp_tele,
                    inp_logo,
                    inp_q,
                ]

                btn_submit.click(
                    fn=analyze_single_job,
                    inputs=all_inputs,
                    outputs=[out_badge, out_proba, out_threshold, out_saran],
                )

                def load_legit():
                    return (
                        "Senior Software Engineer",
                        "Design and maintain backend services in Python and Go with a team of eight engineers.",
                        "Acme Systems is a 200-person software company building logistics tools.",
                        "5+ years of experience, BSc in Computer Science, PostgreSQL and AWS.",
                        "Health insurance, paid leave, 401k.",
                        "US, CA, San Francisco",
                        "Engineering",
                        "120000-150000",
                        "Full-time",
                        "Mid-Senior level",
                        "Bachelor's Degree",
                        "Information Technology",
                        "Engineering",
                        False,
                        True,
                        True,
                    )

                def load_scam():
                    return (
                        "Work From Home - Earn $5000 Weekly!!!",
                        (
                            "No experience needed! Send your bank details and a small registration fee to start now. "
                            "Contact us on WhatsApp immediately!!!"
                        ),
                        "",
                        "",
                        "",
                        "US",
                        "",
                        "",
                        "Part-time",
                        "",
                        "",
                        "",
                        "",
                        True,
                        False,
                        False,
                    )

                def clear_form():
                    return (
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        False,
                        False,
                        False,
                    )

                btn_demo_legit.click(fn=load_legit, outputs=all_inputs)
                btn_demo_scam.click(fn=load_scam, outputs=all_inputs)
                btn_clear.click(fn=clear_form, outputs=all_inputs)

            # =========================================================================
            # TAB 3: CEK BANYAK (CSV)
            # =========================================================================
            with gr.Tab("📂  Cek Banyak (CSV)", id="tab_batch"):
                gr.Markdown(
                    "### 📂 Skrining Massal Lowongan Kerja (Berkas CSV)\n"
                    f"Unggah berkas CSV untuk memindai sekumpulan lowongan kerja secara serentak. "
                    rf"Batas pemrosesan: maksimal **{config.MAX_BATCH} baris** dan ukuran berkas **$\le {config.MAX_CSV_SIZE // (1024 * 1024)}$ MB**. "
                    "Kolom `title` dan `description` wajib ada pada berkas CSV."
                )

                with gr.Row():
                    csv_input = gr.File(label="Pilih Berkas CSV", file_types=[".csv"])
                    with gr.Column():
                        btn_download_template = gr.Button("📥 Unduh Contoh Template CSV", variant="secondary")
                        btn_process_csv = gr.Button("⚙️ PROSES ANALISIS BATCH", variant="primary")

                out_template_file = gr.File(label="Unduh Template", visible=False)
                btn_download_template.click(fn=create_template_csv, outputs=out_template_file)

                out_summary = gr.Markdown("")
                out_table = gr.Dataframe(label="Pratinjau Hasil Prediksi", interactive=False)
                out_download_csv = gr.File(label="📥 Unduh Hasil Lengkap Beranotasi (.csv)")

                btn_process_csv.click(
                    fn=analyze_batch_csv,
                    inputs=csv_input,
                    outputs=[out_summary, out_table, out_download_csv],
                )

            # =========================================================================
            # TAB 4: PUSAT EDUKASI
            # =========================================================================
            with gr.Tab("🛡️  Pusat Edukasi", id="tab_edu"):
                gr.Markdown(
                    "### 🛡️ Pusat Edukasi & Panduan Keamanan Pencari Kerja\n"
                    "Kenali modus operandi penipuan rekrutmen di Indonesia dan pelajari langkah perlindungan diri sebelum melamar."
                )

                # 5 Modul Edukasi
                with gr.Accordion("1. Mengenali Tanda Bahaya Lowongan Mencurigakan", open=True):
                    gr.Markdown(
                        "Kenali tanda-tanda berikut saat membaca pengumuman lowongan kerja:\n\n"
                        "• **Pungutan Biaya:** Diminta membayar biaya pendaftaran, seragam, akomodasi, tes kesehatan, atau transportasi dengan janji akan diganti (*reimburse*).\n"
                        "• **Gaji Tidak Masuk Akal:** Menjanjikan kompensasi sangat tinggi untuk pekerjaan tanpa syarat pengalaman atau keahlian khusus.\n"
                        "• **Deskripsi Pekerjaan Kabur:** Tanggung jawab kerja tidak dijelaskan secara spesifik, hanya menggunakan frasa umum seperti 'bantu input data' atau 'tugas daring santai'.\n"
                        "• **Proses Terlalu Cepat:** Dinyatakan langsung diterima tanpa wawancara resmi, portofolio, atau seleksi kualifikasi yang wajar.\n"
                        "• **Kontak Tidak Konsisten:** Menggunakan alamat email publik gratisan (@gmail.com, @yahoo.com) atau mengarahkan komunikasi hanya melalui WhatsApp / Telegram pribadi."
                    )

                with gr.Accordion("2. Modus Penipuan Rekrutmen Populer di Indonesia", open=False):
                    gr.Markdown(
                        "Berikut adalah pola-pola penipuan lowongan kerja yang kerap terjadi di Indonesia:\n\n"
                        "• **Penyamaran BUMN / Perusahaan Ternama:** Mencatut nama dan logo perusahaan besar seperti Pertamina, PLN, KAI, atau bank nasional, disertai surat panggilan palsu berformat resmi.\n"
                        "• **Modus Tiket Travel & Akomodasi Rekanan:** Calon korban diminta memesan tiket pesawat atau reservasi hotel melalui agen travel tertentu dengan jaminan biaya akan diganti saat tiba di lokasi wawancara.\n"
                        "• **Tugas Like, Follow, & Deposit Uang (Job Online Freelance):** Korban diberi tugas daring mudah lalu diminta mendepositokan sejumlah dana dengan janji komisi berlipat ganda, yang kemudian tidak bisa ditarik.\n"
                        "• **Pencurian Identitas (Phishing):** Formulir pendaftaran meminta foto KTP, KK, selfie dengan identitas, atau nomor rekening bank sebelum proses wawancara bahkan dimulai."
                    )

                with gr.Accordion("3. Cara Memverifikasi Keabsahan Perusahaan", open=False):
                    gr.Markdown(
                        "Lakukan verifikasi bertahap berikut sebelum merespons panggilan seleksi:\n\n"
                        "• **Cek Situs Resmi Perusahaan:** Kunjungi situs web perusahaan langsung dengan mengetikkan alamat domain resmi di peramban. Periksa menu **Karier / Career**.\n"
                        "• **Periksa Domain Email:** Email panggilan kerja resmi umumnya menggunakan akhiran domain korporat (misal: `@nama-perusahaan.co.id` atau `@nama-perusahaan.com`).\n"
                        "• **Hubungi Kontak Resmi Independen:** Cari nomor telepon kantor pusat perusahaan melalui pencarian mandiri (bukan nomor kontak yang tercantum pada surat panggilan yang mencurigakan).\n"
                        "• **Verifikasi Alamat Fisik:** Cek alamat lokasi wawancara di peta digital (Google Maps/Street View) untuk memastikan keberadaan kantor fisik yang sah."
                    )

                with gr.Accordion("4. Perlindungan Data Pribadi Pelamar", open=False):
                    gr.Markdown(
                        "Prinsip penting menjaga kerahasiaan data pribadi (selaras dengan prinsip UU Pelindungan Data Pribadi):\n\n"
                        "• **Jangan Pernah Bagikan OTP / PIN:** Perekrut sah tidak akan pernah meminta kode OTP WhatsApp, PIN SMS perbankan, atau password akun Anda.\n"
                        "• **Batasi Dokumen di Tahap Awal:** Cukup kirimkan resume/CV profesional dan portofolio. Jangan kirimkan nomor rekening atau foto buku tabungan di tahap awal.\n"
                        "• **Watermark Identitas:** Jika diminta salinan KTP di tahap akhir kontrak, bubuhkan watermark digital bertuliskan tujuan spesifik (misal: *'HANYA UNTUK KEPERLUAN VERIFIKASI KERJA DI PT XYZ - [TANGGAL]'*)."
                    )

                with gr.Accordion("5. Langkah Jika Terlanjur Menghadapi Indikasi Penipuan", open=False):
                    gr.Markdown(
                        "Jika Anda merasa sedang berhadapan dengan penipu rekrutmen:\n\n"
                        "1. **Hentikan Komunikasi:** Jangan lakukan pembayaran apa pun dan jangan lanjutkan obrolan.\n"
                        "2. **Simpan Bukti:** Ambil tangkapan layar surat panggilan, tautan form, nomor kontak, dan riwayat obrolan.\n"
                        "3. **Hubungi Pihak Bank:** Jika sempat mentransfer dana, segera hubungi call center resmi bank Anda untuk permintaan pemblokiran rekening tujuan penipu.\n"
                        "4. **Laporkan ke Saluran Resmi:** Laporkan indikasi kejahatan siber ke portal resmi pemerintah:\n"
                        "   - Portal Pengaduan Publik Nasional: **lapor.go.id**\n"
                        "   - Patroli Siber Kepolisian RI: **patrolisiber.id**\n"
                        "   - Kementerian Ketenagakerjaan (Kemnaker RI)"
                    )

                gr.HTML("<div style='height: 20px;'></div>")

                # Checklist Interaktif Sebelum Melamar
                gr.HTML("<div class='js-card'><h3>📋 Checklist Interaktif Sebelum Mengirimkan Lamaran</h3><p style='color:#64748b; font-size:0.9rem;'>Centang butir-butir verifikasi di bawah ini untuk menguji kesiapan dan keamanan lamaran Anda:</p></div>")

                with gr.Row():
                    with gr.Column(scale=3):
                        chk_1 = gr.Checkbox(label="1. Perusahaan memiliki situs web resmi dengan nama domain korporat sendiri (bukan blog gratis)", value=False)
                        chk_2 = gr.Checkbox(label="2. Kontak email rekruter menggunakan domain resmi perusahaan (bukan Gmail, Yahoo, dll)", value=False)
                        chk_3 = gr.Checkbox(label="3. Tidak ada permintaan biaya sepeser pun untuk administrasi, seragam, atau tiket travel", value=False)
                        chk_4 = gr.Checkbox(label="4. Gaji dan fasilitas yang dijanjikan realistis sesuai standar pasar dan kualifikasi", value=False)
                        chk_5 = gr.Checkbox(label="5. Deskripsi pekerjaan spesifik dan persyaratan kualifikasi masuk akal", value=False)
                        chk_6 = gr.Checkbox(label="6. Lokasi kantor fisik dapat diverifikasi di peta atau kontak resmi dapat dihubungi", value=False)

                    with gr.Column(scale=2):
                        chk_eval_out = gr.HTML(
                            value=(
                                "<div style='background-color: #f8fafc; color: #64748b; padding: 16px 20px; "
                                "border-radius: 12px; font-weight: 600; border: 1px dashed #cbd5e1;'>"
                                "Centang butir-butir verifikasi di sebelah kiri untuk melihat evaluasi kesiapan lamaran Anda."
                                "</div>"
                            )
                        )

                chk_inputs = [chk_1, chk_2, chk_3, chk_4, chk_5, chk_6]
                for chk in chk_inputs:
                    chk.change(fn=evaluate_checklist, inputs=chk_inputs, outputs=chk_eval_out)

                gr.HTML("<div style='height: 20px;'></div>")

                # FAQ Section
                gr.HTML("<div class='js-card'><h3>❓ Pertanyaan yang Sering Diajukan (FAQ)</h3></div>")
                with gr.Accordion("Apakah hasil evaluasi kecerdasan buatan JobShield pasti 100% akurat?", open=False):
                    gr.Markdown("Tidak. Model AI adalah instrumen skrining risiko awal (*decision support*), bukan penentu kebenaran mutlak atau bukti hukum. Hasil prediksi dapat dipengaruhi oleh gaya bahasa dan kelengkapan informasi. Pengguna tetap wajib melakukan verifikasi independen.")
                with gr.Accordion("Apa yang harus saya lakukan jika perekrut meminta biaya transportasi / tiket pesawat?", open=False):
                    gr.Markdown("Segera tolak dan batalkan proses seleksi. Perusahaan kredibel di Indonesia tidak pernah memungut biaya transportasi atau mewajibkan pembelian tiket melalui agen tertentu dalam proses rekrutmen.")
                with gr.Accordion("Mengapa ada peringatan bahasa Inggris pada aplikasi ini?", open=False):
                    gr.Markdown("Model Machine Learning dilatih menggunakan dataset EMSCAD yang berbasis teks bahasa Inggris. Lowongan berbahasa Indonesia tetap dapat diperiksa, namun tingkat keandalannya dapat bervariasi. Peningkatan model lokal berbahasa Indonesia sedang dalam agenda pemeliharaan.")
                with gr.Accordion("Apakah saya perlu memasukkan data pribadi sensitif (seperti NIK / Nomor KTP) ke JobShield?", open=False):
                    gr.Markdown("Sama sekali **TIDAK PERLU**. JobShield hanya mengevaluasi teks lowongan pekerjaan (judul, profil, uraian tugas, kualifikasi). Jangan pernah memasukkan NIK, nomor rekening, atau informasi pribadi Anda ke formulir publik mana pun.")

            # =========================================================================
            # TAB 5: TENTANG JOBSHIELD
            # =========================================================================
            with gr.Tab("ℹ️  Tentang JobShield", id="tab_about"):
                gr.Markdown("### ℹ️ Tentang JobShield — Fake Job Detector")
                gr.Markdown(
                    "JobShield adalah inisiatif sistem cerdas yang dirancang untuk membantu para pencari kerja mendeteksi "
                    "potensi penipuan lowongan kerja daring menggunakan Machine Learning dan Natural Language Processing.\n\n"
                    "#### Alur Analisis Bahasa Awam\n"
                    "1. **Ekstraksi Fitur Teks:** Sistem membersihkan teks dari tag HTML, token khusus, dan menghitung proporsi huruf kapital, tanda seru, serta token kontak.\n"
                    "2. **Vektorisasi TF-IDF:** Teks lowongan diubah menjadi representasi bobot kata frekuensi tinggi.\n"
                    "3. **Klasifikasi Pembelajaran Mesin:** Model Logistic Regression terkalibrasi mengevaluasi probabilitas apakah profil lowongan menyerupai pola penipuan.\n"
                    "4. **Penentuan Tingkat Risiko:** Skor probabilitas dipetakan terhadap ambang batas dinamis untuk menyajikan rekomendasi tindakan."
                )

                gr.Markdown(
                    "> ⚠️ **Batasan Model & Bahasa:** Model dikembangkan dan dievaluasi menggunakan korpus data lowongan berbahasa Inggris. "
                    "Hasil evaluasi pada teks berbahasa Indonesia atau campuran bahasa dapat menghasilkan akurasi yang lebih rendah."
                )

                # Verified Privacy Policy Card
                gr.HTML(
                    "<div class='js-card' style='border-left: 5px solid #2457d6; margin: 16px 0;'>"
                    "<h4>🔒 Kebijakan Privasi Terverifikasi (*Zero Raw-Text Logging*)</h4>"
                    "<p style='color: #475569; font-size: 0.92rem; line-height: 1.6; margin: 0;'>"
                    "Sistem beroperasi secara <b>murni stateless</b> tanpa basis data relasional untuk menyimpan teks lowongan pengguna. "
                    "Teks mentah lowongan yang diinput hanya diproses sementara di RAM saat inferensi dan "
                    "<b>dilarang keras dicatat ke berkas log server</b> oleh sistem middleware. "
                    "Pengguna dapat mengecek lowongan dengan aman tanpa risiko kebocoran data."
                    "</p>"
                    "</div>"
                )

                with gr.Accordion("Detail Teknis Model & Metrik Evaluasi (Hold-out Test Set)", open=False):
                    metrics_rows = "\n".join([f"| **{k}** | `{v}` |" for k, v in metrics_holdout.items()])

                    gr.Markdown(
                        f"**Arsitektur Model:** `{model_name}`  \n"
                        f"**Ambang Batas Dinamis (*Threshold*):** `{threshold:.4f}` ({threshold * 100:.2f}%)  \n"
                        f"**Versi Library Runtime:** `scikit-learn=={info.get('sklearn_version', '1.9.1')}`  \n"
                        f"**Tanggal Rilis Model:** `{info.get('created_at', '2026-11-04')}`\n\n"
                        "#### 📈 Metrik Evaluasi Data Uji (Hold-out Test Set)\n"
                        "| Metrik | Nilai Evaluasi |\n"
                        "|---|---|\n"
                        f"{metrics_rows}\n"
                    )

        # Global Footer
        gr.HTML(
            "<footer class='js-footer'>"
            "JobShield · Smart Job Safety Checker · Dibuat untuk membantu pencari kerja Indonesia · "
            "Hasil AI adalah skrining awal dan tetap memerlukan verifikasi manusia."
            "</footer>"
        )

    return ui
