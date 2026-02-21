import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface Props {
  distribution: Record<string, number>;
}

const COLORS = [
  '#6366f1', '#8b5cf6', '#a78bfa', '#c084fc',
  '#e879f9', '#f472b6', '#fb7185', '#f87171',
  '#fb923c', '#fbbf24', '#a3e635', '#34d399',
];

export default function LanguagePieChart({ distribution }: Props) {
  const data = Object.entries(distribution)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return (
      <div className="p-6 bg-gray-900 border border-gray-800 rounded-xl">
        <h3 className="text-white font-semibold mb-4">Language Distribution</h3>
        <p className="text-gray-500 text-sm">No language data available</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 border border-gray-800 rounded-xl">
      <h3 className="text-white font-semibold mb-4">Language Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            labelStyle={{ color: '#fff' }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
