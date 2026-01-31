/**
 * Inventix AI - API Endpoints
 * 
 * All backend API calls centralized here.
 * Phase 10 Complete: Projects, Evidence, Analysis, Feedback, Audit, Compliance
 */
import client from './client';

// ============== Projects ==============
export const projects = {
  list: () => client.get('/projects'),
  get: (id) => client.get(`/projects/${id}`),
  create: (data) => client.post('/projects', data),
  update: (id, data) => client.put(`/projects/${id}`, data),
  delete: (id) => client.delete(`/projects/${id}`),
};

// ============== File Upload ==============
export const files = {
  upload: (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post(`/projects/${projectId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (projectId) => client.get(`/projects/${projectId}/files`),
};

// ============== Text Extraction ==============
export const extraction = {
  extract: (projectId, fileId) => client.post(`/projects/${projectId}/extract/${fileId}`),
};

// ============== Evidence Retrieval (Phase 3) ==============
export const evidence = {
  retrieve: (projectId, data) => client.post(`/projects/${projectId}/retrieve`, data),
  list: (projectId) => client.get(`/projects/${projectId}/evidence`),
};

// ============== Similarity & Novelty (Phase 4) ==============
export const similarity = {
  compute: (projectId) => client.post(`/projects/${projectId}/similarity/compute`),
  getNovelty: (projectId) => client.get(`/projects/${projectId}/novelty`),
  list: (projectId) => client.get(`/projects/${projectId}/similarity`),
};

// ============== Comparative Analysis (Phase 5) ==============
export const analysis = {
  generate: (projectId, data) => client.post(`/projects/${projectId}/compare`, data),
  get: (projectId) => client.get(`/projects/${projectId}/comparison`),
};

// ============== Draft Optimization (Phase 6) ==============
export const draft = {
  optimize: (projectId, data) => client.post(`/projects/${projectId}/draft-optimize`, data),
  getSuggestions: (projectId) => client.get(`/projects/${projectId}/suggestions`),
  updateSuggestion: (suggestionId, data) => client.put(`/suggestions/${suggestionId}`, data),
};

// ============== Venue Recommendations (Phase 7) ==============
export const venues = {
  get: (projectId) => client.get(`/projects/${projectId}/recommendations`),
};

// ============== Patent Claims (Phase 8) ==============
export const claims = {
  generate: (projectId) => client.post(`/projects/${projectId}/claims/generate`),
  list: (projectId) => client.get(`/projects/${projectId}/claims`),
  update: (claimId, data) => client.put(`/claims/${claimId}`, data),
  getGraph: (projectId) => client.get(`/projects/${projectId}/claims/graph`),
};

// ============== Feedback & Confidence (Phase 9) ==============
export const feedback = {
  submit: (projectId, data) => client.post(`/feedback?project_id=${projectId}`, data),
  getForOutput: (outputId) => client.get(`/feedback/${outputId}`),
  getProjectStats: (projectId) => client.get(`/feedback/project/${projectId}`),
};

export const confidence = {
  get: (projectId) => client.get(`/projects/${projectId}/confidence`),
};

// ============== Audit & Compliance (Phase 10) ==============
export const audit = {
  getProjectTrail: (projectId) => client.get(`/projects/${projectId}/audit`),
};

export const compliance = {
  getStatus: () => client.get('/system/compliance'),
};

// ============== System ==============
export const system = {
  health: () => client.get('/health', { baseURL: 'http://127.0.0.1:8000' }),
  status: () => client.get('/system/status'),
};

export default {
  projects,
  files,
  extraction,
  evidence,
  similarity,
  analysis,
  draft,
  venues,
  claims,
  feedback,
  confidence,
  audit,
  compliance,
  system,
};
