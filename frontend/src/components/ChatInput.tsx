import React, { useState } from 'react';
import { Send, Sparkles, TrendingDown, AlertTriangle, Calendar, PieChart, Layers } from 'lucide-react';

interface ChatInputProps {
  onSubmit: (query: string) => void;
  disabled?: boolean;
}

const PRESET_QUERIES = [
  {
    icon: TrendingDown,
    label: "August F&O Drop",
    query: "Why did F&O volume drop in August?",
    highlight: "text-amber-400"
  },
  {
    icon: AlertTriangle,
    label: "Aug 14 RMS Spike",
    query: "What caused the spike in RMS margin rejections on August 14?",
    highlight: "text-rose-400"
  },
  {
    icon: Calendar,
    label: "Thursday Expiry",
    query: "Compare Thursday expiry turnover against other weekdays",
    highlight: "text-emerald-400"
  },
  {
    icon: Layers,
    label: "Fill Rate by Type",
    query: "What is our order fill rate broken down by order type?",
    highlight: "text-cyan-400"
  },
  {
    icon: PieChart,
    label: "Brokerage Yield (bps)",
    query: "Analyze net brokerage yield in bps by market segment",
    highlight: "text-purple-400"
  }
];

export const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSubmit(input.trim());
  };

  const handleSelectPreset = (q: string) => {
    setInput(q);
    onSubmit(q);
  };

  return (
    <div className="w-full space-y-3">
      {/* Quick Suggestion Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-semibold whitespace-nowrap pl-1">
          <Sparkles className="w-3.5 h-3.5 text-orange-400" /> Key Investigations:
        </span>
        {PRESET_QUERIES.map((preset, idx) => {
          const Icon = preset.icon;
          return (
            <button
              key={idx}
              onClick={() => handleSelectPreset(preset.query)}
              disabled={disabled}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800/90 hover:bg-slate-700/90 border border-slate-700/60 text-slate-300 hover:text-white transition-all whitespace-nowrap disabled:opacity-50"
            >
              <Icon className={`w-3 h-3 ${preset.highlight}`} />
              <span>{preset.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask an analytical question in plain English (e.g., 'Why did F&O volume drop in August?')..."
          disabled={disabled}
          className="w-full px-5 py-4 pr-14 rounded-2xl bg-slate-900/90 border border-slate-700/80 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 text-white placeholder-slate-500 shadow-2xl transition-all outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white shadow-md shadow-orange-600/30 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          {disabled ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </form>
    </div>
  );
};
