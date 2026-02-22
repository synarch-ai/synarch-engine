import React from 'react';

export type Approval = {
  id: string;
  mission_id: string;
  action_type: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'rejected' | 'timeout';
  requested_at: string;
};

interface ApprovalCardProps {
  approval: Approval;
  onDecide: (id: string, decision: 'approved' | 'rejected', reason?: string) => void;
}

export function ApprovalCard({ approval, onDecide }: ApprovalCardProps) {
  const [reason, setReason] = React.useState('');

  const handleApprove = () => onDecide(approval.id, 'approved', reason);
  const handleReject = () => onDecide(approval.id, 'rejected', reason);

  return (
    <div className="p-4 border border-border-primary bg-bg-plate rounded-md mb-2">
      <div className="flex justify-between items-center mb-2">
        <span className="font-bold text-signal-amber uppercase text-xs">
          {approval.risk_level} Risk
        </span>
        <span className="text-xs text-muted-foreground">
          {new Date(approval.requested_at).toLocaleTimeString()}
        </span>
      </div>

      <h3 className="font-semibold mb-1">{approval.action_type}</h3>
      <p className="text-sm mb-4">{approval.description}</p>

      {approval.status === 'pending' ? (
        <div className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Reason (optional)"
            className="p-2 text-sm bg-bg-void border border-border-primary rounded"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="flex gap-2 justify-end">
            <button
              onClick={handleReject}
              className="px-3 py-1 text-sm bg-red-900/20 text-red-400 border border-red-900 rounded hover:bg-red-900/40"
            >
              Reject
            </button>
            <button
              onClick={handleApprove}
              className="px-3 py-1 text-sm bg-green-900/20 text-green-400 border border-green-900 rounded hover:bg-green-900/40"
            >
              Approve
            </button>
          </div>
        </div>
      ) : (
        <div className="text-sm italic text-muted-foreground">
          {approval.status}
        </div>
      )}
    </div>
  );
}
