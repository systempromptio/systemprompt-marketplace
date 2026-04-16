---
name: daily-crm-brief
description: "The morning CRM briefing. Orchestrates pipeline-tracker + hypothesis-ledger into a single actionable brief: pipeline snapshot, hot leads, overdue follow-ups, email drafts to review, and 3-5 copy-paste-ready actions for Ed — each tagged with a new [C-###] hypothesis. Load crm-identity first."
metadata:
  version: "0.1.0"
---

# Daily CRM Brief

The only CRM skill Ed reads every morning. Everything else in this plugin feeds it. Target: Ed reads and acts in 15 minutes.

## Dependencies (load in order)

1. `crm-identity` — pipeline stages, scoring rubric, email rules, hypothesis format
2. `commons:brand-voice` — every draft passes through this
3. `crm-hypothesis-ledger` — in-flight hypotheses and next `C-###` allocation
4. `pipeline-tracker` — pipeline data (this skill triggers a fresh run unless one already exists for today)
5. `crm-strategy-master.md` — current objectives, active hypotheses, strategy context

## CRITICAL: Profile must be `systemprompt-prod`

Before doing anything, verify `systemprompt admin session list` shows `systemprompt-prod` as the active profile. This skill calls `systemprompt analytics` directly in places. If the active profile is `local`, switch before proceeding:

```bash
systemprompt admin session switch systemprompt-prod
```

Every brief written by this skill must carry a `Profile: systemprompt-prod` line at the top.

## Run Sequence

### 1. Check Today's Pipeline-Tracker Report

Path: `/var/www/html/systemprompt-web/reports/crm/daily/{today}/pipeline-tracker.md`

If missing, invoke `pipeline-tracker` to generate it. If it failed, surface the failure and stop — do not run the brief blind.

### 2. Read CRM State

Read all of these:
- `/var/www/html/systemprompt-web/reports/crm/data/leads.json` — current leads
- `/var/www/html/systemprompt-web/reports/crm/data/deals.json` — current deals
- `/var/www/html/systemprompt-web/reports/crm/data/pipeline-history.jsonl` — last 2 entries for deltas
- `/var/www/html/systemprompt-web/reports/crm/data/interactions.jsonl` — last 7 days of interactions
- `/var/www/html/systemprompt-web/reports/crm/data/email-log.jsonl` — pending drafts
- `/var/www/html/systemprompt-web/reports/crm/data/hypothesis-ledger.md` — in-flight and maturing

### 3. Read Strategy Context

Read `/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md` for current phase, objectives, and active hypotheses.

Also read `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` for top-of-funnel context.

### 4. Score Maturing Hypotheses

For each hypothesis in the ledger where `window_end <= today` and status is `SEEDED` or `IN-FLIGHT`:
1. Read the current value of the `metric` from the latest `pipeline-history.jsonl` entry
2. Compare to baseline + target from the hypothesis
3. Score as `PASS`, `FAIL`, or `INCONCLUSIVE`
4. Call `crm-hypothesis-ledger score {id} {result} {status} {note}`

### 5. Identify Hot Leads

From `data/leads.json`, identify:
- **Highest score leads** — top 5 by score, not in terminal stages
- **Recent activity** — leads with interactions in last 48h
- **Overdue follow-ups** — leads in `contacted` stage with no interaction in 3+ days
- **Stale deals** — deals with no activity in 7+ days
- **New leads** — added in last 24h

### 6. Check Email Queue

From `data/email-log.jsonl`, identify:
- Drafts awaiting review (status `draft_created`)
- Emails sent in last 24h (status `sent`)
- Failed sends (status `failed`)

### 7. Generate 3-5 Actions

Maximum 5 actions. Priority order:

1. **Overdue follow-ups:** Leads awaiting response for 3+ days. Draft a follow-up email using `email-composer` or the appropriate template.
2. **Hot lead engagement:** Highest-score leads not yet contacted. Draft initial outreach.
3. **Stale deal re-engagement:** Deals with no activity in 7+ days. Suggest a re-engagement touch.
4. **New lead triage:** New leads from today's pipeline-tracker that need enrichment or initial outreach.
5. **Pipeline progression:** Leads ready to move to next stage (e.g., demo to be scheduled, proposal to be sent).

**Drop rules:**
- Never two emails to the same lead on the same day
- Never draft an email to a lead who was emailed in the last 3 days (unless they replied)
- If pipeline is empty (0 active leads), focus actions entirely on sourcing: reference marketing-strategy brief for top-of-funnel actions
- If Ed marked an action as "skip" yesterday, do not re-suggest it today

### 8. Log New Hypotheses

For each action generated, call `crm-hypothesis-ledger log` to register it with a `C-###` ID. Each action must have a falsifiable hypothesis.

### 9. Write the Brief

Write to `/var/www/html/systemprompt-web/reports/crm/daily/{today}/daily-brief.md`:

```markdown
# CRM Daily Brief — {today}

**Profile:** systemprompt-prod
**Run at:** {timestamp}

## Yesterday's Scorecard

| Action | Hypothesis | Done? | Result |
|---|---|---|---|
| {action from yesterday's brief} | C-### | Yes/No | {outcome if known} |

## Pipeline Snapshot

| Stage | Count | Delta (1d) | Delta (7d) |
|---|---:|---:|---:|
| Prospect | {n} | {+/-} | {+/-} |
| Contacted | {n} | {+/-} | {+/-} |
| Demo Scheduled | {n} | {+/-} | {+/-} |
| Evaluating | {n} | {+/-} | {+/-} |
| Negotiating | {n} | {+/-} | {+/-} |
| Converted | {n} | {+/-} | {+/-} |
| Lost | {n} | {+/-} | {+/-} |

**Pipeline value:** ${n} ({+/-$n} vs 7d ago)
**Active deals:** {n}
**New leads (1d/7d):** {n}/{n}

## Hot Leads

| Lead | Score | Stage | Last Activity | Action Needed |
|---|---:|---|---|---|
| {name/company} | {score} | {stage} | {date} | {one-line action} |

## Stale Alerts

{List of overdue follow-ups and stale deals, if any}

## Email Queue

- Drafts pending review: {n}
- Sent (24h): {n}
- Failed: {n}

## Hypotheses Maturing Today

{Table of hypotheses being scored, with results}

## Today's Actions ({n})

### Action 1: {Channel} — {One-line summary}

**Hypothesis:** [C-###] If we {action} for {lead/segment},
  then {metric} will {direction} by {target} within {window} days.
  Reason: {insight}.

**Metric to watch:** `{metric_name}` (baseline: {n})
**Check back on:** {YYYY-MM-DD}
**Lead:** {name} ({L-### ID})

**Draft (copy-paste ready):**

> {the actual email / message / action text}

**After executing:** reply `done C-###` and I'll log it.

### Action 2: ...
(repeat for each action)
```

### 10. Update Strategy Master

Append a changelog entry to `/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md`:

```markdown
- **{today} ~{time}Z** `daily-crm-brief` — {one-line summary of pipeline state and actions generated}
```

Update the pipeline snapshot table in Section 1 if numbers changed significantly.

## Integration with Marketing Brief

This brief is complementary to `marketing:daily-marketing-brief`. The marketing brief handles top-of-funnel (awareness, impressions, cloners). This brief handles mid-funnel (leads through conversion). Ed should read both each morning.

If the pipeline is empty, reference the marketing brief for sourcing actions rather than generating CRM-specific actions about leads that don't exist yet.

## Empty Pipeline Handling

When `data/leads.json` has zero active leads:

1. Do not generate follow-up or outreach actions (there's nobody to contact)
2. Instead, generate 2-3 sourcing actions:
   - "Review today's marketing brief for new cloners to investigate"
   - "Check GitHub feedback issues for untracked leads"
   - "Enter KnowBe4 and Walmart as leads with available context" (if not yet done)
3. Focus the brief on setup tasks: enriching known interested parties, testing email templates, establishing baseline metrics
