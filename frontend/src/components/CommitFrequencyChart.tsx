import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { DailyCommit } from '../api/client';

interface Props {
  data: DailyCommit[];
}

export default function CommitFrequencyChart({ data }: Props) {
  return (
    <div className="p-6 bg-gray-900 border border-gray-800 rounded-xl">
      <h3 className="text-white font-semibold mb-4">Daily Commit Timeline</h3>
      {data.length === 0 ? (
        <p className="text-gray-500 text-sm">No commit data available.</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="date"
              stroke="#9ca3af"
              tick={{ fontSize: 11 }}
              interval={data.length > 20 ? Math.floor(data.length / 10) : 0}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis stroke="#9ca3af" allowDecimals={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
              labelStyle={{ color: '#fff' }}
              formatter={(value: number) => [`${value} commits`, 'Commits']}
            />
            <Bar dataKey="commits" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
