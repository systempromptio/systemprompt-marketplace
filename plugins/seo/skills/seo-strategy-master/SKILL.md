---
name: seo-strategy-master
description: "Maintains the living SEO strategy doc at reports/seo/seo-strategy-master.md. Never rewrites wholesale, only diffs. Contains objectives, pillar health, hypotheses, technical SEO issues, and content pipeline. Load identity first."
metadata:
  version: "1.0.0"
---

# SEO Strategy Master

Owner of the single living SEO strategy doc. Every other SEO skill **reads** this doc for current priorities; only this skill and `seo-monitor` **write** to it.

## Dependencies

Load `identity` first. It defines positioning, ICP, and keyword strategy context.

## The Strategy Doc

```
/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md
```

Structure (enforced on every write):

```markdown
# systemprompt.io -- SEO Strategy Master

**Last updated:** {YYYY-MM-DD by {skill-name}}
**Phase:** {1: Baseline | 2: Content Expansion & CTR Optimization | 3: Scale}
**North Star:** Organic sessions/week + GSC clicks/week

## 1. Current Performance Snapshot
(tables updated by seo-monitor; this skill only reads, never overwrites)

## 2. Objectives -- 30 / 60 / 90
| Horizon | Organic sessions/wk | GSC clicks/wk | GSC CTR | Guides indexed | Published guides |

## 3. Active Hypotheses (in flight)
Table of hypotheses currently being tested, rendered from data/hypothesis-ledger.md

## 4. Winning Tactics (validated)
SEO tactics where hypothesis tests passed.

## 5. Dead Hypotheses (and why)
Short table: hypothesis, result, reason for failure, lesson.

## 6. Pillar Health
Cluster-by-cluster assessment with strength ratings.

## 7. Technical SEO Issues
Active issues with priority and action items.

## 8. Content Pipeline
Upcoming content with target dates and primary keywords.

## 9. Changelog
Append-only. One line per diff, newest first.
```

## Write Rules

**This skill NEVER rewrites the doc wholesale.** It only applies targeted diffs, and every diff appends a line to section 9 Changelog.

Permitted operations:

| Operation | When | Who triggers |
|-----------|------|-------------|
| Seed (first run only) | Doc doesn't exist | This skill, one time |
| Update objectives (section 2) | Monthly review or explicit Ed instruction | This skill |
| Move hypothesis to section 4 | A hypothesis passed in ledger | seo-monitor |
| Retire hypothesis to section 5 | A hypothesis failed in ledger | seo-monitor |
| Update pillar health (section 6) | After seo-monitor run | seo-monitor |
| Flag technical issue (section 7) | Any skill detects an issue | Any |
| Update content pipeline (section 8) | New guide published or planned | This skill |

Sections 1 (performance snapshot) and 3 (active hypotheses) are **rendered**. The actual source is `seo-monitor` output and `data/hypothesis-ledger.md`. This skill only re-renders them, never stores derived data.

## Satellite Documents

All satellite documents live in `reports/seo/`:

| Document | Purpose |
|----------|---------|
| `keyword-research.md` | DataForSEO keyword data: volumes, difficulty, trends |
| `guide-inventory.md` | All guides with metadata, publication history |
| `metadata-audit.md` | Title and description length audits per guide |
| `interlinking-strategy.md` | Internal link map between guides |
| `backlink-strategy.md` | External link opportunities |
| `traffic-analytics.md` | Traffic source history |
| `data/hypothesis-ledger.md` | SEO hypothesis test records |
| `data/seo-metrics.jsonl` | Append-only daily metric snapshots |
