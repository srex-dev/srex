import { headers } from 'next/headers';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000');

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

// Server-side API fetch
async function fetchApiServer(endpoint: string, options: FetchOptions = {}) {
  const { params, ...fetchOptions } = options;
  const headersList = await headers();
  const token = headersList.get('authorization');

  const queryString = params
    ? '?' + new URLSearchParams(params).toString()
    : '';

  const response = await fetch(`${API_BASE_URL}${endpoint}${queryString}`, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: token }),
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

// Client-side API fetch
async function fetchApiClient(endpoint: string, options: FetchOptions = {}) {
  const { params, ...fetchOptions } = options;

  const queryString = params
    ? '?' + new URLSearchParams(params).toString()
    : '';

  const response = await fetch(`${API_BASE_URL}${endpoint}${queryString}`, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

// Metrics API
export const metricsApi = {
  getSystemHealth: () => fetchApiServer('/api/metrics/health'),
  getRecentActivity: () => fetchApiServer('/api/metrics/activity'),
  getPerformanceMetrics: (params?: { startDate?: string; endDate?: string }) =>
    fetchApiServer('/api/metrics/performance', { params }),
};

// Alerts API
export const alertsApi = {
  getAlerts: (params?: { status?: string; severity?: string }) =>
    fetchApiClient('/api/alerts', { params }),
  getAlertDetails: (id: string) => fetchApiClient(`/api/alerts/${id}`),
  updateAlertStatus: (id: string, status: string) =>
    fetchApiClient(`/api/alerts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
};

// Components API
export const componentsApi = {
  getComponents: () => fetchApiClient('/api/components'),
  getComponentDetails: (id: string) => fetchApiClient(`/api/components/${id}`),
  getComponentMetrics: (id: string) => fetchApiClient(`/api/components/${id}/metrics`),
};

// Settings API
export const settingsApi = {
  getUserSettings: () => fetchApiClient('/api/settings/user'),
  updateUserSettings: (settings: any) =>
    fetchApiClient('/api/settings/user', {
      method: 'PUT',
      body: JSON.stringify(settings),
    }),
};

// Help API
export const helpApi = {
  getGuides: () => fetchApiClient('/api/help/guides'),
  getGuideDetails: (id: string) => fetchApiClient(`/api/help/guides/${id}`),
};

// Logs API
export const logsApi = {
  getLogs: (params?: { level?: string; component?: string; timeRange?: string }) =>
    fetchApiClient('/api/logs', { params }),
};

// Users API
export const usersApi = {
  getUsers: () => fetchApiClient('/api/users'),
  getUserDetails: (id: string) => fetchApiClient(`/api/users/${id}`),
  updateUser: (id: string, data: any) =>
    fetchApiClient(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
}; 