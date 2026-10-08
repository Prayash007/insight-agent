import React, { useState } from 'react';
import { Header } from './components/Header';
import { ChatInput } from './components/ChatInput';
import { ExecutionTrace } from './components/ExecutionTrace';
import { ChartRenderer } from './components/ChartRenderer';
import { SQLViewer } from './components/SQLViewer';
import { MetricsDrawer } from './components/MetricsDrawer';
import { useAgentStream } from './hooks/useAgentStream';
import { Sparkles, Bot, AlertTriangle, ShieldCheck, Database, Layers } from 'lucide-react';

export const App: React.FC = () => {
  const { isStreaming, currentResponse, liveTrace, error, executeQuery } = useAgentStream();
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
      {/* Header */}
      <Header onOpenMetrics={() => setIsMetricsOpen(true)} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Prompt Input Section */}
        <section className="bg-slate-900/40 rounded-3xl border border-slate-800 p-5 shadow-xl backdrop-blur-sm">
          <ChatInput onSubmit={executeQuery} disabled={isStreaming} />
        </section>

        {/* Error Banner */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Live Streaming Trace Accordion */}
        {isStreaming && (
          <section className="animate-in fade-in duration-300">
            <ExecutionTrace trace={liveTrace} isStreaming={true} />
          </section>
        )}

        {/* Results Workspace */}
        {currentResponse && !isStreaming && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Dynamic Charts & KPI Cards */}
            {currentResponse.chart_config && (
              <section>
                <ChartRenderer config={currentResponse.chart_config} />
              </section>
            )}

            {/* Executive Briefing Card */}
            {currentResponse.narrative_summary && (
              <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-orange-400 border-b border-slate-800 pb-2.5">
                  <Bot className="w-4 h-4" /> Executive Synthesis
                </div>
                <div className="prose prose-invert prose-sm max-w-none text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                  {currentResponse.narrative_summary}
                </div>
              </section>
            )}

            {/* Side-by-Side: Execution Trace & AST-Validated SQL */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <ExecutionTrace trace={currentResponse.trace} isStreaming={false} />
              <SQLViewer queries={currentResponse.generated_sql} />
            </div>
          </div>
        )}

        {/* Welcome / Empty State */}
        {!currentResponse && !isStreaming && (
          <div className="py-14 text-center max-w-2xl mx-auto space-y-5">
            <div className="w-16 h-16 mx-auto rounded-3xl bg-gradient-to-tr from-orange-500/20 to-amber-500/10 border border-orange-500/30 flex items-center justify-center text-orange-400 shadow-xl shadow-orange-500/5">
              <Sparkles className="w-8 h-8" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                Autonomous Capital Markets AI Data Analyst
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                InsightAgent turns plain-English business inquiries into certified calculations, multi-dimensional root-cause breakdowns, and interactive visualizations.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 text-left">
              <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-orange-400">
                  <Database className="w-3.5 h-3.5" /> Semantic Catalog
                </div>
                <p className="text-[11px] text-slate-400">Strict YAML formulas eliminate arithmetic and SQL hallucination.</p>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-blue-400">
                  <ShieldCheck className="w-3.5 h-3.5" /> AST Guardrails
                </div>
                <p className="text-[11px] text-slate-400">sqlglot enforces read-only SELECT, blocks catalogs, and injects limits.</p>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                  <Layers className="w-3.5 h-3.5" /> Deterministic Math
                </div>
                <p className="text-[11px] text-slate-400">All PoP variances and contribution % calculated via Pandas.</p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Slide-over Semantic Metrics Drawer */}
      <MetricsDrawer isOpen={isMetricsOpen} onClose={() => setIsMetricsOpen(false)} />
    </div>
  );
};

export default App;
