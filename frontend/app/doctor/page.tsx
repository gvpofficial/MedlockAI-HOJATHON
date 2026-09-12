'use client';

import React, { useState, useEffect } from 'react';
import { 
  Stethoscope, 
  PlusCircle, 
  QrCode, 
  Trash2, 
  CheckCircle2, 
  Calendar, 
  FileText, 
  AlertCircle,
  X,
  Building2,
  Lock
} from 'lucide-react';
import { api } from '@/lib/api';
import { getStoredSession, setStoredSession } from '@/lib/auth';
import { getStatusBadge, formatDate } from '@/lib/utils';
import QRCodeDisplay from '@/components/qr/QRCodeDisplay';

export default function DoctorDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedQR, setSelectedQR] = useState<any | null>(null);

  // Form State
  const [patientId, setPatientId] = useState('');
  const [expiryDays, setExpiryDays] = useState(30);
  const [notes, setNotes] = useState('Take medications strictly as instructed. Follow-up in 4 weeks.');
  const [items, setItems] = useState([
    { medicine_name: 'Demo Restricted Medicine X', authorized_quantity: 30, dosage_instructions: '1 tablet every 8 hours', is_restricted: true }
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const currentSession = getStoredSession();
      if (!currentSession || currentSession.role !== 'DOCTOR') {
        const docSession = await api.login('doctor.vance@medlock.ai', 'password123');
        setStoredSession(docSession);
      }
      const res = await api.getDoctorDashboard();
      setData(res);
      if (res.available_patients && res.available_patients.length > 0) {
        setPatientId(res.available_patients[0].id);
      }
    } catch (err: any) {
      console.error('Doctor dashboard load error', err);
      // Fallback: force doctor login
      try {
        const docSession = await api.login('doctor.vance@medlock.ai', 'password123');
        setStoredSession(docSession);
        const res = await api.getDoctorDashboard();
        setData(res);
        if (res.available_patients && res.available_patients.length > 0) {
          setPatientId(res.available_patients[0].id);
        }
      } catch (innerErr) {
        console.error('Secondary fallback error', innerErr);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = () => {
    setItems([
      ...items,
      { medicine_name: '', authorized_quantity: 20, dosage_instructions: '1 tablet daily', is_restricted: true }
    ]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, idx) => idx !== index));
    }
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    setItems(updated);
  };

  const handleCreatePrescription = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await api.createPrescription({
        patient_id: patientId,
        expiry_days: Number(expiryDays),
        notes,
        items: items.map(it => ({
          ...it,
          authorized_quantity: Number(it.authorized_quantity)
        }))
      });
      setIsModalOpen(false);
      loadDashboard();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create prescription');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelPrescription = async (rxId: string) => {
    if (confirm('Are you sure you want to revoke/cancel this digital prescription?')) {
      try {
        await api.cancelPrescription(rxId);
        loadDashboard();
      } catch (err: any) {
        alert(err.message || 'Failed to cancel');
      }
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-500">
        <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm">Loading physician credentials & prescribed history...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-2">
            <Stethoscope className="w-3.5 h-3.5" />
            <span>Physician Portal • {data?.license_number || 'Verified'}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
            {data?.doctor_name || 'Dr. Arthur Vance, MD'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            {data?.hospital || 'Metropolitan General Hospital'} • Cryptographic Digital Prescription Issuance
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Issue New Digital Prescription</span>
        </button>
      </div>

      {/* Prescriptions Table */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            Prescriptions Issued ({data?.prescriptions?.length || 0})
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 uppercase text-[10px]">
                <th className="pb-3 font-semibold">Prescription Code</th>
                <th className="pb-3 font-semibold">Patient Name</th>
                <th className="pb-3 font-semibold">Authorized Medicines</th>
                <th className="pb-3 font-semibold">Issue / Expiry</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data?.prescriptions && data.prescriptions.map((rx: any) => {
                const badge = getStatusBadge(rx.status);
                return (
                  <tr key={rx.id} className="hover:bg-slate-50/50">
                    <td className="py-3.5 font-mono font-bold text-blue-700">{rx.prescription_code}</td>
                    <td className="py-3.5 font-semibold text-slate-900">{rx.patient_name}</td>
                    <td className="py-3.5 space-y-1">
                      {rx.items.map((it: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-1.5">
                          <span className="font-semibold text-slate-800">{it.medicine_name}</span>
                          <span className="text-[11px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-mono">
                            Qty: {it.authorized_quantity}
                          </span>
                        </div>
                      ))}
                    </td>
                    <td className="py-3.5 text-slate-500">
                      <div>Issued: {formatDate(rx.issue_date)}</div>
                      <div className="text-[11px] text-slate-400">Exp: {formatDate(rx.expiry_date)}</div>
                    </td>
                    <td className="py-3.5">
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${badge.bg}`}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="py-3.5 text-right space-x-2">
                      <button
                        onClick={() => setSelectedQR(rx)}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-[11px] transition"
                      >
                        <QrCode className="w-3.5 h-3.5" />
                        <span>QR</span>
                      </button>
                      {rx.status === 'ACTIVE' && (
                        <button
                          onClick={() => handleCancelPrescription(rx.id)}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 font-semibold text-[11px] transition"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Revoke</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Prescription Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 sm:p-8 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="mb-6 space-y-1">
              <div className="inline-flex p-2 rounded-xl bg-blue-50 text-blue-600 mb-1">
                <Stethoscope className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Issue Digital Prescription</h2>
              <p className="text-xs text-slate-500">
                Authorized items are digitally finalized and synchronized into the central cross-pharmacy ledger.
              </p>
            </div>

            {formError && (
              <div className="mb-4 flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreatePrescription} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Select Patient</label>
                <select
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm font-medium"
                >
                  {data?.available_patients?.map((p: any) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.email}) — DOB: {p.dob}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Prescription Validity (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={expiryDays}
                  onChange={(e) => setExpiryDays(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
                />
              </div>

              {/* Medicine Items Builder */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <label className="font-bold text-slate-800">Authorized Medicine Items</label>
                  <button
                    type="button"
                    onClick={handleAddItem}
                    className="text-blue-600 font-semibold hover:underline text-xs flex items-center gap-1"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Add Another Medicine</span>
                  </button>
                </div>

                {items.map((item, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 relative">
                    {items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(idx)}
                        className="absolute top-2 right-2 text-rose-500 hover:text-rose-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                    <div className="grid grid-cols-3 gap-2">
                      <div className="col-span-2">
                        <label className="text-[10px] font-semibold text-slate-500">Medicine Name</label>
                        <input
                          type="text"
                          required
                          value={item.medicine_name}
                          onChange={(e) => handleItemChange(idx, 'medicine_name', e.target.value)}
                          placeholder="e.g. Oxycodone 10mg"
                          className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-semibold"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500">Authorized Qty</label>
                        <input
                          type="number"
                          min="1"
                          required
                          value={item.authorized_quantity}
                          onChange={(e) => handleItemChange(idx, 'authorized_quantity', e.target.value)}
                          className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-semibold"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] font-semibold text-slate-500">Dosage Instructions</label>
                      <input
                        type="text"
                        value={item.dosage_instructions}
                        onChange={(e) => handleItemChange(idx, 'dosage_instructions', e.target.value)}
                        placeholder="1 tablet orally every 8 hours"
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Clinical Notes & Precautions</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-sm disabled:opacity-50"
                >
                  <Lock className="w-3.5 h-3.5" />
                  <span>{submitting ? 'Signing & Finalizing...' : 'Digitally Finalize Prescription'}</span>
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {selectedQR && (
        <QRCodeDisplay
          isOpen={true}
          onClose={() => setSelectedQR(null)}
          prescriptionCode={selectedQR.prescription_code}
          qrCodeData={selectedQR.qr_code_data}
          patientName={selectedQR.patient_name}
          doctorName={data?.doctor_name}
          status={selectedQR.status}
        />
      )}

    </div>
  );
}
