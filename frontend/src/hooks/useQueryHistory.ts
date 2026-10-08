import { useState, useEffect } from 'react';

export function useQueryHistory() {
  const [history, setHistory] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('insight_query_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const addQuery = (q: string) => {
    setHistory((prev) => {
      const updated = [q, ...prev.filter((item) => item !== q)].slice(0, 15);
      try {
        localStorage.setItem('insight_query_history', JSON.stringify(updated));
      } catch {}
      return updated;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem('insight_query_history');
    } catch {}
  };

  return { history, addQuery, clearHistory };
}
