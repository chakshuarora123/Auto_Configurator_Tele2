# Architecture Decisions

## 1. AI Agent → Config Plan (Structured Output)

**Context:** The OpenAI `response_format={"type": "json_object"}` forces valid JSON, and we parse it
into a validated `ConfigPlan` Pydantic model. This gives deterministic, typed output instead of raw
LLM text.

**Decision:** Use JSON mode + Pydantic validation. Reject/retry plans that fail to parse.

**Trade-off:** Field schemas must match the LLM prompt. Any prompt change requires updating
`prompts.py` and `models.py` together.

## 2. Approval Gate with DRY_RUN

**Context:** OSS changes carry real operational risk (customer impact, billing errors).

**Decision:** Default to `DRY_RUN=true` — the agent proposes, a human approves in the dashboard.
Flip to `false` only after validation.

## 3. System Selection

- **Nokia NSP** — configured for network/service provisioning.
- **TM Forum Open APIs** — standardized catalogue/inventory operations across BSS.
- **Tele2 custom API** — proprietary endpoints.

Each is behind a common `RestClient` interface so the executor is system-agnostic.
