import React from 'react';

export function GlassCard({ children, className = '', ...props }: React.HTMLAttributes<HTMLDivElement> & { children: React.ReactNode; className?: string }) {
  return (
    <div className={`relative overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl ${className}`} {...props}>
      {/* Soft Inner Highlight */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      {/* Extruded Inner Shadow effect for Claymorphism */}
      <div className="absolute inset-0 shadow-[inset_0_0_20px_rgba(0,0,0,0.4)] pointer-events-none rounded-xl" />

      <div className="relative z-10 h-full">
        {children}
      </div>
    </div>
  );
}
