from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.activity_entry import ActivityEntry
from app.models.engagement import Engagement
from app.models.engagement_kpi import EngagementKpi
from app.models.engagement_stage_state import EngagementStageState
from app.models.user import User
from app.schemas.activity import ActivityRead
from app.schemas.dashboard import DashboardSummary, KpiTrackerRow
from app.schemas.engagement import (
    EngagementCreate,
    EngagementKpiCreate,
    EngagementKpiRead,
    EngagementKpiUpdate,
    EngagementRead,
    EngagementUpdate,
    PlaybookGenerationResponse,
    StageGeneratedContent,
    StageGenerationResult,
    StageStateRead,
    StageStateUpdate,
)
from app.schemas.pitch import PitchGenerateRequest, PitchGeneratedContent, PitchGenerateResponse
from app.services.gtm_content_service import (
    GtmContentGenerationError,
    generate_pitch_content,
    generate_stage_content,
)

router = APIRouter()

STAGE_ORDER = ["discovery", "design", "integration", "measurement", "scale"]
STAGE_LABELS = {
    "discovery": "Discovery",
    "design": "Design",
    "integration": "Integration",
    "measurement": "Measurement",
    "scale": "Scale",
}
KPI_ON_TRACK_THRESHOLD = 70


def _is_checklist_complete(checklist: list[bool]) -> bool:
    return bool(checklist) and all(checklist)


def _owner_name(user: User | None) -> str | None:
    if user is None:
        return None
    return user.full_name or user.email


def _engagement_to_read(engagement: Engagement) -> EngagementRead:
    return EngagementRead(
        id=engagement.id,
        owner_id=engagement.owner_id,
        client_name=engagement.client_name,
        industry=engagement.industry,
        stage=engagement.stage,
        health=engagement.health,
        started_at=engagement.started_at,
        closed_at=engagement.closed_at,
        roi_value=float(engagement.roi_value) if engagement.roi_value is not None else None,
        created_at=engagement.created_at,
        updated_at=engagement.updated_at,
        owner_name=_owner_name(engagement.owner),
    )


def _get_engagement_or_404(db: Session, engagement_id: int, owner_id: int) -> Engagement:
    engagement = db.execute(
        select(Engagement).where(Engagement.id == engagement_id, Engagement.owner_id == owner_id)
    ).scalar_one_or_none()
    if engagement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engagement not found")
    return engagement


def _log_activity(db: Session, engagement: Engagement, activity_type: str, text: str) -> None:
    db.add(ActivityEntry(engagement_id=engagement.id, type=activity_type, text=text))


def _stage_state_to_read(state: EngagementStageState) -> StageStateRead:
    return StageStateRead(
        engagement_id=state.engagement_id,
        stage=state.stage,
        checklist_json=state.checklist_json,
        notes=state.notes,
        generated_content=StageGeneratedContent(**state.generated_content_json) if state.generated_content_json else None,
        content_generated_at=state.content_generated_at,
        content_model=state.content_model,
        updated_at=state.updated_at,
    )


# --- Engagements -----------------------------------------------------------


@router.get("/engagements", response_model=list[EngagementRead])
def list_engagements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EngagementRead]:
    engagements = db.execute(
        select(Engagement).where(Engagement.owner_id == current_user.id).order_by(Engagement.updated_at.desc())
    ).scalars().all()
    return [_engagement_to_read(item) for item in engagements]


@router.post("/engagements", response_model=EngagementRead, status_code=status.HTTP_201_CREATED)
def create_engagement(
    payload: EngagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementRead:
    if payload.stage not in STAGE_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage")

    engagement = Engagement(
        owner_id=current_user.id,
        client_name=payload.client_name,
        industry=payload.industry,
        stage=payload.stage,
        health=payload.health,
        started_at=payload.started_at or date.today(),
        roi_value=payload.roi_value,
    )
    db.add(engagement)
    db.commit()
    db.refresh(engagement)

    _log_activity(db, engagement, "update", f"New engagement created for {engagement.client_name}")
    db.commit()

    return _engagement_to_read(engagement)


@router.get("/engagements/{engagement_id}", response_model=EngagementRead)
def get_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementRead:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    return _engagement_to_read(engagement)


@router.patch("/engagements/{engagement_id}", response_model=EngagementRead)
def update_engagement(
    engagement_id: int,
    payload: EngagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementRead:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    updates = payload.model_dump(exclude_unset=True)

    if "stage" in updates and updates["stage"] not in STAGE_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage")

    previous_stage = engagement.stage
    for field, value in updates.items():
        setattr(engagement, field, value)

    if "stage" in updates and updates["stage"] != previous_stage:
        _log_activity(
            db,
            engagement,
            "milestone",
            f"{STAGE_LABELS.get(engagement.stage, engagement.stage)} stage started for {engagement.client_name}",
        )

    if "closed_at" in updates and updates["closed_at"] is not None:
        _log_activity(db, engagement, "milestone", f"Engagement closed for {engagement.client_name}")

    db.commit()
    db.refresh(engagement)
    return _engagement_to_read(engagement)


@router.delete(
    "/engagements/{engagement_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    db.delete(engagement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- KPIs --------------------------------------------------------------


@router.post(
    "/engagements/{engagement_id}/kpis",
    response_model=EngagementKpiRead,
    status_code=status.HTTP_201_CREATED,
)
def add_engagement_kpi(
    engagement_id: int,
    payload: EngagementKpiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementKpiRead:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    kpi = EngagementKpi(engagement_id=engagement.id, **payload.model_dump())
    db.add(kpi)
    _log_activity(db, engagement, "data-entry", f"Baseline KPI data entered for {engagement.client_name}: {kpi.label}")
    db.commit()
    db.refresh(kpi)
    return EngagementKpiRead.model_validate(kpi)


@router.patch("/engagements/{engagement_id}/kpis/{kpi_id}", response_model=EngagementKpiRead)
def update_engagement_kpi(
    engagement_id: int,
    kpi_id: int,
    payload: EngagementKpiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EngagementKpiRead:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    kpi = db.execute(
        select(EngagementKpi).where(EngagementKpi.id == kpi_id, EngagementKpi.engagement_id == engagement.id)
    ).scalar_one_or_none()
    if kpi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")

    previous_progress = kpi.progress
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(kpi, field, value)

    if "progress" in updates:
        if previous_progress < KPI_ON_TRACK_THRESHOLD <= kpi.progress:
            _log_activity(db, engagement, "milestone", f"{kpi.label} reached target for {engagement.client_name}")
        else:
            _log_activity(db, engagement, "update", f"{kpi.label} updated for {engagement.client_name}")

    db.commit()
    db.refresh(kpi)
    return EngagementKpiRead.model_validate(kpi)


@router.delete(
    "/engagements/{engagement_id}/kpis/{kpi_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_engagement_kpi(
    engagement_id: int,
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)
    kpi = db.execute(
        select(EngagementKpi).where(EngagementKpi.id == kpi_id, EngagementKpi.engagement_id == engagement.id)
    ).scalar_one_or_none()
    if kpi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    db.delete(kpi)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Pitch builder -----------------------------------------------------


@router.post("/pitch/generate", response_model=PitchGenerateResponse)
def generate_pitch(
    payload: PitchGenerateRequest,
    current_user: User = Depends(get_current_user),
) -> PitchGenerateResponse:
    if not payload.pain_points:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select at least one pain point")

    try:
        generated = generate_pitch_content(industry=payload.industry, pain_points=payload.pain_points)
    except GtmContentGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    model_name = generated.pop("_model", None)
    return PitchGenerateResponse(content=PitchGeneratedContent(**generated), model=model_name)


# --- Stage checklist + notes -----------------------------------------------


@router.get("/engagements/{engagement_id}/stages/{stage}", response_model=StageStateRead)
def get_stage_state(
    engagement_id: int,
    stage: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StageStateRead:
    if stage not in STAGE_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage")
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)

    state = db.execute(
        select(EngagementStageState).where(
            EngagementStageState.engagement_id == engagement.id, EngagementStageState.stage == stage
        )
    ).scalar_one_or_none()

    if state is None:
        state = EngagementStageState(
            engagement_id=engagement.id,
            stage=stage,
            checklist_json=[],
            notes=None,
        )
        db.add(state)
        db.commit()
        db.refresh(state)

    return _stage_state_to_read(state)


@router.put("/engagements/{engagement_id}/stages/{stage}", response_model=StageStateRead)
def put_stage_state(
    engagement_id: int,
    stage: str,
    payload: StageStateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StageStateRead:
    if stage not in STAGE_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage")

    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)

    state = db.execute(
        select(EngagementStageState).where(
            EngagementStageState.engagement_id == engagement.id, EngagementStageState.stage == stage
        )
    ).scalar_one_or_none()

    expected_length = len(state.generated_content_json["checklist"]) if state and state.generated_content_json else None
    if expected_length is not None and len(payload.checklist_json) != expected_length:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Checklist length does not match generated content")

    was_complete = _is_checklist_complete(state.checklist_json) if state is not None else False

    if state is None:
        state = EngagementStageState(engagement_id=engagement.id, stage=stage)
        db.add(state)

    state.checklist_json = payload.checklist_json
    state.notes = payload.notes

    is_complete = _is_checklist_complete(state.checklist_json)
    if is_complete and not was_complete:
        _log_activity(
            db,
            engagement,
            "milestone",
            f"{STAGE_LABELS.get(stage, stage)} playbook completed for {engagement.client_name}",
        )
    else:
        _log_activity(
            db,
            engagement,
            "data-entry",
            f"{STAGE_LABELS.get(stage, stage)} notes updated for {engagement.client_name}",
        )

    db.commit()
    db.refresh(state)
    return _stage_state_to_read(state)


@router.post("/engagements/{engagement_id}/generate-playbook", response_model=PlaybookGenerationResponse)
def generate_playbook(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlaybookGenerationResponse:
    engagement = _get_engagement_or_404(db, engagement_id, current_user.id)

    kpis = db.execute(
        select(EngagementKpi).where(EngagementKpi.engagement_id == engagement.id)
    ).scalars().all()
    kpi_payload = [
        {"label": kpi.label, "baseline_value": kpi.baseline_value, "target_value": kpi.target_value} for kpi in kpis
    ]

    existing_states = {
        state.stage: state
        for state in db.execute(
            select(EngagementStageState).where(EngagementStageState.engagement_id == engagement.id)
        ).scalars().all()
    }

    results: list[StageGenerationResult] = []
    generated_count = 0

    for stage in STAGE_ORDER:
        state = existing_states.get(stage)
        try:
            generated = generate_stage_content(
                client_name=engagement.client_name,
                industry=engagement.industry,
                stage_label=STAGE_LABELS[stage],
                kpis=kpi_payload,
                existing_notes=state.notes if state else None,
            )
        except GtmContentGenerationError as exc:
            results.append(StageGenerationResult(stage=stage, status="failed", error=str(exc)))
            continue

        model_name = generated.pop("_model", None)
        if state is None:
            state = EngagementStageState(engagement_id=engagement.id, stage=stage)
            db.add(state)
            existing_states[stage] = state

        state.generated_content_json = generated
        state.checklist_json = [False] * len(generated["checklist"])
        state.content_generated_at = datetime.utcnow()
        state.content_model = model_name

        results.append(StageGenerationResult(stage=stage, status="generated"))
        generated_count += 1

    if generated_count == 0:
        db.rollback()
        failures = "; ".join(f"{item.stage}: {item.error}" for item in results)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed for every stage. {failures}",
        )

    _log_activity(
        db,
        engagement,
        "update",
        f"AI-generated full playbook ({generated_count}/{len(STAGE_ORDER)} stages) for {engagement.client_name}",
    )
    db.commit()

    return PlaybookGenerationResponse(results=results)


# --- Activity feed -----------------------------------------------------


@router.get("/activity", response_model=list[ActivityRead])
def list_activity(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActivityRead]:
    rows = db.execute(
        select(ActivityEntry, Engagement)
        .join(Engagement, Engagement.id == ActivityEntry.engagement_id)
        .where(Engagement.owner_id == current_user.id)
        .order_by(ActivityEntry.created_at.desc())
        .limit(limit)
    ).all()

    return [
        ActivityRead(
            id=entry.id,
            engagement_id=entry.engagement_id,
            type=entry.type,
            text=entry.text,
            created_at=entry.created_at,
            client_name=engagement.client_name,
            author=_owner_name(current_user),
        )
        for entry, engagement in rows
    ]


# --- Dashboard summary + KPI tracker ---------------------------------------


@router.get("/dashboard-summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    engagements = db.execute(
        select(Engagement).where(Engagement.owner_id == current_user.id)
    ).scalars().all()

    active = [item for item in engagements if item.closed_at is None]
    closed = [item for item in engagements if item.closed_at is not None]

    today = date.today()
    avg_cycle_time_days = (
        round(sum((today - item.started_at).days for item in active) / len(active), 1) if active else None
    )
    baseline_cycle_time_days = (
        round(sum((item.closed_at - item.started_at).days for item in closed) / len(closed), 1) if closed else None
    )

    active_ids = [item.id for item in active]
    kpis: list[EngagementKpi] = []
    if active_ids:
        kpis = db.execute(
            select(EngagementKpi).where(EngagementKpi.engagement_id.in_(active_ids))
        ).scalars().all()

    kpis_on_track = sum(1 for kpi in kpis if kpi.progress >= KPI_ON_TRACK_THRESHOLD)
    est_roi_delivered = sum(float(item.roi_value) for item in engagements if item.roi_value is not None)

    return DashboardSummary(
        active_engagements=len(active),
        avg_cycle_time_days=avg_cycle_time_days,
        baseline_cycle_time_days=baseline_cycle_time_days,
        kpis_on_track=kpis_on_track,
        kpis_total=len(kpis),
        est_roi_delivered=est_roi_delivered,
    )


@router.get("/kpi-tracker", response_model=list[KpiTrackerRow])
def kpi_tracker(
    industry: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[KpiTrackerRow]:
    rows = db.execute(
        select(EngagementKpi)
        .join(Engagement, Engagement.id == EngagementKpi.engagement_id)
        .where(
            Engagement.owner_id == current_user.id,
            Engagement.industry == industry,
            Engagement.closed_at.is_(None),
        )
        .order_by(EngagementKpi.updated_at.desc())
        .limit(10)
    ).scalars().all()

    return [
        KpiTrackerRow(label=kpi.label, progress=kpi.progress, current_value=kpi.current_value) for kpi in rows
    ]
