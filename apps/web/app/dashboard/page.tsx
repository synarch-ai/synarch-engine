"use client";

import React, { useEffect, useState } from 'react';
import { GlassCard } from '../../components/ui/GlassCard';
import { NeonBadge } from '../../components/ui/NeonBadge';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Activity, Coins, Fingerprint, Zap } from 'lucide-react';

interface Metric {
  metrics_date: string;
  authority_mode: string;
  total_missions: number;
  daily_cost_usd: number;
  daily_tokens: number;
  avg_confidence_score: number | null;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mocking for the static UI build as backend might not be seeded
    setTimeout(() => {
      setMetrics([
        { metrics_date: '2026-02-20', authority_mode: 'supervised', total_missions: 12, daily_cost_usd: 1.25, daily_tokens: 12500, avg_confidence_score: 0.92 },
        { metrics_date: '2026-02-21', authority_mode: 'supervised', total_missions: 18, daily_cost_usd: 2.10, daily_tokens: 21000, avg_confidence_score: 0.88 },
        { metrics_date: '2026-02-22', authority_mode: 'free_rein', total_missions: 8, daily_cost_usd: 4.50, daily_tokens: 45000, avg_confidence_score: 0.95 },
        { metrics_date: '2026-02-23', authority_mode: 'supervised', total_missions: 24, daily_cost_usd: 2.80, daily_tokens: 28000, avg_confidence_score: 0.91 },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  const totalCost = metrics.reduce((acc, curr) => acc + curr.daily_cost_usd, 0);
  const totalTokens = metrics.reduce((acc, curr) => acc + curr.daily_tokens, 0);

  return (
    <main className="min-h-screen bg-[#030303] text-white p-8 relative overflow-hidden">
      {/* Cinematic SVG Noise Background */}
      <div
        className="absolute inset-0 z-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Soft gradient mesh */}
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-gradient-to-br from-indigo-900/30 to-transparent blur-[120px] z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-gradient-to-tl from-cyan-900/20 to-transparent blur-[100px] z-0" />

      <div className="relative z-10 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-1000">
        <header className="flex justify-between items-end border-b border-white/10 pb-6">
          <div>
            <h1 className="font-outfit text-4xl font-light tracking-tight flex items-center gap-3">
              <Activity className="text-cyan-400" size={32} />
              Quality & Telemetry
            </h1>
            <p className="font-mono text-sm text-gray-400 mt-2 uppercase tracking-widest">
              Live Mission Aggregates
            </p>
          </div>
          <NeonBadge variant="cyan">System Optimal</NeonBadge>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Cost Metric */}
          <GlassCard className="p-6 flex flex-col justify-between" aria-busy={loading} aria-label="Total Spend over 30 days">
            <div className="flex items-center gap-2 text-gray-400 mb-4 font-mono text-xs uppercase">
              <Coins size={16} className="text-green-400" aria-hidden="true" /> Total Spend (30d)
            </div>
            <div className="font-outfit text-5xl font-light">
              {loading ? (
                <div className="h-12 w-32 bg-white/5 rounded-md animate-pulse" role="status" aria-label="Loading total spend" />
              ) : (
                `$${totalCost.toFixed(2)}`
              )}
            </div>
          </GlassCard>

          {/* Tokens Metric */}
          <GlassCard className="p-6 flex flex-col justify-between" aria-busy={loading} aria-label="Total Tokens Consumed">
            <div className="flex items-center gap-2 text-gray-400 mb-4 font-mono text-xs uppercase">
              <Zap size={16} className="text-yellow-400" aria-hidden="true" /> Tokens Consumed
            </div>
            <div className="font-outfit text-5xl font-light">
              {loading ? (
                <div className="h-12 w-24 bg-white/5 rounded-md animate-pulse" role="status" aria-label="Loading tokens consumed" />
              ) : (
                `${(totalTokens / 1000).toFixed(1)}k`
              )}
            </div>
          </GlassCard>

          {/* Quality Score Metric */}
          <GlassCard className="p-6 flex flex-col justify-between" aria-busy={loading} aria-label="Average Evaluation Score">
            <div className="flex items-center gap-2 text-gray-400 mb-4 font-mono text-xs uppercase">
              <Fingerprint size={16} className="text-fuchsia-400" aria-hidden="true" /> Avg Eval Score
            </div>
            <div className="font-outfit text-5xl font-light text-fuchsia-100 flex items-baseline">
              {loading ? (
                <div className="h-12 w-36 bg-white/5 rounded-md animate-pulse" role="status" aria-label="Loading average score" />
              ) : (
                <>
                  91.5<span className="text-2xl text-gray-500 ml-1">/100</span>
                </>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          <GlassCard className="p-6 h-96">
             <h3 className="font-mono text-sm text-gray-400 uppercase tracking-widest mb-6">Mission Throughput</h3>
             {loading ? (
               <div className="h-full flex items-center justify-center font-mono text-sm text-gray-500">Initializing telemetry...</div>
             ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="metrics_date" stroke="#ffffff40" tick={{fontFamily: 'JetBrains Mono', fontSize: 10}} />
                  <YAxis stroke="#ffffff40" tick={{fontFamily: 'JetBrains Mono', fontSize: 10}} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000000ee', border: '1px solid #333', fontFamily: 'JetBrains Mono' }}
                    itemStyle={{ color: '#06b6d4' }}
                  />
                  <Line type="monotone" dataKey="total_missions" stroke="#06b6d4" strokeWidth={2} dot={{r: 4, fill: '#000'}} activeDot={{r: 6}} />
                </LineChart>
              </ResponsiveContainer>
             )}
          </GlassCard>

          <GlassCard className="p-6 h-96">
             <h3 className="font-mono text-sm text-gray-400 uppercase tracking-widest mb-6">Cost vs Context Length</h3>
             {loading ? (
               <div className="h-full flex items-center justify-center font-mono text-sm text-gray-500">Initializing telemetry...</div>
             ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="metrics_date" stroke="#ffffff40" tick={{fontFamily: 'JetBrains Mono', fontSize: 10}} />
                  <YAxis yAxisId="left" stroke="#ffffff40" tick={{fontFamily: 'JetBrains Mono', fontSize: 10}} />
                  <YAxis yAxisId="right" orientation="right" stroke="#ffffff40" tick={{fontFamily: 'JetBrains Mono', fontSize: 10}} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000000ee', border: '1px solid #333', fontFamily: 'JetBrains Mono' }}
                  />
                  <Line yAxisId="left" type="monotone" dataKey="daily_cost_usd" stroke="#4ade80" strokeWidth={2} dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="daily_tokens" stroke="#facc15" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
             )}
          </GlassCard>
        </div>
      </div>
    </main>
  );
}
