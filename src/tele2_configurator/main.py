"""CLI entry point for the Tele2 Auto-Configurator."""

from __future__ import annotations

import argparse
import asyncio

import structlog
import uvicorn

from tele2_configurator.config import settings
from tele2_configurator.dashboard.app import app
from tele2_configurator.jira.watcher import run_watcher

logger = structlog.get_logger(__name__)


def _run_watcher() -> None:
    logger.info("starting_watcher", dry_run=settings.dry_run)
    asyncio.run(run_watcher())


def _run_dashboard() -> None:
    logger.info("starting_dashboard", host=settings.dashboard_host, port=settings.dashboard_port)
    uvicorn.run(app, host=settings.dashboard_host, port=settings.dashboard_port)


def cli() -> None:
    parser = argparse.ArgumentParser(description="Tele2 Auto-Configurator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("watch", help="Start the Jira inbox watcher")
    sub.add_parser("dashboard", help="Start the approval dashboard")

    args = parser.parse_args()

    if args.command == "watch":
        _run_watcher()
    elif args.command == "dashboard":
        _run_dashboard()


if __name__ == "__main__":
    cli()
