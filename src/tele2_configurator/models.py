"""Pydantic data models shared across all layers."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RequestType(StrEnum):
    NEW_PRICE_PLAN = "new_price_plan"
    UPDATE_PRICE_PLAN = "update_price_plan"
    NEW_PRODUCT = "new_product"
    UPDATE_PRODUCT = "update_product"
    NEW_TECHNICAL_SERVICE = "new_technical_service"
    UPDATE_TECHNICAL_SERVICE = "update_technical_service"
    OTHER = "other"


class TicketPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfigAction(BaseModel):
    target_system: str = Field(
        description="OSS system to configure: nokia_nsp | tmforum | custom_api"
    )
    operation: str = Field(description="create | update | delete")
    resource_type: str = Field(description="price_plan | product | technical_service")
    resource_id: str | None = Field(default=None, description="Existing resource ID for updates")
    payload: dict[str, object] = Field(
        default_factory=dict, description="Configuration payload for the target system"
    )


class ConfigPlan(BaseModel):
    """Structured configuration plan produced by the AI agent."""

    ticket_key: str
    request_type: RequestType
    priority: TicketPriority = TicketPriority.MEDIUM
    summary: str = Field(description="Human-readable summary of what needs to be configured")
    actions: list[ConfigAction] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list, description="Potential risks or side effects")
    estimated_duration_seconds: int = Field(default=0)


class ExecutionResult(BaseModel):
    plan: ConfigPlan
    success: bool
    executed_actions: int = 0
    errors: list[str] = Field(default_factory=list)
    output: dict[str, object] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Ticket(BaseModel):
    key: str
    summary: str
    description: str
    status: str
    assignee: str | None = None
    labels: list[str] = Field(default_factory=list)
    created: datetime | None = None
