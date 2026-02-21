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
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  if (!analysis || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh]">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
        <p className="text-gray-400">
          {analysis?.status === 'in_progress'
            ? 'Analyzing repository... This may take a minute.'
            : 'Loading analysis...'}
        </p>
      </div>
    );
  }

  if (analysis.status === 'failed') {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-400">Analysis failed</p>
          <p className="text-gray-500 text-sm mt-1">{analysis.error_message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Analysis Results</h2>
        <p className="text-gray-400 text-sm">
          {analysis.commits_count} commits analyzed &middot; Completed{' '}
          {analysis.completed_at
            ? new Date(analysis.completed_at).toLocaleString()
            : ''}
        </p>
      </div>

      {/* Metrics cards */}
      <MetricsGrid metrics={analysis.metrics} />

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
