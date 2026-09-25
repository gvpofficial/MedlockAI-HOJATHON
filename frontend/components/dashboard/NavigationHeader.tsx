'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { 
  ShieldCheck, 
  User, 
  Stethoscope, 
  Building2, 
  ShieldAlert, 
  PlayCircle, 
  LogOut, 
  ChevronDown,
  Activity,
  LogIn,
  Menu,
  X
} from 'lucide-react';
import { getStoredSession, clearStoredSession, setStoredSession, DEMO_PRESET_USERS } from '@/lib/auth';
import { api } from '@/lib/api';
import { UserSession } from '@/types';

export default function NavigationHeader() {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<UserSession | null>(null);
  const [isRoleMenuOpen, setIsRoleMenuOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    setSession(getStoredSession());
    setIsMobileMenuOpen(false);
    setIsRoleMenuOpen(false);
  }, [pathname]);

  const handleRoleSwitch = async (email: string) => {
    setIsSwitching(true);
    try {
      const newSession = await api.login(email, 'password123');
      setStoredSession(newSession);
      setSession(newSession);
      setIsRoleMenuOpen(false);

      if (newSession.role === 'PATIENT') router.push('/patient');
      else if (newSession.role === 'DOCTOR') router.push('/doctor');
      else if (newSession.role === 'PHARMACY') router.push('/pharmacy');
      else if (newSession.role === 'ADMIN') router.push('/admin');
    } catch (err) {
      console.error('Failed to switch role', err);
    } finally {
      setIsSwitching(false);
    }
  };

  const handleLogout = () => {
    clearStoredSession();
    setSession(null);
    router.push('/login');
  };

  const getRoleIcon = (role?: string) => {
    switch (role) {
      case 'PATIENT': return <User className="w-4 h-4 text-emerald-500" />;
      case 'DOCTOR': return <Stethoscope className="w-4 h-4 text-blue-500" />;
      case 'PHARMACY': return <Building2 className="w-4 h-4 text-purple-500" />;
      case 'ADMIN': return <ShieldAlert className="w-4 h-4 text-amber-500" />;
      default: return <User className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <header className="sticky top-0 z-50 glass border-b border-slate-200/80 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-emerald-400 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg tracking-tight text-slate-900">MEDLOCK</span>
              <span className="bg-brand-500/10 text-brand-700 text-xs font-semibold px-1.5 py-0.5 rounded border border-brand-500/20">AI</span>
            </div>
            <p className="text-[10px] text-slate-500 font-medium tracking-tight -mt-0.5">Cross-Pharmacy Integrity</p>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden lg:flex items-center gap-1 bg-slate-100/70 p-1 rounded-xl border border-slate-200/60 text-sm font-medium">
          <Link
            href="/demo"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
              pathname === '/demo' ? 'bg-white text-brand-700 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <PlayCircle className="w-4 h-4 text-brand-600 animate-pulse" />
            <span>Judge Demo Arena</span>
          </Link>
          <Link
            href="/patient"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
              pathname === '/patient' ? 'bg-white text-emerald-700 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <User className="w-4 h-4 text-emerald-600" />
            <span>Patient Portal</span>
          </Link>
          <Link
            href="/doctor"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
              pathname === '/doctor' ? 'bg-white text-blue-700 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Stethoscope className="w-4 h-4 text-blue-600" />
            <span>Doctor Portal</span>
          </Link>
          <Link
            href="/pharmacy"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
              pathname === '/pharmacy' ? 'bg-white text-purple-700 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Building2 className="w-4 h-4 text-purple-600" />
            <span>Pharmacy Portal</span>
          </Link>
          <Link
            href="/admin"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
              pathname === '/admin' ? 'bg-white text-amber-700 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>Admin & Review</span>
          </Link>
        </nav>

        {/* Right Section: Role Switcher & Profile or Sign In */}
        <div className="flex items-center gap-2 sm:gap-3">
          {session ? (
            <div className="relative">
              <button
                onClick={() => setIsRoleMenuOpen(!isRoleMenuOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition shadow-sm text-sm"
              >
                {getRoleIcon(session.role)}
                <div className="text-left hidden sm:block">
                  <div className="text-xs font-semibold text-slate-900 leading-tight">{session.full_name}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">{session.role}</div>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {/* Quick Role Switcher Dropdown */}
              {isRoleMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 z-50">
                  <div className="px-3 py-2 border-b border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Demo Role Switcher</p>
                    <p className="text-[11px] text-slate-400">Instantly toggle roles for testing</p>
                  </div>
                  <div className="py-1 space-y-1">
                    {DEMO_PRESET_USERS.map((preset) => (
                      <button
                        key={preset.email}
                        disabled={isSwitching}
                        onClick={() => handleRoleSwitch(preset.email)}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left text-xs font-medium transition ${
                          session.email === preset.email
                            ? 'bg-brand-50 text-brand-800 border border-brand-200'
                            : 'hover:bg-slate-50 text-slate-700'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {getRoleIcon(preset.role)}
                          <span>{preset.label}</span>
                        </div>
                        {session.email === preset.email && (
                          <span className="w-2 h-2 rounded-full bg-brand-500" />
                        )}
                      </button>
                    ))}
                  </div>
                  <div className="pt-2 border-t border-slate-100 space-y-1">
                    <Link
                      href="/login"
                      onClick={() => setIsRoleMenuOpen(false)}
                      className="w-full flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs text-slate-700 hover:bg-slate-50 font-medium transition"
                    >
                      <LogIn className="w-3.5 h-3.5 text-brand-600" />
                      Sign In with another account
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs text-rose-600 hover:bg-rose-50 font-medium transition"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className={`flex items-center gap-1.5 px-3.5 py-1.5 sm:px-4 sm:py-2 text-sm font-semibold rounded-xl border transition-all shadow-sm ${
                  pathname === '/login'
                    ? 'border-brand-500 bg-brand-50 text-brand-700 ring-2 ring-brand-500/20 shadow-brand-500/10'
                    : 'border-slate-200 bg-white hover:bg-slate-50 hover:border-slate-300 text-slate-700 hover:text-slate-900'
                }`}
              >
                <LogIn className="w-4 h-4 text-brand-600" />
                <span>Sign In</span>
              </Link>
              <Link
                href="/demo"
                className="flex items-center gap-1.5 px-3.5 py-1.5 sm:px-4 sm:py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-sm shadow-brand-500/20 hover:shadow-brand-500/30 transition group"
              >
                <PlayCircle className="w-4 h-4 text-white/90 group-hover:scale-110 transition-transform" />
                <span className="hidden sm:inline">Live Demo</span>
                <span className="sm:hidden">Demo</span>
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer Navigation */}
      {isMobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200/80 bg-white px-4 py-3 space-y-1 shadow-lg">
          <Link
            href="/demo"
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition ${
              pathname === '/demo' ? 'bg-brand-50 text-brand-700 font-semibold' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <PlayCircle className="w-4 h-4 text-brand-600" />
            <span>Judge Demo Arena</span>
          </Link>
          <Link
            href="/patient"
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition ${
              pathname === '/patient' ? 'bg-emerald-50 text-emerald-800 font-semibold' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <User className="w-4 h-4 text-emerald-600" />
            <span>Patient Portal</span>
          </Link>
          <Link
            href="/doctor"
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition ${
              pathname === '/doctor' ? 'bg-blue-50 text-blue-800 font-semibold' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Stethoscope className="w-4 h-4 text-blue-600" />
            <span>Doctor Portal</span>
          </Link>
          <Link
            href="/pharmacy"
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition ${
              pathname === '/pharmacy' ? 'bg-purple-50 text-purple-800 font-semibold' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Building2 className="w-4 h-4 text-purple-600" />
            <span>Pharmacy Portal</span>
          </Link>
          <Link
            href="/admin"
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition ${
              pathname === '/admin' ? 'bg-amber-50 text-amber-800 font-semibold' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>Admin & Review</span>
          </Link>
          {!session && (
            <div className="pt-2 border-t border-slate-100">
              <Link
                href="/login"
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold transition ${
                  pathname === '/login' ? 'bg-brand-50 text-brand-700' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                <LogIn className="w-4 h-4 text-brand-600" />
                <span>Sign In</span>
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
