import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface Props {
  distribution: Record<string, number>;
}

const COLORS = [
  'rgba(129,140,248,0.8)', 'rgba(167,139,250,0.8)', 'rgba(192,132,252,0.7)',
  'rgba(232,121,249,0.7)', 'rgba(244,114,182,0.7)', 'rgba(251,113,133,0.7)',
  'rgba(251,146,60,0.7)', 'rgba(250,204,21,0.7)', 'rgba(163,230,53,0.7)',
  'rgba(52,211,153,0.7)', 'rgba(56,189,248,0.7)', 'rgba(99,102,241,0.7)',
];

export default function LanguagePieChart({ distribution }: Props) {
  const data = Object.entries(distribution)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return (
      <div className="glass p-6">
        <h3 className="text-white/70 text-sm font-medium mb-5">Languages</h3>
        <p className="text-white/20 text-sm">No language data available</p>
      </div>
    );
  }

  return (
    <div className="glass p-6">
      <h3 className="text-white/70 text-sm font-medium mb-5">Languages</h3>
      <div className="flex items-center gap-6">
        <div className="flex-shrink-0">
          <ResponsiveContainer width={200} height={200}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15,15,25,0.9)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '10px',
                  backdropFilter: 'blur(12px)',
                }}
                labelStyle={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}
                itemStyle={{ color: 'rgba(255,255,255,0.8)', fontSize: 12 }}
                formatter={(value: number) => `${value.toFixed(1)}%`}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-1 space-y-2">
          {data.slice(0, 6).map((lang, i) => (
            <div key={lang.name} className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              />
              <span className="text-white/50 text-xs flex-1">{lang.name}</span>
              <span className="text-white/30 text-xs tabular-nums">{lang.value.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
