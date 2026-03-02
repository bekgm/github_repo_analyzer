import { Contributor } from '../api/client';

interface Props {
  contributors: Contributor[];
}

export default function ContributorRanking({ contributors }: Props) {
  const sorted = [...contributors].sort((a, b) => b.total_commits - a.total_commits);
  const maxCommits = sorted[0]?.total_commits || 1;

  return (
    <div className="glass p-6">
      <h3 className="text-slate-600 text-sm font-semibold mb-5">
        Contributors
        <span className="text-slate-300 ml-2 font-normal">{contributors.length}</span>
      </h3>
      <div className="space-y-3.5">
        {sorted.slice(0, 15).map((c, index) => (
          <div key={c.username + index} className="flex items-center gap-3">
            <span className="text-slate-300 text-xs w-5 text-right font-mono">
              {index + 1}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-slate-700 text-sm font-semibold truncate">{c.username}</span>
                <span className="text-slate-400 text-xs flex-shrink-0 ml-3 tabular-nums">
                  {c.total_commits} commits &middot; +{c.additions.toLocaleString()} -{c.deletions.toLocaleString()}
                </span>
              </div>
              <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${(c.total_commits / maxCommits) * 100}%`,
                    background: 'linear-gradient(90deg, #818cf8, #a78bfa)',
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
