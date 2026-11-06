// API Client untuk JobShield Backend (FastAPI)

const API_BASE = import.meta.env.VITE_API_URL || '';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed with status: ${res.status}`);
  return await res.json();
}

export async function getModelInfo() {
  const res = await fetch(`${API_BASE}/api/v1/model-info`);
  if (!res.ok) throw new Error(`Failed to fetch model info (${res.status})`);
  return await res.json();
}

export async function predictSingle(jobData) {
  const res = await fetch(`${API_BASE}/api/v1/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jobData),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail?.[0]?.msg || errorData.detail || `Prediksi gagal (${res.status})`);
  }

  return await res.json();
}

export async function predictBatchCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/v1/predict/batch`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analisis CSV gagal (${res.status})`);
  }

  return await res.json();
}

export async function chatWithAssistant(messages, jobContext = null, apiKey = null) {
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
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail?.[0]?.msg || errorData.detail || `Gagal menghubungi asisten (${res.status})`);
  }

  return await res.json();
}
