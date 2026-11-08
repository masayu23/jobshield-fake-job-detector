// API Client untuk JobShield (Hybrid: Mendukung Backend FastAPI dan Client-side Standalone untuk GitHub Pages)

import { 
  predictSingleClient, 
  predictBatchCsvClient, 
  chatAssistantClient,
  loadModel 
} from './clientDetector';

const API_BASE = import.meta.env.VITE_API_URL || '';

export async function checkHealth() {
  if (API_BASE) {
    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) return await res.json();
    } catch {
      // Backend tidak aktif, beralih ke Client-side mode
    }
  }
  
  // Jika static web / GitHub Pages: pastikan model client siap
  await loadModel();
  return {
    status: "ok",
    model_loaded: true,
    version: "1.0.0 (Client-side Web)",
    mode: "standalone_static"
  };
}

export async function getModelInfo() {
  if (API_BASE) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/model-info`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) return await res.json();
    } catch {
      // Lanjut ke fallback client
    }
  }

  const model = await loadModel();
  return {
    model_name: model.model_name,
    threshold: model.threshold,
    accuracy: 0.9875,
    f1_score: 0.8625,
    roc_auc: 0.9934,
    features_count: model.tfidf_vocab_len || 30260,
    training_data: "17,880 lowongan kerja (EMSCAD)",
    status: "Active (Client-side Browser AI)"
  };
}

export async function predictSingle(jobData) {
  if (API_BASE) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData),
        signal: AbortSignal.timeout(5000),
      });

      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Backend gagal/tidak ada, gunakan model di browser
    }
  }

  // Gunakan model client-side mandiri di browser
  return await predictSingleClient(jobData);
}

export async function predictBatchCsv(file) {
  if (API_BASE) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/api/v1/predict/batch`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(10000),
      });

      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Backend gagal/tidak ada, gunakan batch parser di browser
    }
  }

  return await predictBatchCsvClient(file);
}

export async function chatWithAssistant(messages, jobContext = null, apiKey = null) {
  if (API_BASE) {
    try {
      const headers = {
        'Content-Type': 'application/json',
      };
      if (apiKey) {
        headers['X-Gemini-API-Key'] = apiKey;
      }

      const res = await fetch(`${API_BASE}/api/v1/assistant/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          messages,
          job_context: jobContext,
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Backend gagal/tidak ada, gunakan client assistant
    }
  }

  return await chatAssistantClient(messages, jobContext, apiKey);
}
