import React, { useEffect, useState } from 'react';
import { X, BookOpen, Database, Calculator, Layers } from 'lucide-react';
import { MetricDefinition } from '../types/agent';

interface MetricsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MetricsDrawer: React.FC<MetricsDrawerProps> = ({ isOpen, onClose }) => {
  const [metrics, setMetrics] = useState<Record<string, MetricDefinition>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && Object.keys(metrics).length === 0) {
      setLoading(true);
      const apiBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
      fetch(`${apiBase}/api/metrics`)
        .then((res) => res.json())
        .then((data) => {
          setMetrics(data.metrics || {});
          setLoading(false);
        })
        .catch((err) => {
          console.error('Failed to load metrics:', err);
          setLoading(false);
        });
    }
  }, [isOpen, metrics]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/70 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <BookOpen className="w-5 h-5 text-orange-400" />
            <div>
              <h2 className="text-base font-bold text-white">Semantic Metrics Catalog</h2>
              <p className="text-xs text-slate-400">Certified business formulas (metrics.yaml)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-slate-400">
              <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            Object.entries(metrics).map(([key, m]) => (
              <div
                key={key}
                className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">{m.name}</h3>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20 font-bold">
                    {m.unit}
                  </span>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">{m.description}</p>

                <div className="space-y-1.5 font-mono text-xs">
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <Calculator className="w-3.5 h-3.5 text-blue-400" />
                    <span className="text-slate-400 font-semibold">Formula:</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-emerald-300 font-mono text-[11px] whitespace-pre-wrap">
                    {m.formula}
                  </div>
                </div>

                <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1">
                  <div className="flex items-center gap-1">
                    <Database className="w-3 h-3 text-slate-400" />
                    <span>Tables: {m.tables?.join(', ')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Layers className="w-3 h-3 text-slate-400" />
                    <span>Dimensions: {m.dimensions?.length || 0}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
