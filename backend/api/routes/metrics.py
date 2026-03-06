from fastapi import APIRouter, Depends
from typing import List

from api.dependencies import get_container
from api.schemas.metrics import DailyMetric, DashboardMetricsResponse
from container import Container

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/daily", response_model=DashboardMetricsResponse)
async def get_daily_metrics(
    container: Container = Depends(get_container),
):
    """Get aggregated daily mission metrics (FR-49)."""
    rows = await container.mission_repo.get_daily_metrics()

    metrics = []
    for row in rows:
        metrics.append(DailyMetric(
            metrics_date=row["metrics_date"],
            authority_mode=str(row["authority_mode"]),
            total_missions=row["total_missions"],
            daily_cost_usd=float(row["daily_cost_usd"]) if row["daily_cost_usd"] is not None else 0.0,
            daily_tokens=int(row["daily_tokens"]) if row["daily_tokens"] is not None else 0,
            avg_confidence_score=float(row["avg_confidence_score"]) if row["avg_confidence_score"] is not None else None
        ))

    return DashboardMetricsResponse(metrics=metrics)
