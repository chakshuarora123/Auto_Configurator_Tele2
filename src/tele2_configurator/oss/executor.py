"""Executes a ConfigPlan against the OSS systems."""

from __future__ import annotations

import structlog

from tele2_configurator.models import ConfigAction, ConfigPlan, ExecutionResult
from tele2_configurator.oss.base_client import RestClient, get_client

logger = structlog.get_logger(__name__)


async def _execute_action(client: RestClient, action: ConfigAction) -> None:
    if action.operation == "create":
        await client.create(action.resource_type, action.payload)
    elif action.operation == "update":
        if not action.resource_id:
            raise ValueError("update requires resource_id")
        await client.update(action.resource_type, action.resource_id, action.payload)
    elif action.operation == "delete":
        if not action.resource_id:
            raise ValueError("delete requires resource_id")
        await client.delete(action.resource_type, action.resource_id)
    else:
        raise ValueError(f"Unsupported operation: {action.operation}")


async def execute_plan(plan: ConfigPlan) -> ExecutionResult:
    result = ExecutionResult(plan=plan, success=True)
    clients: dict[str, RestClient] = {}

    try:
        for action in plan.actions:
            if action.target_system not in clients:
                clients[action.target_system] = get_client(action.target_system)
            logger.info("executing_action", ticket=plan.ticket_key, action=action.dict())
            await _execute_action(clients[action.target_system], action)
            result.executed_actions += 1
    except Exception as e:
        logger.exception("execution_failed", ticket=plan.ticket_key)
        result.success = False
        result.errors.append(str(e))
    finally:
        for client in clients.values():
            await client.aclose()

    logger.info("execution_complete", ticket=plan.ticket_key, success=result.success)
    return result
