"use client";

import React, { useEffect, useState } from 'react';
import { ApprovalCard, Approval } from './ApprovalCard';
import { useMissionStream } from '../../hooks/useMissionStream';

interface ApprovalInboxProps {
  missionId: string;
}

export function ApprovalInbox({ missionId }: ApprovalInboxProps) {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const { events } = useMissionStream(missionId);

  // Initial Fetch
  useEffect(() => {
    fetch(`/api/v1/approvals?mission_id=${missionId}`)
      .then(res => res.json())
      .then(data => setApprovals(data))
      .catch(err => console.error("Failed to fetch approvals", err));
  }, [missionId]);

  // Real-time Update via SSE
  useEffect(() => {
    if (!events.length) return;
    const lastEvent = events[events.length - 1];

    if (lastEvent.type === 'approval.requested') {
      // Add to list (optimistic/event-driven)
      // In a real app, we might re-fetch to get the full ID/timestamp if payload is partial
      // But assuming payload has enough info
      const newApproval = lastEvent.payload as Approval; // simplified cast
      setApprovals(prev => [newApproval, ...prev]);
    } else if (lastEvent.type.startsWith('approval.')) {
        // Update status
        const approvalId = lastEvent.payload.approval_id;
        setApprovals(prev => prev.map(a =>
            a.id === approvalId
                ? { ...a, status: lastEvent.type.split('.')[1] as any }
                : a
        ));
    }
  }, [events]);

  const handleDecide = async (id: string, decision: 'approved'|'rejected', reason?: string) => {
    try {
      await fetch(`/api/v1/approvals/${id}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, reason, decided_by: 'operator' })
      });
      // State update will come via SSE event (approval.approved/rejected)
    } catch (e) {
      console.error("Decision failed", e);
    }
  };

  return (
    <div className="flex flex-col gap-4 max-h-[600px] overflow-y-auto">
      <h2 className="text-lg font-bold border-b border-border-primary pb-2 sticky top-0 bg-bg-void z-10">
        Approval Inbox ({approvals.filter(a => a.status === 'pending').length})
      </h2>
      {approvals.length === 0 ? (
        <div className="text-center text-muted-foreground py-8">
          No approvals pending.
        </div>
      ) : (
        approvals.map(approval => (
          <ApprovalCard
            key={approval.id}
            approval={approval}
            onDecide={handleDecide}
          />
        ))
      )}
    </div>
  );
}
