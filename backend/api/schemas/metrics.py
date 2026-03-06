from datetime import datetime
from typing import List
from pydantic import BaseModel

class DailyMetric(BaseModel):
    metrics_date: datetime
    authority_mode: str
    total_missions: int
    daily_cost_usd: float
    daily_tokens: int
    avg_confidence_score: float | None

class DashboardMetricsResponse(BaseModel):
    metrics: List[DailyMetric]
