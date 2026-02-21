import { AIInsights } from '../api/client';
import { Brain, FileText, Layers, Wrench } from 'lucide-react';

interface Props {
  insights: AIInsights;
}

export default function AIInsightsPanel({ insights }: Props) {
  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-white flex items-center gap-2">
        <Brain className="w-6 h-6 text-purple-400" />
        AI-Powered Insights
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Project Summary */}
        <div className="p-5 bg-gray-900 border border-gray-800 rounded-xl">
          <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-400" />
            Project Summary
          </h4>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
            {insights.ai_summary || 'Not available'}
          </p>
        </div>

        {/* Architecture Analysis */}
        <div className="p-5 bg-gray-900 border border-gray-800 rounded-xl">
          <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-green-400" />
            Architecture Analysis
          </h4>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
            {insights.architecture_analysis || 'Not available'}
          </p>
        </div>

        {/* README Quality */}
        <div className="p-5 bg-gray-900 border border-gray-800 rounded-xl">
          <h4 className="text-white font-semibold mb-3">README Quality</h4>
          {insights.readme_quality_score !== null && (
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl font-bold text-white">
                {insights.readme_quality_score.toFixed(1)}
              </div>
              <div className="text-gray-400 text-sm">/10</div>
              <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${(insights.readme_quality_score / 10) * 100}%`,
                    backgroundColor:
                      insights.readme_quality_score >= 7
                        ? '#34d399'
                        : insights.readme_quality_score >= 4
                        ? '#fbbf24'
                        : '#f87171',
                  }}
                />
              </div>
            </div>
          )}
          <p className="text-gray-300 text-sm leading-relaxed">
            {insights.readme_quality_feedback || 'Not available'}
          </p>
        </div>

        {/* Tech Stack */}
        <div className="p-5 bg-gray-900 border border-gray-800 rounded-xl">
          <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Wrench className="w-4 h-4 text-orange-400" />
            Detected Tech Stack
          </h4>
          {insights.detected_tech_stack.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {insights.detected_tech_stack.map((tech) => (
                <span
                  key={tech}
                  className="px-3 py-1 bg-gray-800 border border-gray-700 rounded-full
                             text-gray-300 text-xs font-medium"
                >
                  {tech}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Not available</p>
          )}
        </div>
      </div>
    </div>
  );
}
