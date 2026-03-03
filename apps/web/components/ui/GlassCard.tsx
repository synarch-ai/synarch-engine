import { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: 'cyan' | 'orange' | 'green' | 'none';
}

export function GlassCard({ children, className, glowColor = 'none' }: GlassCardProps) {
  const glowClasses = {
    cyan: 'shadow-[0_0_30px_rgba(34,211,238,0.15)] border-neon-cyan/20',
    orange: 'shadow-[0_0_30px_rgba(251,146,60,0.15)] border-neon-orange/20',
    green: 'shadow-[0_0_30px_rgba(74,222,128,0.15)] border-neon-green/20',
    none: ''
  };

  return (
    <div className={twMerge("glass-panel p-6 flex flex-col gap-4 relative overflow-hidden", glowClasses[glowColor], className)}>
      {children}
    </div>
  );
}
