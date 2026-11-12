import React, { useState } from 'react';
import { 
  FileSpreadsheet, 
  UploadCloud, 
  Download, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Filter, 
  FileText,
  Trash2,
  Info
} from 'lucide-react';
import { predictBatchCsv } from '../api';

// Sanitasi proteksi Formula Injection untuk ekspor CSV (NFR-03 & Security Best Practice)
function sanitizeCsvCell(value) {
  if (value === null || value === undefined) return '';
  const s = String(value);
  if (s.startsWith('=') || s.startsWith('+') || s.startsWith('-') || s.startsWith('@') || s.startsWith('\t') || s.startsWith('\r')) {
    return `'${s}`;
  }
  return s;
}

export default function BatchPredict() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [batchData, setBatchData] = useState(null);
  const [filterType, setFilterType] = useState('ALL'); // 'ALL' | 'PALSU' | 'ASLI'

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        setError('Hanya berkas berformat .CSV yang diperbolehkan.');
        return;
      }
      setFile(selectedFile);
      setError(null);
      setBatchData(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!droppedFile.name.toLowerCase().endsWith('.csv')) {
        setError('Hanya berkas berformat .CSV yang didukung.');
        return;
      }
      setFile(droppedFile);
      setError(null);
      setBatchData(null);
    }
  };

  const handleProcessCsv = async () => {
    if (!file) {
      setError('Silakan pilih berkas CSV terlebih dahulu.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await predictBatchCsv(file);
      setBatchData(response);
    } catch (err) {
      setError(err.message || 'Gagal memproses berkas CSV.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = () => {
    const csvContent = 
`title,description,company_profile,requirements,benefits,location,department,salary_range,employment_type,required_experience,required_education,industry,function,telecommuting,has_company_logo,has_questions
"Data Entry Assistant - Urgent","Work from home and earn $2500 weekly with no prior experience required. Send CV and registration fee via Telegram.","","","","US","","","Part-time","","","","Customer Service",1,0,0
"Frontend React Developer","Develop high quality modern web interfaces with React, TypeScript and Tailwind CSS. Collaborate with design team.","TechCorp is an established enterprise software company with 150+ engineers.","3+ years React experience, CSS3, REST API.","Full health insurance, flexible working hours.","ID, Jakarta","Engineering","12000000-18000000","Full-time","Mid-Senior level","Bachelor's Degree","Information Technology","Engineering",0,1,1`;

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'jobshield_template_contoh.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportResults = () => {
    if (!batchData || !batchData.results) return;

    const threshold = batchData.threshold ?? 0.7827;
    const headers = ['Indeks', 'Prediksi', 'Probabilitas_Palsu', 'Tingkat_Risiko', 'Ambang_Batas'];
    const rows = batchData.results.map((item) => [
      sanitizeCsvCell(item.index + 1),
      sanitizeCsvCell(item.prediksi),
      sanitizeCsvCell((item.probabilitas_palsu * 100).toFixed(2) + '%'),
      sanitizeCsvCell(item.tingkat_risiko),
      sanitizeCsvCell((threshold * 100).toFixed(2) + '%'),
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `hasil_analisis_jobshield_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filtered results
  const filteredResults = batchData?.results.filter((item) => {
    if (filterType === 'PALSU') return item.prediksi === 'PALSU';
    if (filterType === 'ASLI') return item.prediksi === 'ASLI';
    return true;
  }) || [];

  const totalCount = batchData?.count ?? batchData?.total ?? batchData?.results?.length ?? 0;
  const fakeCount = batchData?.results.filter((r) => r.prediksi === 'PALSU').length || 0;
  const legitCount = Math.max(0, totalCount - fakeCount);
  const threshold = batchData?.threshold ?? 0.7827;

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <span>📊 Analisis Massal Banyak Lowongan (CSV)</span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Unggah berkas CSV berisi hingga 500 baris lowongan kerja untuk skrining risiko sekaligus.
          </p>
        </div>

        <button
          type="button"
          onClick={handleDownloadTemplate}
          className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors flex items-center space-x-2 cursor-pointer self-start sm:self-auto"
        >
          <Download className="w-4 h-4" />
          <span>Unduh Template CSV</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs sm:text-sm flex items-start space-x-2.5">
          <ShieldAlert className="w-5 h-5 shrink-0 text-rose-500 mt-0.5" />
          <div>
            <p className="font-semibold">Kesalahan Pemrosesan CSV</p>
            <p className="mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="border-2 border-dashed border-slate-300 hover:border-blue-500 bg-slate-50/50 hover:bg-blue-50/30 rounded-2xl p-8 text-center transition-all cursor-pointer relative"
        >
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <div className="max-w-md mx-auto space-y-3 pointer-events-none">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center shadow-inner">
              <UploadCloud className="w-7 h-7" />
            </div>

            <div>
              <p className="text-sm font-bold text-slate-800">
                {file ? file.name : 'Tarik & Letakkan Berkas CSV di Sini'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Atau klik untuk memilih berkas dari komputer Anda (Maksimal 500 baris, ukuran &lt; 10 MB)
              </p>
            </div>

            {file && (
              <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-100/70 text-blue-800 rounded-full text-xs font-semibold">
                <FileText className="w-3.5 h-3.5" />
                <span>{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-500 flex items-center space-x-1.5">
            <Info className="w-4 h-4 text-slate-400" />
            <span>Wajib memuat kolom minimal: <strong>title</strong> dan <strong>description</strong>.</span>
          </div>

          <div className="flex items-center space-x-2">
            {file && (
              <button
                type="button"
                onClick={() => {
                  setFile(null);
                  setBatchData(null);
                }}
                className="px-3.5 py-2.5 text-xs font-semibold text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors flex items-center space-x-1.5 cursor-pointer"
              >
                <Trash2 className="w-4 h-4" />
                <span>Batal</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleProcessCsv}
              disabled={!file || loading}
              className={`px-5 py-2.5 rounded-xl text-white font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all flex items-center space-x-2 cursor-pointer ${
                !file || loading
                  ? 'bg-slate-300 cursor-not-allowed shadow-none'
                  : 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/25'
              }`}
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Memproses Baris CSV...</span>
                </>
              ) : (
                <>
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Jalankan Analisis CSV</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Batch Results View */}
      {batchData && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Dievaluasi</span>
              <p className="text-2xl font-extrabold text-slate-900 mt-1">{totalCount} Lowongan</p>
            </div>

            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-rose-700 uppercase tracking-wider">Terindikasi Palsu</span>
                <ShieldAlert className="w-4 h-4 text-rose-500" />
              </div>
              <p className="text-2xl font-extrabold text-rose-800 mt-1">{fakeCount} Lowongan</p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">Konsisten Asli</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </div>
              <p className="text-2xl font-extrabold text-emerald-800 mt-1">{legitCount} Lowongan</p>
            </div>
          </div>

          {/* Filter Bar & Export */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-100">
            {/* Filter buttons */}
            <div className="flex items-center space-x-1.5">
              <Filter className="w-4 h-4 text-slate-400 mr-1" />
              <button
                type="button"
                onClick={() => setFilterType('ALL')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  filterType === 'ALL'
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                Semua ({totalCount})
              </button>
              <button
                type="button"
                onClick={() => setFilterType('PALSU')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  filterType === 'PALSU'
                    ? 'bg-rose-600 text-white'
                    : 'bg-rose-50 text-rose-700 hover:bg-rose-100'
                }`}
              >
                Palsu ({fakeCount})
              </button>
              <button
                type="button"
                onClick={() => setFilterType('ASLI')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  filterType === 'ASLI'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                }`}
              >
                Asli ({legitCount})
              </button>
            </div>

            {/* Export CSV Button */}
            <button
              type="button"
              onClick={handleExportResults}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white transition-colors flex items-center space-x-2 cursor-pointer shadow-sm self-start sm:self-auto"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Ekspor Hasil (CSV Terproteksi)</span>
            </button>
          </div>

          {/* Results Table */}
          <div className="overflow-x-auto border border-slate-200 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-700 font-bold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">No</th>
                  <th className="px-4 py-3">Status Keputusan</th>
                  <th className="px-4 py-3">Probabilitas Penipuan</th>
                  <th className="px-4 py-3">Tingkat Risiko</th>
                  <th className="px-4 py-3">Ambang Batas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredResults.map((item) => (
                  <tr key={item.index} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-4 py-3 font-semibold text-slate-500">#{item.index + 1}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                          item.prediksi === 'PALSU'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}
                      >
                        {item.prediksi === 'PALSU' ? (
                          <>
                            <ShieldAlert className="w-3 h-3 text-rose-600" />
                            <span>PALSU</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            <span>ASLI</span>
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-800">
                      {(item.probabilitas_palsu * 100).toFixed(2)}%
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`font-semibold ${
                          item.tingkat_risiko === 'TINGGI'
                            ? 'text-rose-600'
                            : item.tingkat_risiko === 'WASPADA'
                            ? 'text-amber-600'
                            : 'text-emerald-600'
                        }`}
                      >
                        {item.tingkat_risiko}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {(threshold * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
