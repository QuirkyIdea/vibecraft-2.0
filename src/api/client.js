/**
 * Inventix AI - API Client
 * 
 * Base configuration for all API calls to the backend.
 * This replaces all mock data with real API integration.
 */
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for LLM calls
});

// Request interceptor for logging
client.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
client.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(`[API] Error ${error.response.status}:`, error.response.data);
    } else if (error.request) {
      // No response received
      console.error('[API] No Response - Is the backend running?');
    } else {
      console.error('[API] Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default client;
