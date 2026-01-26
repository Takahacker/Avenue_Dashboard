// API Configuration
// Uses VITE_API_URL environment variable if available, defaults to localhost for development

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const fetchAPI = async (endpoint: string) => {
  const url = `${API_URL}${endpoint}?t=${Date.now()}`;
  console.log(`Fetching from: ${url}`);
  return fetch(url);
};
