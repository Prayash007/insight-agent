import React, { useState } from 'react';
import { Terminal, ShieldCheck, Copy, Check, Eye } from 'lucide-react';

interface SQLViewerProps {
  queries: string[];
}

export const SQLViewer: React.FC<SQLViewerProps> = ({ queries }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!queries || queries.length === 0) return null;

  const handleCopy = (sql: string, idx: number) => {
    navigator.clipboard.writeText(sql);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Validated SQL Queries ({queries.length})
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <ShieldCheck className="w-3 h-3" /> AST Verified
          </span>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
            LIMIT 500
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {queries.map((sql, idx) => (
          <div key={idx} className="relative rounded-xl border border-slate-800 bg-slate-950 p-3.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-2">
              <span className="font-semibold text-slate-400">Query #{idx + 1}</span>
              <button
                onClick={() => handleCopy(sql, idx)}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              >
                {copiedIndex === idx ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" /> Copy
                  </>
                )}
              </button>
            </div>
            <pre className="font-mono text-xs text-emerald-300/90 whitespace-pre-wrap overflow-x-auto leading-relaxed">
              {sql.trim()}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
};
