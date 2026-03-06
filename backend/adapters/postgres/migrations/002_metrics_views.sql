-- Migration 002: Add Materialized Views for Quality and Cost Dashboards (FR-49)

CREATE MATERIALIZED VIEW daily_mission_metrics AS
SELECT
    DATE_TRUNC('day', m.completed_at AT TIME ZONE 'UTC') AS metrics_date,
    m.authority_mode,
    COUNT(m.id) AS total_missions,
    SUM(m.mission_cost_usd) AS daily_cost_usd,
    SUM(m.token_usage_total) AS daily_tokens,
    AVG(m.confidence_score) AS avg_confidence_score
FROM missions m
WHERE m.status = 'completed' AND m.completed_at IS NOT NULL
GROUP BY 1, 2;

CREATE UNIQUE INDEX ux_daily_mission_metrics_date_mode
ON daily_mission_metrics (metrics_date, authority_mode);

CREATE OR REPLACE FUNCTION refresh_daily_mission_metrics()
RETURNS TRIGGER LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_mission_metrics;
    RETURN NULL;
END;
$$;
