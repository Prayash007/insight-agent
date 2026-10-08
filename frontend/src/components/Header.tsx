import React from 'react';
import { Activity, Database, BookOpen, ShieldCheck, Cpu } from 'lucide-react';

interface HeaderProps {
  onOpenMetrics: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenMetrics }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center shadow-lg shadow-orange-500/20 font-bold text-white text-xl">
            IA
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight text-white">InsightAgent</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">
                Angel One Edition
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Capital Markets AI Analyst • LangGraph & MCP</p>
          </div>
        </div>

        {/* Live Architecture Status Indicators */}
        <div className="hidden md:flex items-center gap-5 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>250k Trades Seeded</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span>MCP SSE Server Active</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60">
            <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
            <span>AST sqlglot Guardrails</span>
          </div>

          <button
            onClick={onOpenMetrics}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 border border-orange-500/30 font-medium transition-all"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Semantic Catalog</span>
          </button>
        </div>
      </div>
    </header>
  );
};
