import React, { useState } from 'react';
import { 
  AlertOctagon, 
  CheckSquare, 
  ExternalLink, 
  PhoneCall, 
  ShieldCheck, 
  UserX, 
  CreditCard, 
  Building2, 
  FileWarning, 
  Smartphone,
  CheckCircle2
} from 'lucide-react';

const SCAM_MODES = [
  {
    id: 1,
    title: '1. Modus Tiket Travel & Akomodasi Rekanan Bodong',
    icon: CreditCard,
    color: 'rose',
    summary: 'Modus paling banyak memakan korban di Indonesia.',
    desc: 'Korban menerima surat panggilan wawancara kerja palsu di kota besar (misal Jakarta/Bali) dan diwajibkan memesan tiket pesawat & hotel melalui agen travel tertentu dengan janji dana akan diganti (reimburse) 100% saat tiba di lokasi. Begitu dana ditransfer, panitia menghilang.',
    redFlags: [
      'Surat panggilan mencantumkan daftar peserta yang sangat banyak.',
      'Format surat mengutip nama hotel atau logo maskapai penerbangan secara amatir.',
      'Kontak yang bisa dihubungi hanya berupa nomor ponsel/WhatsApp agen travel.',
    ]
  },
  {
    id: 2,
    title: '2. Modus Tes Psikotes & Seragam Berbayar',
    icon: FileWarning,
    color: 'amber',
    summary: 'Meminta sejumlah uang di awal untuk administrasi.',
    desc: 'Pelamar dinyatakan lolos seleksi berkas, namun diminta membayar sejumlah uang (Rp 150.000 - Rp 1.000.000) untuk biaya modul tes psikotes, sertifikat pelatihan awal, seragam kerja, atau biaya tes kesehatan (MCU).',
    redFlags: [
      'Perusahaan legal TIDAK PERNAH memungut biaya tes atau seragam.',
      'Kompensasi kerja dijanjikan tidak wajar untuk memancing korban membayar.',
      'Tekanan waktu agar segera mentransfer uang dalam tempo 1-2 jam.',
    ]
  },
  {
    id: 3,
    title: '3. Modus Mengatasnamakan BUMN & Korporasi Besar',
    icon: Building2,
    color: 'blue',
    summary: 'Pencatutan nama PT Pertamina, PLN, KAI, Unilever, dsb.',
    desc: 'Pelaku membuat lowongan atau surat rekrutmen berlogo BUMN/korporasi ternama. Namun alamat email pengirim menggunakan domain webmail publik gratis (seperti @gmail.com, @yahoo.com, atau domain mirip typo/spoofed).',
    redFlags: [
      'Email pengirim bukan dari domain resmi perusahaan.',
      'Undangan seleksi tidak tercatat di portal karier resmi BUMN terkait.',
      'Penyelenggara tidak bisa dihubungi melalui call center resmi perusahaan.',
    ]
  },
  {
    id: 4,
    title: '4. Modus Phishing Data KTP & Buku Tabungan (Pinjol Ilegal)',
    icon: UserX,
    color: 'purple',
    summary: 'Pencurian identitas untuk pembukaan rekening atau pinjaman online.',
    desc: 'Pelamar diminta mengisi formulir pendaftaran yang meminta foto KTP tampak depan, foto selfie memegang KTP, foto kartu keluarga, dan nama ibu kandung dengan dalih pembukaan rekening gaji sebelum diterima bekerja.',
    redFlags: [
      'Meminta dokumen sensitif sebelum tahap wawancara pertama.',
      'Meminta nomor rekening bank beserta foto buku tabungan dan nomor kartu debit.',
      'Meminta akses kode OTP atau verifikasi akun e-wallet.',
    ]
  },
  {
    id: 5,
    title: '5. Modus Pekerjaan Sampingan "Like & Subscribe" Telegram',
    icon: Smartphone,
    color: 'emerald',
    summary: 'Skema ponzi berkedok tugas lepas (freelance).',
    desc: 'Penipu menawarkan kerja online mudah: hanya follow akun Instagram, like video YouTube, atau review produk di marketplace dengan komisi Rp 30.000 per tugas. Di awal komisi dibayar, namun selanjutnya korban diminta "deposit" jutaan rupiah untuk membuka tugas VIP yang dananya tidak bisa ditarik.',
    redFlags: [
      'Tawaran kerja dikirim secara acak via WhatsApp atau Telegram tanpa Anda melamar.',
      'Menjanjikan imbalan tidak masuk akal untuk tugas yang sangat sepele.',
      'Mewajibkan deposit uang ke rekening perorangan untuk naik level/komisi.',
    ]
  }
];

export default function Education() {
  const [checklist, setChecklist] = useState({
    c1: false,
    c2: false,
    c3: false,
    c4: false,
    c5: false,
    c6: false,
    c7: false,
  });

  const toggleCheck = (key) => {
    setChecklist((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const totalChecked = Object.values(checklist).filter(Boolean).length;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-md">
        <div className="max-w-3xl space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Panduan Keamanan Pencari Kerja Indonesia</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight">
            Pusat Edukasi & Pencegahan Penipuan Kerja
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Kecerdasan Buatan membantu mendeteksi teks manipulatif, namun kewaspadaan diri Anda adalah benteng pertahanan terbaik. Pahami modus operandi umum dan lakukan verifikasi mandiri sebelum melamar.
          </p>
        </div>
      </div>

      {/* 5 Modus Penipuan Terpopuler */}
      <div className="space-y-4">
        <div className="border-b border-slate-200 pb-2">
          <h3 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <AlertOctagon className="w-5 h-5 text-rose-600" />
            <span>5 Modus Penipuan Lowongan Kerja Terpopuler di Indonesia</span>
          </h3>
          <p className="text-xs text-slate-500">Kenali tanda bahaya (red flags) sebelum menjadi korban kerugian finansial.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SCAM_MODES.map((mode) => {
            const Icon = mode.icon;
            return (
              <div
                key={mode.id}
                className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow space-y-3"
              >
                <div className="flex items-start space-x-3">
                  <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 shrink-0">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{mode.title}</h4>
                    <p className="text-xs font-semibold text-blue-600 mt-0.5">{mode.summary}</p>
                  </div>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">{mode.desc}</p>

                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                    Ciri-Ciri Bahaya (Red Flags):
                  </span>
                  <ul className="text-xs text-slate-600 space-y-1">
                    {mode.redFlags.map((flag, idx) => (
                      <li key={idx} className="flex items-start space-x-1.5">
                        <span className="text-rose-500 font-bold shrink-0">•</span>
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Interactive 7-Step Verification Checklist */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <CheckSquare className="w-5 h-5 text-blue-600" />
              <span>Checklist Interaktif: 7 Langkah Sebelum Melamar</span>
            </h3>
            <p className="text-xs text-slate-500">Centang setiap langkah setelah Anda berhasil memverifikasinya.</p>
          </div>

          <div className="px-3 py-1 bg-blue-50 text-blue-800 rounded-full text-xs font-bold border border-blue-200 self-start sm:self-auto">
            Progres: {totalChecked} dari 7 Terverifikasi
          </div>
        </div>

        <div className="space-y-2.5">
          {[
            { id: 'c1', text: 'Periksa domain email pengirim — Bukan @gmail.com, @yahoo.com, atau domain tiruan.' },
            { id: 'c2', text: 'Buka website karier resmi perusahaan dan pastikan lowongan tersebut tercatat di sana.' },
            { id: 'c3', text: 'Cek profil resmi perusahaan di LinkedIn, Google Maps (kantor fisik nyata), atau direktori Kemenkumham.' },
            { id: 'c4', text: 'Pastikan tidak ada pungutan uang apapun (tiket travel, tes psikotes, biaya seragam, atau deposit).' },
            { id: 'c5', text: 'Gaji dan benefit yang ditawarkan masuk akal sesuai standar UMR dan keahlian di industri.' },
            { id: 'c6', text: 'Tidak ada permintaan data sensitif di awal (foto selfie dengan KTP, nomor PIN, atau akses akun perbankan).' },
            { id: 'c7', text: 'Panggilan wawancara dilakukan secara profesional melalui platform resmi atau tatap muka di kantor.' },
          ].map((item) => (
            <label
              key={item.id}
              onClick={() => toggleCheck(item.id)}
              className={`flex items-start space-x-3 p-3 rounded-xl border transition-all cursor-pointer select-none ${
                checklist[item.id]
                  ? 'bg-emerald-50/60 border-emerald-300 text-emerald-900'
                  : 'bg-slate-50/50 border-slate-200 text-slate-700 hover:bg-slate-100/60'
              }`}
            >
              <input
                type="checkbox"
                checked={checklist[item.id]}
                onChange={() => {}}
                className="mt-0.5 rounded text-blue-600 focus:ring-blue-500"
              />
              <span className={`text-xs sm:text-sm ${checklist[item.id] ? 'line-through opacity-80' : ''}`}>
                {item.text}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Kanal Pengaduan Resmi Indonesia */}
      <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-4">
        <div>
          <h3 className="text-base sm:text-lg font-bold flex items-center space-x-2 text-white">
            <PhoneCall className="w-5 h-5 text-blue-400" />
            <span>Kanal Pengaduan Resmi Penipuan di Indonesia</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Jika Anda menemukan indikasi penipuan atau telah mengalami kerugian finansial, segera laporkan ke instansi berwenang:
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <a
            href="https://patrolisiber.id"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 transition-colors space-y-2 block"
          >
            <span className="text-xs font-bold text-blue-400 flex items-center justify-between">
              <span>Patroli Siber Polri</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </span>
            <p className="text-xs text-slate-300">Laporan tindak pidana siber, penipuan online, dan rekening penipu.</p>
            <span className="text-[11px] text-slate-400 font-mono block">patrolisiber.id</span>
          </a>

          <a
            href="https://aduankonten.id"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 transition-colors space-y-2 block"
          >
            <span className="text-xs font-bold text-blue-400 flex items-center justify-between">
              <span>Kominfo Aduan Konten</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </span>
            <p className="text-xs text-slate-300">Pemblokiran website phishing, tautan form penipu, dan konten ilegal.</p>
            <span className="text-[11px] text-slate-400 font-mono block">aduankonten.id</span>
          </a>

          <a
            href="https://siapkerja.kemnaker.go.id"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 transition-colors space-y-2 block"
          >
            <span className="text-xs font-bold text-blue-400 flex items-center justify-between">
              <span>Kemnaker SIAPkerja</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </span>
            <p className="text-xs text-slate-300">Pengaduan penyalur tenaga kerja ilegal dan rekrutmen bodong.</p>
            <span className="text-[11px] text-slate-400 font-mono block">siapkerja.kemnaker.go.id</span>
          </a>

          <a
            href="https://www.lapor.go.id"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700 transition-colors space-y-2 block"
          >
            <span className="text-xs font-bold text-blue-400 flex items-center justify-between">
              <span>SP4N-LAPOR!</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </span>
            <p className="text-xs text-slate-300">Layanan aspirasi dan pengaduan daring rakyat untuk instansi pemerintah.</p>
            <span className="text-[11px] text-slate-400 font-mono block">lapor.go.id</span>
          </a>
        </div>
      </div>
    </div>
  );
}
