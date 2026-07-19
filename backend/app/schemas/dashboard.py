from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    active_engagements: int
    avg_cycle_time_days: float | None = None
    baseline_cycle_time_days: float | None = None
    kpis_on_track: int
    kpis_total: int
    est_roi_delivered: float


class KpiTrackerRow(BaseModel):
    label: str
    progress: int
    current_value: str | None = None
