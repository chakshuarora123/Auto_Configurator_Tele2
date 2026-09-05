"""In-memory store for pending approvals awaiting human review.

Note: swap this for a persistent backend (SQLite/Postgres) in production.
"""

from __future__ import annotations

from uuid import uuid4

from tele2_configurator.models import ConfigPlan

_pending: dict[str, ConfigPlan] = {}


def add_plan(plan: ConfigPlan) -> str:
    approval_id = uuid4().hex
    _pending[approval_id] = plan
    return approval_id


def get_plan(approval_id: str) -> ConfigPlan | None:
    return _pending.get(approval_id)


def list_pending() -> dict[str, ConfigPlan]:
    return dict(_pending)


def remove_plan(approval_id: str) -> None:
    _pending.pop(approval_id, None)
