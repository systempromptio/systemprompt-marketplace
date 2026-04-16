---
name: pipeline-tracker
description: "Daily CRM data collection. Pulls GitHub Traffic API, website analytics, and marketing-strategy lead-tracker data. Updates leads.json and deals.json, snapshots pipeline state to pipeline-history.jsonl, and writes a dated report. Source of truth for all CRM metrics."
metadata:
  version: "0.1.0"
---

# Pipeline Tracker

The measurable truth for the CRM. Runs daily. Pulls every signal we have into a single pipeline report and updates the persistent lead and deal databases. Every `crm-hypothesis-ledger` metric resolves here.

## Why This Must Run Daily

1. **GitHub Traffic API retains only 14 days.** Missing runs means lost clone data.
2. **Pipeline staleness detection** requires daily snapshots to flag leads/deals with no activity.
3. **Hypothesis maturation** depends on daily metric snapshots for scoring.

Production cadence is daily via `/loop`, ideally after `marketing:lead-tracker` completes (so we can read its output).

## Dependencies

Load `crm-identity` first (for pipeline stage definitions, scoring rubric, and exclusion list).

The `marketing:lead-tracker` report for today should exist before this skill runs. Check `/var/www/html/systemprompt-web/reports/marketing/daily/{today}/lead-tracker.md`. If missing, tell Ed to run `lead-tracker` first — do not run it yourself (it has its own profile requirements).

## CRITICAL: Profile must be `systemprompt-prod` for analytics reads

Before running any `systemprompt analytics *` command, verify the active profile:

```bash
systemprompt admin session list --json 2>&1 | grep -A1 '"is_active": true' | head -3
```

If not `systemprompt-prod`, switch:

```bash
systemprompt admin session switch systemprompt-prod
```

Every report this skill writes must include a top-line `Profile: systemprompt-prod` marker.

## Run Sequence

### Step 1: Read Current State

Read the current `data/leads.json` and `data/deals.json` to understand the starting position.

### Step 2: Pull Fresh Data

#### 2a. GitHub Traffic API (both repos)

```bash
# Template repo — primary lead signal
gh api repos/systempromptio/systemprompt-template/traffic/clones
gh api repos/systempromptio/systemprompt-template/traffic/views
gh api repos/systempromptio/systemprompt-template/traffic/popular/referrers

# Core repo — secondary signal
gh api repos/systempromptio/systemprompt-core/traffic/clones
gh api repos/systempromptio/systemprompt-core/traffic/views
```

Extract unique cloners from the last 24h. Cross-reference against `leads.json` — any new unique cloner not in leads and not in the exclusion list should be added as a `prospect` with source `github_clone`.

**Anomaly flag:** If any single day has raw clones > 5x the median of non-zero days, flag as `probable_automation` and exclude from new lead creation.

#### 2b. GitHub Issues with `feedback` Label

```bash
gh api search/issues -f q="repo:systempromptio/systemprompt-template label:feedback created:>={yesterday}" --jq '.items[] | {user: .user.login, title: .title, html_url: .html_url, created_at: .created_at}'
gh api search/issues -f q="repo:systempromptio/systemprompt-core label:feedback created:>={yesterday}" --jq '.items[] | {user: .user.login, title: .title, html_url: .html_url, created_at: .created_at}'
```

For each feedback issue:
- If the user is already a lead, bump their stage to at least `contacted` (if currently `prospect`) and add 25 points for `feedback_given`
- If the user is new, create a lead with source `github_clone`, stage `prospect`, score including `feedback_given`
- Create an interaction record of type `github_issue` in `data/interactions.jsonl`

#### 2c. Website Analytics

```bash
systemprompt analytics sessions list --limit 50 --since 1d
systemprompt analytics traffic overview --since 7d
```

Look for:
- Return visitors (3+ sessions) — if matchable to a known lead, add `website_return_visit` score
- Demo request form submissions — create leads with source `demo_request` and +30 score
- High-engagement sessions (duration > 5min, 3+ pages) on guides — note as enrichment data

#### 2d. Check Email Log for Recent Activity

Read `/var/www/html/systemprompt-web/reports/crm/data/email-log.jsonl` for emails sent/received in the last 24h. Cross-reference with `interactions.jsonl` to ensure all email activity is logged.

**Note:** Inbound email detection is manual. If Ed received a reply from a lead, he should tell the CRM skill to log it as an interaction. This skill does not read inboxes.

#### 2e. Read Today's Marketing Lead-Tracker Report

Read `/var/www/html/systemprompt-web/reports/marketing/daily/{today}/lead-tracker.md` for:
- Aggregate funnel numbers (for pipeline-history snapshot)
- Any new signals not captured above
- GSC metrics for context

### Step 3: Update Lead Scores

For each active, non-excluded lead in `data/leads.json`:
1. Recalculate score based on all available signals (using rubric from `crm-identity`)
2. Update `score` and `score_breakdown` fields
3. Update `updated_at` timestamp

### Step 4: Flag Stale Deals

For each open deal in `data/deals.json`:
- If `last_activity` is > 7 days ago, add a `stale` flag
- If `last_activity` is > 14 days ago, add a `critical_stale` flag
- If `expected_close` is past and deal is still open, add an `overdue` flag

### Step 5: Snapshot Pipeline State

Append one line to `data/pipeline-history.jsonl`:

```json
{
  "run_at": "{ISO timestamp}",
  "run_by": "pipeline-tracker v0.1.0",
  "profile": "systemprompt-prod",
  "pipeline": {
    "prospect": {count},
    "contacted": {count},
    "demo_scheduled": {count},
    "evaluating": {count},
    "negotiating": {count},
    "converted": {count},
    "lost": {count}
  },
  "total_leads": {count},
  "total_active_deals": {count},
  "total_pipeline_value_usd": {sum},
  "new_leads_1d": {count},
  "new_leads_7d": {count},
  "stage_changes_1d": {count},
  "emails_sent_1d": {count from email-log.jsonl},
  "flags": ["{any anomalies detected}"]
}
```

### Step 6: Compute Deltas

Compare today's snapshot to yesterday's (read previous line from `pipeline-history.jsonl`). Calculate:
- Lead count deltas by stage
- New leads (1d, 7d)
- Pipeline value change
- Deal stage movements

### Step 7: Write Daily Report

Write to `/var/www/html/systemprompt-web/reports/crm/daily/{today}/pipeline-tracker.md`:

```markdown
# Pipeline Tracker — {today}

**Profile:** systemprompt-prod
**Run at:** {timestamp}
**Run by:** pipeline-tracker v0.1.0

## Pipeline Summary

| Stage | Count | Delta (1d) |
|---|---:|---:|
| Prospect | {n} | {+/-n} |
| Contacted | {n} | {+/-n} |
| ... | | |

**Total leads:** {n} ({+/-n} vs yesterday)
**Active deals:** {n} (${value} pipeline value)
**New leads today:** {n}

## New Leads Added

{table of any leads added today with source, score, and notes}

## Stage Changes

{table of any leads that changed stage today}

## Stale Alerts

{list of deals/leads flagged as stale or overdue}

## Interactions Today

{summary of all interactions logged today from interactions.jsonl}

## Data Sources

- GitHub Traffic API: {status}
- Website Analytics: {status}
- Email log: {status}
- Marketing Lead-Tracker: {status}
```

### Step 8: Save Updated State

Write the updated `data/leads.json` and `data/deals.json` with all changes from this run.

## Error Handling

- If GitHub API returns 403, note it in the report but continue with other data sources
- If `systemprompt analytics` fails, note it and skip website data
- If email-log.jsonl is empty or missing, note it and continue
- Never fail silently — every data source should have a status line in the report
- If `leads.json` or `deals.json` is corrupted, stop and tell Ed — do not overwrite

## Output

After completing all steps, print a brief summary:
- New leads added: {n}
- Stage changes: {n}
- Stale alerts: {n}
- Pipeline value: ${n}
- Report written to: {path}
