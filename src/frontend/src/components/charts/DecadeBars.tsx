// src/components/charts/DecadeBars.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { cn } from '@/utils/cn';

interface DecadeBarsProps {
  data: Record<string, number>;
  className?: string;
}

export function DecadeBars({ data, className }: DecadeBarsProps) {
  const entries = Object.entries(data)
    .filter(([decade]) => decade !== 'undefined' && decade !== 'null')
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
  
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  
  if (entries.length === 0) {
    return (
      <div className={cn('h-64 flex items-center justify-center', className)}>
        <p className="text-[var(--text-muted)]">Nenhum dado de década disponível</p>
      </div>
    );
  }
  
  const chartData = entries.map(([decade, value]) => ({
    name: decade,
    value,
    percentage: ((value / total) * 100).toFixed(1),
  }));
  
  return (
    <div className={cn('h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <YAxis
            type="category"
            dataKey="name"
            width={80}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-body)' }}
            axisLine={false}
            tickLine={false}
          />
          <XAxis type="number" hide={true} tick={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
            }}
            labelFormatter={(name: string) => {
              const item = chartData.find(d => d.name === name);
              return item ? `${item.name} — ${item.percentage}%` : name;
            }}
          />
          <Bar dataKey="value" fill="var(--accent)" radius={[0, 4, 4, 0]} maxBarSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}