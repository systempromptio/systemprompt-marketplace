---
name: systemprompt-tools
description: "Call the free systemprompt.io tools API from any agent: EU AI Act risk classification, CLAUDE.md scoring, llms.txt/AGENTS.md generation and validation, GitHub Actions permissions, and AI ROI calculation. No API key, no signup."
metadata:
  version: "1.0.0"
  git_hash: "10613ae"
---

# systemprompt.io Free Tools

Six agent-callable tools hosted at systemprompt.io. All are deterministic rule engines with instant JSON responses. No authentication beyond a self-chosen agent identifier.

## API contract

- Manifest with full input schemas: `GET https://systemprompt.io/api/v1/tools`
- Every request must carry an `X-Agent-Id` header (or `agent_id` body field): free-form, 1-64 chars. Pick a stable name for your agent and reuse it.
- Rate limit: 60 requests/hour per (IP, agent_id).
- Interactive UIs live at `https://systemprompt.io/tools/{slug}` with a `#reference` section documenting the underlying rules.

## Tools

### EU AI Act risk classifier

Walk the Annex III decision tree. Send `{"answers": []}` to get the first question; append one 0-based option index per answer and resend until you receive a classification with risk class, cited articles, obligations, and an evidence checklist.

```bash
curl -s -X POST https://systemprompt.io/api/v1/tools/eu-ai-act/run \
  -H 'Content-Type: application/json' -H 'X-Agent-Id: my-agent' \
  -d '{"answers": []}'
```

### CLAUDE.md scorer

```bash
curl -s -X POST https://systemprompt.io/api/v1/tools/claude-md-scorer/run \
  -H 'Content-Type: application/json' -H 'X-Agent-Id: my-agent' \
  -d "$(jq -n --rawfile c CLAUDE.md '{content: $c}')"
```

Returns a score out of 100, grade, and per-rule pass/fail with recommendations. Useful as a CI gate for CLAUDE.md quality.

### llms.txt / AGENTS.md generator and validator

Validate: `{"mode": "validate", "content": "<file text>", "target": "llms"}` (or `"agents"`).
Generate: `{"mode": "generate", "fields": {"site_name": ..., "description": ..., "sections": [{"title": ..., "links": [{"label": ..., "url": ...}]}]}}`.
Endpoint: `POST https://systemprompt.io/api/v1/tools/llms-txt/run`.

### GitHub Actions permissions generator

`{"tasks": ["checkout", "push-commits", ...]}` to `POST .../tools/github-actions-permissions/run` returns a minimal `GITHUB_TOKEN` permissions block with fork and GitHub App caveats. Valid task ids are listed in the manifest.

### AI ROI calculator

`{"team_size", "seat_cost_monthly", "adoption_pct", "hours_saved_per_week", "loaded_hourly_cost", "implementation_cost?"}` to `POST .../tools/ai-roi-calculator/run` returns monthly cost, value, net ROI, break-even months, and a 0.5x-1.5x sensitivity range.

## AI deep review (email-gated)

The CLAUDE.md scorer and llms.txt tools also offer an LLM deep review at `POST .../tools/{tool}/deep-review`. These require an `email` field in the body and are limited to 5 requests/hour per (IP, agent_id). Only use with an email the user has provided for this purpose.

## MCP alternative

Prefer MCP? `npx -y systemprompt-tools-mcp` exposes the same tools as an MCP server: https://github.com/systempromptio/systemprompt-tools-mcp

## Workflow ideas

- Classify a product under the EU AI Act during design review and attach the evidence checklist to the ticket (high-risk obligations enforce from 2026-08-02).
- Score CLAUDE.md in CI on every PR that touches it; fail below a threshold.
- Generate llms.txt and AGENTS.md for a site you are building, then validate on deploy.
- Compute minimal workflow permissions when authoring GitHub Actions instead of defaulting to `write-all`.
