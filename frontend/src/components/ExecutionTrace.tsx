import React, { useState } from 'react';
import { TraceStep } from '../types/agent';
import { CheckCircle2, Clock, ChevronDown, ChevronRight, RefreshCw, AlertCircle, Layers } from 'lucide-react';

interface ExecutionTraceProps {
  trace: TraceStep[];
  isStreaming?: boolean;
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ trace, isStreaming }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!trace || trace.length === 0) return null;

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  const totalElapsed = trace.reduce((acc, step) => acc + (step.elapsed_ms || 0), 0);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-orange-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            LangGraph Execution Trace
          </span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-[10px] text-amber-400 font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 animate-pulse">
              <RefreshCw className="w-2.5 h-2.5 animate-spin" /> Live State
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{totalElapsed.toFixed(0)} ms total</span>
        </div>
      </div>

      <div className="space-y-2">
        {trace.map((step, idx) => {
          const isExpanded = expandedIndex === idx;
          const isRetry = step.title.toLowerCase().includes('retry') || step.title.toLowerCase().includes('self-correction');

          return (
            <div
              key={step.step_id || idx}
              className="rounded-xl border border-slate-800/80 bg-slate-950/40 overflow-hidden text-xs transition-all"
            >
              <div
                onClick={() => toggleExpand(idx)}
                className="flex items-center justify-between px-3.5 py-2.5 cursor-pointer hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  {step.status === 'completed' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : step.status === 'failed' ? (
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  ) : (
                    <RefreshCw className="w-4 h-4 text-amber-400 animate-spin shrink-0" />
                  )}

                  <span className="font-semibold text-slate-200">{step.title}</span>

                  {isRetry && (
                    <span className="px-1.5 py-0.5 text-[10px] rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                      REPAIR LOOP
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-400 font-mono">{step.elapsed_ms?.toFixed(1)} ms</span>
                  {isExpanded ? (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && step.details && (
                <div className="px-3.5 py-2.5 bg-slate-950 border-t border-slate-800/60 font-mono text-[11px] text-slate-300 overflow-x-auto">
                  <pre className="whitespace-pre-wrap">{JSON.stringify(step.details, null, 2)}</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
