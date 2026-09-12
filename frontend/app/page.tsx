'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ShieldCheck, 
  Cpu, 
  Scale, 
  Activity, 
  FileCheck, 
  AlertOctagon, 
  ArrowRight, 
  PlayCircle, 
  Building2, 
  Stethoscope, 
  User, 
  ShieldAlert, 
  Layers,
  Database,
  Lock,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { api } from '@/lib/api';

export default function LandingPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.getSystemStats()
      .then(data => setStats(data))
      .catch(() => {
        // Fallback default stats if backend is booting
        setStats({
          total_prescriptions: 5,
          active_prescriptions: 5,
          total_dispensing_transactions: 4,
          prevented_excess_dispenses: 2,
          pending_review_cases: 1,
          active_pharmacies: 5,
          active_doctors: 2,
          active_patients: 5
        });
      });
  }, []);

  return (
    <div className="space-y-16 py-4">

      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto space-y-6 pt-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Agentic Cross-Pharmacy Prescription Integrity System</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
          Prevent Prescription Over-Dispensing Across <span className="bg-gradient-to-r from-brand-600 to-emerald-500 bg-clip-text text-transparent">Multiple Pharmacies</span>
        </h1>

        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Combining <strong>Hard Deterministic Ledger Limits</strong>, centralized cross-pharmacy dispensing history, and a <strong>Multi-Agent AI Layer</strong> with human pharmacist review.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            href="/demo"
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-brand-600 hover:bg-brand-700 text-white font-bold shadow-lg shadow-brand-500/25 transition-all hover:scale-105"
          >
            <PlayCircle className="w-5 h-5 animate-pulse" />
            <span>Launch Interactive Demo</span>
          </Link>
          <Link
            href="/pharmacy"
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-bold border border-slate-200 shadow-sm transition"
          >
            <Building2 className="w-5 h-5 text-purple-600" />
            <span>Pharmacy Scanner Portal</span>
          </Link>
        </div>

        {/* Real-time Telemetry Bar */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-8 max-w-3xl mx-auto text-left">
            <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
              <div className="text-xs text-slate-500 font-medium">Prevented Over-Dispenses</div>
              <div className="text-2xl font-black text-rose-600 mt-1">{stats.prevented_excess_dispenses} Attempts</div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
              <div className="text-xs text-slate-500 font-medium">Connected Pharmacies</div>
              <div className="text-2xl font-black text-slate-900 mt-1">{stats.active_pharmacies} (Physical & Online)</div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
              <div className="text-xs text-slate-500 font-medium">Active Prescriptions</div>
              <div className="text-2xl font-black text-emerald-600 mt-1">{stats.active_prescriptions} Active</div>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
              <div className="text-xs text-slate-500 font-medium">Pending HITL Reviews</div>
              <div className="text-2xl font-black text-amber-600 mt-1">{stats.pending_review_cases} Cases</div>
            </div>
          </div>
        )}
      </section>

      {/* The Core Problem vs MedLock AI Solution */}
      <section className="bg-white rounded-3xl border border-slate-200 p-8 md:p-12 shadow-sm">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">The Problem & MedLock Solution</h2>
          <p className="text-sm text-slate-500 mt-1">How disconnected pharmacy systems enable multi-pharmacy prescription leakage.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Legacy Flaw */}
          <div className="p-6 rounded-2xl bg-rose-50/50 border border-rose-200 space-y-4">
            <div className="flex items-center gap-2 text-rose-700 font-bold text-base">
              <AlertOctagon className="w-5 h-5" />
              <span>Current Status Quo (Disconnected Silos)</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Pharmacies maintain isolated databases. A patient with a 30-tablet prescription can visit Pharmacy A (10 tabs), Pharmacy B (10 tabs), and Online Pharmacy C (20 tabs) on the same day without detection, acquiring 40 tablets when only 30 were authorized.
            </p>
            <div className="bg-white p-3 rounded-xl border border-rose-200 text-xs text-rose-800 space-y-1">
              <div className="font-semibold">Result: +10 Unauthorized Tablets Acquired</div>
              <div className="text-slate-500 text-[11px]">Zero central synchronization • High fraud risk • No velocity tracking</div>
            </div>
          </div>

          {/* MedLock AI Solution */}
          <div className="p-6 rounded-2xl bg-emerald-50/50 border border-emerald-200 space-y-4">
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-base">
              <ShieldCheck className="w-5 h-5" />
              <span>MedLock AI Solution</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              A shared central dispensing ledger where hard database rules mathematically enforce: <code className="bg-emerald-100 px-1 py-0.5 rounded text-emerald-800 font-semibold">remaining = authorized - dispensed</code>. Every dispensing action is cryptographically signed and analyzed by AI agents in real time.
            </p>
            <div className="bg-white p-3 rounded-xl border border-emerald-200 text-xs text-emerald-800 space-y-1">
              <div className="font-semibold">Result: 100% Deterministic Over-Dispensing Prevention</div>
              <div className="text-slate-500 text-[11px]">Centralized ledger • Anomaly pattern detection • Pharmacist review triage</div>
            </div>
          </div>
        </div>
      </section>

      {/* The 5 Controlled Agents Layer */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-brand-600 uppercase tracking-widest mb-1">
            <Cpu className="w-4 h-4" />
            <span>Agent Architecture</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">5 Controlled Agentic AI Layers</h2>
          <p className="text-sm text-slate-500 mt-1">Strict separation between deterministic authorization rules and AI reasoning.</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Agent 1 */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-brand-300 transition shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Agent 1</span>
              <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">Deterministic</span>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Prescription Verification Agent</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Validates Rx existence, expiry date, status (ACTIVE), doctor verification license, and patient identity match.
            </p>
          </div>

          {/* Agent 2 */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-brand-300 transition shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Agent 2</span>
              <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">Deterministic</span>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Dispensing Integrity Agent</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Queries central ledger history, computes remaining balance, and enforces mathematical bounds (no LLM quantity calculation).
            </p>
          </div>

          {/* Agent 3 */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-brand-300 transition shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Agent 3</span>
              <span className="text-[10px] font-semibold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200">Heuristic AI</span>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Cross-Pharmacy Pattern Agent</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Detects rapid provider switching (&lt; 2h), online vs physical channel bursts, and repeat attempts after rejections.
            </p>
          </div>

          {/* Agent 4 */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-brand-300 transition shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Agent 4</span>
              <span className="text-[10px] font-semibold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">Scoring Engine</span>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Transparent Risk Engine</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Computes transparent risk score [0–100] across weighted factors and maps to LOW, MEDIUM, HIGH, or CRITICAL.
            </p>
          </div>

          {/* Agent 5 */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-brand-300 transition shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">Agent 5</span>
              <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">LLM Synthesis</span>
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Review Summary Agent</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Synthesizes grounded, clinical-grade narrative briefings for human pharmacists without hallucination.
            </p>
          </div>

          {/* Decision Gate */}
          <div className="bg-slate-900 text-white p-5 rounded-2xl border border-slate-800 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-brand-400 font-mono">Gate 6</span>
              <span className="text-[10px] font-semibold text-brand-400 bg-brand-950 px-2 py-0.5 rounded-full border border-brand-800">Deterministic Guard</span>
            </div>
            <h3 className="font-bold text-white text-sm">Central Decision Gate</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Dispatches APPROVED, REJECTED, or ON_HOLD with SHA-256 tamper-evident immutable audit log entries.
            </p>
          </div>
        </div>
      </section>

      {/* Role Portal Cards */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Explore System Portals</h2>
          <p className="text-sm text-slate-500 mt-1">Experience MedLock AI from all four distinct healthcare stakeholder viewpoints.</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/patient"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-brand-500 hover:shadow-md transition space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <User className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900">Patient Portal</h3>
            <p className="text-xs text-slate-500">View active prescriptions, remaining quantity gauges, and warning alerts.</p>
            <div className="flex items-center gap-1 text-xs font-semibold text-brand-600">
              <span>Open Portal</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link
            href="/doctor"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Stethoscope className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900">Doctor Portal</h3>
            <p className="text-xs text-slate-500">Create digital prescriptions, sign cryptographically, and generate QR codes.</p>
            <div className="flex items-center gap-1 text-xs font-semibold text-blue-600">
              <span>Open Portal</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link
            href="/pharmacy"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-purple-500 hover:shadow-md transition space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Building2 className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900">Pharmacy Portal</h3>
            <p className="text-xs text-slate-500">Scan QR codes, trigger real-time AI evaluation, and submit authorized dispensing.</p>
            <div className="flex items-center gap-1 text-xs font-semibold text-purple-600">
              <span>Open Portal</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link
            href="/admin"
            className="group bg-white p-6 rounded-2xl border border-slate-200 hover:border-amber-500 hover:shadow-md transition space-y-3"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900">Admin & Review</h3>
            <p className="text-xs text-slate-500">Triage held transactions, review clinical summaries, and inspect SHA-256 audit logs.</p>
            <div className="flex items-center gap-1 text-xs font-semibold text-amber-600">
              <span>Open Portal</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </div>
      </section>

    </div>
  );
}
