"use client";

import React, { useEffect, useState } from 'react';
import { useMissionStream } from '../../hooks/useMissionStream';

export type Task = {
  id: string;
  mission_id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'revision_needed';
  assigned_agent: string;
  created_at: string;
};

interface TaskBoardProps {
  missionId: string;
}

export function TaskBoard({ missionId }: TaskBoardProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const { events } = useMissionStream(missionId);

  useEffect(() => {
    fetch(`/api/v1/missions/${missionId}/tasks`)
      .then(res => res.json())
      .then(data => setTasks(data))
      .catch(err => console.error(err));
  }, [missionId]);

  useEffect(() => {
    if (!events.length) return;
    const lastEvent = events[events.length - 1];

    // Optimistic / Real-time updates logic
    if (lastEvent.type === 'task.created') {
        // We'd typically re-fetch or construct from payload if full
        // Assuming payload has task details or we trigger refresh
        // For contract, we'll assume we can push to list
        const newTask = lastEvent.payload as Task; // simplified
        setTasks(prev => [...prev, newTask]);
    } else if (lastEvent.type === 'task.completed') {
        const taskId = lastEvent.payload.task_id || (lastEvent.payload as any).id; // check payload shape in catalog
        setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'completed' } : t));
    }
  }, [events]);

  const renderColumn = (status: string, title: string) => (
    <div className="flex-1 min-w-[200px] bg-bg-plate p-4 rounded border border-border-primary">
      <h3 className="font-bold mb-4 uppercase text-xs tracking-wider">{title}</h3>
      <div className="flex flex-col gap-2">
        {tasks.filter(t => t.status === status).map(t => (
          <div key={t.id} className="p-3 bg-bg-void border border-border-primary rounded text-sm">
            <div className="flex justify-between items-start mb-1">
                <span className="font-mono text-xs text-signal-amber">{t.assigned_agent}</span>
            </div>
            {t.description}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {renderColumn('pending', 'Pending')}
      {renderColumn('in_progress', 'In Progress')}
      {renderColumn('completed', 'Done')}
    </div>
  );
}
