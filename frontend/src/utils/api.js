import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const loginUser = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  const response = await api.post('/auth/login', formData);
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await api.post('/auth/signup', userData);
  return response.data;
};

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/ocr/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// FIX: Ensure this hits /predict/ (matching the backend router)
export const predictRisk = async (data) => {
  const response = await api.post('/predict/', data);
  return response.data;
};

export const fetchHistory = async () => {
  const token = Cookies.get('token');
  const response = await api.get('/history/my-logs', {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export default api;