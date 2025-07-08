import axios from 'axios';
import { AuthTokens, User, JobPreference, Job, JobMatch, DashboardStats } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authTokens: AuthTokens | null = null;

export const setAuthTokens = (tokens: AuthTokens) => {
  authTokens = tokens;
  localStorage.setItem('authTokens', JSON.stringify(tokens));
  api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
};

export const getAuthTokens = (): AuthTokens | null => {
  if (authTokens) return authTokens;
  
  const stored = localStorage.getItem('authTokens');
  if (stored) {
    authTokens = JSON.parse(stored);
    if (authTokens) {
      api.defaults.headers.common['Authorization'] = `Bearer ${authTokens.access}`;
    }
  }
  return authTokens;
};

export const clearAuthTokens = () => {
  authTokens = null;
  localStorage.removeItem('authTokens');
  delete api.defaults.headers.common['Authorization'];
};

// Initialize auth on app start
getAuthTokens();

// Auth API
export const authAPI = {
  register: async (userData: {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
  }): Promise<AuthTokens> => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  login: async (credentials: { email: string; password: string }): Promise<AuthTokens> => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put('/auth/profile/', userData);
    return response.data;
  },
};

// Job Preferences API
export const preferencesAPI = {
  getPreferences: async (): Promise<JobPreference[]> => {
    const response = await api.get('/auth/preferences/');
    return response.data;
  },

  createPreference: async (preference: Omit<JobPreference, 'id' | 'created_at' | 'updated_at'>): Promise<JobPreference> => {
    const response = await api.post('/auth/preferences/', preference);
    return response.data;
  },

  updatePreference: async (id: number, preference: Partial<JobPreference>): Promise<JobPreference> => {
    const response = await api.put(`/auth/preferences/${id}/`, preference);
    return response.data;
  },

  deletePreference: async (id: number): Promise<void> => {
    await api.delete(`/auth/preferences/${id}/`);
  },
};

// Jobs API
export const jobsAPI = {
  getJobs: async (params?: {
    search?: string;
    location_type?: string;
    job_type?: string;
    min_salary?: number;
    max_salary?: number;
    days_ago?: number;
  }): Promise<Job[]> => {
    const response = await api.get('/jobs/', { params });
    return response.data.results || response.data;
  },

  getJob: async (id: number): Promise<Job> => {
    const response = await api.get(`/jobs/${id}/`);
    return response.data;
  },

  getMatches: async (): Promise<JobMatch[]> => {
    const response = await api.get('/jobs/matches/');
    return response.data.results || response.data;
  },

  bookmarkJob: async (jobId: number): Promise<{ bookmarked: boolean; message: string }> => {
    const response = await api.post(`/jobs/${jobId}/bookmark/`);
    return response.data;
  },

  markApplied: async (jobId: number): Promise<{ message: string }> => {
    const response = await api.post(`/jobs/${jobId}/apply/`);
    return response.data;
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/jobs/dashboard/');
    return response.data;
  },
};

export default api;