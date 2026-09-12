'use client';

import React, { useState, useEffect } from 'react';
import { 
  PlayCircle, 
  RotateCcw, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Code, 
  Sparkles,
  Layers,
  ArrowRight,
  ShieldCheck,
  Building2
} from 'lucide-react';
import { api } from '@/lib/api';
import { DemoScenario, MultiAgentEvaluationResult } from '@/types';
import AIDecisionTimeline from '@/components/timeline/AIDecisionTimeline';

export default function DemoArenaPage() {
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [activeScenarioId, setActiveScenarioId] = useState<string>('scenario-1');
  const [evaluationResult, setEvaluationResult] = useState<MultiAgentEvaluationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
    // Auto-run Scenario 1 on load for instant visual punch
    runScenario('scenario-1');
  }, []);

  const loadScenarios = async () => {
    try {
      const res = await api.getDemoScenarios();
      setScenarios(res);
    } catch (err) {
      console.error(err);
    }
  };

  const runScenario = async (id: string) => {
    setActiveScenarioId(id);
    setIsRunning(true);
    setEvaluationResult(null);
    setResetMessage(null);
    try {
      const result = await api.executeDemoScenario(id);
      setEvaluationResult(result);
    } catch (err: any) {
      alert(err.message || 'Failed to execute scenario');
    } finally {
      setIsRunning(false);
    }
  };

  const handleResetDatabase = async () => {
    setIsResetting(true);
    try {
      const res = await api.resetSeedDatabase();
      setResetMessage(res.message || 'Database reset successfully!');
      // Re-run scenario 1
      runScenario(activeScenarioId);
    } catch (err: any) {
      alert(err.message || 'Failed to reset database');
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 text-white p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-400 text-xs font-semibold mb-1 border border-brand-500/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Hackathon Judge Demonstration Arena</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Live Scenario Validation Suite
          </h1>
          <p className="text-xs text-slate-400">
            1-Click triggers demonstrating hard quantity limits, cross-pharmacy velocity tracking, and AI review briefings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleResetDatabase}
            disabled={isResetting}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs border border-slate-700 transition disabled:opacity-50"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
            <span>{isResetting ? 'Resetting DB...' : 'Reset Demo Seed Data'}</span>
          </button>
        </div>
      </div>

      {resetMessage && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{resetMessage}</span>
        </div>
      )}

      {/* Scenario Selector Cards */}
      <div className="space-y-3">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Layers className="w-4 h-4 text-brand-600" />
          Select Demo Scenario to Trigger
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {scenarios.map((sc) => {
            const isActive = activeScenarioId === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => runScenario(sc.id)}
                disabled={isRunning}
                className={`p-4 rounded-2xl border text-left transition-all ${
                  isActive
                    ? 'bg-white border-brand-500 shadow-md ring-2 ring-brand-500/20'
                    : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-xs'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md font-mono ${
                    isActive ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {sc.id.toUpperCase()}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    sc.expected_outcome === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    sc.expected_outcome === 'REJECTED' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                    'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {sc.expected_outcome}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-xs mb-1 line-clamp-1">{sc.title}</h3>
                <p className="text-[11px] text-slate-500 line-clamp-2 mb-2">{sc.description}</p>

                <div className="text-[10px] font-mono text-slate-400 flex items-center justify-between pt-2 border-t border-slate-100">
                  <span>{sc.prescription_code}</span>
                  <span className="font-bold text-slate-700">{sc.risk_level}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Action Toolbar */}
      <div className="flex items-center justify-between">
        <div className="text-xs text-slate-500 font-medium">
          Currently Evaluating: <strong className="text-slate-900 font-mono">{activeScenarioId}</strong>
        </div>

        <button
          onClick={() => setShowJson(!showJson)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition"
        >
          <Code className="w-3.5 h-3.5 text-slate-500" />
          <span>{showJson ? 'Hide Raw Agent JSON' : 'Inspect Raw Agent JSON'}</span>
        </button>
      </div>

      {/* Raw JSON Debug Box for Judges */}
      {showJson && evaluationResult && (
        <div className="bg-slate-900 rounded-3xl p-6 border border-slate-800 text-slate-200 text-xs font-mono overflow-x-auto">
          <div className="text-xs font-bold text-brand-400 mb-2 font-sans flex items-center gap-2">
            <Code className="w-4 h-4" />
            <span>Agent Orchestrator JSON Response Payload</span>
          </div>
          <pre className="text-[11px] leading-relaxed text-emerald-300">
            {JSON.stringify(evaluationResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Live AI Decision Timeline */}
      <AIDecisionTimeline evaluation={evaluationResult} isLoading={isRunning} />

    </div>
  );
}
