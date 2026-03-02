import { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface NeonBadgeProps {
  children: ReactNode;
  status?: 'active' | 'warning' | 'neutral' | 'success';
}

export function NeonBadge({ children, status = 'neutral' }: NeonBadgeProps) {
  const styles = {
    active: 'text-neon-cyan bg-neon-cyan/10 border-neon-cyan/30 shadow-[0_0_10px_rgba(34,211,238,0.2)]',
    warning: 'text-neon-orange bg-neon-orange/10 border-neon-orange/30 shadow-[0_0_10px_rgba(251,146,60,0.2)]',
    success: 'text-neon-green bg-neon-green/10 border-neon-green/30 shadow-[0_0_10px_rgba(74,222,128,0.2)]',
    neutral: 'text-slate-300 bg-white/5 border-white/10',
  };

  return (
    <span className={twMerge(
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border backdrop-blur-sm",
      styles[status]
    )}>
      {children}
    </span>
  );
}
