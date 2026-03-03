import { GlassCard } from '@/components/ui/GlassCard';
import { TactileButton } from '@/components/ui/TactileButton';
import { NeonBadge } from '@/components/ui/NeonBadge';
import { Activity, ShieldAlert, Cpu } from 'lucide-react';
import { ApprovalInbox } from '@/components/approvals/ApprovalInbox';
import { TaskBoard } from '@/components/mission/TaskBoard';
import { DeliverableFeed } from '@/components/mission/DeliverableFeed';

export default function MissionControl() {
  const missionId = '4358f853-2f62-4985-83c4-f24eaed8ca2c'; // Replace with dynamic id later

  return (
    <div className="flex flex-col gap-8 max-w-6xl mx-auto">

      {/* Header Section */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-white/10 pb-6">
        <div>
          <h1 className="text-4xl font-display font-bold tracking-tight text-white flex items-center gap-3">
            <Cpu className="text-neon-cyan w-8 h-8" />
            SYNARCH <span className="font-light opacity-60">NEXUS</span>
          </h1>
          <p className="text-slate-400 font-mono text-sm mt-2 flex gap-3 items-center">
            MISSION_ID: <span className="text-neon-cyan">{missionId}</span>
            <NeonBadge status="active">EXECUTING</NeonBadge>
          </p>
        </div>
        <div className="flex gap-3">
          <TactileButton variant="secondary">Intervene</TactileButton>
          <TactileButton variant="danger">Abort Mission</TactileButton>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">

        {/* Left Column - Approvals */}
        <div className="xl:col-span-1 flex flex-col gap-6">
          <GlassCard glowColor="orange">
            <ApprovalInbox missionId={missionId} />
          </GlassCard>
        </div>

        {/* Middle Column - Task Board */}
        <div className="xl:col-span-2">
          <GlassCard glowColor="cyan" className="h-[600px] overflow-hidden flex flex-col">
            <TaskBoard missionId={missionId} />
          </GlassCard>
        </div>

        {/* Right Column - Feed */}
        <div className="xl:col-span-1">
          <GlassCard glowColor="green" className="h-[600px] overflow-hidden flex flex-col">
            <DeliverableFeed missionId={missionId} />
          </GlassCard>
        </div>

      </div>
    </div>
  );
}
