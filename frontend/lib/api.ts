import { getStoredSession, setStoredSession } from './auth';
import {
  UserSession,
  Prescription,
  MultiAgentEvaluationResult,
  DispenseExecuteResponse,
  DispensingTransaction,
  ReviewCase,
  AuditLog,
  Warning,
  DemoScenario
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const session = getStoredSession();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  login: async (email: string, password: string = 'password123') => {
    const session = await fetchAPI<UserSession>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setStoredSession(session);
    return session;
  },

  register: async (payload: any) => {
    const session = await fetchAPI<UserSession>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    setStoredSession(session);
    return session;
  },

  getMe: () => fetchAPI<any>('/auth/me'),

  // Prescriptions
  getPrescriptions: () => fetchAPI<Prescription[]>('/prescriptions'),
  getPrescription: (id: string) => fetchAPI<Prescription>(`/prescriptions/${id}`),
  getPrescriptionByCode: (code: string) => fetchAPI<Prescription>(`/prescriptions/code/${encodeURIComponent(code)}`),
  createPrescription: (payload: any) =>
    fetchAPI<Prescription>('/prescriptions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  cancelPrescription: (id: string) =>
    fetchAPI<Prescription>(`/prescriptions/${id}/cancel`, {
      method: 'POST',
    }),

  // Dispensing & Agents
  evaluateDispense: (prescription_code: string, requested_quantity: number, medicine_name?: string, pharmacy_id?: string) =>
    fetchAPI<MultiAgentEvaluationResult>('/dispense/evaluate', {
      method: 'POST',
      body: JSON.stringify({ prescription_code, requested_quantity, medicine_name, pharmacy_id }),
    }),

  executeDispense: (prescription_code: string, requested_quantity: number, medicine_name?: string, pharmacy_id?: string) =>
    fetchAPI<DispenseExecuteResponse>('/dispense/execute', {
      method: 'POST',
      body: JSON.stringify({ prescription_code, requested_quantity, medicine_name, pharmacy_id }),
    }),

  getDispenseHistory: (prescription_id?: string, pharmacy_id?: string) => {
    let q = '';
    if (prescription_id) q += `?prescription_id=${prescription_id}`;
    else if (pharmacy_id) q += `?pharmacy_id=${pharmacy_id}`;
    return fetchAPI<DispensingTransaction[]>(`/dispense/history${q}`);
  },

  // Reviews & Admin
  getReviewCases: (status_filter?: string) => {
    const q = status_filter ? `?status_filter=${status_filter}` : '';
    return fetchAPI<ReviewCase[]>(`/reviews/cases${q}`);
  },
  getReviewCase: (id: string) => fetchAPI<ReviewCase>(`/reviews/cases/${id}`),
  resolveReviewCase: (id: string, resolution: string, reviewer_notes: string) =>
    fetchAPI<ReviewCase>(`/reviews/cases/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution, reviewer_notes }),
    }),
  getAuditLogs: (limit: number = 50) => fetchAPI<AuditLog[]>(`/reviews/audit-logs?limit=${limit}`),
  getWarnings: () => fetchAPI<Warning[]>('/reviews/warnings'),
  getSystemStats: () => fetchAPI<any>('/reviews/stats'),

  // Dashboards
  getPatientDashboard: () => fetchAPI<any>('/dashboard/patient'),
  getDoctorDashboard: () => fetchAPI<any>('/dashboard/doctor'),
  getPharmacyDashboard: () => fetchAPI<any>('/dashboard/pharmacy'),

  // Demo Scenarios
  getDemoScenarios: () => fetchAPI<DemoScenario[]>('/demo/scenarios'),
  executeDemoScenario: (scenario_id: string) =>
    fetchAPI<MultiAgentEvaluationResult>(`/demo/scenarios/${scenario_id}/execute`, {
      method: 'POST',
    }),
  resetSeedDatabase: () =>
    fetchAPI<any>('/demo/reset-seed', {
      method: 'POST',
    }),
};
