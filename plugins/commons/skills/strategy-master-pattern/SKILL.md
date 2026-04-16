---
name: strategy-master-pattern
description: "Shared living strategy document pattern. Defines 9-section structure, diff-only write rules, and changelog requirements for domain strategy docs."
metadata:
  version: "1.1.0"
  git_hash: "dc0c940"
---

# Strategy Master Pattern

Every domain maintains a single living strategy document. This pattern defines the shared structure and rules. Domain strategy skills configure it with their own north star metric, sections, and report path.

## Principle

The strategy master is a living document. It is never rewritten wholesale. Every change is a targeted diff with a changelog entry. Numbers come from authenticated data sources, never from memory.

## Storage

Each domain stores its strategy master at:

```
/var/www/html/systemprompt-web/reports/{domain}/{domain}-strategy-master.md
```

## Standard Section Structure

Every strategy master follows this 9-section layout:

```markdown
# systemprompt.io -- {Domain} Strategy Master

**Last updated:** {YYYY-MM-DD by {skill-name}}
**Phase:** {domain-specific phase label}
**North Star:** {domain-specific north star metric}

## 1. Current Performance Snapshot
Updated by the domain's monitor/tracker skill. The strategy skill reads this section, never overwrites it.

## 2. Objectives -- 30 / 60 / 90
Horizon table with measurable targets for the north star and supporting metrics.

## 3. Active Hypotheses (in flight)
Table rendered from the domain's hypothesis-ledger.md. Shows ID, action, metric, baseline, window_end.

## 4. Winning Tactics (validated)
Hypotheses that passed. Each entry: what was done, the measured result, why it worked.

## 5. Dead Hypotheses (and why)
Hypotheses that failed. Each entry: what was done, the measured result, the lesson learned.

## 6. Domain Health
Domain-specific health assessment (pillar health for SEO, channel health for marketing, pipeline health for CRM).

## 7. Technical Issues
Active issues with priority (P0/P1/P2) and action items.

## 8. Pipeline
Upcoming actions, content, or initiatives in the queue.

## 9. Changelog
Append-only. Every diff is attributed to an actor (skill name) and date. Format:
- {YYYY-MM-DD} ({skill-name}): {one-line description of what changed and why}
```

## Write Rules

1. **Never rewrite wholesale.** Target specific sections with surgical diffs.
2. **Every write must update** `Last updated: YYYY-MM-DD by {skill-name}` in the header.
3. **Every write must append** a changelog entry to Section 9.
4. **Numbers come from data sources.** The strategy skill reads from monitor reports, ledger stats, and analytics. It never invents numbers.
5. **Section 1 is read-only** for the strategy skill. Only the domain's monitor/tracker skill writes to it.
6. **Sections 3, 4, 5 are rendered** from the hypothesis ledger. The strategy skill formats and displays them but does not maintain independent state.

## Permitted Operations

| Operation | Who writes | Notes |
|-----------|-----------|-------|
| Update Section 1 (snapshot) | Monitor/tracker skill only | Strategy skill reads, never writes |
| Update Section 2 (objectives) | Strategy skill | On phase transitions or quarterly reviews |
| Render Sections 3-5 (hypotheses) | Strategy skill + monitor skill | From hypothesis-ledger.md data |
| Update Section 6 (health) | Strategy skill + monitor skill | Based on data from Section 1 |
| Update Section 7 (issues) | Any skill that discovers an issue | With priority and action item |
| Update Section 8 (pipeline) | Strategy skill | Based on current priorities |
| Append Section 9 (changelog) | Any skill that writes | Mandatory on every write |

## Domain Configuration

| Config | SEO | Marketing | CRM | Content |
|--------|-----|-----------|-----|---------|
| Path | reports/seo/seo-strategy-master.md | reports/marketing/marketing-strategy-master.md | reports/crm/crm-strategy-master.md | reports/content/content-strategy-master.md |
| North star | Organic sessions/week + GSC clicks/week | Qualified leads/week | Deal velocity (days prospect to converted) | Guides at 100+ organic sessions/month within 90d |
| Phase labels | 1: Baseline, 2: Content Expansion, 3: Scale | 1: Instrumentation, 2: Channel Testing, 3: Scale | 1: Pipeline Setup, 2: Active Outreach, 3: Conversion Optimisation, 4: Scale | 1: Foundation, 2: Expansion, 3: Optimisation, 4: Scale |
| Section 6 content | Pillar-by-pillar cluster health | Channel-by-channel performance | Pipeline stage-by-stage health | Guide-by-guide health |
| Monitor skill | daily-seo-brief | daily-marketing-brief via lead-tracker | pipeline-tracker | daily-content-brief via daily-seo-brief |
| Brief skill | daily-seo-brief | daily-marketing-brief | daily-crm-brief | daily-content-brief |
| Hypothesis prefix | S-### | H-### | C-### | CT-### |
| Default window | 14 days | 7 days | 14 days | 14 days |

All domains reference the master strategy at `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` for cross-domain priorities and funnel alignment.
