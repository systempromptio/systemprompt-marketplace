---
name: hypothesis-ledger
description: "Append-only log of every marketing action taken and whether its hypothesis passed. Provides H-### ID allocation, in-flight queries for daily-marketing-brief, and maturation scoring for weekly-marketing-review. The spine of the hypothesis-driven marketing loop."
metadata:
  version: "0.1.0"
---

# Hypothesis Ledger

Append-only ledger of every marketing action. The single source of truth for what we tried, what we predicted, and what actually happened. Every other marketing-strategy skill writes to it.

## Storage

```
{project_root}/reports/marketing/data/hypothesis-ledger.md
(e.g. /var/www/html/systemprompt-web/reports/marketing/data/hypothesis-ledger.md)
```

Single markdown file. One table, append-only. Newest rows at the bottom. Never rewrite history — failed predictions are the most valuable data in the ledger.

## Schema

```markdown
# Hypothesis Ledger

| id | logged | channel | action | hypothesis | metric | baseline | window_end | result | status | notes |
|----|--------|---------|--------|-----------|--------|----------|------------|--------|--------|-------|
| H-001 | 2026-04-16 | reddit | "Posted teardown to r/mcp" | template unique cloners/7d ≥ 70 | template_cloners_7d | 47 | 2026-04-23 | 58 | FAIL | partial lift, wrong subreddit day |
```

Fields:

- **id**: `H-###` sequential, zero-padded to 3 digits, allocated by this skill.
- **logged**: YYYY-MM-DD the action was taken.
- **channel**: one of `reddit`, `linkedin`, `x`, `github`, `website`, `blog`, `newsletter`, `discord`, `crates`, `other`.
- **action**: one-line past-tense description. The actual post/DM/PR text goes in `actions/H-###.md` (see below).
- **hypothesis**: the "If ... then ... within ..." statement, trimmed to one line.
- **metric**: exact field name from `lead-tracker` output that will be read at window close. Must be one of the metrics `lead-tracker` emits — this skill validates on append.
- **baseline**: numeric value of `metric` at the moment of logging (pulled from latest `lead-tracker` report).
- **window_end**: YYYY-MM-DD when the hypothesis matures. Default = logged + 7d.
- **result**: numeric value of `metric` at window_end. Empty while in-flight.
- **status**: `IN-FLIGHT` | `PASS` | `FAIL` | `INCONCLUSIVE` (insufficient data) | `ABORTED` (withdrawn before maturation).
- **notes**: free text, ≤140 chars.

## Action Text Store

Full drafts and context live in a sibling directory:

```
{project_root}/reports/marketing/data/actions/H-###.md
```

Each file contains: timestamp, full post/DM draft, target URL, Ed's post-hoc notes, any screenshots/links collected on maturation. The ledger table stays compact; the story lives in the action file.

## Operations

```
hypothesis-ledger next-id           # Allocates next H-### (no append yet)
hypothesis-ledger log {fields...}   # Append new IN-FLIGHT row + write actions/H-###.md
hypothesis-ledger in-flight         # Print rows where status=IN-FLIGHT
hypothesis-ledger maturing {date}   # Print rows where window_end <= date AND status=IN-FLIGHT
hypothesis-ledger score {id} {result} {status} {note}   # Close out a row
hypothesis-ledger stats             # Pass/fail tally by channel, last 7d / 30d
```

### `log` operation

Inputs required: channel, action, hypothesis, metric, window_days (default 7), full draft text.

Steps:
1. Allocate next `H-###`.
2. Run `lead-tracker latest` to fetch the current value of `metric` → `baseline`.
3. Validate `metric` is in the `lead-tracker` metric whitelist (see below). Reject if not.
4. Append row to ledger with `status=IN-FLIGHT`.
5. Write `actions/H-###.md` with draft, timestamp, logged-by skill, target URL.
6. Print the assigned ID so the caller can reference it.

### `score` operation

Inputs: id, result, status, note.

Steps:
1. Read the row, confirm status is `IN-FLIGHT`.
2. Append a **new row** with the same id and the closed-out values. **Never edit existing rows.** (Append-only means append-only; the most recent row for each id wins.)
3. If `status=PASS`, emit a `marketing-strategy-master diff` suggestion to move this into §4 Winning Tactics.
4. If `status=FAIL`, emit a `marketing-strategy-master diff` suggestion to move this into §5 Dead Hypotheses.

## Metric Whitelist

Only these metric names are valid (they come directly from `lead-tracker` output fields):

```
template_cloners_1d        template_cloners_7d        template_cloners_31d
template_views_1d          template_views_7d          template_views_31d
template_stars_delta_7d    template_stars_delta_31d
template_referrer_{name}_7d      (e.g. template_referrer_github_7d)
core_cloners_1d            core_cloners_7d            core_cloners_31d
core_views_1d              core_views_7d              core_views_31d
core_stars_delta_7d        core_stars_delta_31d
core_referrer_{name}_7d
web_sessions_7d            web_sessions_31d
web_unique_users_7d        web_unique_users_31d
web_content_{slug}_views_7d
web_traffic_{source}_7d    (e.g. web_traffic_github_7d)
leads_new_7d               leads_new_31d
leads_total
qualified_convos_7d        qualified_convos_31d
```

Any metric not in this list is rejected. This forces every hypothesis to target something we can actually measure.

## Seeding

On first run, if ledger file doesn't exist:
1. Create `data/hypothesis-ledger.md` with the header and empty table.
2. Create `data/actions/` directory.
3. Pre-populate with 10 starter hypotheses as `IN-FLIGHT` drafts (unposted) that `daily-marketing-brief` can promote to live actions. These are the Phase 2 channel tests from the plan.

## Anti-Sludge Rules

- Never allow a row with no metric, no numeric baseline, or no window_end.
- If `lead-tracker` has no data yet for a metric, `baseline` is `null` and the hypothesis is auto-aborted with a note "awaiting baseline."
- Never summarise the ledger in prose where a table will do.
- An "inconclusive" result is only valid if `lead-tracker` was unavailable at maturation — not as a cop-out for weak signal.
