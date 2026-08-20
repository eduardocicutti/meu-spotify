// src/components/ui/EmptyState.tsx
import { cn } from '@/utils/cn';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({ title, description, action, icon, className }: EmptyStateProps) {
  return (
    <div className={cn('card-base p-12 text-center', className)}>
      {icon && (
        <div className="text-6xl mb-4" aria-hidden="true">
          {icon}
        </div>
      )}
      <h2 className="font-display text-xl font-semibold mb-2">{title}</h2>
      {description && (
        <p className="text-[var(--text-muted)] mb-6">{description}</p>
      )}
      {action && (
        <div className="mt-4">{action}</div>
      )}
    </div>
  );
}