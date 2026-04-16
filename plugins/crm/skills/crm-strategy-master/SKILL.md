---
name: crm-strategy-master
description: "Maintains the living CRM strategy doc at reports/crm/crm-strategy-master.md. Never rewrites wholesale, only diffs. Contains objectives, pipeline health, hypotheses, and deal velocity. Load crm-identity first."
metadata:
  version: "1.0.0"
  git_hash: "3a55706"
---

# CRM Strategy Master

> **Implements:** `commons:strategy-master-pattern` — 9-section living document structure, diff-only write rules, append-only changelog. This skill configures the pattern for the CRM domain (C-### hypotheses, pipeline-stage health, deal velocity north star).

Owner of the single living CRM strategy doc. Every other CRM skill **reads** this doc for current priorities; only this skill **writes** to it (except Section 1, which `pipeline-tracker` updates).

## Dependencies

1. `crm-identity` — pipeline stages, scoring rubric, hypothesis format
2. `commons:strategy-master-pattern` — 9-section structure and write rules
3. `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — master strategy (CRM domain in §4.7, funnel in §3)
4. `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — marketing funnel context (top-of-funnel feeds CRM)

## The Strategy Doc

```
/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md
```

Single living file. Diffs are appended, never rewritten wholesale.

## Section Structure

Following `commons:strategy-master-pattern`, configured for CRM:

```markdown
# systemprompt.io — CRM Strategy Master

**Last updated:** {YYYY-MM-DD by {skill-name}}
**Phase:** {1: Pipeline Setup | 2: Active Outreach | 3: Conversion Optimisation | 4: Scale}
**North Star:** Deal velocity (days from prospect to converted)
**Owner:** Ed. All outreach executed personally.

## 1. Current Pipeline Snapshot
Updated by `pipeline-tracker` only. This skill reads, never writes.

Tables:
- Pipeline stage counts (prospect, contacted, demo_scheduled, evaluating, negotiating, converted, lost)
- Lead score distribution (low 0-15, medium 16-40, high 41-70, hot 71+)
- GitHub clone-to-feedback conversion rate (14d rolling)
- Stale lead alerts (leads with no interaction in 7d+)

## 2. Objectives — 30 / 60 / 90

| Horizon | New leads | Qualified convos | Demos | Evaluating | Customers |
|---------|----------|-----------------|-------|-----------|-----------|
| Baseline | {from pipeline-tracker} |
| 30d | | | | | |
| 60d | | | | | |
| 90d | | | | | |

## 3. Active Hypotheses (in flight)
Rendered from `crm-hypothesis-ledger.md`. Shows C-### ID, action, metric, baseline, window_end.
Read-only for this skill — display only.

## 4. Winning Tactics (validated)
C-### hypotheses that passed. Each entry: what was done, measured result, why it worked.
Updated when `daily-crm-brief` scores a hypothesis as PASS.

## 5. Dead Hypotheses (and why)
C-### hypotheses that failed. Each entry: what was done, measured result, lesson learned.
Updated when `daily-crm-brief` scores a hypothesis as FAIL.

## 6. Pipeline Health
Stage-by-stage assessment:

| Stage | Count | Avg days in stage | Stale (>7d) | Health |
|-------|-------|-------------------|-------------|--------|
| prospect | | | | |
| contacted | | | | |
| demo_scheduled | | | | |
| evaluating | | | | |
| negotiating | | | | |

Health: GREEN (on track), YELLOW (needs attention), RED (blocked/stale).

Also includes:
- Lead source breakdown (which channels produce the best leads)
- Email response rates by template type
- Score distribution trend (are leads getting more or less qualified?)

## 7. Technical Issues
Priority-ranked blockers:

| Priority | Issue | Action | Owner | Status |
|----------|-------|--------|-------|--------|
| P0 | | | | |

Examples: feedback label missing, email deliverability issues, GitHub API gaps, CRM data quality problems.

## 8. Pipeline Queue
Upcoming actions:
- Leads awaiting first contact
- Follow-ups due this week
- Demos to schedule
- Reactivation candidates (stagnant leads with score > 40)

## 9. Changelog
Append-only. Every diff attributed to skill name and date.
- {YYYY-MM-DD} ({skill-name}): {one-line description of change and why}
```

## Write Rules

Per `commons:strategy-master-pattern`:

1. **Never rewrite wholesale.** Target specific sections with surgical diffs.
2. **Every write must update** `Last updated: YYYY-MM-DD by crm-strategy-master` in the header.
3. **Every write must append** a changelog entry to Section 9.
4. **Numbers come from data sources.** Read from pipeline-tracker reports, lead-tracker data, hypothesis ledger. Never invent numbers.
5. **Section 1 is read-only.** Only `pipeline-tracker` writes to it.
6. **Sections 3, 4, 5 are rendered** from `crm-hypothesis-ledger.md`.

## Permitted Operations

| Operation | Who writes | Notes |
|-----------|-----------|-------|
| Update Section 1 (snapshot) | `pipeline-tracker` only | This skill reads, never writes |
| Update Section 2 (objectives) | This skill | On phase transitions or monthly reviews |
| Render Sections 3-5 (hypotheses) | This skill + `daily-crm-brief` | From hypothesis-ledger.md data |
| Update Section 6 (health) | This skill | Based on Section 1 data |
| Update Section 7 (issues) | Any CRM skill | With priority and action item |
| Update Section 8 (pipeline queue) | This skill | Based on leads.json + deals.json |
| Append Section 9 (changelog) | Any skill that writes | Mandatory on every write |

## Run Modes

```
crm-strategy-master              # Full strategy review and update
crm-strategy-master read         # Read-only: print current state
crm-strategy-master diff         # Show what would change without writing
crm-strategy-master phase        # Phase transition (update objectives, reweight priorities)
```

## Data Sources

| Data | Source | Path |
|------|--------|------|
| Pipeline state | pipeline-tracker | `reports/crm/data/leads.json`, `reports/crm/data/deals.json` |
| Pipeline history | pipeline-tracker | `reports/crm/data/pipeline-history.jsonl` |
| Interactions | pipeline-tracker + email-composer | `reports/crm/data/interactions.jsonl` |
| Hypotheses | crm-hypothesis-ledger | `reports/crm/data/hypothesis-ledger.md` |
| Marketing funnel | lead-tracker | `reports/marketing/data/funnel-history.jsonl` |
| Email log | email-composer | `reports/crm/data/email-log.jsonl` |

## Domain Configuration

Per `commons:strategy-master-pattern`:

| Config | Value |
|--------|-------|
| Path | `reports/crm/crm-strategy-master.md` |
| North star | Deal velocity (days prospect → converted) |
| Secondary north star | Qualified leads/week |
| Phase labels | 1: Pipeline Setup, 2: Active Outreach, 3: Conversion Optimisation, 4: Scale |
| Section 6 content | Pipeline stage-by-stage health |
| Monitor skill | `pipeline-tracker` |
| Brief skill | `daily-crm-brief` |
| Hypothesis prefix | C-### |
| Default window | 14 days |

## Integration with Marketing

The CRM strategy does not exist in isolation. It sits downstream of marketing:

- **Marketing feeds CRM:** When `lead-tracker` detects a new feedback lead, it enters the CRM pipeline as a `prospect`.
- **CRM informs marketing:** When a lead stage changes (especially `converted` or `lost`), the lesson feeds back into marketing channel priorities.
- **Shared strategy reference:** Both this skill and `commons:marketing-strategy-master` reference `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` as the top-level operating document.

## First Run

On first run, if `reports/crm/crm-strategy-master.md` does not exist:

1. Create the file with the template structure above
2. Read `pipeline-tracker` latest data to populate Section 1
3. Set Phase to "1: Pipeline Setup"
4. Set initial 30/60/90 objectives from the master strategy doc §8
5. Render Sections 3-5 from `crm-hypothesis-ledger.md` (may be empty)
6. Assess pipeline health for Section 6 (may show all RED if pipeline is empty)
7. Log any instrumentation gaps in Section 7
8. Append first changelog entry

## Anti-Sludge Rules

- **No vague prose.** "Pipeline is growing" banned. "3 prospects, 1 contacted, 0 demos, avg 4.2 days in prospect stage" required.
- **No motivational language.**
- **No emojis.**
- **Diff-only writes.** Never rewrite the document. Show the specific section and line being changed.
- **Every number traceable.** Every number in the strategy doc must reference its source (pipeline-tracker report date, lead-tracker output, hypothesis ledger row).
