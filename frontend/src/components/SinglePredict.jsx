import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  RotateCcw, 
  Send,
  Building,
  Briefcase,
  DollarSign,
  MapPin,
  ExternalLink
} from 'lucide-react';
import { predictSingle } from '../api';

const INITIAL_FORM = {
  title: '',
  description: '',
  company_profile: '',
  requirements: '',
  benefits: '',
  location: '',
  department: '',
  salary_range: '',
  employment_type: '',
  required_experience: '',
  required_education: '',
  industry: '',
  function: '',
  telecommuting: 0,
  has_company_logo: 0,
  has_questions: 0,
};

export default function SinglePredict({ onNavigateToEdu, onConsultWithGemini }) {
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (checked ? 1 : 0) : value,
    }));
  };

  const handleLoadLegit = () => {
    setFormData({
      title: 'Senior Software Engineer',
      description: 'Design and maintain backend services in Python and Go with a team of eight engineers.',
      company_profile: 'Acme Systems is a 200-person software company building logistics tools.',
      requirements: '5+ years of experience, BSc in Computer Science, PostgreSQL and AWS.',
      benefits: 'Health insurance, paid leave, 401k.',
      location: 'US, CA, San Francisco',
      department: 'Engineering',
      salary_range: '120000-150000',
      employment_type: 'Full-time',
      required_experience: 'Mid-Senior level',
      required_education: "Bachelor's Degree",
      industry: 'Information Technology',
      function: 'Engineering',
      telecommuting: 0,
      has_company_logo: 1,
      has_questions: 1,
    });
    setResult(null);
    setError(null);
  };

  const handleLoadScam = () => {
    setFormData({
      title: 'Work From Home - Earn $5000 Weekly!!!',
      description: 'No experience needed! Send your bank details and a small registration fee to start now. Contact us on WhatsApp immediately!!!',
      company_profile: '',
      requirements: '',
      benefits: '',
      location: 'US',
      department: '',
      salary_range: '',
      employment_type: 'Part-time',
      required_experience: '',
      required_education: '',
      industry: '',
      function: '',
      telecommuting: 1,
      has_company_logo: 0,
      has_questions: 0,
    });
    setResult(null);
    setError(null);
  };

  const handleClear = () => {
    setFormData(INITIAL_FORM);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setError('Judul lowongan kerja wajib diisi.');
      return;
    }
    if (!formData.description.trim()) {
      setError('Deskripsi lowongan kerja wajib diisi.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await predictSingle(formData);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan saat memproses prediksi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Intro & Preset Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <span>🔎 Pemeriksaan Keamanan Lowongan Tunggal</span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Masukkan rincian informasi lowongan kerja untuk mendapatkan skor probabilitas dan evaluasi risiko AI.
          </p>
        </div>

        {/* Demo Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleLoadLegit}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors flex items-center space-x-1.5 cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Contoh Sah</span>
          </button>
          <button
            type="button"
            onClick={handleLoadScam}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 transition-colors flex items-center space-x-1.5 cursor-pointer"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Contoh Penipuan</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition-colors flex items-center space-x-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Form + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Form Column (7 Cols) */}
        <form onSubmit={handleSubmit} className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-base">Formulir Data Lowongan</h3>
            <p className="text-xs text-slate-500">Kolom dengan tanda (*) wajib diisi untuk inferensi model.</p>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs sm:text-sm flex items-start space-x-2.5">
              <ShieldAlert className="w-5 h-5 shrink-0 text-rose-500 mt-0.5" />
              <div>
                <p className="font-semibold">Gagal Memproses Lowongan</p>
                <p className="mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Primary Inputs */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Judul Lowongan Kerja (Job Title) <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Contoh: Senior Python Backend Developer atau Admin Data Entry"
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all bg-slate-50/50 focus:bg-white"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Deskripsi Lengkap Lowongan (Job Description) <span className="text-rose-500">*</span>
              </label>
              <textarea
                name="description"
                rows={6}
                value={formData.description}
                onChange={handleChange}
                placeholder="Tempelkan seluruh uraian pekerjaan, tanggung jawab, dan kualifikasi yang tertera di sini..."
                required
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all bg-slate-50/50 focus:bg-white"
              />
            </div>
          </div>

          {/* Advanced / Optional Accordion */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full px-4 py-3 bg-slate-50/80 hover:bg-slate-100/80 text-left font-semibold text-xs sm:text-sm text-slate-700 flex items-center justify-between transition-colors cursor-pointer"
            >
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <span>Detail Tambahan (Opsional — Tingkatkan Akurasi Deteksi)</span>
              </div>
              {showAdvanced ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
            </button>

            {showAdvanced && (
              <div className="p-4 space-y-4 bg-white border-t border-slate-100">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">
                    Profil Perusahaan (Company Profile)
                  </label>
                  <textarea
                    name="company_profile"
                    rows={2}
                    value={formData.company_profile}
                    onChange={handleChange}
                    placeholder="Profil, visi, atau latar belakang singkat perusahaan pembuat lowongan..."
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Persyaratan Pelamar (Requirements)
                    </label>
                    <textarea
                      name="requirements"
                      rows={2}
                      value={formData.requirements}
                      onChange={handleChange}
                      placeholder="Syarat keahlian, pengalaman, atau kualifikasi..."
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Fasilitas & Tunjangan (Benefits)
                    </label>
                    <textarea
                      name="benefits"
                      rows={2}
                      value={formData.benefits}
                      onChange={handleChange}
                      placeholder="Asuransi, tunjangan cuti, opsi kerja..."
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Lokasi Kerja</label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      placeholder="Contoh: US, CA, San Francisco"
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Departemen / Divisi</label>
                    <input
                      type="text"
                      name="department"
                      value={formData.department}
                      onChange={handleChange}
                      placeholder="Engineering, HR, dll."
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Kisaran Gaji</label>
                    <input
                      type="text"
                      name="salary_range"
                      value={formData.salary_range}
                      onChange={handleChange}
                      placeholder="120000-150000"
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Jenis Pekerjaan</label>
                    <select
                      name="employment_type"
                      value={formData.employment_type}
                      onChange={handleChange}
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="">-- Pilih --</option>
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Temporary">Temporary</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Pengalaman</label>
                    <select
                      name="required_experience"
                      value={formData.required_experience}
                      onChange={handleChange}
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="">-- Pilih --</option>
                      <option value="Entry level">Entry level</option>
                      <option value="Mid-Senior level">Mid-Senior level</option>
                      <option value="Associate">Associate</option>
                      <option value="Director">Director</option>
                      <option value="Executive">Executive</option>
                      <option value="Not Applicable">Not Applicable</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Pendidikan</label>
                    <select
                      name="required_education"
                      value={formData.required_education}
                      onChange={handleChange}
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="">-- Pilih --</option>
                      <option value="Bachelor's Degree">Bachelor's Degree</option>
                      <option value="Master's Degree">Master's Degree</option>
                      <option value="High School or equivalent">High School or equivalent</option>
                      <option value="Unspecified">Unspecified</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Sektor Industri</label>
                    <input
                      type="text"
                      name="industry"
                      value={formData.industry}
                      onChange={handleChange}
                      placeholder="Information Technology, Retail, dll."
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Fungsi Pekerjaan</label>
                    <input
                      type="text"
                      name="function"
                      value={formData.function}
                      onChange={handleChange}
                      placeholder="Engineering, Sales, dll."
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Checkboxes */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                  <label className="flex items-center space-x-2 text-xs text-slate-700 cursor-pointer">
                    <input
                      type="checkbox"
                      name="telecommuting"
                      checked={Boolean(formData.telecommuting)}
                      onChange={handleChange}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span>Remote / WFH</span>
                  </label>

                  <label className="flex items-center space-x-2 text-xs text-slate-700 cursor-pointer">
                    <input
                      type="checkbox"
                      name="has_company_logo"
                      checked={Boolean(formData.has_company_logo)}
                      onChange={handleChange}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span>Ada Logo Perusahaan</span>
                  </label>

                  <label className="flex items-center space-x-2 text-xs text-slate-700 cursor-pointer">
                    <input
                      type="checkbox"
                      name="has_questions"
                      checked={Boolean(formData.has_questions)}
                      onChange={handleChange}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span>Ada Screening Qs</span>
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3.5 px-4 rounded-xl text-white font-bold text-sm tracking-wide shadow-lg transition-all flex items-center justify-center space-x-2 cursor-pointer ${
              loading
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-blue-500/25'
            }`}
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Mengevaluasi Sinyal Lowongan...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>PERIKSA KEAMANAN SEKARANG</span>
              </>
            )}
          </button>
        </form>

        {/* Results Column (5 Cols) */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
          <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-base">Hasil Analisis Keamanan</h3>
            {result && (
              <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                Threshold: {(result.threshold * 100).toFixed(1)}%
              </span>
            )}
          </div>

          {!result ? (
            <div className="text-center py-12 px-4 border-2 border-dashed border-slate-200 rounded-xl space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 text-slate-400 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="font-semibold text-slate-700 text-sm">Formulir Siap Dievaluasi</p>
                <p className="text-xs text-slate-500 max-w-xs mx-auto">
                  Isi judul dan deskripsi lowongan di sebelah kiri, lalu tekan tombol periksa untuk melihat analisis risiko.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Main Status Badge */}
              <div
                className={`p-4 rounded-xl border-l-8 shadow-sm flex items-start space-x-3 ${
                  result.prediksi === 'PALSU'
                    ? 'bg-rose-50 border-rose-500 text-rose-900'
                    : result.tingkat_risiko === 'WASPADA'
                    ? 'bg-amber-50 border-amber-500 text-amber-900'
                    : 'bg-emerald-50 border-emerald-500 text-emerald-900'
                }`}
              >
                {result.prediksi === 'PALSU' ? (
                  <ShieldAlert className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
                ) : result.tingkat_risiko === 'WASPADA' ? (
                  <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
                )}

                <div>
                  <h4 className="font-extrabold text-sm sm:text-base">
                    {result.prediksi === 'PALSU'
                      ? '⚠️ TERINDIKASI PALSU (Risiko Tinggi)'
                      : result.tingkat_risiko === 'WASPADA'
                      ? '⚠️ ASLI — Perlu Waspada'
                      : '✅ TERINDIKASI ASLI (Risiko Rendah)'}
                  </h4>
                  <p className="text-xs mt-1 leading-relaxed opacity-90">
                    {result.prediksi === 'PALSU'
                      ? 'Karakteristik teks dan metadata memiliki kemiripan tinggi dengan pola penipuan lowongan kerja.'
                      : result.tingkat_risiko === 'WASPADA'
                      ? 'Skor di bawah threshold penipuan, namun ada atribut yang minim atau tidak lazim.'
                      : 'Karakteristik linguistik dan susunan informasi konsisten dengan profil lowongan yang sah.'}
                  </p>
                </div>
              </div>

              {/* Gauge & Probability Metrics */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/70 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-700">Probabilitas Penipuan (Skor AI)</span>
                  <span className="font-extrabold text-slate-900 text-sm">
                    {(result.probabilitas_palsu * 100).toFixed(2)}%
                  </span>
                </div>

                {/* Progress Bar Meter */}
                <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden relative">
                  <div
                    className={`h-full transition-all duration-700 ${
                      result.prediksi === 'PALSU'
                        ? 'bg-gradient-to-r from-orange-500 to-rose-600'
                        : result.tingkat_risiko === 'WASPADA'
                        ? 'bg-gradient-to-r from-yellow-400 to-amber-500'
                        : 'bg-gradient-to-r from-emerald-400 to-teal-500'
                    }`}
                    style={{ width: `${Math.min(result.probabilitas_palsu * 100, 100)}%` }}
                  />
                  {/* Threshold marker pin */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-slate-900/60 z-10"
                    style={{ left: `${result.threshold * 100}%` }}
                    title={`Threshold: ${(result.threshold * 100).toFixed(1)}%`}
                  />
                </div>

                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>0% (Aman)</span>
                  <span>Ambang Batas: {(result.threshold * 100).toFixed(1)}%</span>
                  <span>100% (Sangat Berisiko)</span>
                </div>
              </div>

              {/* Language Warning Banner */}
              {result.warnings && result.warnings.length > 0 && (
                <div className="p-3 rounded-lg bg-blue-50/70 border border-blue-200/60 text-blue-900 text-xs flex items-start space-x-2">
                  <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <p className="leading-snug">{result.warnings[0]}</p>
                </div>
              )}

              {/* Recommended Actions */}
              <div className="space-y-3 pt-1">
                <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Rekomendasi Tindakan Keamanan:
                </h5>
                <ul className="text-xs text-slate-600 space-y-2 leading-relaxed">
                  {result.prediksi === 'PALSU' ? (
                    <>
                      <li className="flex items-start space-x-2">
                        <span className="text-rose-500 font-bold">•</span>
                        <span><strong>JANGAN transfer uang:</strong> Waspadai modus pembelian tiket travel, akomodasi, seragam, atau tes seleksi berbayar.</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-rose-500 font-bold">•</span>
                        <span><strong>JANGAN bagikan data sensitif:</strong> Lindungi foto KTP, KK, nomor rekening bank, atau kode OTP/PIN Anda.</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-rose-500 font-bold">•</span>
                        <span><strong>Cek domain pengirim email:</strong> Perusahaan terpercaya menggunakan email resmi (@nama-pt.com), bukan Gmail/Yahoo gratisan.</span>
                      </li>
                    </>
                  ) : (
                    <>
                      <li className="flex items-start space-x-2">
                        <span className="text-emerald-600 font-bold">•</span>
                        <span>Kirim lamaran hanya melalui situs web karier resmi perusahaan atau portal kerja terverifikasi.</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-emerald-600 font-bold">•</span>
                        <span>Ingat bahwa perusahaan bonafide tidak pernah memungut biaya apapun selama tahapan seleksi.</span>
                      </li>
                    </>
                  )}
                </ul>

                <div className="pt-2 space-y-2">
                  <button
                    type="button"
                    onClick={() => onConsultWithGemini && onConsultWithGemini({
                      title: formData.title,
                      prediksi: result.prediksi,
                      probabilitas_palsu: (result.probabilitas_palsu * 100).toFixed(1) + '%',
                    })}
                    className="w-full py-2.5 px-3 text-xs font-bold rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
                  >
                    <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
                    <span>Konsultasikan Hasil ke Asisten AI Gemini</span>
                  </button>

                  <button
                    type="button"
                    onClick={onNavigateToEdu}
                    className="w-full py-2 px-3 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors flex items-center justify-center space-x-1.5 cursor-pointer"
                  >
                    <span>Pelajari Modus Penipuan di Pusat Edukasi</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
