// src/components/ui/Skeleton.tsx
import { cn } from '@/utils/cn';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded bg-[var(--bg-elevated)]', className)}
      {...props}
    />
  );
}