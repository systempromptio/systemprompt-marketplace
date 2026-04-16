---
name: crm-hypothesis-ledger
description: "Append-only log of every CRM/sales action taken and whether its hypothesis passed. Provides C-### ID allocation, in-flight queries for daily-crm-brief, and maturation scoring. The spine of the hypothesis-driven sales loop."
metadata:
  version: "0.1.0"
---

# CRM Hypothesis Ledger

Append-only ledger of every CRM and sales action. The single source of truth for what we tried with leads, what we predicted, and what actually happened. Every other CRM skill writes to it.

## Dependencies

Load `crm-identity` first (for C-### format, metric whitelist, and pipeline stage definitions).

## Storage

```
/var/www/html/systemprompt-web/reports/crm/data/hypothesis-ledger.md
```

Single markdown file. One table, append-only. Newest rows at the bottom. Never rewrite history — failed predictions are the most valuable data in the ledger.

## Schema

```markdown
| id | logged | channel | action | hypothesis | metric | baseline | window_end | result | status | notes |
```

Fields:

- **id**: `C-###` sequential, zero-padded to 3 digits, allocated by this skill.
- **logged**: YYYY-MM-DD the action was taken.
- **channel**: one of `email`, `linkedin`, `github`, `call`, `demo`, `website`, `conference`, `other`.
- **action**: one-line past-tense description. Full draft/context goes in `data/actions/C-###.md`.
- **hypothesis**: the "If ... then ... within ..." statement, trimmed to one line.
- **metric**: exact field name from the metric whitelist below.
- **baseline**: numeric value of `metric` at the moment of logging (pulled from latest `pipeline-tracker` report or `pipeline-history.jsonl`).
- **window_end**: YYYY-MM-DD when the hypothesis matures. Default = logged + 14d (longer than marketing because sales cycles are slower).
- **result**: numeric value of `metric` at window_end. Empty while in-flight.
- **status**: `SEEDED` | `IN-FLIGHT` | `PASS` | `FAIL` | `INCONCLUSIVE` | `ABORTED`.
- **notes**: free text, max 140 chars.

## Metric Whitelist

These are the only valid values for the `metric` column:

```
pipeline_value_total              pipeline_deals_active
leads_new_7d                      leads_new_14d
leads_qualified_7d                leads_converted_7d
emails_sent_7d                    email_reply_rate_7d
avg_days_in_stage_{name}          deal_velocity_7d
interactions_7d                   demos_scheduled_7d
```

If a metric is not on this list, reject the log operation and ask the caller to pick a valid metric.

## Action Text Store

Full context for each hypothesis lives in:

```
/var/www/html/systemprompt-web/reports/crm/data/actions/C-###.md
```

Each file contains:
- Timestamp and skill that logged it
- Full email draft / call notes / outreach text
- Target lead(s) and their current stage
- Expected outcome and reasoning
- Post-maturation notes (added when scored)

## Operations

### `next-id`

Read `hypothesis-ledger.md`, find the highest `C-###`, return the next sequential ID.

### `log`

Inputs: channel, action, hypothesis, metric, window_days (default 14), full context text.

Steps:
1. Allocate next `C-###`.
2. Read latest `pipeline-history.jsonl` entry to fetch the current value of `metric` -> `baseline`. If `pipeline-history.jsonl` is empty, use 0 as baseline.
3. Validate `metric` is in the whitelist. Reject if not.
4. Compute `window_end` = logged + window_days.
5. Append row to ledger with `status=SEEDED` (becomes `IN-FLIGHT` once Ed confirms execution).
6. Write `data/actions/C-###.md` with context.
7. Print the assigned ID.

### `in-flight`

Print all rows where `status` is `SEEDED` or `IN-FLIGHT`.

### `maturing`

Input: date (YYYY-MM-DD).

Print rows where `window_end <= date` AND `status` is `SEEDED` or `IN-FLIGHT`. These need scoring.

### `score`

Inputs: id, result (numeric), status (PASS/FAIL/INCONCLUSIVE/ABORTED), note.

Steps:
1. Find the row by `C-###`.
2. Read the latest `pipeline-history.jsonl` to get the current value of the metric.
3. Update `result` and `status` columns in-place (this is the one exception to append-only: scoring is an update, not a new row).
4. Append post-maturation notes to `data/actions/C-###.md`.

### `stats`

Print pass/fail/inconclusive tally by channel for last 7d and 30d. Include total actions logged and average window length.

## Integration with Daily Brief

`daily-crm-brief` calls:
1. `in-flight` — to show active hypotheses
2. `maturing {today}` — to identify hypotheses that need scoring today
3. `log` — to register new actions from today's brief
4. `score` — to close out matured hypotheses

## Separation from Marketing Ledger

The CRM ledger uses `C-###` IDs. The marketing ledger uses `H-###`. The SEO ledger uses `S-###`. They are completely independent files in different directories. Do not cross-reference IDs across ledgers — they are separate namespaces.
