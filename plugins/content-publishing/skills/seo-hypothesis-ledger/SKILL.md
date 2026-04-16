---
name: seo-hypothesis-ledger
description: "Append-only log of every SEO action taken and whether its hypothesis passed. Provides S-### ID allocation, in-flight queries for seo-monitor, and maturation scoring. The spine of the hypothesis-driven SEO loop."
metadata:
  version: "1.0.0"
---

# SEO Hypothesis Ledger

Append-only ledger of every SEO action. The single source of truth for what we tested, what we predicted, and what actually happened. The `seo-monitor` skill writes to it on each run.

## Storage

```
/var/www/html/systemprompt-web/reports/seo/data/hypothesis-ledger.md
```

Single markdown file. One table, append-only. Newest rows at the bottom. Never rewrite history.

## Schema

```markdown
| id | logged | channel | action | hypothesis | metric | baseline | window_end | result | status | notes |
```

Fields:

- **id**: `S-###` sequential, zero-padded to 3 digits. Separate namespace from marketing `H-###` IDs.
- **logged**: YYYY-MM-DD the action was taken.
- **channel**: one of `seo`, `content`, `technical`, `linking`, `indexing`, `ctr`, `other`.
- **action**: one-line past-tense description. Full draft goes in `data/actions/S-###.md`.
- **hypothesis**: the "If ... then ... within ..." statement, trimmed to one line.
- **metric**: exact field name from the metric whitelist (validated on append).
- **baseline**: numeric value of `metric` at the moment of logging (from latest seo-monitor data).
- **window_end**: YYYY-MM-DD when the hypothesis matures. Default = logged + 14d for SEO (longer than marketing due to crawl/index latency).
- **result**: numeric value of `metric` at window_end. Empty while in-flight.
- **status**: `IN-FLIGHT` | `SEEDED` | `PASS` | `FAIL` | `INCONCLUSIVE` | `ABORTED`.
- **notes**: free text, <=140 chars.

## Action Text Store

Full context lives in:

```
reports/seo/data/actions/S-###.md
```

Each file contains: timestamp, what was changed, before/after title/meta text, target URLs, measurement notes.

## Operations

```
seo-hypothesis-ledger next-id           # Allocates next S-###
seo-hypothesis-ledger log {fields...}   # Append new row + write actions/S-###.md
seo-hypothesis-ledger in-flight         # Print rows where status=IN-FLIGHT
seo-hypothesis-ledger maturing {date}   # Print rows where window_end <= date AND status=IN-FLIGHT
seo-hypothesis-ledger score {id} {result} {status} {note}   # Close out a row
seo-hypothesis-ledger stats             # Pass/fail tally by channel
```

### `log` operation

Steps:
1. Allocate next `S-###`.
2. Pull current value of `metric` from latest seo-monitor report or GSC data.
3. Validate `metric` is in the whitelist (see below). Reject if not.
4. Append row to ledger with `status=IN-FLIGHT` or `status=SEEDED`.
5. Write `actions/S-###.md` with context.
6. Print the assigned ID.

### `score` operation

Steps:
1. Read the row, confirm status is `IN-FLIGHT`.
2. Append a **new row** with the same id and closed-out values. **Never edit existing rows.**
3. If `PASS`, emit a diff suggestion for seo-strategy-master section 4 (Winning Tactics).
4. If `FAIL`, emit a diff suggestion for section 5 (Dead Hypotheses).

## Metric Whitelist

Only these metric names are valid (they come from seo-monitor output and GSC data):

```
gsc_impressions_7d              gsc_clicks_7d              gsc_avg_ctr_7d
gsc_avg_position_7d             organic_sessions_7d        organic_unique_users_7d
gsc_page_{slug}_impressions_7d  gsc_page_{slug}_clicks_7d  gsc_page_{slug}_ctr_7d
gsc_page_{slug}_position_7d     guides_indexed             guides_published
web_sessions_7d                 web_unique_users_7d

# Keyword-specific metrics (from keyword-targets.json + GSC cross-reference)
keyword_{query}_volume          keyword_{query}_difficulty  keyword_{query}_position_7d
keyword_{query}_impressions_7d  keyword_{query}_ctr_7d
keyword_gaps_count              keyword_page1_count        keyword_tracked_count
```

Keyword metrics use the keyword string with spaces replaced by underscores (e.g., `keyword_claude_code_vs_cursor_position_7d`). Volume and difficulty come from DataForSEO (updated monthly). Position, impressions, and CTR come from GSC (updated daily).

## Default Windows

SEO hypotheses default to 14-day windows (vs 7-day for marketing) because:
- Google takes 2-7 days to re-crawl after title/meta changes
- Index updates can take 3-14 days for non-priority pages
- Position changes take 5-14 days to stabilize

For indexing-related hypotheses (sitemap submissions, new content), use 21-day windows.
