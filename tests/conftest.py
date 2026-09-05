"""Shared test fixtures and configuration."""

from __future__ import annotations

import pytest

from tele2_configurator.config import Settings
from tele2_configurator.models import ConfigAction, ConfigPlan, RequestType


@pytest.fixture
def sample_plan() -> ConfigPlan:
    return ConfigPlan(
        ticket_key="TELE2-123",
        request_type=RequestType.NEW_PRICE_PLAN,
        summary="Create a new 5G data price plan",
        actions=[
            ConfigAction(
                target_system="tmforum",
                operation="create",
                resource_type="price_plan",
                payload={"name": "5G Data 50GB", "data": 50},
            ),
            ConfigAction(
                target_system="nokia_nsp",
                operation="create",
                resource_type="technical_service",
                payload={"service": "5G-Data"},
            ),
        ],
    )


@pytest.fixture
def test_settings() -> Settings:
    return Settings()
