/**
 * API client for communicating with the RootCause backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Pipeline
export const runPipeline = (content, source = 'manual') =>
  request('/api/pipeline/run', {
    method: 'POST',
    body: JSON.stringify({ content, source }),
  });

export const runBatch = (documents) =>
  request('/api/pipeline/run-batch', {
    method: 'POST',
    body: JSON.stringify({ documents }),
  });

export const runDemo = () =>
  request('/api/pipeline/run-demo', { method: 'POST' });

// Traces
export const listTraces = (params = {}) => {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.flagged !== undefined) query.set('flagged', params.flagged);
  if (params.failure_type) query.set('failure_type', params.failure_type);
  if (params.limit) query.set('limit', params.limit);
  if (params.offset) query.set('offset', params.offset);
  const qs = query.toString();
  return request(`/api/traces${qs ? '?' + qs : ''}`);
};

export const getTrace = (traceId) =>
  request(`/api/traces/${traceId}`);

// Flagging & Diagnosis
export const flagTrace = (traceId, reason = '') =>
  request(`/api/traces/${traceId}/flag`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  });

export const getDiagnosis = (traceId) =>
  request(`/api/traces/${traceId}/diagnosis`);

export const confirmDiagnosis = (traceId, data = {}) =>
  request(`/api/traces/${traceId}/confirm`, {
    method: 'POST',
    body: JSON.stringify({ confirmed: true, ...data }),
  });

// Eval Dataset
export const getEvalDataset = () => request('/api/eval/dataset');
export const runRegression = () => request('/api/eval/run', { method: 'POST' });
export const getRegressionHistory = () => request('/api/eval/history');

// Analytics
export const getAnalytics = () => request('/api/analytics');
export const getTrends = (days = 30) => request(`/api/analytics/trends?days=${days}`);
export const getTaxonomy = () => request('/api/analytics/taxonomy');
