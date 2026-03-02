import { AIInsights } from '../api/client';
import { Sparkles, FileText, Layers, Wrench } from 'lucide-react';

interface Props {
  insights: AIInsights;
}

export default function AIInsightsPanel({ insights }: Props) {
  return (
    <div className="space-y-5">
      <h3 className="text-white/70 text-sm font-medium flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-violet-400/60" />
        AI Insights
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Project Summary */}
        <div className="glass p-5">
          <h4 className="text-white/50 text-xs font-medium mb-3 flex items-center gap-2 uppercase tracking-wider">
            <FileText className="w-3.5 h-3.5 text-blue-400/50" />
            Summary
          </h4>
          <p className="text-white/40 text-sm leading-relaxed whitespace-pre-wrap">
            {insights.ai_summary || 'Not available'}
          </p>
        </div>

        {/* Architecture Analysis */}
        <div className="glass p-5">
          <h4 className="text-white/50 text-xs font-medium mb-3 flex items-center gap-2 uppercase tracking-wider">
            <Layers className="w-3.5 h-3.5 text-emerald-400/50" />
            Architecture
          </h4>
          <p className="text-white/40 text-sm leading-relaxed whitespace-pre-wrap">
            {insights.architecture_analysis || 'Not available'}
          </p>
        </div>

        {/* README Quality */}
        <div className="glass p-5">
          <h4 className="text-white/50 text-xs font-medium mb-3 uppercase tracking-wider">
            README Quality
          </h4>
          {insights.readme_quality_score !== null && (
            <div className="flex items-center gap-3 mb-3">
              <div className="text-2xl font-semibold text-white/80 tabular-nums">
                {insights.readme_quality_score.toFixed(1)}
              </div>
              <div className="text-white/20 text-xs">/10</div>
              <div className="flex-1 h-1 bg-white/[0.04] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${(insights.readme_quality_score / 10) * 100}%`,
                    background:
                      insights.readme_quality_score >= 7
                        ? 'linear-gradient(90deg, rgba(52,211,153,0.6), rgba(52,211,153,0.3))'
                        : insights.readme_quality_score >= 4
                        ? 'linear-gradient(90deg, rgba(250,204,21,0.6), rgba(250,204,21,0.3))'
                        : 'linear-gradient(90deg, rgba(248,113,113,0.6), rgba(248,113,113,0.3))',
                  }}
                />
              </div>
            </div>
          )}
          <p className="text-white/40 text-sm leading-relaxed">
            {insights.readme_quality_feedback || 'Not available'}
          </p>
        </div>

        {/* Tech Stack */}
        <div className="glass p-5">
          <h4 className="text-white/50 text-xs font-medium mb-3 flex items-center gap-2 uppercase tracking-wider">
            <Wrench className="w-3.5 h-3.5 text-orange-400/50" />
            Tech Stack
          </h4>
          {insights.detected_tech_stack.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {insights.detected_tech_stack.map((tech) => (
                <span
                  key={tech}
                  className="px-2.5 py-1 glass-sm text-white/40 text-xs"
                >
                  {tech}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-white/20 text-sm">Not available</p>
          )}
        </div>
      </div>
    </div>
  );
}
