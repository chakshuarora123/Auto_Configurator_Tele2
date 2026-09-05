# Tele2 Auto-Configurator

Automated OSS configuration for Tele2 Sweden. Monitors Jira tickets in **Inbox** status, uses an AI
agent to translate Commercial requests (new/updated price plans, products, technical services) into
structured configuration plans, and applies them to OSS backend systems with a human-approval gate.

## Architecture

```
┌────────────┐   polls   ┌──────────────┐   analyzes   ┌──────────────┐
│ Jira Client│◄──────────│   Watcher    │──────────────►│  AI Agent    │
└────────────┘           └──────┬───────┘              │ (OpenAI)     │
        ▲                       │                      └──────┬───────┘
        │ Jira comments         │ plan                        │ plan
        │ (status updates)      ▼                              ▼
┌────────────┐           ┌──────────────┐             ┌──────────────┐
│  Notifier  │◄──────────│  Execution   │             │ Approval     │
│  + Email   │           │   Result     │             │  Dashboard   │
└────────────┘           └──────┬───────┘             │  (FastAPI)   │
                                │ executes             └──────┬───────┘
                                ▼                             │ approve/reject
                ┌──────────────────────────────┐              │
                │ OSS Systems                  │◄─────────────┘
                │  • Nokia NSP                 │
                │  • TM Forum Open APIs        │
                │  • Tele2 Custom REST API     │
                └──────────────────────────────┘
```

## Flow

1. Commercial Project Manager creates/updates a Jira ticket in the project. Status = **Inbox**.
2. The **watcher** polls Jira every `POLL_INTERVAL` seconds for Inbox tickets.
3. The **AI agent** reads the ticket and produces a structured `ConfigPlan` (targets, operations, payloads).
4. The plan is posted as a Jira comment and (optionally) queued in the **dashboard** as pending approval.
5. A human approves in the dashboard (or the system executes directly if `DRY_RUN=false`).
6. The **executor** applies each action to the target OSS system (Nokia NSP, TM Forum, custom API).
7. Success/failure is reported back as a Jira comment and email.

## Quick Start

### Prerequisites

- **Xcode command line tools**: `xcode-select --install`
- **Homebrew**
- **uv** (Python package + env manager)

### Install

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Python + dependencies
uv sync

# 3. Copy and edit configuration
cp .env.example .env
$EDITOR .env
```

### Run

```bash
# Start the Jira inbox watcher (recommended: dry-run mode in .env)
uv run tele2-configurator watch

# Start the approval dashboard (FastAPI)
uv run tele2-configurator dashboard
# → http://localhost:8000/docs for Swagger UI
```

### Development

```bash
uv run ruff check .
uv run mypy src
uv run pytest
pre-commit install
```

## Configuration

All configuration is via environment variables (see `.env.example`). Key settings:

| Variable | Description |
|----------|-------------|
| `JIRA_URL / JIRA_USERNAME / JIRA_API_TOKEN` | Jira connection |
| `OPENAI_API_KEY / OPENAI_MODEL` | AI analyzer (`gpt-4o` default) |
| `NOKIA_NSP_URL` | Nokia Network Service Platform endpoint |
| `TMFORUM_URL` | TM Forum Open API endpoint |
| `CUSTOM_API_URL / CUSTOM_API_KEY` | Tele2 custom OSS API |
| `SMTP_*` | Email notifications (optional) |
| `DRY_RUN` | `true` = propose only (no execution); `false` = execute on approval |
| `POLL_INTERVAL` | Seconds between Jira polls |

## Project Structure

```
src/tele2_configurator/
├── main.py               # CLI entry point (watch / dashboard)
├── config.py             # Pydantic settings from env
├── models.py             # Shared Pydantic data models
├── jira/                 # Jira client + inbox watcher
├── agent/                # AI analyzer + prompts
├── oss/                  # OSS integrations + executor
├── notifications/        # Jira comments + email
├── dashboard/            # FastAPI approval UI + store
└── utils/                # Shared utilities

tests/                    # pytest suite
docs/                     # Architecture + runbooks
scripts/                  # Dev/setup scripts
docker/                   # Docker + compose
```

## Roadmap

- [x] Project scaffolding
- [x] Jira integration (watch Inbox)
- [x] AI ticket → config plan (OpenAI)
- [x] OSS executor (Nokia NSP / TM Forum / custom API)
- [x] Approval dashboard + email notifications
- [ ] Persistent approval store (SQLite/Postgres)
- [ ] Slack notifications
- [ ] Nokia NSP auth token acquisition
- [ ] Config drift detection / reconciliation
