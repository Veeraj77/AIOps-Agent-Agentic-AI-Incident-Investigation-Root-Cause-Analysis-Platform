/**
 * AIOps Agent - Centralized API Service
 * Handles communication with the FastAPI backend.
 */
import axios from 'axios';

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL !== undefined) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location.port === '5173') {
    return 'http://localhost:8000';
  }
  // In Docker / production behind reverse proxy, use relative paths
  return '';
};

const API_BASE_URL = getBaseUrl();

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutes timeout (AI investigation & embeddings can take time)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to extract clean error messages
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with non-2xx status
    const data = error.response.data;
    const detail = data?.detail || data?.error || data?.message || 'Server error occurred';
    return new Error(typeof detail === 'object' ? JSON.stringify(detail) : detail);
  } else if (error.request) {
    // Request made but no response (server down or CORS issue)
    return new Error('Cannot reach AIOps backend server. Ensure backend is running at ' + API_BASE_URL);
  } else {
    return new Error(error.message || 'Unknown network error');
  }
};

export const api = {
  // System Health
  async healthCheck() {
    try {
      const response = await client.get('/health');
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Incident Log Analysis (Fast deterministic analysis)
  async analyzeIncident(logs) {
    try {
      const response = await client.post('/api/incidents/analyze', { logs });
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Upload Log File for Analysis
  async uploadIncidentLogs(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await client.post('/api/incidents/analyze/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Run Full LangGraph AI Investigation
  async runInvestigation({ logs, question, document_collection }) {
    try {
      const payload = {
        logs,
        question: question || 'Why is the application failing?',
      };
      if (document_collection) {
        payload.document_collection = document_collection;
      }
      const response = await client.post('/api/investigations/run', payload);
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // List Past Investigations
  async getInvestigations(limit = 50) {
    try {
      const response = await client.get('/api/investigations', {
        params: { limit },
      });
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Get Single Investigation by UUID
  async getInvestigationById(id) {
    try {
      const response = await client.get(`/api/investigations/${id}`);
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Upload Document to ChromaDB Knowledge Base
  async uploadDocument(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await client.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // List Knowledge Base Documents
  async getDocuments() {
    try {
      const response = await client.get('/api/documents');
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },

  // Get Knowledge Base Statistics
  async getDocumentStats() {
    try {
      const response = await client.get('/api/documents/stats');
      return response.data;
    } catch (err) {
      throw handleApiError(err);
    }
  },
};

export default api;
