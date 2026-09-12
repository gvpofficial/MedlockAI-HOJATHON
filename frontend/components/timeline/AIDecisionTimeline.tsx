'use client';

import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Info, 
  Cpu, 
  Scale, 
  Activity, 
  FileText, 
  ShieldCheck, 
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { MultiAgentEvaluationResult, DecisionTimelineStep } from '@/types';
import { getRiskLevelColor, getStatusBadge } from '@/lib/utils';

interface AIDecisionTimelineProps {
  evaluation: MultiAgentEvaluationResult | null;
  isLoading?: boolean;
}

export default function AIDecisionTimeline({ evaluation, isLoading }: AIDecisionTimelineProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-brand-50 border border-brand-200 mb-4 animate-spin">
          <Cpu className="w-8 h-8 text-brand-600" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 mb-1">Evaluating Multi-Agent Integrity Pipeline...</h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto">
          Agent 1 verifying prescription ➔ Agent 2 checking central ledger ➔ Agent 3 analyzing multi-pharmacy velocity ➔ Agent 4 computing transparent risk score.
        </p>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-8 text-center text-slate-400">
        <Cpu className="w-10 h-10 mx-auto mb-2 opacity-40" />
        <p className="text-sm font-medium">No active dispensing request evaluated yet.</p>
        <p className="text-xs text-slate-400 mt-1">Submit a prescription scan or trigger a demo scenario above.</p>
      </div>
    );
  }

  const getStepIcon = (status: string, stepNumber: number) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
      case 'WARNING':
        return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'DANGER':
        return <XCircle className="w-5 h-5 text-rose-600" />;
      case 'INFO':
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getStepBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'WARNING':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'DANGER':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'INFO':
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  const riskColors = getRiskLevelColor(evaluation.risk_level, evaluation.risk_score);
  const decisionBadge = getStatusBadge(evaluation.decision);

  return (
    <div className="bg-white rounded-3xl border border-slate-200/90 shadow-lg overflow-hidden">
      {/* Top Banner: Final Disposition & Score */}
      <div className="bg-slate-900 text-white p-6 border-b border-slate-800">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 uppercase tracking-widest mb-1">
              <Cpu className="w-4 h-4" />
              <span>Multi-Agent Orchestration Engine</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight">Prescription Dispensing Evaluation</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Rx: <span className="font-mono text-slate-200">{evaluation.prescription_code}</span> | Medicine: <span className="text-slate-200">{evaluation.medicine_name}</span> | Requested: <span className="font-semibold text-white">{evaluation.requested_quantity} units</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Risk Score Pill */}
            <div className="bg-slate-800/90 rounded-2xl border border-slate-700 p-3 text-right">
              <div className="text-[10px] uppercase font-bold text-slate-400">Risk Score</div>
              <div className="flex items-baseline gap-1.5 justify-end">
                <span className="text-2xl font-black text-white">{evaluation.risk_score}</span>
                <span className="text-xs text-slate-400">/ 100</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${riskColors.bg} ${riskColors.text} ${riskColors.border}`}>
                  {evaluation.risk_level}
                </span>
              </div>
            </div>

            {/* Final Disposition */}
            <div className="bg-slate-800/90 rounded-2xl border border-slate-700 p-3 text-right min-w-[140px]">
              <div className="text-[10px] uppercase font-bold text-slate-400">Disposition</div>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 mt-1 rounded-xl text-xs font-bold border ${decisionBadge.bg}`}>
                <span className={`w-2 h-2 rounded-full ${decisionBadge.dot}`} />
                {decisionBadge.label}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Body: Step-by-Step AI Decision Timeline */}
      <div className="p-6 md:p-8 space-y-6">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-600" />
          Agentic Decision Pipeline Steps
        </h3>

        <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
          {evaluation.timeline.map((step, idx) => (
            <div key={idx} className="relative group">
              {/* Step indicator dot */}
              <div className="absolute -left-[30px] top-1 bg-white rounded-full p-1 border border-slate-200 shadow-sm group-hover:scale-110 transition-transform">
                {getStepIcon(step.status, step.step_number)}
              </div>

              {/* Step Content Box */}
              <div className={`p-4 rounded-2xl border transition-all ${
                step.status === 'DANGER' ? 'bg-rose-50/50 border-rose-200' :
                step.status === 'WARNING' ? 'bg-amber-50/50 border-amber-200' :
                step.status === 'SUCCESS' ? 'bg-emerald-50/30 border-slate-200' :
                'bg-slate-50 border-slate-200'
              }`}>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-200/80 text-slate-700 font-mono">
                      Step {step.step_number}
                    </span>
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-tight">
                      {step.agent_name}
                    </span>
                  </div>
                  <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${getStepBadge(step.status)}`}>
                    {step.status}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-900 mb-1">{step.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{step.description}</p>

                {/* Extra Data Badges for Key Steps */}
                {step.step_number === 2 && (
                  <div className="mt-3 grid grid-cols-4 gap-2 pt-2 border-t border-slate-200/70 text-center">
                    <div className="bg-white p-2 rounded-xl border border-slate-200">
                      <div className="text-[10px] text-slate-400 font-medium">Authorized</div>
                      <div className="text-sm font-bold text-slate-800">{evaluation.integrity.authorized_quantity}</div>
                    </div>
                    <div className="bg-white p-2 rounded-xl border border-slate-200">
                      <div className="text-[10px] text-slate-400 font-medium">Dispensed</div>
                      <div className="text-sm font-bold text-slate-800">{evaluation.integrity.dispensed_quantity}</div>
                    </div>
                    <div className="bg-white p-2 rounded-xl border border-slate-200">
                      <div className="text-[10px] text-slate-400 font-medium">Remaining</div>
                      <div className="text-sm font-bold text-emerald-600">{evaluation.integrity.remaining_quantity}</div>
                    </div>
                    <div className="bg-white p-2 rounded-xl border border-slate-200">
                      <div className="text-[10px] text-slate-400 font-medium">Requested</div>
                      <div className="text-sm font-bold text-brand-600">{evaluation.requested_quantity}</div>
                    </div>
                  </div>
                )}

                {step.step_number === 4 && evaluation.risk.risk_factors.length > 0 && (
                  <div className="mt-3 space-y-1.5 pt-2 border-t border-slate-200/70">
                    <div className="text-[11px] font-bold text-slate-600">Calculated Risk Factors:</div>
                    {evaluation.risk.risk_factors.map((factor, fIdx) => (
                      <div key={fIdx} className="flex items-center justify-between text-xs bg-white p-2 rounded-xl border border-slate-200 text-slate-700">
                        <span className="text-slate-700">{factor.description}</span>
                        <span className="font-mono font-bold text-orange-600">+{factor.score_addition} pts</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Agent 5: Clinical LLM Summary Briefing */}
        <div className="mt-6 p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-navy-900 text-white border border-slate-800">
          <div className="flex items-center gap-2 text-xs font-bold text-brand-400 uppercase tracking-wider mb-2">
            <FileText className="w-4 h-4" />
            <span>Agent 5: Synthesized Pharmacist Briefing</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-3">
            "{evaluation.summary.clinical_summary}"
          </p>
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800 text-[11px] text-slate-400">
            <span className="font-semibold text-slate-300">Evidence Base:</span>
            {evaluation.summary.key_evidence.map((ev, eIdx) => (
              <span key={eIdx} className="bg-slate-800 px-2 py-0.5 rounded-md border border-slate-700 text-slate-300">
                • {ev}
              </span>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
