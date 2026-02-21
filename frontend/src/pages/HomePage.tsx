import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeRepo } from '../api/client';
import { Search, GitBranch, Loader2 } from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const parts = input.trim().split('/');
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      setError('Please enter in format: owner/repo');
      return;
    }

    setLoading(true);
    try {
      const result = await analyzeRepo(parts[0], parts[1]);
      navigate(`/analysis/${result.analysis_id}`);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to start analysis');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="text-center mb-10">
        <GitBranch className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
        <h2 className="text-4xl font-bold text-white mb-3">
          Analyze Any GitHub Repository
        </h2>
        <p className="text-gray-400 text-lg max-w-xl mx-auto">
          Get deep code metrics, contributor analytics, language breakdowns,
          and AI-powered insights for any public repository.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-lg">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="owner/repo  (e.g. facebook/react)"
              className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg
                         text-white placeholder-gray-500 focus:outline-none focus:ring-2
                         focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium
                       rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyze'}
          </button>
        </div>
        {error && (
          <p className="mt-3 text-red-400 text-sm">{error}</p>
        )}
      </form>

      <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl">
        {[
          { title: 'Code Metrics', desc: 'Commit frequency, churn, bus factor' },
          { title: 'Visualizations', desc: 'Heatmaps, charts, rankings' },
          { title: 'AI Insights', desc: 'Project summary, architecture review' },
        ].map((card) => (
          <div
            key={card.title}
            className="p-5 bg-gray-900 border border-gray-800 rounded-xl text-center"
          >
            <h3 className="text-white font-semibold mb-1">{card.title}</h3>
            <p className="text-gray-400 text-sm">{card.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
