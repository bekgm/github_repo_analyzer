import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface Props {
  distribution: Record<string, number>;
}

const COLORS = [
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#f97316', '#eab308',
  '#84cc16', '#10b981', '#06b6d4', '#3b82f6',
];

export default function LanguagePieChart({ distribution }: Props) {
  const data = Object.entries(distribution)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return (
      <div className="glass p-6">
        <h3 className="text-slate-600 text-sm font-semibold mb-5">Languages</h3>
        <p className="text-slate-300 text-sm">No language data available</p>
      </div>
    );
  }

  return (
    <div className="glass p-6">
      <h3 className="text-slate-600 text-sm font-semibold mb-5">Languages</h3>
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
                stroke="rgba(255,255,255,0.6)"
                strokeWidth={2}
              >
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} opacity={0.75} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255,255,255,0.85)',
                  border: '1px solid rgba(0,0,0,0.06)',
                  borderRadius: '12px',
                  backdropFilter: 'blur(16px)',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                }}
                labelStyle={{ color: '#475569', fontSize: 12 }}
                itemStyle={{ color: '#1e293b', fontSize: 12 }}
                formatter={(value: number) => `${value.toFixed(1)}%`}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-1 space-y-2.5">
          {data.slice(0, 6).map((lang, i) => (
            <div key={lang.name} className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm"
                style={{ backgroundColor: COLORS[i % COLORS.length] }}
              />
              <span className="text-slate-600 text-xs flex-1 font-medium">{lang.name}</span>
              <span className="text-slate-400 text-xs tabular-nums">{lang.value.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
