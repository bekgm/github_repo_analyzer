import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Types ────────────────────────────────────────────────────────────────────

export interface AnalyzeResponse {
  analysis_id: string;
  repository_id: string;
  status: string;
  message: string;
}

export interface Contributor {
  username: string;
  total_commits: number;
  additions: number;
  deletions: number;
  first_commit_at: string | null;
  last_commit_at: string | null;
}

export interface DailyCommit {
  date: string;
  commits: number;
}

export interface Metrics {
  total_commits: number;
  avg_commit_size: number;
  commits_per_day: number;
  code_churn_additions: number;
  code_churn_deletions: number;
  avg_time_between_commits_hours: number;
  bus_factor: number;
  language_distribution: Record<string, number>;
  commits_per_date: DailyCommit[];
}

export interface AIInsights {
  ai_summary: string | null;
  readme_quality_score: number | null;
  readme_quality_feedback: string | null;
  detected_tech_stack: string[];
  architecture_analysis: string | null;
}

export interface AnalysisDetail {
  id: string;
  repository_id: string;
  status: string;
  error_message: string | null;
  metrics: Metrics;
  ai_insights: AIInsights;
  contributors: Contributor[];
  commits_count: number;
  created_at: string;
  completed_at: string | null;
}

// ── API Calls ────────────────────────────────────────────────────────────────

export async function analyzeRepo(owner: string, name: string): Promise<AnalyzeResponse> {
  const { data } = await api.post('/analyses/analyze', { owner, name });
  return data;
}

export async function getAnalysis(analysisId: string): Promise<AnalysisDetail> {
  const { data } = await api.get(`/analyses/${analysisId}`);
  return data;
}

export default api;
