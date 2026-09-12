'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ShieldCheck, User, Stethoscope, Building2, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { setStoredSession } from '@/lib/auth';
import { Role } from '@/types';

export default function RegisterPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>('PATIENT');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('password123');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('+1-555-0199');
  
  // Doctor fields
  const [specialization, setSpecialization] = useState('General Medicine');
  const [hospital, setHospital] = useState('Metropolitan Clinic');
  
  // Pharmacy fields
  const [pharmacyType, setPharmacyType] = useState('PHYSICAL_CHAIN');
  const [address, setAddress] = useState('742 Evergreen Terrace');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const payload: any = {
        email,
        password,
        full_name: fullName,
        role,
        phone
      };

      if (role === 'DOCTOR') {
        payload.specialization = specialization;
        payload.hospital_clinic_name = hospital;
      } else if (role === 'PHARMACY') {
        payload.pharmacy_name = fullName;
        payload.pharmacy_type = pharmacyType;
        payload.address = address;
      }

      const session = await api.register(payload);
      setStoredSession(session);

      if (role === 'PATIENT') router.push('/patient');
      else if (role === 'DOCTOR') router.push('/doctor');
      else if (role === 'PHARMACY') router.push('/pharmacy');
      else router.push('/admin');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8 space-y-6">
        
        <div className="text-center space-y-1">
          <div className="w-12 h-12 rounded-2xl bg-brand-600 text-white flex items-center justify-center mx-auto shadow-md shadow-brand-500/30">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Create Account</h1>
          <p className="text-xs text-slate-500">Register in the MedLock AI network</p>
        </div>

        {/* Role Selector */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-700">Select Stakeholder Role</label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setRole('PATIENT')}
              className={`p-2.5 rounded-xl border text-center transition ${
                role === 'PATIENT' ? 'bg-brand-50 border-brand-500 text-brand-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-600'
              }`}
            >
              <User className="w-4 h-4 mx-auto mb-1 text-emerald-600" />
              <div className="text-xs">Patient</div>
            </button>
            <button
              type="button"
              onClick={() => setRole('DOCTOR')}
              className={`p-2.5 rounded-xl border text-center transition ${
                role === 'DOCTOR' ? 'bg-blue-50 border-blue-500 text-blue-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-600'
              }`}
            >
              <Stethoscope className="w-4 h-4 mx-auto mb-1 text-blue-600" />
              <div className="text-xs">Doctor</div>
            </button>
            <button
              type="button"
              onClick={() => setRole('PHARMACY')}
              className={`p-2.5 rounded-xl border text-center transition ${
                role === 'PHARMACY' ? 'bg-purple-50 border-purple-500 text-purple-800 font-bold' : 'bg-slate-50 border-slate-200 text-slate-600'
              }`}
            >
              <Building2 className="w-4 h-4 mx-auto mb-1 text-purple-600" />
              <div className="text-xs">Pharmacy</div>
            </button>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Full Name / Facility Name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder={role === 'PHARMACY' ? 'e.g. Apex Health Pharmacy' : 'e.g. Jane Doe'}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          {role === 'DOCTOR' && (
            <>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Specialization</label>
                <input
                  type="text"
                  value={specialization}
                  onChange={(e) => setSpecialization(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Hospital / Clinic</label>
                <input
                  type="text"
                  value={hospital}
                  onChange={(e) => setHospital(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
                />
              </div>
            </>
          )}

          {role === 'PHARMACY' && (
            <>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Pharmacy Channel Type</label>
                <select
                  value={pharmacyType}
                  onChange={(e) => setPharmacyType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
                >
                  <option value="PHYSICAL_CHAIN">Physical Chain Pharmacy</option>
                  <option value="INDEPENDENT">Independent Physical Pharmacy</option>
                  <option value="ONLINE">Online Direct Pharmacy</option>
                </select>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Address / Web URL</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 mt-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-sm shadow-sm transition disabled:opacity-50"
          >
            {isLoading ? 'Creating Account...' : 'Complete Registration'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-100">
          Already have an account?{' '}
          <Link href="/login" className="text-brand-600 font-semibold hover:underline">
            Sign In
          </Link>
        </div>

      </div>
    </div>
  );
}
