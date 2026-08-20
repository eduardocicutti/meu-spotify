// src/components/ui/StatCard.tsx
import { cn } from '@/utils/cn';

interface StatCardProps {
  value: string | number;
  label: string;
  trend?: { value: number; label: string };
  className?: string;
}

export function StatCard({ value, label, trend, className }: StatCardProps) {
  return (
    <div className={cn('card-base p-6', className)}>
      <p className="font-display text-5xl font-bold text-[var(--text-primary)] tracking-tight">
        {value}
      </p>
      <p className="mt-2 text-sm text-[var(--text-muted)] font-medium">{label}</p>
      {trend && (
        <p className="mt-3 text-xs font-medium flex items-center gap-1">
          <span className={trend.value >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}>
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="text-[var(--text-muted)]">{trend.label}</span>
        </p>
      )}
    </div>
  );
}