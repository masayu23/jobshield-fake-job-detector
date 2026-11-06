import React from 'react';
import { ShieldCheck, Heart } from 'lucide-react';

export default function Footer({ setActiveTab }) {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 text-xs py-10 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-md">
            <div className="flex items-center space-x-2 text-white">
              <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="font-extrabold text-base tracking-tight">JobShield</span>
              <span className="px-2 py-0.5 text-[10px] bg-blue-500/20 text-blue-300 rounded font-semibold">
                v1.0.0
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Sistem Cerdas Deteksi Penipuan Lowongan Kerja berbasis Machine Learning untuk melindungi para pencari kerja dari kejahatan siber, pungutan rekrutmen ilegal, dan pencurian identitas.
            </p>
          </div>

          <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs">
            <button
              onClick={() => setActiveTab('single')}
              className="text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              Cek Lowongan
            </button>
            <button
              onClick={() => setActiveTab('batch')}
              className="text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              Cek Banyak (CSV)
            </button>
            <button
              onClick={() => setActiveTab('education')}
              className="text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              Pusat Edukasi Anti-Scam
            </button>
            <button
              onClick={() => setActiveTab('model')}
              className="text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              Info Model
            </button>
          </div>
        </div>

        <div className="border-t border-slate-800/80 pt-6 space-y-2 text-[11px] text-slate-500">
          <p className="leading-relaxed">
            <strong>Penafian Hukum (Disclaimer):</strong> Hasil analisis yang ditampilkan oleh sistem ini merupakan estimasi probabilitas statistik berbasis model kecerdasan buatan dan ditujukan semata-mata sebagai alat bantu skrining kewaspadaan dini. Hasil ini bukan merupakan nasihat hukum ataupun jaminan mutlak. Keputusan melamar tetap menjadi tanggung jawab penuh masing-masing pencari kerja.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2">
            <p>© {new Date().getFullYear()} JobShield Security Suite. Built with React & Tailwind CSS.</p>
            <p className="flex items-center space-x-1">
              <span>Dibangun dengan integritas untuk pencari kerja Indonesia</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
