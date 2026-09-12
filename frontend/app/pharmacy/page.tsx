'use client';

import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Search, 
  QrCode, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  ArrowRight,
  ShieldCheck,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { api } from '@/lib/api';
import { getStoredSession, setStoredSession } from '@/lib/auth';
import { getStatusBadge, formatDate } from '@/lib/utils';
import { MultiAgentEvaluationResult, DispenseExecuteResponse } from '@/types';
import AIDecisionTimeline from '@/components/timeline/AIDecisionTimeline';

export default function PharmacyPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Dispense Form State
  const [prescriptionCode, setPrescriptionCode] = useState('RX-2026-DEMO1');
  const [requestedQty, setRequestedQty] = useState(10);
  const [selectedPharmacyId, setSelectedPharmacyId] = useState<string>('');
  
  // Evaluation & Execution State
  const [evaluating, setEvaluating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<MultiAgentEvaluationResult | null>(null);
  const [executeResponse, setExecuteResponse] = useState<DispenseExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPharmacyData();
  }, []);

  const loadPharmacyData = async () => {
    setLoading(true);
    try {
      const currentSession = getStoredSession();
      if (!currentSession || (currentSession.role !== 'PHARMACY' && currentSession.role !== 'ADMIN')) {
        const pharmSession = await api.login('metro@pharmacy.com', 'password123');
        setStoredSession(pharmSession);
      }
      const res = await api.getPharmacyDashboard();
      setData(res);
      if (res.all_pharmacies && res.all_pharmacies.length > 0) {
        setSelectedPharmacyId(res.all_pharmacies[0].id);
      }
    } catch (err) {
      try {
        const pharmSession = await api.login('metro@pharmacy.com', 'password123');
        setStoredSession(pharmSession);
        const res = await api.getPharmacyDashboard();
        setData(res);
        if (res.all_pharmacies && res.all_pharmacies.length > 0) {
          setSelectedPharmacyId(res.all_pharmacies[0].id);
        }
      } catch (innerErr) {
        console.error(innerErr);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateDryRun = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prescriptionCode) return;

    setEvaluating(true);
    setError(null);
    setExecuteResponse(null);
    try {
      const res = await api.evaluateDispense(
        prescriptionCode,
        Number(requestedQty),
        undefined,
        selectedPharmacyId
      );
      setEvaluationResult(res);
    } catch (err: any) {
      setError(err.message || 'Evaluation failed');
    } finally {
      setEvaluating(false);
    }
  };

  const handleExecuteDispense = async () => {
    if (!prescriptionCode) return;

    setSubmitting(true);
    setError(null);
    try {
      const res = await api.executeDispense(
        prescriptionCode,
        Number(requestedQty),
        undefined,
        selectedPharmacyId
      );
      setExecuteResponse(res);
      setEvaluationResult(res.evaluation);
      // Reload history ledger
      loadPharmacyData();
    } catch (err: any) {
      setError(err.message || 'Dispensing execution failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-500">
        <div className="inline-block w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm">Connecting to participating pharmacy network & ledger gateway...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 text-purple-700 text-xs font-semibold mb-2">
            <Building2 className="w-3.5 h-3.5" />
            <span>Pharmacy Dispensing Terminal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
            {data?.pharmacy_name || 'HealthFirst Pharmacy - Metro Branch'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Centralized Prescription Integrity Verification • Real-time Multi-Agent Risk Engine
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs bg-slate-50 border border-slate-200 p-2.5 rounded-2xl">
          <span className="text-slate-400 font-medium">Branch Location:</span>
          <select
            value={selectedPharmacyId}
            onChange={(e) => setSelectedPharmacyId(e.target.value)}
            className="font-semibold text-slate-800 bg-transparent border-none focus:outline-none cursor-pointer"
          >
            {data?.all_pharmacies?.map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.type})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Dispensing Input Box */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Search className="w-4 h-4 text-purple-600" />
              Scan or Enter Digital Prescription ID
            </h2>
            <p className="text-xs text-slate-500">Scan QR payload or enter standard Rx code</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setPrescriptionCode('RX-2026-DEMO1');
                setRequestedQty(10);
              }}
              className="text-[11px] font-semibold text-purple-600 bg-purple-50 hover:bg-purple-100 px-2.5 py-1 rounded-lg transition"
            >
              Demo Rx 1
            </button>
            <button
              type="button"
              onClick={() => {
                setPrescriptionCode('RX-2026-DEMO2');
                setRequestedQty(20);
              }}
              className="text-[11px] font-semibold text-purple-600 bg-purple-50 hover:bg-purple-100 px-2.5 py-1 rounded-lg transition"
            >
              Demo Rx 2 (Over-Limit)
            </button>
            <button
              type="button"
              onClick={() => {
                setPrescriptionCode('RX-2026-DEMO3');
                setRequestedQty(15);
              }}
              className="text-[11px] font-semibold text-purple-600 bg-purple-50 hover:bg-purple-100 px-2.5 py-1 rounded-lg transition"
            >
              Demo Rx 3 (Rapid Burst)
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <XCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleEvaluateDryRun} className="grid sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Prescription Code / QR String
            </label>
            <div className="relative">
              <input
                type="text"
                required
                value={prescriptionCode}
                onChange={(e) => setPrescriptionCode(e.target.value)}
                placeholder="e.g. RX-2026-DEMO1"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-mono font-bold focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 uppercase"
              />
              <QrCode className="w-4 h-4 text-slate-400 absolute right-3.5 top-3" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Requested Quantity
            </label>
            <input
              type="number"
              min="1"
              required
              value={requestedQty}
              onChange={(e) => setRequestedQty(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-purple-500/20"
            />
          </div>

          <div className="sm:col-span-3 flex flex-wrap items-center justify-between gap-3 pt-2">
            <button
              type="submit"
              disabled={evaluating}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition disabled:opacity-50"
            >
              <Cpu className="w-4 h-4 text-brand-400" />
              <span>{evaluating ? 'Running 5 Agents...' : '1. Run Multi-Agent Verification (Dry Run)'}</span>
            </button>

            <button
              type="button"
              disabled={submitting}
              onClick={handleExecuteDispense}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition disabled:opacity-50"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{submitting ? 'Committing to Ledger...' : '2. Finalize & Submit Dispense'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Execution Alert Receipt */}
      {executeResponse && (
        <div className={`p-5 rounded-3xl border flex items-start gap-4 shadow-sm animate-in fade-in ${
          executeResponse.decision === 'APPROVED' ? 'bg-emerald-50 border-emerald-200 text-emerald-900' :
          executeResponse.decision === 'PARTIALLY_APPROVED' ? 'bg-blue-50 border-blue-200 text-blue-900' :
          executeResponse.decision === 'ON_HOLD' ? 'bg-amber-50 border-amber-200 text-amber-900' :
          'bg-rose-50 border-rose-200 text-rose-900'
        }`}>
          {executeResponse.decision === 'APPROVED' ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
          ) : executeResponse.decision === 'ON_HOLD' ? (
            <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
          ) : (
            <XCircle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
          )}

          <div className="flex-1 space-y-1 text-xs">
            <div className="text-base font-bold">
              Transaction Outcome: {executeResponse.decision}
            </div>
            <p className="text-xs opacity-90">{executeResponse.message}</p>
            <div className="text-[11px] font-mono pt-1 opacity-70">
              Tx ID: {executeResponse.transaction_id || 'N/A'} • Remaining Balance: {executeResponse.remaining_quantity} units
            </div>
          </div>
        </div>
      )}

      {/* Visual AI Decision Timeline Component */}
      <AIDecisionTimeline evaluation={evaluationResult} isLoading={evaluating} />

      {/* Recent Pharmacy Transactions Ledger */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Clock className="w-4 h-4 text-purple-600" />
          Recent Pharmacy Dispensing Log
        </h2>

        {data?.recent_transactions && data.recent_transactions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Prescription Code</th>
                  <th className="pb-3 font-semibold">Patient</th>
                  <th className="pb-3 font-semibold">Medicine</th>
                  <th className="pb-3 font-semibold">Req / Appr</th>
                  <th className="pb-3 font-semibold">Rem. After</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {data.recent_transactions.map((tx: any) => {
                  const badge = getStatusBadge(tx.status);
                  return (
                    <tr key={tx.id} className="hover:bg-slate-50/50">
                      <td className="py-3 font-mono font-bold text-purple-700">{tx.prescription_code}</td>
                      <td className="py-3 font-semibold text-slate-900">{tx.patient_name}</td>
                      <td className="py-3">{tx.medicine_name}</td>
                      <td className="py-3 font-mono">{tx.requested_quantity} / {tx.approved_quantity}</td>
                      <td className="py-3 font-mono font-bold text-slate-800">{tx.remaining_after}</td>
                      <td className="py-3">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badge.bg}`}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400">{formatDate(tx.timestamp)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-slate-400 text-center py-4">No transactions recorded yet.</p>
        )}
      </div>

    </div>
  );
}
