import { useState, useCallback } from 'react';
import { QueryResponse, TraceStep } from '../types/agent';

export function useAgentStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState<QueryResponse | null>(null);
  const [liveTrace, setLiveTrace] = useState<TraceStep[]>([]);
  const [error, setError] = useState<string | null>(null);

  const executeQuery = useCallback(async (query: string) => {
    setIsStreaming(true);
    setError(null);
    setLiveTrace([]);
    setCurrentResponse(null);

    try {
      // Use SSE streaming reader
      const streamUrl = `/api/stream?q=${encodeURIComponent(query)}`;
      const response = await fetch(streamUrl);

      if (!response.ok || !response.body) {
        // Fallback to synchronous POST if streaming not available
        const postResp = await fetch('/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query }),
        });
        if (!postResp.ok) throw new Error(`Query failed: ${postResp.statusText}`);
        const data: QueryResponse = await postResp.json();
        setCurrentResponse(data);
        setLiveTrace(data.trace || []);
        setIsStreaming(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const evt of events) {
          if (!evt.trim()) continue;
          const lines = evt.split('\n');
          let eventType = '';
          let dataStr = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.replace('event: ', '').trim();
            } else if (line.startsWith('data: ')) {
              dataStr = line.replace('data: ', '').trim();
            }
          }

          if (eventType === 'trace_step') {
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.step) {
                setLiveTrace((prev) => [...prev, parsed.step]);
              }
            } catch (e) {
              console.error('Error parsing trace_step:', e);
            }
          } else if (eventType === 'result') {
            try {
              const finalData: QueryResponse = JSON.parse(dataStr);
              setCurrentResponse(finalData);
            } catch (e) {
              console.error('Error parsing result:', e);
            }
          }
        }
      }
    } catch (err: any) {
      console.error('Execution error:', err);
      setError(err.message || 'Failed to execute query');
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return {
    isStreaming,
    currentResponse,
    liveTrace,
    error,
    executeQuery,
  };
}
