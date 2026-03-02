import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { DailyCommit } from '../api/client';

interface Props {
  data: DailyCommit[];
}

export default function CommitFrequencyChart({ data }: Props) {
  return (
    <div className="glass p-6">
      <h3 className="text-white/70 text-sm font-medium mb-5">Daily Commits</h3>
      {data.length === 0 ? (
        <p className="text-white/20 text-sm">No commit data available.</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis
              dataKey="date"
              stroke="rgba(255,255,255,0.15)"
              tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.3)' }}
              interval={data.length > 20 ? Math.floor(data.length / 10) : 0}
              angle={-45}
              textAnchor="end"
              height={55}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="rgba(255,255,255,0.15)"
              tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.3)' }}
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15,15,25,0.9)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '10px',
                backdropFilter: 'blur(12px)',
              }}
              labelStyle={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}
              itemStyle={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }}
              formatter={(value: number) => [`${value}`, 'Commits']}
            />
            <Bar dataKey="commits" fill="rgba(129,140,248,0.6)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
