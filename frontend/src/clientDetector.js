// Client-side Machine Learning Detector & Offline Security Advisor
// Menggunakan Logistic Regression teroptimasi & TF-IDF terkalibrasi langsung di browser

let cachedModel = null;

export async function loadModel() {
  if (cachedModel) return cachedModel;
  
  // Ambil model_client.json dari public folder
  const baseUrl = import.meta.env.BASE_URL || './';
  const url = `${baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'}model_client.json`;
  
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Gagal memuat model klien dari ${url}: ${res.status}`);
  }
  cachedModel = await res.json();
  return cachedModel;
}

export async function predictSingleClient(jobData) {
  const model = await loadModel();
  
  const _s = (x) => (x !== null && x !== undefined ? String(x) : "");
  
  const _cleanText = (s) => {
    let text = _s(s);
    // Unescape HTML entities sederhana
    text = text.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');
    text = text.replace(/<[^>]+>/g, " ");
    text = text.replace(/#URL_[A-Za-z0-9]+#/g, " urltoken ");
    text = text.replace(/#EMAIL_[A-Za-z0-9]+#/g, " emailtoken ");
    text = text.replace(/#PHONE_[A-Za-z0-9]+#/g, " phonetoken ");
    text = text.replace(/(?<=[a-z0-9\.\,\)\!])(?=[A-Z][a-z])/g, " ");
    text = text.replace(/[^A-Za-z0-9\s\$\!]/g, " ");
    return text.replace(/\s+/g, " ").trim().toLowerCase();
  };

  const textParts = ["title", "company_profile", "description", "requirements", "benefits"];
  const rawAll = textParts.map((k) => _s(jobData[k])).join(" ");
  const cleanAll = textParts.map((k) => _cleanText(jobData[k])).join(" ");

  // Tokenisasi: kata dengan 2 huruf atau lebih
  const tokens = cleanAll.match(/\b\w\w+\b/g) || [];
  const stopWordsSet = new Set(model.stop_words);
  const filtered = tokens.filter((t) => !stopWordsSet.has(t));

  // Buat unigram dan bigram
  const ngrams = [...filtered];
  for (let i = 0; i < filtered.length - 1; i++) {
    ngrams.push(`${filtered[i]} ${filtered[i + 1]}`);
  }

  // Hitung frekuensi (TF)
  const termCounts = {};
  for (const term of ngrams) {
    termCounts[term] = (termCounts[term] || 0) + 1;
  }

  // 1. Hitung skor TF-IDF dengan sublinear TF
  const tfidfVals = [];
  for (const [term, count] of Object.entries(termCounts)) {
    if (model.tfidf[term]) {
      const [idf, coef] = model.tfidf[term];
      const tf = 1 + Math.log(count);
      const val = tf * idf;
      tfidfVals.push({ val, coef });
    }
  }

  let textDot = 0.0;
  if (tfidfVals.length > 0) {
    let sumSq = 0;
    for (const item of tfidfVals) {
      sumSq += item.val * item.val;
    }
    const norm = Math.sqrt(sumSq);
    if (norm > 0) {
      for (const item of tfidfVals) {
        textDot += (item.val / norm) * item.coef;
      }
    }
  }

  // 2. Hitung One-Hot Encoded (Kategori)
  const locStr = _s(jobData.location);
  const country = locStr.split(',')[0].trim().toUpperCase() || "UNKNOWN";
  
  const catVals = {
    country,
    employment_type: _s(jobData.employment_type) || "unknown",
    required_experience: _s(jobData.required_experience) || "unknown",
    required_education: _s(jobData.required_education) || "unknown",
    function: _s(jobData.function) || "unknown",
    industry: _s(jobData.industry) || "unknown",
  };

  let oheDot = 0.0;
  for (const [col, val] of Object.entries(catVals)) {
    const fname = `${col}_${val}`;
    if (model.ohe[fname] !== undefined) {
      oheDot += model.ohe[fname];
    } else {
      const infName = `${col}_infrequent_sklearn`;
      if (model.ohe[infName] !== undefined) {
        oheDot += model.ohe[infName];
      }
    }
  }

  // 3. Hitung Fitur Numerik
  const countMatches = (str, pattern) => (str.match(pattern) || []).length;
  
  const numVals = {
    len_title: Math.log1p(_s(jobData.title).length),
    len_profile: Math.log1p(_s(jobData.company_profile).length),
    len_desc: Math.log1p(_s(jobData.description).length),
    len_req: Math.log1p(_s(jobData.requirements).length),
    len_benefits: Math.log1p(_s(jobData.benefits).length),
    n_exclaim: countMatches(rawAll, /!/g),
    caps_ratio: rawAll.length > 0 ? (rawAll.match(/[A-Z]/g) || []).length / rawAll.length : 0,
    n_url: countMatches(rawAll, /#URL_/g),
    n_email: countMatches(rawAll, /#EMAIL_/g),
    n_phone: countMatches(rawAll, /#PHONE_/g),
    n_dollar: countMatches(rawAll, /\$/g),
    has_salary: jobData.salary_range ? 1 : 0,
    has_department: jobData.department ? 1 : 0,
    no_profile: _s(jobData.company_profile).length === 0 ? 1 : 0,
    no_req: _s(jobData.requirements).length === 0 ? 1 : 0,
    no_benefits: _s(jobData.benefits).length === 0 ? 1 : 0,
    telecommuting: Number(jobData.telecommuting) || 0,
    has_company_logo: Number(jobData.has_company_logo) || 0,
    has_questions: Number(jobData.has_questions) || 0,
  };

  let numDot = 0.0;
  for (const [col, val] of Object.entries(numVals)) {
    if (model.num[col] !== undefined) {
      numDot += val * model.num[col];
    }
  }

  // 4. Kalkulasi Probabilitas Sigmoid
  const z = model.intercept + textDot + oheDot + numDot;
  const proba = 1.0 / (1.0 + Math.exp(-z));
  const probaRounded = Math.round(proba * 10000) / 10000;
  
  const thr = model.threshold;
  const isFake = proba >= thr;
  const riskLevel = isFake ? "TINGGI" : (proba >= thr / 2 ? "WASPADA" : "RENDAH");

  return {
    prediksi: isFake ? "PALSU" : "ASLI",
    probabilitas_palsu: probaRounded,
    tingkat_risiko: riskLevel,
    threshold: thr,
    model: `${model.model_name} (Client-side AI)`,
    warnings: [
      "Model dilatih pada teks bahasa Inggris. Lowongan berbahasa Indonesia dapat menghasilkan prediksi yang kurang akurat."
    ],
  };
}

// Parser CSV sederhana untuk Batch Predict di browser
function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter(line => line.trim().length > 0);
  if (lines.length < 2) return [];

  // Parse header
  const parseRow = (line) => {
    const entries = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch === ',' && !inQuotes) {
        entries.push(current.trim());
        current = '';
      } else {
        current += ch;
      }
    }
    entries.push(current.trim());
    return entries;
  };

  const headers = parseRow(lines[0]);
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const values = parseRow(lines[i]);
    const rowObj = {};
    headers.forEach((h, idx) => {
      rowObj[h] = values[idx] || '';
    });
    rows.push(rowObj);
  }
  return rows;
}

export async function predictBatchCsvClient(file) {
  const text = await file.text();
  const rows = parseCsv(text);
  
  if (rows.length === 0) {
    throw new Error("File CSV kosong atau tidak memiliki baris data yang valid.");
  }

  const results = [];
  let fakeCount = 0;
  let realCount = 0;
  let highRiskCount = 0;

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const pred = await predictSingleClient(row);
    if (pred.prediksi === "PALSU") fakeCount++;
    else realCount++;
    if (pred.tingkat_risiko === "TINGGI") highRiskCount++;

    results.push({
      index: i + 1,
      title: row.title || `Lowongan #${i + 1}`,
      prediksi: pred.prediksi,
      probabilitas_palsu: pred.probabilitas_palsu,
      tingkat_risiko: pred.tingkat_risiko,
    });
  }

  return {
    total: rows.length,
    fake_count: fakeCount,
    real_count: realCount,
    high_risk_count: highRiskCount,
    model: "Logistic Regression (Client-side AI)",
    results,
  };
}

// Basis Pengetahuan Penasihat Keamanan Lowongan Kerja (Offline)
export function getKnowledgeBaseReply(latestMessage, jobContext) {
  const qLower = (latestMessage || "").toLowerCase();
  
  let contextNote = "";
  if (jobContext && jobContext.title) {
    contextNote = `\n\n*(Menganalisis lowongan terkait: "${jobContext.title}" — Status Prediksi: ${jobContext.prediksi} | Probabilitas: ${(Number(jobContext.probabilitas_palsu) * 100).toFixed(1)}%)*`;
  }

  if (qLower.includes("tiket") || qLower.includes("travel") || qLower.includes("pesawat") || qLower.includes("hotel")) {
    return (
      "🚨 **PERINGATAN MODUS PENIPUAN TIKET TRAVEL:**\n\n" +
      "Ini adalah modus penipuan lowongan kerja paling marak di Indonesia!\n\n" +
      "**Ciri-ciri Modus:**\n" +
      "1. Pengumuman mengatasnamakan BUMN atau perusahaan besar (Pertamina, PLN, Telkom, PT KAI, dsb).\n" +
      "2. Peserta tes diwajibkan memesan tiket pesawat/hotel melalui agen travel yang ditunjuk dengan janji *reimbursement* (penggantian uang) saat di lokasi tes.\n" +
      "3. Uang tiket tidak akan pernah diganti dan tes tidak pernah ada.\n\n" +
      "⚠️ **Aturan Emas:** Perusahaan resmi **TIDAK PERNAH** memungut biaya transportasi atau mewajibkan penggunaan biro perjalanan tertentu!" +
      contextNote
    );
  } else if (qLower.includes("bayar") || qLower.includes("biaya") || qLower.includes("seragam") || qLower.includes("modul") || qLower.includes("uang")) {
    return (
      "⚠️ **WASPADAI PUNGUTAN BIAYA REKRUTMEN:**\n\n" +
      "Perusahaan profesional dan legal **TIDAK AKAN PERNAH** meminta kandidat membayar biaya apa pun dalam proses seleksi, termasuk:\n" +
      "- Biaya seragam atau ID card sebelum mulai bekerja\n" +
      "- Biaya modul psikotes / tes keahlian\n" +
      "- Biaya administrasi pendaftaran\n\n" +
      "Jika Anda diminta mentransfer uang dengan alasan apa pun sebelum bekerja, **segera batalkan proses lamaran.**" +
      contextNote
    );
  } else if (qLower.includes("telegram") || qLower.includes("like") || qLower.includes("youtube") || qLower.includes("deposit") || qLower.includes("freelance")) {
    return (
      "🚨 **WASPADA PENIPUAN TUGAS PARUH WAKTU (TASK SCAM):**\n\n" +
      "Modus ini biasanya menawarkan pekerjaan mudah melalui WhatsApp atau Telegram:\n" +
      "- Tugas awal sangat mudah: like video YouTube, review Google Maps, atau follow akun media sosial dengan reward kecil (Rp 10.000 - Rp 30.000).\n" +
      "- Di tahap berikutnya, Anda dimasukkan ke grup Telegram dan diminta melakukan 'deposit dana tugas' dengan janji komisi 20-50%.\n" +
      "- Saat uang deposit besar masuk, pelaku akan memblokir Anda atau beralasan sistem eror dan meminta deposit tambahan.\n\n" +
      "🛑 **Tindakan:** Jangan pernah transfer uang untuk mendapatkan tugas pekerjaan!" +
      contextNote
    );
  } else if (qLower.includes("ktp") || qLower.includes("rekening") || qLower.includes("pinjol") || qLower.includes("selfie") || qLower.includes("buku tabungan")) {
    return (
      "🔒 **LINDUNGI DATA PRIBADI ANDA:**\n\n" +
      "Waspadalah jika pemberi kerja meminta:\n" +
      "- Foto KTP tampak depan\n" +
      "- Selfie memegang KTP\n" +
      "- Foto buku tabungan atau nama ibu kandung\n\n" +
      "Semua data ini **hanya boleh diminta setelah Anda resmi menandatangani Surat Perjanjian Kerja (Offering Letter)**, bukan di tahap interview atau tes awal.\n\n" +
      "Data identitas ini kerap disalahgunakan sindikat penipu untuk membobol akun perbankan atau mengajukan pinjaman online (pinjol) ilegal atas nama korban." +
      contextNote
    );
  } else {
    return (
      "Halo! Saya **JobShield Security Advisor** (Asisten Keamanan Karir). 🛡️✨\n\n" +
      "Saya siap membantu Anda memverifikasi keabsahan tawaran kerja, memeriksa surat panggilan, dan mengenali modus penipuan rekrutmen.\n\n" +
      "**Panduan Verifikasi Mandiri:**\n" +
      "1. **Cek Email Pengirim:** Rekruter resmi menggunakan domain email perusahaan (`hrd@perusahaan.com`), bukan `@gmail.com` atau `@yahoo.com`.\n" +
      "2. **Cek Situs Resmi:** Pastikan lowongan terdaftar di tab *Karier / Career* pada situs resmi perusahaan terkait.\n" +
      "3. **Prinsip Nol Rupiah:** Tidak ada biaya apa pun untuk proses rekrutmen kerja profesional.\n\n" +
      "*Tips: Jika Anda memasukkan Google Gemini API Key di menu atas, asisten dapat memberikan konsultasi analisis interaktif berbasis Gemini AI secara real-time!*" +
      contextNote
    );
  }
}

export async function chatAssistantClient(messages, jobContext = null, apiKey = null) {
  const latestMessage = messages[messages.length - 1]?.content || "";

  // Jika ada API Key Gemini, panggil langsung Google Gemini REST API dari browser
  if (apiKey && apiKey.trim().length > 0) {
    try {
      const systemInstruction = 
        "Kamu adalah JobShield AI Assistant, seorang pakar keamanan siber, anti-fraud, " +
        "dan konsultan perlindungan pencari kerja profesional di Indonesia. " +
        "Tugasmu adalah menganalisis indikasi penipuan lowongan kerja, mengidentifikasi modus operandi " +
        "(tiket travel bodong, tes berbayar, rekrutmen palsu atas nama BUMN/korporasi ternama, phishing identitas KTP/rekening, " +
        "dan tugas deposit Telegram), serta memberikan saran pencegahan yang taktis, ramah, dan solutif. " +
        "Format jawabanmu dalam Markdown yang terstruktur, jelas, dan mudah dipahami.";

      let contextPrompt = "";
      if (jobContext && jobContext.title) {
        contextPrompt = `\n\n[KONTEKS LOWONGAN SAAT INI]: Judul: '${jobContext.title}', Hasil AI ML: ${jobContext.prediksi} (Probabilitas Penipuan: ${jobContext.probabilitas_palsu}).`;
      }

      const contents = messages.map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }]
      }));

      const payload = {
        system_instruction: { parts: [{ text: systemInstruction + contextPrompt }] },
        contents,
        generationConfig: {
          temperature: 0.3,
          maxOutputTokens: 2048,
        }
      };

      const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey.trim()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        const candidate = data.candidates?.[0];
        const text = candidate?.content?.parts?.[0]?.text;
        if (text) {
          return {
            reply: text,
            model: "Gemini 1.5 Flash (Direct API)",
            is_live_gemini: true,
          };
        }
      }
    } catch (e) {
      console.warn("Gagal menghubungi Google Gemini API langsung, menggunakan Basis Pengetahuan:", e);
    }
  }

  // Fallback ke Basis Pengetahuan JobShield
  const reply = getKnowledgeBaseReply(latestMessage, jobContext);
  return {
    reply,
    model: "JobShield Knowledge Base (Client Advisor)",
    is_live_gemini: false,
  };
}
