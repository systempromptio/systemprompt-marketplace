---
name: content-strategy-master
description: "Maintains the living content strategy doc at reports/content/content-strategy-master.md. Never rewrites wholesale — writes diffs. Contains objectives, guide health, hypotheses, technical issues, and publishing pipeline. Load identity first."
metadata:
  version: "1.1.0"
  git_hash: "d32d335"
---

# Content Strategy Master

> **Implements:** `commons:strategy-master-pattern` — 9-section living strategy document, diff-only write rules, changelog requirements. This skill configures the pattern for the content domain (guide performance north star, content-specific phase labels, guide-by-guide health assessment).

The single living document for content strategy. Updated by diffs, never rewritten. Every number comes from daily-seo-brief data or guide inventory — never from memory.

## Dependencies

Load `commons:identity` and `commons:brand-voice` first.

## Storage

```
/var/www/html/systemprompt-web/reports/content/content-strategy-master.md
```

## North Star

**Guides producing 100+ organic sessions/month within 90 days of publication.**

Supporting metrics:
- Total organic sessions/week across all guides
- GSC clicks/week across all guides
- Guides indexed / guides published ratio
- Average guide engagement rate

## Phase Labels

| Phase | Name | Focus |
|-------|------|-------|
| 1 | Foundation | Inventory baseline, per-guide reporting, identify gaps |
| 2 | Expansion | Fill content gaps, publish new guides for target keywords |
| 3 | Optimisation | Improve existing guides using GSC data and audit scores |
| 4 | Scale | Systematic publishing cadence, distribution playbook, contributor programme |

## Section Structure

Follows the standard 9-section `strategy-master-pattern` layout:

### Section 1: Current Performance Snapshot

Updated by `daily-content-brief` (via daily-seo-brief data). Read-only for this skill.

Contents:
- Total guides published / indexed
- Aggregate organic sessions/week (7d, 31d, delta)
- Aggregate GSC clicks/week, impressions/week, average CTR
- Top 3 guides by sessions
- Bottom 3 guides by sessions (with diagnosis)
- Publishing cadence: guides published in last 30/60/90 days

### Section 2: Objectives -- 30 / 60 / 90

| Horizon | Objective | Metric | Current | Target |
|---------|-----------|--------|---------|--------|
| 30d | ... | ... | ... | ... |
| 60d | ... | ... | ... | ... |
| 90d | ... | ... | ... | ... |

### Section 3: Active Hypotheses (in-flight)

Rendered from `reports/content/data/hypothesis-ledger.md`. Shows CT-### ID, action, metric, baseline, window_end.

### Section 4: Winning Tactics (validated)

CT-### hypotheses that passed. Each entry: what was done, the measured result, why it worked.

### Section 5: Dead Hypotheses (and why)

CT-### hypotheses that failed. Each entry: what was done, the measured result, the lesson learned.

### Section 6: Domain Health — Guide-by-Guide

| Guide Slug | Status | Sessions/7d | GSC Position | Engagement | Trend | Action Needed |
|------------|--------|------------:|:------------:|:----------:|:-----:|---------------|

Categories:
- Healthy: 100+ sessions/month, stable or growing
- Watch: 50-100 sessions/month or declining trend
- Underperforming: <50 sessions/month or poor engagement
- New: published <90 days ago, building baseline

### Section 7: Technical Issues

Active issues affecting content performance:
- P0: Broken pages, deindexed content, 404 errors
- P1: Schema markup missing, slow page load, mobile issues
- P2: Internal linking gaps, image optimisation, structured data

### Section 8: Pipeline

| Priority | Guide/Action | Status | Target Date | Owner |
|----------|-------------|--------|-------------|-------|
| 1 | ... | Draft/Planned/In Review | ... | ... |

### Section 9: Changelog

Append-only. Format:
- {YYYY-MM-DD} ({skill-name}): {one-line description of what changed and why}

## Write Rules

1. **Never rewrite wholesale.** Target specific sections with surgical diffs.
2. **Every write must update** `Last updated: YYYY-MM-DD by {skill-name}` in the header.
3. **Every write must append** a changelog entry to Section 9.
4. **Numbers come from data sources.** Read from daily-seo-brief reports, guide inventory, hypothesis ledger stats. Never invent numbers.
5. **Section 1 is read-only** for this skill. Only `daily-content-brief` writes to it (using daily-seo-brief data).
6. **Sections 3, 4, 5 are rendered** from the content hypothesis ledger.

## Permitted Operations

| Operation | Who writes |
|-----------|-----------|
| Update Section 1 (snapshot) | `daily-content-brief` only |
| Update Section 2 (objectives) | This skill on phase transitions |
| Render Sections 3-5 (hypotheses) | This skill + `daily-content-brief` |
| Update Section 6 (guide health) | This skill + `daily-content-brief` |
| Update Section 7 (issues) | Any skill that discovers an issue |
| Update Section 8 (pipeline) | This skill based on priorities |
| Append Section 9 (changelog) | Any skill that writes |

## Data Sources

- **daily-seo-brief output**: guide traffic, GSC metrics, engagement rates
- **Guide inventory**: `/var/www/html/systemprompt-web/services/content/guides/*/index.md` frontmatter
- **Per-guide reports**: `reports/content/guides/*/guide-report.md` (from guide-optimiser)
- **Content hypothesis ledger**: `reports/content/data/hypothesis-ledger.md`
