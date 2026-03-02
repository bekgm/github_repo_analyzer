import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeRepo } from '../api/client';
import { Search, Loader2, ArrowRight, BarChart3, Brain, GitFork } from 'lucide-react';

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
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      {/* Hero */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-sm text-xs text-slate-500 mb-6 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft" />
          Powered by Gemini AI
        </div>
        <h2 className="text-5xl font-bold text-gradient mb-4 leading-tight">
          Analyze Any Repository
        </h2>
        <p className="text-slate-400 text-lg max-w-md mx-auto font-light leading-relaxed">
          Deep code metrics, contributor analytics, and AI-powered insights
          for any public GitHub repo.
        </p>
      </div>

      {/* Search */}
      <form onSubmit={handleSubmit} className="w-full max-w-xl mb-16">
        <div className="glass p-2 flex gap-2 glow-purple">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="owner/repo"
              className="w-full pl-11 pr-4 py-3 bg-transparent text-slate-700 placeholder-slate-300
                         focus:outline-none text-sm"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600
                       text-white text-sm font-medium rounded-[14px] transition-all 
                       disabled:opacity-40 disabled:cursor-not-allowed
                       flex items-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                Analyze
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
        {error && (
          <p className="mt-3 text-red-500/80 text-xs text-center">{error}</p>
        )}
      </form>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl">
        {[
          { icon: BarChart3, title: 'Code Metrics', desc: 'Commit frequency, churn, bus factor', color: 'text-indigo-500' },
          { icon: GitFork, title: 'Visualizations', desc: 'Charts, timelines, rankings', color: 'text-violet-500' },
          { icon: Brain, title: 'AI Insights', desc: 'Summary, architecture & tech stack', color: 'text-emerald-500' },
        ].map((card) => (
          <div
            key={card.title}
            className="glass-sm glass-hover p-6 text-center"
          >
            <card.icon className={`w-5 h-5 ${card.color} mx-auto mb-3 opacity-70`} />
            <h3 className="text-slate-700 text-sm font-semibold mb-1">{card.title}</h3>
            <p className="text-slate-400 text-xs">{card.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
