/**
 * API Service - Handles all backend communication
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Check API health
 */
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

/**
 * Upload a PDF file
 */
export const uploadPDF = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

/**
 * Send a chat message
 */
export const sendMessage = async (question, sessionId, documentId) => {
  const response = await api.post('/chat', {
    question,
    session_id: sessionId,
    document_id: documentId,
  });

  return response.data;
};

/**
 * Get conversation history
 */
export const getHistory = async (sessionId) => {
  const response = await api.get(`/history/${sessionId}`);
  return response.data;
};

/**
 * Clear conversation history
 */
export const clearHistory = async (sessionId) => {
  const response = await api.delete(`/history/${sessionId}`);
  return response.data;
};

/**
 * List all documents
 */
export const listDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

/**
 * Delete a document
 */
export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export default api;
