// src/components/charts/GenreBars.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { cn } from '@/utils/cn';

interface GenreBarsProps {
  data: Record<string, number>;
  className?: string;
}

const COLORS = [
  'var(--accent)',
  '#7c3aed',
  '#ec4899',
  '#f97316',
  '#06b6d4',
  '#84cc16',
  '#f43f5e',
  '#6366f1',
  '#14b8a6',
  '#eab308',
];

export function GenreBars({ data, className }: GenreBarsProps) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  
  if (entries.length === 0) {
    return (
      <div className={cn('h-64 flex items-center justify-center', className)}>
        <p className="text-[var(--text-muted)]">Nenhum dado de gênero disponível</p>
      </div>
    );
  }
  
  const chartData = entries.map(([name, value], i) => ({
    name: name.length > 20 ? name.slice(0, 18) + '…' : name,
    value,
    percentage: ((value / total) * 100).toFixed(1),
    color: COLORS[i % COLORS.length],
  }));
  
  return (
    <div className={cn('h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-body)' }}
            axisLine={false}
            tickLine={false}
          />
          <XAxis
            type="number"
            hide={true}
            tick={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
            }}
            formatter={(value: number, name: string) => [value, name]}
            labelFormatter={(name: string) => {
              const item = chartData.find(d => d.name === name);
              return item ? `${item.name} — ${item.percentage}%` : name;
            }}
          />
          <Bar
            dataKey="value"
            radius={[0, 4, 4, 0]}
            maxBarSize={24}
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-2 mt-4" role="list" aria-label="Legenda de gêneros">
        {chartData.map((entry, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs" role="listitem">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: entry.color }}
              aria-hidden="true"
            />
            <span className="text-[var(--text-secondary)]">{entry.name}</span>
            <span className="text-[var(--text-muted)]">{entry.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}