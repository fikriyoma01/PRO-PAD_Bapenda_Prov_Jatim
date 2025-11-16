import axios from 'axios';

// API base URL - adjust this based on your backend setup
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;

// Data API
export const dataAPI = {
  // Load historical data
  loadHistoricalData: () => api.get('/data/historical'),

  // Load PKB inputs
  loadPKBInputs: () => api.get('/data/pkb-inputs'),

  // Load BBNKB inputs
  loadBBNKBInputs: () => api.get('/data/bbnkb-inputs'),

  // Update data
  updateData: (data) => api.post('/data/update', data),

  // Export data
  exportData: (format = 'excel') => api.get(`/data/export?format=${format}`, {
    responseType: 'blob',
  }),
};

// Model API
export const modelAPI = {
  // Run OLS regression
  runOLSRegression: (params) => api.post('/model/ols', params),

  // Run ARIMA model
  runARIMA: (params) => api.post('/model/arima', params),

  // Run Exponential Smoothing
  runExpSmoothing: (params) => api.post('/model/exp-smoothing', params),

  // Run ensemble model
  runEnsemble: (params) => api.post('/model/ensemble', params),

  // Validate model
  validateModel: (params) => api.post('/model/validate', params),

  // Cross validation
  crossValidate: (params) => api.post('/model/cross-validate', params),

  // Backtest model
  backtestModel: (params) => api.post('/model/backtest', params),
};

// Projection API
export const projectionAPI = {
  // Generate projections
  generateProjection: (params) => api.post('/projection/generate', params),

  // Get scenario analysis
  getScenarioAnalysis: (params) => api.post('/projection/scenarios', params),

  // Calculate confidence intervals
  getConfidenceIntervals: (params) => api.post('/projection/confidence-intervals', params),
};

// Analysis API
export const analysisAPI = {
  // Sensitivity analysis
  getSensitivityAnalysis: (params) => api.post('/analysis/sensitivity', params),

  // Decomposition analysis
  getDecomposition: (params) => api.post('/analysis/decomposition', params),

  // Correlation analysis
  getCorrelation: (params) => api.post('/analysis/correlation', params),

  // Statistical summary
  getStatsSummary: (params) => api.post('/analysis/stats-summary', params),
};

// Audit API
export const auditAPI = {
  // Log activity
  logActivity: (activity) => api.post('/audit/log', activity),

  // Get audit trail
  getAuditTrail: (filters) => api.get('/audit/trail', { params: filters }),

  // Export audit log
  exportAuditLog: () => api.get('/audit/export', {
    responseType: 'blob',
  }),
};

// Policy API
export const policyAPI = {
  // Get policy settings
  getPolicySettings: () => api.get('/policy/settings'),

  // Update policy settings
  updatePolicySettings: (settings) => api.post('/policy/settings', settings),

  // Get targets
  getTargets: () => api.get('/policy/targets'),

  // Update targets
  updateTargets: (targets) => api.post('/policy/targets', targets),
};
