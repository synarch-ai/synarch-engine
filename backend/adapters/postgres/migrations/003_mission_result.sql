-- SYN-054: persist the mission result (final_output, deliverables, messages, tasks).
ALTER TABLE mission_payloads ADD COLUMN IF NOT EXISTS result JSONB;
