import { ButtonHTMLAttributes } from 'react';
import { twMerge } from 'tailwind-merge';

interface TactileButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
}

export function TactileButton({ children, className, variant = 'secondary', ...props }: TactileButtonProps) {
  const variants = {
    primary: 'bg-neon-cyan/20 text-neon-cyan border-neon-cyan/50 hover:bg-neon-cyan/30 shadow-clay-sm',
    secondary: 'bg-glass-medium text-slate-200 border-glass-border hover:bg-glass-heavy shadow-clay-sm',
    danger: 'bg-neon-orange/20 text-neon-orange border-neon-orange/50 hover:bg-neon-orange/30 shadow-clay-sm',
  };

  return (
    <button
      className={twMerge(
        "px-6 py-2.5 rounded-2xl font-display font-medium text-sm tracking-wide border backdrop-blur-md tactile-press flex items-center justify-center gap-2",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
