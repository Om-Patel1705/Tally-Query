import axios from 'axios';
import type { UploadResponse, AnswerResponse } from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
});

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData);
  return response.data;
};

export const submitQuery = async (sessionId: string, question: string): Promise<AnswerResponse> => {
  const response = await api.post<AnswerResponse>('/query', {
    session_id: sessionId,
    question,
  });
  return response.data;
};

export const clearSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/session/clear?session_id=${sessionId}`);
};

export const getSessionStatus = async (sessionId: string) => {
  const response = await api.get(`/session/status?session_id=${sessionId}`);
  return response.data;
};

export const getSessionData = async (sessionId: string, page: number = 1, pageSize: number = 50) => {
  const response = await api.get(`/session/data?session_id=${sessionId}&page=${page}&page_size=${pageSize}`);
  return response.data;
};
