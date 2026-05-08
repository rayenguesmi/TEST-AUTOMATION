import axios from 'axios';

// ─── Axios instance (Auth) ──────────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api/auth`
    : '/api/auth',
  withCredentials: true,
});

// ─── Auth endpoints ──────────────────────────────────────────────────────────
export const registerUser   = (data) => api.post('/register', data);
export const loginUser      = (data) => api.post('/login', data);
export const logoutUser     = ()     => api.post('/logout');
export const getMe          = ()     => api.get('/me');
export const forgotPassword = (data) => api.post('/forgot-password', data);
export const resetPassword  = (data) => api.post('/reset-password', data);

// ─── General API client (users, tests, admin) ────────────────────────────────
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) window.location.href = '/login';
    return Promise.reject(err);
  }
);

// ─── User Admin endpoints ─────────────────────────────────────────────────────
export const getAllUsers     = ()              => apiClient.get('/api/users/all');
export const updateUserRole  = (userId, role) => apiClient.patch('/api/users/role', { userId, role });
export const deleteUser      = (userId)       => apiClient.delete(`/api/users/${userId}`);

// ─── Test endpoints ───────────────────────────────────────────────────────────
export const runTest           = (data)          => apiClient.post('/api/tests/run', data);
export const fetchMyTests      = ()              => apiClient.get('/api/tests/my-tests');
export const fetchTestById     = (id)            => apiClient.get(`/api/tests/${id}`);
export const fetchTestProgress = (id)            => apiClient.get(`/api/tests/${id}/progress`);
export const fetchTestResults  = (id)            => apiClient.get(`/api/tests/${id}/results`);
export const fetchFilteredTests = (params)       => apiClient.get('/api/tests/filtered', { params });
export const fetchCompareTests = (id1, id2)      => apiClient.get('/api/tests/compare', { params: { id1, id2 } });
export const getGlobalStats    = ()              => apiClient.get('/api/tests/stats');
export const getAllTestsAdmin   = ()              => apiClient.get('/api/tests/all');
export const getHealthStatus   = ()              => apiClient.get('/api/health');

// ─── Admin endpoints ──────────────────────────────────────────────────────────
export const getAdminHealth        = ()     => apiClient.get('/api/admin/health');
export const getAdminActivityStats = ()     => apiClient.get('/api/admin/stats/activity');
export const getAdminLLMComparison = ()     => apiClient.get('/api/admin/stats/llm-comparison');
export const getAdminUsers         = ()     => apiClient.get('/api/admin/users');
export const disableAdminUser      = (id)   => apiClient.patch(`/api/admin/users/${id}/disable`);
export const getAdminAlerts        = ()     => apiClient.get('/api/admin/alerts');
export const getAdminFeatureFailures = ()   => apiClient.get('/api/admin/stats/feature-failures');
export const getAdminPrompts       = ()     => apiClient.get('/api/admin/config/prompts');
export const updateAdminPrompts    = (data) => apiClient.put('/api/admin/config/prompts', data);
