"""FastAPI application exposing approval endpoints for the dashboard."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from tele2_configurator.config import settings
from tele2_configurator.dashboard.store import get_plan, list_pending, remove_plan
from tele2_configurator.models import ConfigPlan
from tele2_configurator.oss.executor import execute_plan

app = FastAPI(title="Tele2 Auto-Configurator", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, bool | str]:
    return {"status": "ok", "dry_run": settings.dry_run}


@app.get("/approvals")
async def approvals() -> dict[str, ConfigPlan]:
    return list_pending()


@app.get("/approvals/{approval_id}", response_model=ConfigPlan)
async def approval_detail(approval_id: str) -> ConfigPlan:
    plan = get_plan(approval_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Approval not found")
    return plan


@app.post("/approvals/{approval_id}/approve")
async def approve(approval_id: str) -> dict[str, object]:
    plan = get_plan(approval_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Approval not found")
    if settings.dry_run:
        remove_plan(approval_id)
        return {"approved": True, "note": "dry-run mode active; nothing executed"}
    result = await execute_plan(plan)
    remove_plan(approval_id)
    return {"approved": True, "result": result.model_dump()}


@app.post("/approvals/{approval_id}/reject")
async def reject(approval_id: str) -> dict[str, object]:
    plan = get_plan(approval_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Approval not found")
    remove_plan(approval_id)
    return {"approved": False, "ticket": plan.ticket_key}
