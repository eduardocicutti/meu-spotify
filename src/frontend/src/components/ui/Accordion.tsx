// src/components/ui/Accordion.tsx
import { useState, forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { ChevronDown } from 'lucide-react';

interface AccordionProps {
  title: string;
  count?: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export const Accordion = forwardRef<HTMLDivElement, AccordionProps>(
  ({ title, count, children, defaultOpen = false, className, ...props }, ref) => {
    const [open, setOpen] = useState(defaultOpen);
    
    return (
      <div ref={ref} className={cn('card-base overflow-hidden', className)} {...props}>
        <button
          className="w-full px-6 py-4 flex items-center justify-between text-left gap-4"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
        >
          <div className="flex items-center gap-3">
            <h3 className="font-display text-xl font-semibold text-[var(--text-primary)]">
              {title}
            </h3>
            {count !== undefined && (
              <span className="px-2 py-0.5 text-xs font-medium bg-[var(--bg-elevated)] text-[var(--text-secondary)] rounded-full">
                {count}
              </span>
            )}
          </div>
          <ChevronDown
            className={cn('h-5 w-5 text-[var(--text-muted)] transition-transform', open && 'rotate-180')}
            aria-hidden="true"
          />
        </button>
        <div
          className={cn('transition-all duration-200 overflow-hidden', open ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0')}
        >
          <div className="px-6 pb-6 border-t border-[var(--border)]">
            {children}
          </div>
        </div>
      </div>
    );
  }
);

Accordion.displayName = 'Accordion';