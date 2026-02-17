import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
