
import joblib
import pandas as pd
import gradio as gr
import fake_job_utils                       # harus di-import agar model bisa dimuat
from fake_job_utils import predict_postings

bundle = joblib.load("fake_job_detector.joblib")

def deteksi(title, company_profile, description, requirements, benefits,
            location, salary_range, employment_type, has_company_logo, has_questions):
    row = pd.DataFrame([{
        "title": title, "company_profile": company_profile, "description": description,
        "requirements": requirements, "benefits": benefits, "location": location,
        "salary_range": salary_range or None, "employment_type": employment_type or None,
        "has_company_logo": int(has_company_logo), "has_questions": int(has_questions),
    }])
    r = predict_postings(bundle, row).iloc[0]
    return f"{r['prediksi']}  |  probabilitas palsu = {r['probabilitas_palsu']:.1%}  |  risiko {r['tingkat_risiko']}"

demo = gr.Interface(
    fn=deteksi,
    inputs=[gr.Textbox(label="Judul lowongan"),
            gr.Textbox(label="Profil perusahaan", lines=3),
            gr.Textbox(label="Deskripsi pekerjaan", lines=6),
            gr.Textbox(label="Persyaratan", lines=3),
            gr.Textbox(label="Benefit", lines=2),
            gr.Textbox(label="Lokasi (mis. US, NY, New York)"),
            gr.Textbox(label="Rentang gaji (opsional)"),
            gr.Textbox(label="Tipe pekerjaan (Full-time/Part-time/...)"),
            gr.Checkbox(label="Ada logo perusahaan"),
            gr.Checkbox(label="Ada pertanyaan screening")],
    outputs=gr.Textbox(label="Hasil deteksi"),
    title="Deteksi Lowongan Kerja Palsu",
    description="Tempel isi lowongan (bahasa Inggris, sesuai dataset pelatihan) untuk dicek.")

if __name__ == "__main__":
    demo.launch()
