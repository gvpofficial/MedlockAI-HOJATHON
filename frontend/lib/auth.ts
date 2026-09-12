import { UserSession, Role } from '@/types';

const AUTH_STORAGE_KEY = 'medlock_auth_session';

export function getStoredSession(): UserSession | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as UserSession;
  } catch {
    return null;
  }
}

export function setStoredSession(session: UserSession): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredSession(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export const DEMO_PRESET_USERS = [
  { role: 'PATIENT' as Role, email: 'john.doe@patient.com', label: 'Patient (Johnathan Doe)' },
  { role: 'DOCTOR' as Role, email: 'doctor.vance@medlock.ai', label: 'Doctor (Dr. Arthur Vance, MD)' },
  { role: 'PHARMACY' as Role, email: 'metro@pharmacy.com', label: 'Pharmacy (HealthFirst Metro)' },
  { role: 'ADMIN' as Role, email: 'admin@medlock.ai', label: 'Admin / Reviewer (Dr. Eleanor Vance)' },
];
