---
name: daily-master-brief
description: "The single morning entry point. Orchestrates all 5 domain briefs (SEO, marketing, CRM, social, content) into one unified report answering: strategy effectiveness, pipeline growth, what's working, what's not, today's priorities, and system health."
metadata:
  version: "1.1.0"
  git_hash: "c05387b"
---

# Daily Master Brief

The one skill Ed runs every morning. Reads all 5 domain briefs and produces a single unified report that answers 9 business questions. This is the operator's command centre — it curates, correlates, and prioritises across all domains.

## Principle

Ed should never need to read 5 separate briefs to understand the state of the business. The master brief answers the 9 KPIs in 10 minutes. Domain briefs are drill-down documents — the master brief is the dashboard.

## Autonomy Contract (READ BEFORE ACTING)

This skill runs end-to-end without user confirmation between domains. Do not ask Ed "should I run the {X} brief?" — invoke it via the Skill tool and move on.

Exactly **two** user-facing gates exist in this skill's run:

1. **Step 0 — Yesterday Debrief.** One structured question batch at the very top. Four grouped prompts in a single invocation. After Ed answers, persist the data and proceed silently.
2. **Downstream action execution.** When Ed later chooses to execute a proposed action, the downstream skills (`email-composer`, `reddit-reply`, `content-publish`, etc.) run their own approval flows. Not this skill's concern.

Everything in between — data collection, hypothesis scoring, action generation, brief writing — is fully autonomous.

The only permitted unscheduled pause is an auth failure on `systemprompt-prod` that persists after one retry. Missing data, stale reports, API errors, empty ledgers, failed sub-briefs — all are handled by degrading gracefully and noting the degradation in Section 6 (System Health).

If every sub-brief fails, still produce the master brief. Never return control to Ed without a written report at `reports/master/daily/{today}/daily-master-brief.md`.

## Dependencies (load in order)

1. `commons:identity` — product positioning, ICP

Also read:
- `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — cross-domain strategy, funnel definition, domain weights
- All 5 domain briefs for today (see Domain Brief Map below)
- All 4 hypothesis ledgers (SEO, marketing, CRM, content)
- All 5 strategy master documents

## CRITICAL: Profile must be `systemprompt-prod`

Before this skill does anything, verify `systemprompt admin session list` shows `systemprompt-prod` as the active profile. Every domain brief enforces this independently, but the master brief must also verify because it reads hypothesis ledger stats directly.

```bash
systemprompt admin session switch systemprompt-prod
```

## The 9 KPIs This Brief Must Answer

Every run of this skill must produce a report that explicitly answers:

1. **How effective are our strategies?** — Hypothesis win rates by domain with trends
2. **Are our strategies up to date?** — Last-updated timestamps on all strategy masters with staleness warnings
3. **How many people have we put in the pipeline?** — Pipeline deltas (7d/31d) with new lead counts
4. **Where did they come from?** — Full funnel attribution: which domain drove which stage
5. **How can we improve?** — Cross-domain signals: broken funnels, gaps, missed opportunities
6. **What is working?** — Hypotheses that PASSED today, winning tactics
7. **What is not working?** — Hypotheses that FAILED today, dead hypotheses
8. **What do we need to do today?** — All priority actions curated from all domain briefs, ranked by strategic weight, with the top 5 marked PRIORITY
9. **Is everything consistent, standardised and updated?** — System health: stale briefs, missing reports, overdue hypotheses

If the brief cannot answer any of these, it must say why (missing data, stale brief, failed collection) — never skip silently.

## Domain Brief Map

| Domain | Brief Skill | Report Path | Hypothesis Prefix |
|--------|------------|-------------|-------------------|
| SEO | `seo:daily-seo-brief` | `reports/seo/daily/{today}/daily-seo-brief.md` | S-### |
| Marketing | `commons:daily-marketing-brief` | `reports/marketing/daily/{today}/daily-brief.md` | H-### |
| CRM | `crm:daily-crm-brief` | `reports/crm/daily/{today}/daily-brief.md` | C-### |
| Social Media | `social-media:daily-social-brief` | `reports/social/daily/{today}/daily-social-brief.md` | H-### (shared with marketing) |
| Content | `content:daily-content-brief` | `reports/content/daily/{today}/daily-content-brief.md` | CT-### |

## Strategy Master Map

| Domain | Path | North Star |
|--------|------|-----------|
| SEO | `reports/seo/seo-strategy-master.md` | Organic sessions/week + GSC clicks/week |
| Marketing | `reports/marketing/marketing-strategy-master.md` | Qualified leads/week |
| CRM | `reports/crm/crm-strategy-master.md` | Deal velocity (days prospect to converted) |
| Content | `reports/content/content-strategy-master.md` | Guides at 100+ organic sessions/month within 90d |
| Cross-domain | `reports/sales-marketing-strategy.md` | Active evaluations (self-reported signals) |

## Hypothesis Ledger Map

| Domain | Path | Prefix |
|--------|------|--------|
| SEO | `reports/seo/data/hypothesis-ledger.md` | S-### |
| Marketing | `reports/marketing/data/hypothesis-ledger.md` | H-### |
| CRM | `reports/crm/data/hypothesis-ledger.md` | C-### |
| Content | `reports/content/data/hypothesis-ledger.md` | CT-### |

Note: Social media uses the marketing ledger (H-### prefix). Social H-### rows are a subset of marketing H-###, not additive. When aggregating, do not double-count.

## Run Sequence

### Step 0: Yesterday Debrief (the only ask gate)

Before any data collection, locate yesterday's master brief at `reports/master/daily/{yesterday}/daily-master-brief.md`. Extract from Section 5 ("Today's Priority Actions") the full list of action IDs with their one-line titles and domains. If yesterday's brief is missing, fall back to the most recent master brief in `reports/master/daily/` and note the gap in the debrief summary.

Then ask Ed a single structured batch of prompts. Use one question-tool invocation — do not drip-feed.

**Prompt 1 — Action reconciliation.** Present yesterday's proposed actions verbatim:

```
Yesterday's proposed actions:
  [S-042] Publish tuning guide for Claude Code hooks (SEO)
  [H-118] DM 5 AI governance leads on LinkedIn (Marketing/Social)
  [C-031] Follow up with Acme Corp on evaluation call (CRM)
  [CT-055] Refresh MCP server comparison doc (Content)
  ...

Which did you complete? For each: outcome / result / numbers.
Format: `{ID} done {outcome}` or `{ID} skipped {reason}` or `all done` / `none done`.
```

**Prompt 2 — New data to record.** Inbound signals not yet in the system? Replies received, calls taken, new leads, DMs, GitHub stars that became conversations, social engagement numbers, anything else Ed saw yesterday that the trackers wouldn't have caught.

**Prompt 3 — External events.** Anything happening today that should shape priorities? Launches, deadlines, freezes, planned time-off, customer calls, personal availability.

**Prompt 4 — Corrections.** Any prior hypothesis, lead, or strategy state Ed wants updated before the briefs run?

**Persist before continuing.** Parse the answer and write to the correct stores:

- For each confirmed action ID → call `done {ID} {outcome}` against the matching hypothesis ledger (prefix S- → `seo:seo-hypothesis-ledger`, H- → `commons:marketing-hypothesis-ledger`, C- → `crm:crm-hypothesis-ledger`, CT- → `content:content-hypothesis-ledger`). For skipped actions → call `skip {ID} {reason}` on the same ledger.
- For new leads → append via `crm:lead-enrichment` or `crm:pipeline-tracker` (match the signal type).
- For external events → write to `reports/master/daily/{today}/context.md` so Step 7 can read them when ranking priorities.
- For corrections → apply to the named ledger/tracker directly.

Only after the debrief data is persisted does Step 1 proceed. If Ed responds "nothing" / "skip" / "all quiet" to every prompt, persist nothing and continue — but still write Section 0 of the report noting the debrief was skipped.

### Step 1: Verify Data Context

Confirm `systemprompt-prod` profile is active.

### Step 2: Check Domain Briefs

For each of the 5 domains, check whether today's brief exists at the expected path.

**Trigger order** (dependencies flow top-down):
1. `seo:daily-seo-brief` — must run first (content depends on SEO data)
2. `content:daily-content-brief` — depends on SEO data
3. `commons:daily-marketing-brief` — independent
4. `social-media:daily-social-brief` — reads marketing brief output
5. `crm:daily-crm-brief` — reads marketing context

For each missing brief:
- Invoke the domain brief via the Skill tool. **Do not ask Ed before invoking.** Proceed to the next domain when it returns, regardless of whether it succeeded. Failures are logged to Section 6 (System Health), never escalated as questions.
- If invocation fails, fall back to the **most recent** report for that domain. Mark as `STALE: last run {date}` in the master brief.
- Never skip a domain entirely. Always show last known state.

### Step 3: Read Cross-Domain Strategy

Load `sales-marketing-strategy.md` for:
- Current domain weights (used to rank actions in Step 7)
- Funnel stage definitions (used for pipeline table in KPI 3)
- Decision framework and priorities

### Step 4: Read All Domain Briefs

For **each of the 5 domains**, extract:
- **Headline**: the one-sentence summary
- **Key metrics**: 2-3 numbers with deltas
- **Hypothesis status**: count of in-flight, count scored today, pass/fail breakdown
- **Today's actions**: list with hypothesis IDs — **every action, not a subset**
- **Yesterday's execution**: actions assigned vs completed (from previous day's brief)

**Aggregation contract (MUST).** Section 5 of the master brief must contain the *union* of every action from every domain brief that returned. Never show a single-domain subset. Before moving to Step 5, assert:

1. The master action pool has a contribution from every domain whose brief returned successfully. If a domain returned without actions, that's a finding — add a one-line "Domain {X}: zero actions (reason: {stale data / empty ledger / degrade-mode})" entry to System Health, but the aggregation still counts that domain as represented.
2. If fewer than 5 domains are represented in the pool (counting degrade-mode), treat it as a system-health alert: Section 6 must call out the missing domains at the top.
3. If the pool contains actions from only one domain after all 5 briefs ran, this is a bug — log a `master-brief-aggregation-failure` warning in the brief's Headline and proceed with what was collected.

### Step 5: Read Hypothesis Ledgers Directly

For each of the 4 hypothesis ledgers, run `stats` to get:
- Total hypotheses logged (all time)
- In-flight count
- Pass/fail/inconclusive counts (all time)
- Win rate percentage
- Trend: compare last 30d win rate to all-time win rate

### Step 6: Read Strategy Master Headers

For each of the 5 strategy master documents, read:
- `Last updated: YYYY-MM-DD by {skill-name}` header
- Current phase
- Compute days since last update
- Flag as STALE if > 7 days since last update

### Step 7: Build the Report

Assemble all data into the report structure below, answering each of the 9 KPIs.

### Step 8: Write the Master Brief

Write to `reports/master/daily/{today}/daily-master-brief.md` and print to Ed.

## Report Structure

```markdown
# Master Brief -- {YYYY-MM-DD}

**Profile:** systemprompt-prod | **Run at:** {HH:MM}
**Domains reporting:** {N}/5 {list any STALE with last-run date}

---

## 0. Yesterday Debrief Summary

- **Actions confirmed done:** {list of IDs with one-line outcomes}
- **Actions skipped:** {list of IDs with reasons}
- **New data recorded:** {summary of leads/replies/events persisted, with destinations}
- **External events noted:** {summary or "none"}
- **Corrections applied:** {list or "none"}
- **Debrief source:** Ed, {HH:MM today}

If Ed skipped every prompt: "Debrief skipped by operator — no yesterday reconciliation performed."

## 1. Strategy Effectiveness

> KPI: How effective are our strategies? What is working? What is not working?

| Domain | Prefix | In-Flight | Scored Today | Pass | Fail | Inconclusive | Win Rate (all time) | Trend (30d vs all) |
|--------|--------|----------:|-------------:|-----:|-----:|-------------:|--------------------:|:------------------:|
| SEO | S-### | | | | | | | |
| Marketing | H-### | | | | | | | |
| CRM | C-### | | | | | | | |
| Content | CT-### | | | | | | | |
| **Total** | | | | | | | | |

Note: Social uses H-### (shared with marketing). Social stats are included in the Marketing row.

### What Passed Today

| ID | Domain | Action | Metric | Baseline | Result | Delta | Lesson |
|----|--------|--------|--------|----------|--------|------:|--------|

If zero: "No hypotheses scored today."

### What Failed Today

| ID | Domain | Action | Metric | Baseline | Result | Delta | Lesson |
|----|--------|--------|--------|----------|--------|------:|--------|

If zero: "No failures today."

## 2. Strategy Freshness

> KPI: Are our strategies up to date?

| Document | Last Updated | Updated By | Days Ago | Status |
|----------|:------------|:-----------|--------:|:------:|
| SEO Strategy Master | | | | |
| Marketing Strategy Master | | | | |
| CRM Strategy Master | | | | |
| Content Strategy Master | | | | |
| Sales-Marketing Strategy | | | | |

Status: OK (updated within 7 days) | STALE (7-14 days) | CRITICAL (14+ days)

{If any STALE or CRITICAL: "Action required: update {document} — last touched {N} days ago by {skill}."}

## 3. Pipeline Growth

> KPI: How many people in the pipeline? Where did they come from?

| Stage | Count | 7d Delta | 31d Delta | Primary Source |
|-------|------:|:--------:|:---------:|:---------------|
| Awareness (GSC impressions/wk) | | | | SEO |
| Website Visit (sessions/wk) | | | | SEO + Content |
| GitHub Visit (repo views/14d) | | | | Marketing + Social |
| Clone (unique cloners/14d) | | | | Marketing |
| Active Lead | | | | CRM |
| Qualified Contact | | | | CRM |
| Deal | | | | CRM |

### New Leads This Week

| Name/Company | Source Channel | Date Entered | Current Stage |
|-------------|:--------------|:-------------|:-------------|

Data from CRM brief's pipeline snapshot. If no new leads: "No new leads entered the pipeline this week."

## 4. Cross-Domain Signals

> KPI: How can we improve?

{1-3 specific observations. Each must name concrete numbers and domains. Examples:}

- **Funnel break:** GSC impressions up {N}% but cloners flat — content is attracting visitors who don't convert. Check landing page CTAs.
- **Attribution gap:** {N} new GitHub stars this week but zero referral sessions — README links may be broken.
- **Timing opportunity:** Guide "{slug}" hit page 1 for "{keyword}" — CRM should watch for inbound leads mentioning this topic.
- **Stale channel:** No social actions taken in {N} days despite {N} hypotheses available — social brief may need attention.

If no cross-domain signals: "All domains operating independently. No cross-domain gaps detected."

## 5. Today's Priority Actions

> KPI: What do we need to do today?

**All** actions from all domain briefs, ranked by strategic weight from sales-marketing-strategy.md. No cap — if domains produced 18 hypothesis- and data-driven actions today, show 18. The top 5 are marked PRIORITY so Ed can read top-down and stop when time runs out.

**Per-domain contribution table** (must be emitted before the ranked list):

| Domain | Actions Contributed | Status |
|--------|-------------------:|--------|
| SEO | {N} | {fresh / stale / degrade / failed} |
| Content | {N} | {fresh / stale / degrade / failed} |
| Marketing | {N} | {fresh / stale / degrade / failed} |
| Social | {N} | {fresh / stale / degrade / failed} |
| CRM | {N} | {fresh / stale / degrade / failed} |
| **Total** | **{sum}** | |

If any domain shows 0 actions AND status=fresh, this is anomalous — investigate in Section 6. Single-domain action lists (e.g., all 12 actions from content, zero from the other four) are a bug signature of the aggregation failing; the Headline must flag it.

### 1. [{PREFIX}-###] {title} PRIORITY
**Domain:** {domain} | **Channel:** {channel}
**Why priority:** {one sentence linking to a KPI gap above — strategy effectiveness, pipeline growth, or cross-domain signal}
**Full draft:** See {domain} daily brief, Action {N}

### 2. ... PRIORITY
### 3. ... PRIORITY
### 4. ... PRIORITY
### 5. ... PRIORITY
### 6. ...
### 7. ...
...

**PRIORITY ranking criteria** (applies to the top 5 marker, not a cap on total):
1. Actions that address a cross-domain signal (Section 4) rank highest
2. Actions aligned with the current phase priorities in sales-marketing-strategy.md
3. Actions from domains with declining win rates (need course correction)
4. Dues from yesterday (unfinished business)
5. Experiments in undersampled channels

Actions that don't meet a PRIORITY criterion still appear in rank order below the top 5. Never truncate.

## 6. System Health

> KPI: Is everything consistent, standardised and updated?

| Check | Status | Detail |
|-------|:------:|--------|
| SEO brief ran today | | |
| Marketing brief ran today | | |
| CRM brief ran today | | |
| Social brief ran today | | |
| Content brief ran today | | |
| All strategy docs updated this week | | {list stale ones} |
| Overdue hypotheses (past window_end, not scored) | | {count + list IDs} |
| Orphaned actions (logged but never confirmed) | | {count + list IDs} |
| Data collection errors today | | {list from domain briefs} |
| Hypothesis ledger consistency | | {any gaps in ID sequences} |

### Domain Brief Links

- SEO: `reports/seo/daily/{today}/daily-seo-brief.md`
- Marketing: `reports/marketing/daily/{today}/daily-brief.md`
- CRM: `reports/crm/daily/{today}/daily-brief.md`
- Social: `reports/social/daily/{today}/daily-social-brief.md`
- Content: `reports/content/daily/{today}/daily-content-brief.md`
```

**Length target:** Under 600 words of prose (tables excluded). This is a 10-minute read. Ed drills into domain briefs for copy-paste-ready drafts and detailed analysis.

## Run Modes

```
daily-master-brief              # Full run: check/trigger all domains, write report
daily-master-brief dry          # Read existing briefs only, do not trigger missing ones
daily-master-brief quick        # Skip Steps 5-6 (hypothesis stats + strategy freshness), faster output
```

## What This Skill Does NOT Do

- **Does not generate hypotheses.** The master brief curates and prioritises domain-generated actions. It has no ledger of its own.
- **Does not score hypotheses.** Domain briefs score their own hypotheses in their own run sequences.
- **Does not update strategy documents.** Strategy masters are updated by their owning domain skills.
- **Does not create copy-paste-ready drafts.** Those live in domain briefs. The master brief references them.
- **Does not replace domain briefs.** Each domain brief remains independently runnable. The master brief is a summary layer.

## Anti-Sludge Rules

- **No vague prose.** Every observation must cite a specific number, domain, and metric.
- **No motivational language.** This is an operator's dashboard, not a pep talk.
- **No emojis.** Brand voice rules apply.
- **Fail loudly.** If a domain brief is stale, missing, or errored, the report says so prominently at the top — not buried in a footnote.
- **No double-counting.** Social H-### hypotheses are a subset of marketing. The total row accounts for this.
- **Answer all 9 KPIs or explain why not.** If a KPI cannot be answered (e.g., no CRM data), the section must say "Cannot answer: {reason}" rather than being omitted.
- **Under 600 words of prose.** If longer, it's not a brief — it's a report. Cut the prose, keep the tables.
