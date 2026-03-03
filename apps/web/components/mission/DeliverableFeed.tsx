"use client";

import React, { useEffect, useState } from 'react';
import { useMissionStream } from '../../hooks/useMissionStream';

export type Deliverable = {
  id: string;
  type: string;
  content: any;
  review_status: string;
  created_at: string;
};

interface DeliverableFeedProps {
  missionId: string;
}

export function DeliverableFeed({ missionId }: DeliverableFeedProps) {
  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const { events } = useMissionStream(missionId);

  useEffect(() => {
    fetch(`/api/v1/missions/${missionId}/deliverables`)
      .then(res => res.json())
      .then(data => setDeliverables(data))
      .catch(err => console.error(err));
  }, [missionId]);

  useEffect(() => {
    if (!events.length) return;
    const lastEvent = events[events.length - 1];

    // In a real implementation, we'd listen for 'deliverable.created' or similar
    // The Event Catalog v2.0 doesn't explicitly list 'deliverable.created', but 'agent.result' usually implies it.
    // Or we might have added it in a specific domain.
    // For now, let's assume we re-fetch if we see relevant events.
  }, [events]);

  return (
    <div className="flex flex-col gap-4">
      {deliverables.map(d => (
        <div key={d.id} className="p-4 border border-border-primary bg-bg-plate rounded">
          <div className="flex justify-between mb-2">
            <span className="font-bold text-sm">{d.type}</span>
            <span className="text-xs text-muted-foreground">
                {new Date(d.created_at).toLocaleTimeString()}
            </span>
          </div>
          <pre className="text-xs bg-bg-void p-2 rounded overflow-x-auto">
            {JSON.stringify(d.content, null, 2)}
          </pre>
        </div>
      ))}
    </div>
  );
}
