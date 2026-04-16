---
name: daily-brief-pattern
description: "Shared daily briefing pattern. Defines the orchestration sequence, action selection, and report format for SEO/marketing/CRM morning briefs."
metadata:
  version: "1.0.0"
  git_hash: "5079c7a"
---

# Daily Brief Pattern

Every domain has a daily briefing skill that Ed reads each morning. This pattern defines the shared orchestration sequence, action format, and quality rules. Domain briefs configure it with their own data sources, report paths, and action types.

## Principle

The brief is the only thing Ed reads per domain each morning. Everything else in the domain feeds it. Target: Ed reads and executes the actions in 20 minutes over one coffee.

## Run Sequence

Every daily brief follows these 8 steps in order:

### Step 1: Verify Data Context

Confirm the correct production profile/authentication is active. Domain briefs specify their profile check. Running against a dev/local profile produces silently wrong numbers. Every brief must carry a profile verification line at the top.

### Step 2: Check Today's Data Report

Check that the domain's data collection report exists for today. Path pattern: `reports/{domain}/daily/{YYYY-MM-DD}/{report-name}.md`. If missing, trigger the data collection skill. If the data collection fails, surface the failure and stop. Never run the brief blind.

### Step 3: Read Strategy Document

Load the domain's strategy master for current phase, priorities, and channel weights.

### Step 4: Read Hypotheses

Query the domain's hypothesis ledger:
- `in-flight`: all active hypotheses
- `maturing {today}`: hypotheses whose window_end <= today

### Step 5: Score Maturing Hypotheses

For each hypothesis where `window_end <= today`:
1. Pull the current value of `metric` from today's data report.
2. Compare to baseline + target.
3. Call `score {id} {result} {PASS|FAIL|INCONCLUSIVE} {note}`.
4. Emit the result in the brief.

### Step 6: Generate Actions

Generate 3-5 actions for today. Selection priority:

1. **Dues:** actions from previous day's brief that were confirmed but not yet scored.
2. **Theme-aligned:** 2-3 actions matching the current weekly/phase theme from the strategy master.
3. **Channel-balanced:** weighted by channel priorities in the strategy master. Do not over-sample one channel unless explicitly prioritised.
4. **One experiment:** one net-new hypothesis in a channel not tested in >= 7 days. Bias toward learning when data is thin.
5. **Floor rules:** domain-specific minimum actions when key metrics are zero (e.g., if leads = 0 for 3+ days, force a direct outreach action).

### Step 7: Log Actions

Each generated action is logged to the hypothesis ledger via `log`. Each gets a new {PREFIX}-### ID and a full draft written to `data/actions/{PREFIX}-###.md`.

### Step 8: Write the Brief

Write the brief to `reports/{domain}/daily/{YYYY-MM-DD}/{brief-name}.md` and print to Ed.

## Drop Rules

- Maximum 5 actions per brief.
- No action without a measurable hypothesis.
- No repeat of an approach that failed in the past 14 days (check Dead Hypotheses).
- No action targeting a channel where 3+ hypotheses are already in-flight.
- If the data collection step failed, do not generate actions. Report the failure only.

## Output Format

```markdown
# {Domain} Brief -- {YYYY-MM-DD}

**Profile:** {production profile name}

## Headline
{One sentence: most important thing that changed since yesterday}

## Metric Snapshot

| Metric | Today | 7d ago | 31d ago | Delta (7d) |
|--------|------:|-------:|--------:|-----------:|

## Hypothesis Status

### Maturing Today
| ID | Action | Metric | Baseline | Result | Verdict |
|----|--------|--------|----------|--------|---------|

### In-Flight ({N} total)
{Summary of active hypotheses by channel}

## Today's Actions

### 1. {Action title} [{PREFIX}-###]
**Channel:** {channel}
**Hypothesis:** If {action} then {metric} {direction} within {window}
**Copy-paste ready:**
{The exact text/command/draft Ed needs to execute}

### 2. ...
(repeat for 3-5 actions)
```

## Domain Configuration

| Config | SEO | Marketing | CRM |
|--------|-----|-----------|-----|
| Brief name | seo-monitor.md | daily-brief.md | daily-crm-brief.md |
| Report path | reports/seo/daily/ | reports/marketing/daily/ | reports/crm/daily/ |
| Data source skill | seo-monitor (self) | lead-tracker | pipeline-tracker |
| Hypothesis prefix | S-### | H-### | C-### |
| Profile check | GSC service account | systemprompt-prod | systemprompt-prod |
| Floor rule | — | If leads_new_7d = 0 for 3+ days, force direct outreach | If deals_active = 0, force pipeline action |
