"use client";

import { useEffect, useState } from 'react';

export type MissionEvent = {
  id: string;
  type: string;
  payload: any;
  timestamp: string;
};

export function useMissionStream(missionId: string) {
  const [events, setEvents] = useState<MissionEvent[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!missionId) return;

    const url = `/api/v1/missions/${missionId}/stream`;
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      setIsConnected(false);
      setError(new Error('Stream connection failed'));
      // Browser reconnects automatically usually, but we track state
    };

    // Generic handler for 'mission_event' type
    eventSource.addEventListener('mission_event', (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setEvents((prev) => [...prev, parsed]);
      } catch (e) {
        console.error('Failed to parse event data', event.data);
      }
    });

    // Also listen to default 'message' event just in case
    eventSource.onmessage = (event) => {
       // logic...
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [missionId]);

  return { events, isConnected, error };
}
