// src/components/ui/Badge.tsx
import { cn } from '@/utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'warning' | 'danger' | 'success' | 'info';
  size?: 'sm' | 'md';
}

export function Badge({ className, variant = 'default', size = 'md', children, ...props }: BadgeProps) {
  const base = 'inline-flex items-center font-medium rounded-full';
  
  const variants = {
    default: 'bg-[var(--bg-elevated)] text-[var(--text-secondary)]',
    warning: 'bg-[var(--warning-bg)] text-[var(--warning)]',
    danger: 'bg-[var(--danger-bg)] text-[var(--danger)]',
    success: 'bg-[var(--success-bg)] text-[var(--success)]',
    info: 'bg-[var(--accent-bg)] text-[var(--accent)]',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  };
  
  return (
    <span className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
}