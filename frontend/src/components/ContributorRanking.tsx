import { Contributor } from '../api/client';

interface Props {
  contributors: Contributor[];
}

export default function ContributorRanking({ contributors }: Props) {
  const sorted = [...contributors].sort((a, b) => b.total_commits - a.total_commits);
  const maxCommits = sorted[0]?.total_commits || 1;

  return (
    <div className="p-6 bg-gray-900 border border-gray-800 rounded-xl">
      <h3 className="text-white font-semibold mb-4">
        Top Contributors ({contributors.length})
      </h3>
      <div className="space-y-3">
        {sorted.slice(0, 15).map((c, index) => (
          <div key={c.username + index} className="flex items-center gap-3">
            <span className="text-gray-500 text-sm w-6 text-right">
              #{index + 1}
            </span>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-white text-sm font-medium">{c.username}</span>
                <span className="text-gray-400 text-xs">
                  {c.total_commits} commits &middot; +{c.additions.toLocaleString()} -{c.deletions.toLocaleString()}
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all"
                  style={{ width: `${(c.total_commits / maxCommits) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
