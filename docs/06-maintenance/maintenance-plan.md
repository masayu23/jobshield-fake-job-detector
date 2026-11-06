# Rencana Pemeliharaan (Maintenance Plan) — Fase 6

Dokumen ini mendefinisikan prosedur operasional pemeliharaan, alur kerja pembaruan model Machine Learning, pemantauan performa & *data drift*, penanganan dependensi, serta siklus hidup rilis aplikasi **Fake Job Detector**.

---

## 1. Prosedur Pembaruan Model (Model Retraining & Swap)

Model Machine Learning tidak dilatih ulang di lingkungan aplikasi backend (`src/`). Seluruh eksperimen, re-training, dan evaluasi model dilakukan di Google Colab menggunakan notebook pada folder `notebooks/`.

### 1.1 Persyaratan Artefak Model Baru
Paket ekspor dari notebook Colab harus menyediakan 4 file artefak wajib dalam satu direktori (misalnya `deploy_package/`):
1. `fake_job_detector.joblib`: Bundle dictionary scikit-learn Pipeline berisi key `model`, `threshold`, `raw_columns`, dan `model_name`.
2. `model_metadata.json`: Metadata evaluasi (metrik holdout, cross-validation, threshold, nama model, dan `sklearn_version`).
3. `fake_job_utils.py`: Modul utilitas feature engineering (`prepare_features`, `predict_postings`, dsb.).
4. `requirements.txt`: Spesifikasi dependensi inferensi model (khususnya versi tepat `scikit-learn==x.y.z`).

### 1.2 Langkah-Langkah dan Perintah Penggantian Model

Penggantian model aktif diatur secara otomatis dan aman menggunakan skrip `scripts/swap_model.py`. Skrip ini melakukan validasi menyeluruh (keberadaan file, integritas format, kecocokan 16 fitur input, konsistensi threshold, dan uji asap inferensi) sebelum memindahkan file apa pun.

```bash
# Langkah 1: Siapkan folder artefak baru hasil export Colab
# Contoh: simpan di models/incoming_model/

# Langkah 2: Jalankan uji validasi awal tanpa mengubah file aktif (--dry-run)
python scripts/swap_model.py models/incoming_model --dry-run

# Langkah 3: Eksekusi penukaran model secara aman
# Tindakan: mengarsipkan models/current/ ke models/archive/<timestamp>/ lalu memasang model baru
python scripts/swap_model.py models/incoming_model

# Atau dengan label backup kustom:
python scripts/swap_model.py models/incoming_model --backup-tag "v1.1.0_20261201"

# Langkah 4: Sesuaikan versi scikit-learn jika berubah
# Periksa models/current/requirements.txt dan perbarui requirements.txt aplikasi utama jika diperlukan

# Langkah 5: Jalankan pengujian regresi seluruh sistem
pytest --cov=src/detector --cov-report=term-missing
ruff check src tests scripts

# Langkah 6: Re-deploy atau restart service
# Docker:
make docker-build && make docker-run
# Verifikasi kesehatan aplikasi
curl http://localhost:8000/health
```

### 1.3 Prosedur Rollback Model
Jika model baru terdeteksi bermasalah di lingkungan produksi:
```bash
# Kembalikan model dari arsip sebelumnya:
python scripts/swap_model.py models/archive/<timestamp_sebelumnya>

# Jalankan ulang pengujian dan restart service:
pytest
```

---

## 2. Pemantauan Operasional & Deteksi Drift (Monitoring & Drift Detection)

Sistem harus dipantau secara berkala untuk menjaga keandalan dan mendeteksi penurunan kualitas inferensi model.

### 2.1 Metrik Sistem & Layanan
- **Throughput & Request Count**: Volume permintaan per menit pada `/api/v1/predict` dan `/api/v1/predict/batch`.
- **Latency (P50, P95, P99)**: Memastikan inferensi tetap memenuhi NFR-01 (< 500 ms per permintaan tunggal).
- **Tingkat Kesalahan (Error Rate)**: Memantau lonjakan status HTTP 422 (validasi gagal), 500 (internal error), atau 503 (model tidak tersedia).

### 2.2 Metrik Model & Deteksi Data / Concept Drift
- **Rasio Prediksi PALSU**: Rasio normal lowongan palsu pada dataset referensi berkisar antara 4% hingga 6%. Jika rasio prediksi PALSU melonjak signifikan (> 15%) atau turun drastis (< 1%) dalam periode 7 hari, ini menandakan potensi *concept drift* atau variasi masukan baru.
- **Distribusi Probabilitas**: Memantau rata-rata probabilitas dan sebaran skor risiko (RENDAH, WASPADA, TINGGI).
- **Frekuensi Peringatan Bahasa**: Memantau proporsi teks non-Inggris yang masuk ke sistem.

### 2.3 Kebijakan Privasi Logging (NFR-03 & NFR-06)
- **DILARANG KERAS** mencatat teks mentah lowongan (`title`, `description`, `company_profile`, dll) ke file log produksi.
- Log hanya mencakup: `timestamp`, `request_id`, `client_ip` (atau hash), `endpoint`, `processing_time_ms`, `http_status`, `predicted_label`, dan `predicted_probability`.

---

## 3. Siklus Umpan Balik & Pengumpulan Data (Feedback Loop)

Untuk terus meningkatkan akurasi model:
1. **Pencatatan Anomali**: Pengguna dapat menandai prediksi yang keliru (False Positive atau False Negative) melalui tombol feedback di UI atau kanal pelaporan internal.
2. **Review Ahli / Labeling**: Setiap data lowongan yang dilaporkan diverifikasi secara manual oleh verifikator manusia sebelum dimasukkan ke dalam basis data kandidat training berikutnya.
3. **Penyimpanan Aman & Sanitasi Data**: Data umpan balik disanitasi dari informasi kontak sensitif pelamar (PII) sebelum digabungkan ke dataset pelatihan di `notebooks/`.

---

## 4. Pemeliharaan Dependensi & Keamanan

1. **Audit Keamanan Berkala**:
   - Lakukan pemindaian dependensi bulanan menggunakan `pip audit` atau Dependabot GitHub.
   - Perbarui dependensi non-kritis (FastAPI, Gradio, uvicorn, pydantic) saat terdapat patch keamanan.
2. **Batasan Kompatibilitas Model**:
   - Versi `scikit-learn` pada lingkungan aplikasi harus selalu identik dengan `sklearn_version` pada `models/current/model_metadata.json` guna mencegah ketidakcocokan deserialisasi unpickling.

---

## 5. Pengembangan Jangka Panjang (Future Enhancements)

- **Dukungan Bahasa Indonesia**: Fine-tuning transformer lokal (misalnya IndoBERT / IndoRoBERTa) untuk mendeteksi lowongan penipuan berbahasa Indonesia di portal kerja lokal.
- **Explainability (XAI)**: Menyediakan visualisasi kontribusi fitur atau kata kunci paling mencurigakan (misalnya via LIME atau SHAP) di antarmuka Gradio.
- **Integrasi Database & Webhook**: Menyimpan riwayat audit skrining terenkripsi dan integrasi alert via Slack/Discord webhook saat terdeteksi indikasi penipuan massal.

---

## 6. Log Rilis

| Versi | Tanggal | Model | Perubahan Utama |
|---|---|---|---|
| `v1.0.0` | 2026-11-04 | Logistic Regression (Colab 2026-11-04, thr=0.7827) | Rilis awal: API FastAPI, Gradio UI 3 tab, Docker non-root, 58 unit/integration/NFR tests (92% coverage). |

---

## 7. Definition of Done (DoD) Fase 6

- [x] Prosedur pembaruan model terdokumentasi lengkap dengan perintah persis
- [x] Skrip validasi dan penukaran model (`scripts/swap_model.py`) dibuat dan berfungsi
- [x] Pengujian otomatis untuk skrip swap model (`tests/test_swap_model.py`) tersedia dan lulus
- [x] Prosedur monitoring, drift detection, privasi, dan feedback loop terdokumentasi
- [ ] Gate fase 6 dicentang (menunggu persetujuan pemilik proyek)
