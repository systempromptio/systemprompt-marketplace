---
name: seo-strategy-master
description: "Maintains the living SEO strategy doc at reports/seo/seo-strategy-master.md. Never rewrites wholesale, only diffs. Contains objectives, pillar health, hypotheses, technical SEO issues, and content pipeline. Load identity first."
metadata:
  version: "1.3.0"
  git_hash: "2406d58"
---

# SEO Strategy Master

> **Implements:** `commons:strategy-master-pattern` — 9-section living document structure, diff-only write rules, append-only changelog. This skill configures the pattern for the SEO domain (S-### hypotheses, pillar-by-pillar health, organic sessions north star).

Owner of the single living SEO strategy doc. Every other SEO skill **reads** this doc for current priorities; only this skill and `daily-seo-brief` **write** to it.

## Dependencies

Load `identity` first. It defines positioning, ICP, and keyword strategy context.

Also reference:
- `commons:strategy-master-pattern` — shared 9-section structure and write rules
- `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — master strategy (SEO domain priorities in §4.1)

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
(tables updated by daily-seo-brief; this skill only reads, never overwrites)

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
| Move hypothesis to section 4 | A hypothesis passed in ledger | daily-seo-brief |
| Retire hypothesis to section 5 | A hypothesis failed in ledger | daily-seo-brief |
| Update pillar health (section 6) | After daily-seo-brief run | daily-seo-brief |
| Flag technical issue (section 7) | Any skill detects an issue | Any |
| Update content pipeline (section 8) | New guide published or planned | This skill |

Sections 1 (performance snapshot) and 3 (active hypotheses) are **rendered**. The actual source is `daily-seo-brief` output and `data/hypothesis-ledger.md`. This skill only re-renders them, never stores derived data.

## Satellite Documents

All satellite documents live in `reports/seo/`:

| Document | Purpose |
|----------|---------|
| `keyword-research.md` | DataForSEO keyword data: volumes, difficulty, trends |
| `guide-inventory.md` | All guides with metadata, publication history |
| `metadata-audit.md` | Title and description length audits per guide |
| `interlinking-strategy.md` | Internal link map between guides |
| `backlink-strategy.md` | External link opportunities — Tier 1 (permanent assets), Tier 2 (automated), Tier 3 (manual). **Always read before recommending off-page actions.** |
| `traffic-analytics.md` | Traffic source history |
| `data/hypothesis-ledger.md` | SEO hypothesis test records |
| `data/seo-metrics.jsonl` | Append-only daily metric snapshots |

## Off-Page SEO Strategy

The strategy doc covers on-page SEO (content, CTR, technical). Off-page (authority, backlinks) is tracked in `backlink-strategy.md`. Key permanent assets as of 2026-04-21:

- **`Ejb503/awesome-ai-agent-governance`** (GitHub) — 13-section curated list, 80+ entries. Targets "ai agent governance" and "awesome ai governance" in Google. systemprompt-template listed twice. Links to OWASP, NIST, ENISA, CISA, ISO — authority signal. Maintain and grow this repo actively.
- **hesreallyhim/awesome-claude-code** — submission pending merge (issue #1652, 2026-04-21).
- **mcpservers.org** — systemprompt-core submitted 2026-04-21.

When an SEO action involves publishing an external GitHub repo, curated list, or tool that links back to systemprompt.io, log it in `backlink-strategy.md` Tier 1 table and note the target keywords and section placement.

When assessing indexation failures (guides "Discovered but not indexed"), check `backlink-strategy.md` before recommending content changes — the root cause is often zero inbound backlinks, not content quality.
