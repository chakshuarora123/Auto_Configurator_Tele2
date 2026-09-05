"""Tests for the dashboard approval store."""

from __future__ import annotations

from tele2_configurator.dashboard import store


def test_add_and_get_plan(sample_plan) -> None:
    approval_id = store.add_plan(sample_plan)
    assert store.get_plan(approval_id) == sample_plan
    store.remove_plan(approval_id)
    assert store.get_plan(approval_id) is None


def test_list_pending(sample_plan) -> None:
    store._pending.clear()
    store.add_plan(sample_plan)
    assert len(store.list_pending()) == 1
    store.remove_plan(next(iter(store._pending)))
