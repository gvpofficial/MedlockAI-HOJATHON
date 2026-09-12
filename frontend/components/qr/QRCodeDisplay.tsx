'use client';

import React from 'react';
import { QrCode, X, Download, ShieldCheck } from 'lucide-react';

interface QRCodeDisplayProps {
  isOpen: boolean;
  onClose: () => void;
  prescriptionCode: string;
  qrCodeData?: string;
  patientName?: string;
  doctorName?: string;
  status?: string;
}

export default function QRCodeDisplay({
  isOpen,
  onClose,
  prescriptionCode,
  qrCodeData,
  patientName,
  doctorName,
  status
}: QRCodeDisplayProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-sm w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-4">
          <div className="inline-flex p-2.5 rounded-2xl bg-brand-50 text-brand-600 mb-2">
            <QrCode className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Digital Prescription QR</h3>
          <p className="text-xs font-mono text-slate-500">{prescriptionCode}</p>
        </div>

        {/* QR Code Container */}
        <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 flex items-center justify-center mb-4">
          {qrCodeData ? (
            <img
              src={qrCodeData}
              alt={`QR Code for ${prescriptionCode}`}
              className="w-56 h-56 object-contain rounded-xl shadow-inner bg-white p-2"
            />
          ) : (
            <div className="w-56 h-56 flex items-center justify-center text-slate-400 text-xs">
              Generating QR Code...
            </div>
          )}
        </div>

        <div className="space-y-1.5 text-xs text-slate-600 mb-5 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div className="flex justify-between">
            <span className="text-slate-400">Patient:</span>
            <span className="font-semibold text-slate-800">{patientName || 'Patient'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Prescribing MD:</span>
            <span className="font-semibold text-slate-800">{doctorName || 'Doctor'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Status:</span>
            <span className="font-bold text-emerald-600">{status || 'ACTIVE'}</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-slate-400 justify-center">
          <ShieldCheck className="w-3.5 h-3.5 text-brand-600" />
          <span>Verifiable across all participating network pharmacies</span>
        </div>
      </div>
    </div>
  );
}
