import React, { useState } from 'react';
import { ChartConfig, KPICard } from '../types/agent';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { TrendingUp, TrendingDown, Table, BarChart2 } from 'lucide-react';

interface ChartRendererProps {
  config?: ChartConfig;
}

const PALETTE = ['#FF5722', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

export const ChartRenderer: React.FC<ChartRendererProps> = ({ config }) => {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');

  if (!config) return null;

  const { chart_type, title, x_key, y_keys = [], series_labels = {}, kpi_cards = [], data = [] } = config;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-5">
      {/* KPI Cards Grid */}
      {kpi_cards.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {kpi_cards.map((kpi, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col justify-between"
            >
              <span className="text-xs font-semibold text-slate-400">{kpi.label}</span>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-xl font-extrabold text-white font-mono">{kpi.value}</span>
                {kpi.delta && (
                  <span
                    className={`text-xs font-bold flex items-center gap-0.5 ${
                      kpi.status === 'positive'
                        ? 'text-emerald-400'
                        : kpi.status === 'negative'
                        ? 'text-rose-400'
                        : 'text-slate-400'
                    }`}
                  >
                    {kpi.status === 'positive' ? (
                      <TrendingUp className="w-3.5 h-3.5" />
                    ) : kpi.status === 'negative' ? (
                      <TrendingDown className="w-3.5 h-3.5" />
                    ) : null}
                    {kpi.delta}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Chart Header & Controls */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-slate-200">{title}</h3>
        {data.length > 0 && (
          <div className="flex items-center gap-1 p-0.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <button
              onClick={() => setViewMode('chart')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all ${
                viewMode === 'chart' ? 'bg-orange-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5" /> Chart
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all ${
                viewMode === 'table' ? 'bg-orange-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Table className="w-3.5 h-3.5" /> Table
            </button>
          </div>
        )}
      </div>

      {/* Chart or Table Body */}
      {data.length > 0 && viewMode === 'chart' && (
        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            {chart_type === 'line' ? (
              <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey={x_key} stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                {y_keys.map((yCol, idx) => (
                  <Line
                    key={yCol}
                    type="monotone"
                    dataKey={yCol}
                    name={series_labels[yCol] || yCol}
                    stroke={PALETTE[idx % PALETTE.length]}
                    strokeWidth={2.5}
                    dot={{ r: 3 }}
                  />
                ))}
              </LineChart>
            ) : chart_type === 'area' ? (
              <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey={x_key} stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                {y_keys.map((yCol, idx) => (
                  <Area
                    key={yCol}
                    type="monotone"
                    dataKey={yCol}
                    name={series_labels[yCol] || yCol}
                    stroke={PALETTE[idx % PALETTE.length]}
                    fill={PALETTE[idx % PALETTE.length]}
                    fillOpacity={0.2}
                  />
                ))}
              </AreaChart>
            ) : (
              <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey={x_key} stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                {y_keys.map((yCol, idx) => (
                  <Bar
                    key={yCol}
                    dataKey={yCol}
                    name={series_labels[yCol] || yCol}
                    fill={PALETTE[idx % PALETTE.length]}
                    radius={[4, 4, 0, 0]}
                  />
                ))}
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      )}

      {/* Table Mode */}
      {data.length > 0 && viewMode === 'table' && (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-800/80 text-slate-300 border-b border-slate-700">
              <tr>
                {Object.keys(data[0]).map((col) => (
                  <th key={col} className="px-4 py-2.5 font-bold uppercase tracking-wider">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-slate-800/30 transition-colors">
                  {Object.values(row).map((val: any, cIdx) => (
                    <td key={cIdx} className="px-4 py-2 text-slate-200">
                      {typeof val === 'number' ? val.toLocaleString() : String(val)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
