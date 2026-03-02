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
      color: 'text-indigo-500',
    },
    {
      label: 'Avg Commit Size',
      value: `${metrics.avg_commit_size.toFixed(1)} lines`,
      icon: FileDiff,
      color: 'text-emerald-500',
    },
    {
      label: 'Commits / Day',
      value: metrics.commits_per_day.toFixed(2),
      icon: TrendingUp,
      color: 'text-violet-500',
    },
    {
      label: 'Avg Between Commits',
      value: `${metrics.avg_time_between_commits_hours.toFixed(1)} hrs`,
      icon: Clock,
      color: 'text-amber-500',
    },
    {
      label: 'Bus Factor',
      value: metrics.bus_factor.toString(),
      icon: metrics.bus_factor <= 1 ? AlertTriangle : Users,
      color: metrics.bus_factor <= 1 ? 'text-red-500' : 'text-emerald-500',
    },
    {
      label: 'Code Churn',
      value: `+${metrics.code_churn_additions.toLocaleString()} / -${metrics.code_churn_deletions.toLocaleString()}`,
      icon: FileDiff,
      color: 'text-orange-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card) => (
        <div
          key={card.label}
          className="glass-sm glass-hover p-4"
        >
          <card.icon className={`w-4 h-4 ${card.color} mb-2.5 opacity-60`} />
          <p className="text-slate-800 text-lg font-bold tracking-tight">{card.value}</p>
          <p className="text-slate-400 text-[11px] mt-0.5">{card.label}</p>
        </div>
      ))}
    </div>
  );
}
