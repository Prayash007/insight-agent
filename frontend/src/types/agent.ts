export interface TraceStep {
  step_id: string;
  node: string;
  title: string;
  status: 'running' | 'completed' | 'failed' | 'retrying';
  timestamp: string;
  elapsed_ms: number;
  details?: Record<string, any>;
}

export interface KPICard {
  label: string;
  value: string;
  delta?: string;
  status?: 'positive' | 'negative' | 'neutral';
}

export interface ChartConfig {
  chart_type: 'line' | 'bar' | 'stacked_bar' | 'area' | 'kpi_grid';
  title: string;
  x_key?: string;
  y_keys?: string[];
  series_labels?: Record<string, string>;
  kpi_cards?: KPICard[];
  data?: Record<string, any>[];
}

export interface QueryResponse {
  query_id: string;
  user_query: string;
  intent: string;
  narrative_summary: string;
  chart_config?: ChartConfig;
  generated_sql: string[];
  trace: TraceStep[];
  analytics_summary: Record<string, any>;
}

export interface MetricDefinition {
  name: string;
  description: string;
  formula: string;
  sql_expression?: string;
  tables: string[];
  unit: string;
  dimensions: string[];
  synonyms: string[];
}
