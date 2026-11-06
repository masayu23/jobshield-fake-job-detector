import React from 'react';
import { ShieldCheck, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';

export default function Hero({ onStartCheck }) {
  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white border-b border-slate-800">
      {/* Decorative gradient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-64 bg-blue-600/15 blur-3xl pointer-events-none rounded-full" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-14 relative z-10">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            <span>Cybersecurity & Anti-Fraud Suite</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Lindungi Diri dari <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-sky-400 bg-clip-text text-transparent">Penipuan Lowongan Kerja</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed text-balance">
            Evaluasi keaslian tawaran kerja dalam hitungan detik menggunakan model Machine Learning yang menganalisis 16 parameter, pola kata manipulatif, dan indikator red-flag penipuan.
          </p>

          <div className="pt-2 flex flex-wrap justify-center gap-3">
            <button
              onClick={onStartCheck}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-600/30 transition-all flex items-center space-x-2 text-sm sm:text-base cursor-pointer"
            >
              <Zap className="w-4 h-4" />
              <span>Mulai Verifikasi Lowongan</span>
            </button>
          </div>
        </div>

        {/* 3 Pillar Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm flex items-start space-x-3.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">Akurasi Teruji (F1 ≈ 0.86)</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Dioptimalkan untuk mendeteksi lowongan palsu pada dataset global dengan hold-out test set independen.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm flex items-start space-x-3.5">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 shrink-0">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">Inferensi Kilat &lt; 100ms</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Evaluasi instan tanpa menyimpan data pribadi lowongan Anda ke database atau log server (NFR-03).
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm flex items-start space-x-3.5">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">Edukasi & Perlindungan Korban</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Panduan modus penipuan berkedok travel ticketing, tes berbayar, dan saluran pengaduan resmi Siber Polri.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
