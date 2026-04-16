---
name: content-hypothesis-ledger
description: "Append-only log of every content action taken and whether its hypothesis passed. Provides CT-### ID allocation, in-flight queries for daily-content-brief, and maturation scoring. The spine of the hypothesis-driven content loop."
metadata:
  version: "1.0.0"
  git_hash: "dc0c940"
---

# Content Hypothesis Ledger

> **Implements:** `commons:hypothesis-ledger-pattern` — shared append-only ledger schema, status lifecycle, and scoring operations. This skill configures the pattern for the content domain (CT-### prefix, 14-day default window, content metric whitelist).

Append-only ledger of every content action. The single source of truth for what we published, optimised, or distributed, what we predicted, and what actually happened. The `daily-content-brief` skill writes to it on each run. Metric data comes from `daily-seo-brief` output and guide inventory.

## Dependencies

Load `commons:identity` first (for product positioning and ICP context).

## Storage

```
/var/www/html/systemprompt-web/reports/content/data/hypothesis-ledger.md
```

Single markdown file. One table, append-only. Newest rows at the bottom. Never rewrite history.

## Schema

```markdown
| id | logged | channel | action | hypothesis | metric | baseline | window_end | result | status | notes |
```

Fields:

- **id**: `CT-###` sequential, zero-padded to 3 digits. Separate namespace from SEO `S-###`, marketing `H-###`, and CRM `C-###`.
- **logged**: YYYY-MM-DD the action was taken.
- **channel**: one of `optimisation`, `new-guide`, `revision`, `github-contribution`, `distribution`, `technical`.
- **action**: one-line past-tense description. Full context goes in `data/actions/CT-###.md`.
- **hypothesis**: the "If ... then ... within ..." statement, trimmed to one line.
- **metric**: exact field name from the metric whitelist (validated on append).
- **baseline**: numeric value of `metric` at the moment of logging (from latest daily-seo-brief data or guide inventory).
- **window_end**: YYYY-MM-DD when the hypothesis matures. Default = logged + 14d (content performance takes time to materialise due to crawl/index latency and engagement buildup).
- **result**: numeric value of `metric` at window_end. Empty while in-flight.
- **status**: `IN-FLIGHT` | `SEEDED` | `PASS` | `FAIL` | `INCONCLUSIVE` | `ABORTED`.
- **notes**: free text, <=140 chars.

## Channel Definitions

| Channel | When to use |
|---------|-------------|
| `optimisation` | Title/meta rewrites, internal link additions, content restructuring on existing guides |
| `new-guide` | Publishing a brand-new guide |
| `revision` | Major content updates to reflect product changes or new data |
| `github-contribution` | PRs, issues, or discussions on external repos to build backlinks and authority |
| `distribution` | Syndication of existing content to new platforms (LinkedIn, Reddit, newsletters) |
| `technical` | Schema markup, sitemap changes, page speed fixes, structured data |

## Action Text Store

Full context for each hypothesis lives in:

```
/var/www/html/systemprompt-web/reports/content/data/actions/CT-###.md
```

Each file contains: timestamp, skill that logged it, guide slug (if applicable), what was changed, before/after values, target URLs, measurement notes.

## Operations

```
content-hypothesis-ledger next-id              # Allocates next CT-###
content-hypothesis-ledger log {fields...}      # Append new row + write actions/CT-###.md
content-hypothesis-ledger in-flight            # Print rows where status=IN-FLIGHT or SEEDED
content-hypothesis-ledger maturing {date}      # Print rows where window_end <= date AND status=IN-FLIGHT
content-hypothesis-ledger score {id} {result} {status} {note}   # Close out a row
content-hypothesis-ledger stats                # Pass/fail tally by channel
```

### `log` operation

Steps:
1. Allocate next `CT-###`.
2. Pull current value of `metric` from latest daily-seo-brief report or guide inventory frontmatter.
3. Validate `metric` is in the whitelist (see below). Reject if not.
4. Compute `window_end` = logged + window_days (default 14).
5. Append row to ledger with `status=IN-FLIGHT` or `status=SEEDED`.
6. Write `actions/CT-###.md` with context.
7. Print the assigned ID.

### `score` operation

Steps:
1. Read the row, confirm status is `IN-FLIGHT`.
2. Append a **new row** with the same id and closed-out values. **Never edit existing rows.**
3. If `PASS`, emit a diff suggestion for content-strategy-master section 4 (Winning Tactics).
4. If `FAIL`, emit a diff suggestion for section 5 (Dead Hypotheses).

## Metric Whitelist

Only these metric names are valid (sourced from daily-seo-brief output, GSC data, guide frontmatter, and github-monitor):

```
# Guide-level metrics (from daily-seo-brief / GSC)
guide_{slug}_sessions_7d            guide_{slug}_sessions_31d
guide_{slug}_gsc_clicks_7d          guide_{slug}_gsc_impressions_7d
guide_{slug}_gsc_ctr_7d             guide_{slug}_gsc_position_7d
guide_{slug}_engagement_rate

# Aggregate metrics (from daily-seo-brief)
guides_published_total              guides_indexed
organic_sessions_7d                 gsc_clicks_7d
gsc_impressions_7d                  gsc_avg_ctr_7d

# GitHub metrics (from github-monitor)
github_contributions_7d             github_referral_sessions_7d
github_backlinks_total

# Distribution metrics (from lead-tracker / analytics)
web_sessions_7d                     content_referral_sessions_7d
```

Guide-level metrics use the guide slug with hyphens (e.g., `guide_claude-code-system-prompt_sessions_7d`).

## Default Windows

Content hypotheses default to 14-day windows because:
- New guides take 3-7 days to be indexed by Google
- Title/meta changes take 5-14 days to affect rankings
- Distribution effects take 3-7 days to materialise in referral traffic
- GitHub contributions take 7-14 days to generate backlink value

For new guide publications, use 21-day windows (indexing + ranking stabilisation).

## Integration with Daily Content Brief

`daily-content-brief` calls:
1. `in-flight` — to show active content hypotheses
2. `maturing {today}` — to identify hypotheses that need scoring today
3. `log` — to register new actions from today's brief
4. `score` — to close out matured hypotheses

## Separation from Other Ledgers

The content ledger uses `CT-###` IDs. The SEO ledger uses `S-###`. The marketing ledger uses `H-###`. The CRM ledger uses `C-###`. They are completely independent files in different directories. Do not cross-reference IDs across ledgers.
