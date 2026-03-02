import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalysis, AnalysisDetail } from '../api/client';
import { Loader2, AlertCircle } from 'lucide-react';
import LanguagePieChart from '../components/LanguagePieChart';
import ContributorRanking from '../components/ContributorRanking';
import MetricsGrid from '../components/MetricsGrid';
import AIInsightsPanel from '../components/AIInsightsPanel';
import CommitFrequencyChart from '../components/CommitFrequencyChart';

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;

    const poll = async () => {
      try {
        const data = await getAnalysis(id);
        setAnalysis(data);

        // Keep polling if not yet complete
        if (data.status === 'pending' || data.status === 'in_progress') {
          setTimeout(poll, 3000);
        } else {
          setLoading(false);
        }
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch analysis');
        setLoading(false);
      }
    };

    poll();
  }, [id]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="glass p-8 text-center max-w-sm">
          <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
          <p className="text-slate-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!analysis || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="glass p-10 text-center">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400 text-sm">
            {analysis?.status === 'in_progress'
              ? 'Analyzing repository...'
              : 'Loading analysis...'}
          </p>
        </div>
      </div>
    );
  }

  if (analysis.status === 'failed') {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="glass p-8 text-center max-w-sm">
          <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
          <p className="text-slate-700 text-sm font-medium mb-1">Analysis failed</p>
          <p className="text-slate-400 text-xs">{analysis.error_message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gradient mb-1">Analysis Results</h2>
        <p className="text-slate-400 text-sm">
          {analysis.commits_count} commits &middot;{' '}
          {analysis.completed_at
            ? new Date(analysis.completed_at).toLocaleString()
            : ''}
        </p>
      </div>

      {/* Metrics */}
      <MetricsGrid metrics={analysis.metrics} />

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <LanguagePieChart distribution={analysis.metrics.language_distribution} />
        <CommitFrequencyChart data={analysis.metrics.commits_per_date} />
      </div>

      {/* Contributors */}
      <ContributorRanking contributors={analysis.contributors} />

      {/* AI Insights */}
      <AIInsightsPanel insights={analysis.ai_insights} />
    </div>
  );
}
