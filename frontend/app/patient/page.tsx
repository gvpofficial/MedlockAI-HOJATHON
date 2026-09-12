'use client';

import React, { useState, useEffect } from 'react';
import { 
  User, 
  Pill, 
  QrCode, 
  AlertTriangle, 
  CheckCircle2, 
  Calendar, 
  Stethoscope, 
  Clock, 
  Building2, 
  ShieldAlert,
  ArrowUpRight,
  ExternalLink
} from 'lucide-react';
import { api } from '@/lib/api';
import { getStoredSession, setStoredSession } from '@/lib/auth';
import { getStatusBadge, formatDate } from '@/lib/utils';
import QRCodeDisplay from '@/components/qr/QRCodeDisplay';

export default function PatientDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedQR, setSelectedQR] = useState<any | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const currentSession = getStoredSession();
      if (!currentSession || currentSession.role !== 'PATIENT') {
        const patSession = await api.login('john.doe@patient.com', 'password123');
        setStoredSession(patSession);
      }
      const res = await api.getPatientDashboard();
      setData(res);
    } catch (err: any) {
      try {
        const patSession = await api.login('john.doe@patient.com', 'password123');
        setStoredSession(patSession);
        const res = await api.getPatientDashboard();
        setData(res);
      } catch (innerErr: any) {
        setError(innerErr.message || 'Failed to load patient dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-500">
        <div className="inline-block w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm">Loading patient health records & central dispensing balances...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold mb-2">
            <User className="w-3.5 h-3.5" />
            <span>Patient Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
            Welcome back, {data?.user_name || 'Patient'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time digital prescription balance tracked across all network pharmacies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-slate-50 border border-slate-200 p-3 rounded-2xl text-center min-w-[100px]">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Active Rx</div>
            <div className="text-xl font-bold text-brand-700">{data?.active_prescriptions || 0}</div>
          </div>
          <div className="bg-slate-50 border border-slate-200 p-3 rounded-2xl text-center min-w-[100px]">
            <div className="text-[10px] text-slate-400 font-bold uppercase">Total Items</div>
            <div className="text-xl font-bold text-slate-900">{data?.total_prescriptions || 0}</div>
          </div>
        </div>
      </div>

      {/* Safety Alerts / Warning Notices */}
      {data?.warnings && data.warnings.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            Safety Notices & Dispensing Alerts
          </h2>
          <div className="space-y-2">
            {data.warnings.map((w: any) => (
              <div
                key={w.id}
                className={`p-4 rounded-2xl border flex items-start gap-3.5 ${
                  w.severity === 'CRITICAL' ? 'bg-rose-50 border-rose-200 text-rose-900' : 'bg-amber-50 border-amber-200 text-amber-900'
                }`}
              >
                <AlertTriangle className={`w-5 h-5 shrink-0 mt-0.5 ${
                  w.severity === 'CRITICAL' ? 'text-rose-600' : 'text-amber-600'
                }`} />
                <div className="flex-1 text-xs space-y-0.5">
                  <div className="font-bold text-sm">{w.title}</div>
                  <p className="opacity-90">{w.message}</p>
                  <div className="text-[10px] opacity-60 pt-1">{formatDate(w.created_at)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Digital Prescriptions */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Pill className="w-4 h-4 text-brand-600" />
          Active Digital Prescriptions
        </h2>

        <div className="grid md:grid-cols-2 gap-4">
          {data?.prescriptions && data.prescriptions.map((rx: any) => {
            const statusBadge = getStatusBadge(rx.status);
            return (
              <div
                key={rx.id}
                className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition space-y-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-xs font-mono font-bold text-brand-700">{rx.prescription_code}</div>
                    <div className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                      <Stethoscope className="w-3.5 h-3.5 text-slate-400" />
                      <span>{rx.doctor_name}</span>
                      <span className="text-slate-300">•</span>
                      <span>{rx.hospital}</span>
                    </div>
                  </div>
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${statusBadge.bg}`}>
                    {statusBadge.label}
                  </span>
                </div>

                {/* Medicine Items & Balance Gauges */}
                <div className="space-y-3 pt-2 border-t border-slate-100">
                  {rx.items.map((item: any, iIdx: number) => {
                    const pct = Math.round((item.remaining_quantity / item.authorized_quantity) * 100);
                    return (
                      <div key={iIdx} className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100 space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="font-bold text-sm text-slate-900">{item.medicine_name}</div>
                          <div className="text-xs font-mono font-bold text-brand-700">
                            {item.remaining_quantity} / {item.authorized_quantity} Left
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 rounded-full ${
                              pct > 50 ? 'bg-emerald-500' : pct > 20 ? 'bg-amber-500' : 'bg-rose-500'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>

                        <div className="flex justify-between text-[11px] text-slate-500">
                          <span>Dispensed: {item.dispensed_quantity}</span>
                          <span>{item.dosage_instructions || 'Take as directed'}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Footer Action: View QR Code */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Expires {formatDate(rx.expiry_date)}</span>
                  </div>

                  <button
                    onClick={() => setSelectedQR(rx)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs shadow-xs transition"
                  >
                    <QrCode className="w-3.5 h-3.5" />
                    <span>Show Pharmacy QR</span>
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      </div>

      {/* Central Dispensing Transaction History */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Clock className="w-4 h-4 text-purple-600" />
          Central Cross-Pharmacy Dispensing Ledger
        </h2>

        {data?.recent_transactions && data.recent_transactions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Pharmacy / Provider</th>
                  <th className="pb-3 font-semibold">Medicine Item</th>
                  <th className="pb-3 font-semibold">Requested</th>
                  <th className="pb-3 font-semibold">Approved</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {data.recent_transactions.map((tx: any) => {
                  const badge = getStatusBadge(tx.status);
                  return (
                    <tr key={tx.id} className="hover:bg-slate-50/50">
                      <td className="py-3 font-semibold text-slate-900 flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5 text-slate-400" />
                        {tx.pharmacy_name}
                      </td>
                      <td className="py-3">{tx.medicine_name}</td>
                      <td className="py-3 font-mono">{tx.requested_quantity}</td>
                      <td className="py-3 font-mono font-bold text-slate-900">{tx.approved_quantity}</td>
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
          <p className="text-xs text-slate-400 text-center py-4">No dispensing records yet.</p>
        )}
      </div>

      {/* QR Code Modal */}
      {selectedQR && (
        <QRCodeDisplay
          isOpen={true}
          onClose={() => setSelectedQR(null)}
          prescriptionCode={selectedQR.prescription_code}
          qrCodeData={selectedQR.qr_code_data}
          patientName={data?.user_name}
          doctorName={selectedQR.doctor_name}
          status={selectedQR.status}
        />
      )}

    </div>
  );
}
