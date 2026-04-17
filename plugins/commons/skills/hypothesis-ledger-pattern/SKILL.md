---
name: hypothesis-ledger-pattern
description: "Shared append-only hypothesis ledger pattern. Defines schema, operations, and rules for S-###/H-###/C-###/CT-### ledgers across SEO, marketing, CRM, and content domains."
metadata:
  version: "1.3.0"
  git_hash: "c05387b"
---

# Hypothesis Ledger Pattern

Every action across every domain is logged as a falsifiable hypothesis with a measurable outcome. This pattern defines the shared infrastructure. Domain ledgers (SEO, marketing, CRM) configure it with their own prefix, window, path, and metrics.

## Principle

No action without a hypothesis. No hypothesis without a metric. No metric without a baseline. Every row is append-only. History is never rewritten.

## Storage

Each domain stores its ledger at:

```
/var/www/html/systemprompt-web/reports/{domain}/data/hypothesis-ledger.md
```

Single markdown file. One table. Newest rows at the bottom.

## Schema

```markdown
| id | logged | channel | action | hypothesis | metric | baseline | window_end | result | status | notes |
```

| Field | Description |
|-------|-------------|
| id | `{PREFIX}-###` sequential, zero-padded to 3 digits. Each domain has its own namespace. |
| logged | YYYY-MM-DD the action was taken. |
| channel | Domain-specific enum (see domain config below). |
| action | One-line past-tense description. Full draft goes in `data/actions/{PREFIX}-###.md`. |
| hypothesis | "If ... then ... within ..." statement, trimmed to one line. Must be falsifiable. |
| metric | Exact field name from the domain's metric whitelist (validated on append). |
| baseline | Numeric value of metric at the moment of logging. |
| window_end | YYYY-MM-DD when the hypothesis matures. Uses domain default window. |
| result | Numeric value of metric at window_end. Empty while in-flight. |
| status | IN-FLIGHT, SEEDED, PASS, FAIL, INCONCLUSIVE, or ABORTED. |
| notes | Free text, max 140 characters. |

## Status Lifecycle

```
SEEDED → IN-FLIGHT → PASS | FAIL | INCONCLUSIVE
                   → ABORTED (if conditions change before window_end)
```

- **SEEDED:** hypothesis logged but prerequisites not yet met (e.g., waiting for indexing)
- **IN-FLIGHT:** action taken, waiting for window_end
- **PASS/FAIL/INCONCLUSIVE:** scored at or after window_end

## Action Text Store

Full context for each action lives in:

```
reports/{domain}/data/actions/{PREFIX}-###.md
```

Each file contains: timestamp, what was changed, before/after values, target URLs, measurement notes.

## Operations

Every domain ledger implements these 6 operations:

| Operation | Description |
|-----------|-------------|
| `next-id` | Allocate the next sequential {PREFIX}-### ID |
| `log {fields}` | Append new row + write actions/{PREFIX}-###.md |
| `in-flight` | Return rows where status = IN-FLIGHT |
| `maturing {date}` | Return rows where window_end <= date AND status = IN-FLIGHT |
| `score {id} {result} {status} {note}` | Close out a hypothesis row |
| `stats` | Pass/fail tally by channel |

### Log operation

1. Allocate next ID via `next-id`.
2. Pull current value of `metric` from the domain's data source (monitor report, GSC data, analytics).
3. Validate `metric` is in the domain's whitelist. Reject if not.
4. Append row to ledger with status = IN-FLIGHT or SEEDED.
5. Write `actions/{PREFIX}-###.md` with full context.
6. Return the assigned ID.

### Score operation

1. Read the row, confirm status is IN-FLIGHT.
2. Append a **new row** with the same ID and closed-out values. **Never edit existing rows.**
3. If PASS, emit a diff suggestion for the strategy master's Winning Tactics section.
4. If FAIL, emit a diff suggestion for the Dead Hypotheses section.

## Anti-Sludge Rules

- Every hypothesis must be falsifiable: it must name a specific metric, a baseline, and a target direction.
- Every metric must come from the domain's validated whitelist. No invented metrics.
- Rows are never edited in place. Corrections are appended as new rows.
- No hypothesis without a measurable outcome. "Improve brand awareness" is not a hypothesis.
- No action without a logged hypothesis. If you take an action, log it.

## Domain Configuration

| Config | SEO | Marketing | CRM | Content |
|--------|-----|-----------|-----|---------|
| Prefix | S-### | H-### | C-### | CT-### |
| Default window | 14 days | 7 days | 14 days | 14 days |
| Storage path | reports/seo/data/ | reports/marketing/data/ | reports/crm/data/ | reports/content/data/ |
| Actions path | reports/seo/data/actions/ | reports/marketing/data/actions/ | reports/crm/data/actions/ | reports/content/data/actions/ |
| Metric source | GSC + DataForSEO + daily-seo-brief | lead-tracker + analytics | pipeline-tracker + lead-enrichment | daily-seo-brief |
| Strategy master | seo-strategy-master | marketing-strategy-master | crm-strategy-master | content-strategy-master |
| Channels | seo, content, technical, linking, indexing, ctr | reddit, linkedin, x, hn, crates, website, email, seo, ai-agent | pipeline, email, enrichment, outreach | optimisation, new-guide, revision, distribution, technical |

Note: Social media uses the marketing ledger (H-### prefix). Social hypotheses are a subset of marketing hypotheses, not a separate ledger.

Domain ledger skills (seo:seo-hypothesis-ledger, commons:marketing-hypothesis-ledger, crm:crm-hypothesis-ledger, content:content-hypothesis-ledger) reference this pattern and add their specific metric whitelist and channel enum.
