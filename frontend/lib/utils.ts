import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString?: string): string {
  if (!dateString) return 'N/A';
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
}

export function getStatusBadge(status: string) {
  switch (status.toUpperCase()) {
    case 'ACTIVE':
    case 'APPROVED':
      return { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500', label: status };
    case 'PARTIALLY_APPROVED':
      return { bg: 'bg-blue-50 text-blue-700 border-blue-200', dot: 'bg-blue-500', label: 'PARTIALLY APPROVED' };
    case 'ON_HOLD':
    case 'PHARMACIST_REVIEW_REQUIRED':
    case 'PENDING':
      return { bg: 'bg-amber-50 text-amber-700 border-amber-200', dot: 'bg-amber-500', label: 'ON HOLD / REVIEW' };
    case 'REJECTED':
    case 'SUSPENDED':
    case 'CONFIRMED_FRAUD':
      return { bg: 'bg-rose-50 text-rose-700 border-rose-200', dot: 'bg-rose-500', label: status };
    case 'EXPIRED':
    case 'EXHAUSTED':
    case 'CANCELLED':
    case 'DISMISSED':
      return { bg: 'bg-slate-100 text-slate-700 border-slate-200', dot: 'bg-slate-400', label: status };
    default:
      return { bg: 'bg-slate-50 text-slate-600 border-slate-200', dot: 'bg-slate-400', label: status };
  }
}

export function getRiskLevelColor(level: string, score?: number) {
  switch (level?.toUpperCase()) {
    case 'LOW':
      return { text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', bar: 'bg-emerald-500' };
    case 'MEDIUM':
      return { text: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', bar: 'bg-amber-500' };
    case 'HIGH':
      return { text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200', bar: 'bg-orange-500' };
    case 'CRITICAL':
      return { text: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-200', bar: 'bg-rose-500' };
    default:
      return { text: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200', bar: 'bg-slate-400' };
  }
}
