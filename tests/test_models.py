"""Tests for shared Pydantic data models."""

from __future__ import annotations

from tele2_configurator.models import (
    ConfigAction,
    ConfigPlan,
    ExecutionResult,
    RequestType,
)


def test_config_plan_roundtrip(sample_plan: ConfigPlan) -> None:
    data = sample_plan.model_dump()
    restored = ConfigPlan(**data)
    assert restored == sample_plan
    assert len(restored.actions) == 2


def test_config_action_requires_resource_id_for_update() -> None:
    action = ConfigAction(
        target_system="tmforum",
        operation="update",
        resource_type="price_plan",
        payload={},
    )
    assert action.resource_id is None


def test_execution_result_defaults() -> None:
    plan = ConfigPlan(
        ticket_key="X-1", request_type=RequestType.OTHER, summary="test", actions=[]
    )
    result = ExecutionResult(plan=plan, success=True)
    assert result.executed_actions == 0
    assert result.errors == []
