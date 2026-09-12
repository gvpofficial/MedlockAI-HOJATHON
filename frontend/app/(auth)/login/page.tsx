'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ShieldCheck, User, Stethoscope, Building2, ShieldAlert, KeyRound, AlertCircle, PlayCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { setStoredSession, DEMO_PRESET_USERS } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('password123');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (loginEmail: string, loginPass: string = 'password123') => {
    setIsLoading(true);
    setError(null);
    try {
      const session = await api.login(loginEmail, loginPass);
      setStoredSession(session);
      
      if (session.role === 'PATIENT') router.push('/patient');
      else if (session.role === 'DOCTOR') router.push('/doctor');
      else if (session.role === 'PHARMACY') router.push('/pharmacy');
      else if (session.role === 'ADMIN') router.push('/admin');
      else router.push('/demo');
    } catch (err: any) {
      setError(err.message || 'Failed to authenticate');
    } finally {
      setIsLoading(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'PATIENT': return <User className="w-4 h-4 text-emerald-500" />;
      case 'DOCTOR': return <Stethoscope className="w-4 h-4 text-blue-500" />;
      case 'PHARMACY': return <Building2 className="w-4 h-4 text-purple-500" />;
      case 'ADMIN': return <ShieldAlert className="w-4 h-4 text-amber-500" />;
      default: return <User className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="max-w-md mx-auto py-8">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8 space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-brand-600 text-white flex items-center justify-center mx-auto shadow-md shadow-brand-500/30">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Sign In to MedLock AI</h1>
          <p className="text-xs text-slate-500">Access your role-based prescription portal</p>
        </div>

        {/* 1-Click Demo Login for Judges */}
        <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
              <PlayCircle className="w-4 h-4 text-brand-600" />
              1-Click Demo Logins for Judges
            </span>
            <span className="text-[10px] bg-brand-100 text-brand-800 font-semibold px-2 py-0.5 rounded-full">
              Quick Test
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {DEMO_PRESET_USERS.map((preset) => (
              <button
                key={preset.email}
                type="button"
                disabled={isLoading}
                onClick={() => handleLogin(preset.email)}
                className="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-white hover:border-brand-500 hover:bg-brand-50/50 text-left transition group"
              >
                <div className="p-1 rounded-lg bg-slate-50 group-hover:bg-white">
                  {getRoleIcon(preset.role)}
                </div>
                <div className="truncate">
                  <div className="text-xs font-bold text-slate-800 group-hover:text-brand-700">{preset.role}</div>
                  <div className="text-[10px] text-slate-400 truncate">{preset.email.split('@')[0]}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Standard Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLogin(email, password);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@domain.com"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-sm transition disabled:opacity-50"
          >
            {isLoading ? 'Signing In...' : 'Sign In with Password'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-100">
          Need a new test account?{' '}
          <Link href="/register" className="text-brand-600 font-semibold hover:underline">
            Register New User
          </Link>
        </div>

      </div>
    </div>
  );
}
