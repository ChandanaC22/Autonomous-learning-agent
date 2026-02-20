import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const response = await api.post('/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const register = async (username, email, password) => {
  const response = await api.post('/register', { username, email, password });
  return response.data;
};

export const startLearning = async (topic, objectives) => {
  const response = await api.post('/start', { topic, objectives });
  return response.data;
};

export const getQuiz = async () => {
  const response = await api.get('/quiz');
  return response.data;
};

export const submitQuiz = async (userAnswers) => {
  const response = await api.post('/submit', { user_answers: userAnswers });
  return response.data;
};

export const getRemediation = async () => {
  const response = await api.get('/remediation');
  return response.data;
};

export const resetState = async () => {
  const response = await api.post('/reset');
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get('/history');
  return response.data;
};

export default api;
