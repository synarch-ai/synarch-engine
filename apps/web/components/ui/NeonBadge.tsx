import React from 'react';

type BadgeVariant = 'cyan' | 'green' | 'fuchsia' | 'yellow';

export function NeonBadge({ children, variant = 'cyan' }: { children: React.ReactNode; variant?: BadgeVariant }) {
  const colors = {
    cyan: 'border-cyan-500 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.3)]',
    green: 'border-green-500 text-green-400 shadow-[0_0_10px_rgba(74,222,128,0.3)]',
    fuchsia: 'border-fuchsia-500 text-fuchsia-400 shadow-[0_0_10px_rgba(217,70,239,0.3)]',
    yellow: 'border-yellow-500 text-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.3)]'
  };

  return (
    <span className={`px-3 py-1 text-xs font-mono font-bold uppercase tracking-wider rounded-full border bg-black/40 backdrop-blur-md ${colors[variant]}`}>
      {children}
    </span>
  );
}
