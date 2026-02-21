import { Metrics } from '../api/client';
import { GitCommit, Clock, Users, TrendingUp, FileDiff, AlertTriangle } from 'lucide-react';

interface Props {
  metrics: Metrics;
}

export default function MetricsGrid({ metrics }: Props) {
  const cards = [
    {
      label: 'Total Commits',
      value: metrics.total_commits.toLocaleString(),
      icon: GitCommit,
      color: 'text-blue-400',
    },
    {
      label: 'Avg Commit Size',
      value: `${metrics.avg_commit_size.toFixed(1)} lines`,
      icon: FileDiff,
      color: 'text-green-400',
    },
    {
      label: 'Commits / Day',
      value: metrics.commits_per_day.toFixed(2),
      icon: TrendingUp,
      color: 'text-purple-400',
    },
    {
      label: 'Avg Time Between Commits',
      value: `${metrics.avg_time_between_commits_hours.toFixed(1)} hrs`,
      icon: Clock,
      color: 'text-yellow-400',
    },
    {
      label: 'Bus Factor',
      value: metrics.bus_factor.toString(),
      icon: metrics.bus_factor <= 1 ? AlertTriangle : Users,
      color: metrics.bus_factor <= 1 ? 'text-red-400' : 'text-emerald-400',
    },
    {
      label: 'Code Churn',
      value: `+${metrics.code_churn_additions.toLocaleString()} / -${metrics.code_churn_deletions.toLocaleString()}`,
      icon: FileDiff,
      color: 'text-orange-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="p-4 bg-gray-900 border border-gray-800 rounded-xl"
        >
          <card.icon className={`w-5 h-5 ${card.color} mb-2`} />
          <p className="text-white text-lg font-bold">{card.value}</p>
          <p className="text-gray-400 text-xs">{card.label}</p>
        </div>
      ))}
    </div>
  );
}
