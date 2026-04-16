---
name: seo-monitor
description: "Daily SEO performance review. Analyses content traffic, engagement, and search performance across published guides using internal analytics and Google Search Console. Generates actionable reports. Designed for daily /loop. Load identity first."
metadata:
  version: "2.1.0"
  git_hash: "3a55706"
---

# SEO Monitor

> **Implements:** `commons:daily-brief-pattern` — 8-step orchestration sequence (adapted for SEO: performance review + hypothesis scoring + action generation). Also writes to Section 1 of `seo-strategy-master` per `commons:strategy-master-pattern`.

Daily performance review of all published content. Pulls internal analytics and Google Search Console data, cross-references with the content inventory, and generates an actionable report. Designed for `/loop 1d`.

## Dependencies

**Load `identity` before this skill.** Identity defines positioning, ICP, and keyword strategy context. This skill handles performance measurement and recommendations.

## Source of Truth

**Read the SEO Strategy Master before running this skill:**

```
/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md
```

This living document is the single source of truth for:
- Current performance snapshot (updated by this skill on each run)
- 30/60/90 objectives for organic sessions, GSC clicks, CTR, indexing
- Active SEO hypotheses (rendered from the hypothesis ledger)
- Pillar health assessments
- Technical SEO issues
- Content pipeline and gap analysis

**Hypothesis ledger:**

```
/var/www/html/systemprompt-web/reports/seo/data/hypothesis-ledger.md
```

The SEO hypothesis ledger tracks testable SEO actions with S-### IDs. On each run, this skill:
1. Checks for hypotheses with `window_end <= today` and scores them
2. Logs new hypotheses discovered during analysis
3. Updates the strategy master's section 3 (Active Hypotheses) rendering

**Keyword targets** (machine-readable, read by content skills):

```
/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json
```

On each daily run, cross-reference this file with GSC query data to produce the Keyword Movements section. No DataForSEO API calls needed daily. See `seo-keyword-tracker` skill for the monthly full refresh that updates this file.

**Satellite documents** (all in `reports/seo/`):
- `keyword-research.md` -- DataForSEO keyword data (updated monthly by seo-keyword-tracker)
- `data/keyword-targets.json` -- Canonical keyword registry (updated monthly)
- `data/keyword-snapshots.jsonl` -- Append-only keyword history (updated monthly)
- `guide-inventory.md` -- All guides with metadata
- `metadata-audit.md` -- Title and description audits
- `interlinking-strategy.md` -- Internal link map
- `backlink-strategy.md` -- External link opportunities
- `traffic-analytics.md` -- Traffic source history

**Daily metrics** are appended to `reports/seo/data/seo-metrics.jsonl` after each run.

## Overview

This skill runs eight steps:

1. Read the SEO strategy master and inventory all published guides
2. Pull internal analytics (systemprompt CLI)
3. Pull Google Search Console data (if configured)
4. Cross-reference keyword targets with GSC queries (daily keyword intelligence, zero API cost)
5. Cross-reference GitHub engagement data (from latest github-monitor report)
6. Score maturing hypotheses from the SEO hypothesis ledger
7. Analyse performance against strategy targets
8. Generate and save a structured report (including Keyword Movements section)
9. Append daily metrics to seo-metrics.jsonl and update the strategy master

## Step 1: Read Strategy and Inventory Content

First, read the SEO Strategy Master at `/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md`. Extract:
- The complete guide inventory tables (slugs, primary keywords, long-tail keywords, search intent, status)
- Keyword cluster map (pillar pages, sub-topics, cluster strength assessments)
- Content gap analysis (high-priority topics not yet covered)
- Suggested future publishing schedule (what should have been published by now)
- Performance benchmarks (100+ sessions/month within 90 days, page 1 ranking within 90 days)
- Internal linking recommendations (what links should exist)

Then read the frontmatter from every guide in `/var/www/html/systemprompt-web/services/content/guides/*/index.md` to get current metadata:
- `title`, `slug`, `keywords`, `category`, `tags`
- `published_at`, `updated_at`
- `public` (true/false)
- `description` (used as meta description)

Cross-reference the live inventory against the strategy document to identify:
- Guides that exist in the strategy but have not been published yet
- Guides that are past their target publication date
- Keyword targets from the strategy that are not reflected in guide frontmatter

## Step 2: Pull Internal Analytics

Run these commands to collect traffic and engagement data. Use `--json` for parseable output and `--since 7d` for the current period.

```bash
systemprompt analytics overview --since 7d --json
systemprompt analytics content top --limit 30 --since 7d --json
systemprompt analytics content trends --since 7d --json
systemprompt analytics content popular --limit 30 --since 7d --json
systemprompt analytics traffic sources --since 7d --json
systemprompt analytics sessions stats --since 7d --json
systemprompt analytics sessions trends --since 7d --json
```

For week-over-week comparison, also run:

```bash
systemprompt analytics content top --limit 30 --since 14d --json
systemprompt analytics sessions stats --since 14d --json
```

Subtract the 7d data from the 14d data to derive the previous week's numbers.

### Key Metrics to Extract

| Metric | Source Command |
|--------|--------------|
| Sessions per guide | `analytics content top` |
| Engagement pattern (bounce/skimmer/reader/engaged) | `analytics content top` |
| Traffic sources (organic/direct/referral/social) | `analytics traffic sources` |
| Total sessions and visitors | `analytics sessions stats` |
| Session trends | `analytics sessions trends` |
| Content popularity ranking | `analytics content popular` |

## Step 3: Pull Google Search Console Data

### Prerequisites

GSC integration requires a service account. If not configured, skip this step and note "GSC data: Not configured" in the report.

**One-time setup:**
1. Create a Google Cloud project with the Search Console API enabled
2. Create a service account and download the JSON key
3. Add the service account email as a user in Google Search Console for `sc-domain:systemprompt.io`
4. Save the JSON key as `gsc.json` in the systemprompt-web project root (`/var/www/html/systemprompt-web/gsc.json`)

### Service Account Key

The key file is at:

```
/var/www/html/systemprompt-web/gsc.json
```

If this file does not exist, skip the GSC step and note "GSC data: Not configured" in the report.

### Authentication

Generate a JWT and exchange it for an access token. The service account JSON contains `client_email`, `private_key`, and `token_uri`.

```bash
# Load the service account key from file
GSC_KEY_FILE="/var/www/html/systemprompt-web/gsc.json"

# Use python3 to authenticate and get an access token:
ACCESS_TOKEN=$(python3 -c "
import json, sys, time, base64
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from pathlib import Path

# Load key from file
key_file = Path('$GSC_KEY_FILE')
if not key_file.exists():
    print('GSC_NOT_CONFIGURED', file=sys.stderr)
    sys.exit(1)

try:
    key_data = json.loads(key_file.read_text())
except json.JSONDecodeError as e:
    print(f'ERROR: gsc.json is not valid JSON: {e}', file=sys.stderr)
    sys.exit(1)

# Validate required fields
for field in ('client_email', 'private_key', 'token_uri'):
    if field not in key_data:
        print(f'ERROR: gsc.json missing required field: {field}', file=sys.stderr)
        sys.exit(1)

email = key_data['client_email']
private_key = key_data['private_key']

# Build and sign JWT
now = int(time.time())
claims = {
    'iss': email,
    'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
    'aud': 'https://oauth2.googleapis.com/token',
    'iat': now,
    'exp': now + 3600
}

try:
    import jwt as pyjwt
    token = pyjwt.encode(claims, private_key, algorithm='RS256')
except ImportError:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    header = base64.urlsafe_b64encode(json.dumps({'alg':'RS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b'=').decode()
    key = serialization.load_pem_private_key(private_key.encode(), password=None)
    message = f'{header}.{payload}'.encode()
    signature = key.sign(message, padding.PKCS1v15(), hashes.SHA256())
    token = f'{header}.{payload}.{base64.urlsafe_b64encode(signature).rstrip(b\"=\").decode()}'

# Exchange JWT for access token
data = urlencode({
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': token
}).encode()
req = Request('https://oauth2.googleapis.com/token', data=data, method='POST')
try:
    resp = json.loads(urlopen(req).read())
except Exception as e:
    print(f'ERROR: Token exchange failed: {e}', file=sys.stderr)
    sys.exit(1)

if 'access_token' not in resp:
    print(f'ERROR: No access_token in response. Check service account permissions. Response: {resp}', file=sys.stderr)
    sys.exit(1)

print(resp['access_token'])
")

# If authentication failed, skip GSC and note it in the report
if [ $? -ne 0 ]; then
    echo "GSC authentication failed. Skipping Search Console data."
    GSC_AVAILABLE=false
else
    GSC_AVAILABLE=true
fi
```

### Querying Search Analytics

Only run these queries if `GSC_AVAILABLE=true`. For each API call, check the HTTP response for errors. A 403 means the service account does not have permission in Search Console. A 401 means the access token is invalid or expired. Any error response should be logged and the GSC section skipped gracefully.

```bash
# Last 7 days performance by page
curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -d '7 days ago' +%Y-%m-%d)'",
    "endDate": "'$(date -d 'yesterday' +%Y-%m-%d)'",
    "dimensions": ["page"],
    "rowLimit": 100
  }'

# Last 7 days performance by query
curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -d '7 days ago' +%Y-%m-%d)'",
    "endDate": "'$(date -d 'yesterday' +%Y-%m-%d)'",
    "dimensions": ["query", "page"],
    "rowLimit": 500
  }'

# Previous 7 days for comparison
curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -d '14 days ago' +%Y-%m-%d)'",
    "endDate": "'$(date -d '8 days ago' +%Y-%m-%d)'",
    "dimensions": ["page"],
    "rowLimit": 100
  }'
```

### GSC Data to Extract

| Metric | Use |
|--------|-----|
| Impressions per page | How visible is each guide in search results |
| Clicks per page | How many searchers actually visit |
| CTR per page | Title/description effectiveness |
| Average position per page | Ranking strength |
| Top queries per page | What searches drive traffic |
| High-impression low-CTR pages | Quick wins for title/meta improvements |
| Position 5-20 queries | Near page-1 ranking opportunities |

## Step 4: Cross-Reference Keyword Targets with GSC Queries

Read `reports/seo/data/keyword-targets.json`. For each tracked keyword:

1. **Match against GSC query data** (fuzzy match: the GSC query contains the tracked keyword string)
2. **Record position, impressions, clicks, CTR** for each matched keyword
3. **Compare to target_position** from keyword-targets.json
4. **Flag movements:** if position changed >2 spots WoW, note as movement

Generate three tables for the report:

**Tracked Keywords in GSC:**
Keywords from keyword-targets.json that appear in today's GSC data, with their actual vs target position.

**Tracked Keywords Missing from GSC:**
Keywords we target but that have zero GSC impressions (guide not indexed, or not ranking for this keyword).

**Untracked Queries with Impressions:**
GSC queries with >30 impressions that don't match any tracked keyword. These are keyword discovery opportunities. For each, recommend: "Add '{query}' to keyword-targets.json" with an action to either assign an existing guide or flag as a content gap.

**Daily keyword actions (1-3 per day):**
- Tracked keyword dropped >2 positions: "Investigate ranking drop for '{keyword}' on {guide}"
- Tracked keyword with >500 impressions and <1% CTR: "Rewrite title/meta for {guide} to better match '{keyword}'"
- Untracked query with >50 impressions: "Add '{query}' to keyword tracking and assign to {guide_or_gap}"
- `status: "gap"` keyword with volume >200 and difficulty <30: "Create content for '{keyword}' ({volume}/mo)"

## Step 5: Analyse Performance

Cross-reference all four data sources (inventory, internal analytics, GSC, keyword targets) to build a complete picture.

### Analysis Framework

**Winners (top 5 by combined score):**
- High sessions AND good engagement (reader or engaged pattern)
- Strong organic traffic OR improving trend
- If GSC available: high clicks, good CTR, improving position
- Analyse WHY: topic relevance, keyword targeting, freshness, internal links

**Underperformers (bottom 5 by combined score):**
- Low sessions OR declining trend
- Poor engagement (bounce or skimmer pattern)
- If GSC available: low CTR despite impressions, declining position
- Diagnose the specific problem and recommend a specific fix

**Quick wins (GSC required):**
- Pages with >100 impressions but <3% CTR
- Action: rewrite title tag and meta description to improve click-through

**Ranking opportunities (GSC required):**
- Queries where average position is 5-20 (close to page 1 but not there)
- Action: strengthen the targeting page with better keyword placement, internal links, content depth

**Content gaps (cross-reference with strategy document):**
- High-priority gaps listed in the strategy document that have not been published yet
- Guides past their target publication date from the suggested future publishing schedule
- Keywords from guide frontmatter with no GSC impressions (not indexed or not ranking)
- GSC queries with impressions but no matching guide (content to create)
- Keyword clusters with weak strength ratings that need supporting content

**Strategy compliance:**
- Are guides hitting the benchmark of 100+ organic sessions/month within 90 days of publication?
- Are primary keywords ranking page 1 within 90 days?
- Are the recommended internal links from the strategy document actually in place?
- Is the publishing cadence on track with the suggested schedule?
- Are there content refresh triggers firing (ranking drops, traffic declines, product updates)?

### Anti-Sludge Rules

- Be specific with numbers. "Sessions increased 34% week-over-week" not "traffic is doing well"
- Name the actual guide, URL, and metric in every recommendation
- Diagnose specific problems: "bounce rate is 72% suggesting the title promises something the content does not deliver" not "engagement could be improved"
- Recommendations must be actionable: "Rewrite the meta description from X to Y" not "consider improving SEO"
- No generic praise. If something is working, explain the specific mechanism.
- No em dashes. Use commas, periods, or parentheses.
- No AI cliches (revolutionize, game-changer, unlock, supercharge, seamlessly, cutting-edge)

## Step 5: Score Maturing Hypotheses

Read the SEO hypothesis ledger at `reports/seo/data/hypothesis-ledger.md`.

For each row where `status = IN-FLIGHT` and `window_end <= today`:
1. Look up the current value of `metric` from today's analytics/GSC data
2. Compare to `baseline` and the hypothesis target
3. Append a new row with the result and status (PASS/FAIL/INCONCLUSIVE)
4. If PASS, note the winning tactic for the strategy master section 4
5. If FAIL, note the dead hypothesis for section 5

For new insights discovered during analysis (e.g., a new high-impression low-CTR page), consider logging a new hypothesis with the next available S-### ID.

## Step 6: Generate and Save Report

Save the report to:

```
reports/seo/daily/YYYY-MM-DD/seo-monitor.md
```

Use today's date in the filename.

### Report Structure

```markdown
# SEO Monitor Report

**Date:** {YYYY-MM-DD}
**Period:** Last 7 days (compared to previous 7 days)
**Guides published:** {N} total | {N} public
**GSC data:** Available | Not configured

---

## Traffic Summary

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Total sessions | {N} | {N} | {+/-N%} |
| Unique visitors | {N} | {N} | {+/-N%} |
| Organic search sessions | {N} | {N} | {+/-N%} |
| Avg engagement rate | {N%} | {N%} | {+/-N%} |

## Traffic Sources

| Source | Sessions | % of Total |
|--------|----------|-----------|
| Organic search | {N} | {N%} |
| Direct | {N} | {N%} |
| Referral | {N} | {N%} |
| Social | {N} | {N%} |

---

## Search Console Performance

(Include only if GSC is configured)

### Top Search Queries

| Query | Impressions | Clicks | CTR | Avg Position |
|-------|------------|--------|-----|-------------|
| {query} | {N} | {N} | {N%} | {N} |

### Quick Wins (high impressions, low CTR)

| Page | Query | Impressions | CTR | Position | Action |
|------|-------|------------|-----|----------|--------|
| {slug} | {query} | {N} | {N%} | {N} | {Specific fix} |

### Ranking Opportunities (position 5-20)

| Query | Page | Position | Impressions | Action |
|-------|------|----------|------------|--------|
| {query} | {slug} | {N} | {N} | {Specific action} |

---

## Top Performers

### 1. {Guide Title}
- **URL:** /guides/{slug}
- **Sessions:** {N} ({+/-N%} wow)
- **Engagement:** {reader|engaged} ({N%} read >50%)
- **Top source:** {organic|referral|direct}
- **GSC:** {N} clicks, {N} impressions, position {N} for "{top query}"
- **Why it works:** {Specific analysis of what makes this content successful}

(repeat for top 5)

---

## Underperformers

### 1. {Guide Title}
- **URL:** /guides/{slug}
- **Sessions:** {N} ({+/-N%} wow)
- **Engagement:** {bounce|skimmer} ({N%} bounce rate)
- **Keywords targeted:** {from frontmatter}
- **GSC:** {N} impressions but {N} clicks (CTR {N%})
- **Problem:** {Specific diagnosis}
- **Recommendation:** {Specific, actionable fix}

(repeat for bottom 5)

---

## Content Inventory Status

| Category | Guides | Avg Sessions/Week | Avg GSC Position | Trend |
|----------|--------|-------------------|-----------------|-------|
| claude-code | {N} | {N} | {N} | {up/down/flat} |
| plugins | {N} | {N} | {N} | {up/down/flat} |
| mcp | {N} | {N} | {N} | {up/down/flat} |
| content | {N} | {N} | {N} | {up/down/flat} |

---

## Strategy Compliance

**Source:** reports/seo/seo-strategy-master.md

### Publishing Schedule

| Planned Guide | Target Date | Status |
|--------------|-------------|--------|
| {Guide from strategy} | {date} | Published | On track | Overdue |

### Benchmark Tracking

| Guide | Days Since Published | Organic Sessions/Month | Target (100+) | Status |
|-------|---------------------|----------------------|---------------|--------|
| {slug} | {N} | {N} | {met/not met} | {on track/at risk/missed} |

### Missing Internal Links

| From | To | Recommended By Strategy | Status |
|------|----|------------------------|--------|
| {slug} | {slug} | Yes | Missing | Present |

### Cluster Health

| Cluster | Pillar Page | Guides | Strength | Change |
|---------|------------|--------|----------|--------|
| Claude Code | claude-code-daily-workflows | {N} | {Strong/Moderate/Weak} | {improved/stable/declined} |
| MCP | claude-code-mcp-servers-extensions | {N} | {Strong/Moderate/Weak} | {improved/stable/declined} |
| Marketplace | getting-started-anthropic-marketplace | {N} | {Strong/Moderate/Weak} | {improved/stable/declined} |
| Agent SDK | build-custom-claude-agent | {N} | {Strong/Moderate/Weak} | {improved/stable/declined} |
| Enterprise | enterprise-claude-code-managed-settings | {N} | {Strong/Moderate/Weak} | {improved/stable/declined} |

---

## GitHub Engagement (External Authority)

Cross-reference with the latest github-monitor report. Read the most recent report from:

```bash
ls -t reports/github/daily/*/github-monitor.md 2>/dev/null | head -1
```

If a github-monitor report exists, include this section. If not, note "GitHub monitor: Not yet configured. Run `github-monitor` skill to start tracking."

### GitHub Referral Traffic

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| GitHub referral sessions | {N} | {N} | {+/-N%} |
| GitHub % of total traffic | {N%} | {N%} | {+/-pp} |

(Pull from `analytics traffic sources` data, filter for GitHub referrer)

### Contributions Made

| Date | Repo | Action | Guide Linked | Engagement |
|------|------|--------|-------------|------------|
| {date} | {repo} | Issue comment #{N} | {guide} | {upvotes/replies} |

(Pull from the tracking table in the github-monitor report)

### Backlink Status

| Source | Type | URL | Status | Domain Authority |
|--------|------|-----|--------|-----------------|
| {awesome-list or repo} | {PR/comment/discussion} | {URL} | {merged/pending/open} | {stars}k stars |

### Pending Opportunities

List the top 3 opportunities from the latest github-monitor report that have not yet been actioned.

---

## Opportunities

1. **{Topic}**: {Why this is an opportunity, citing specific data from analytics or strategy gaps}
2. ...

## Prioritised Next Steps

1. [ ] {Highest impact action with specific guide/content}
2. [ ] ...
3. [ ] ...
4. [ ] {Content to create}
5. [ ] {Content to update}
```

## Step 7: Append Daily Metrics and Update Strategy Master

### Append to seo-metrics.jsonl

After generating the report, append a single JSON line to `reports/seo/data/seo-metrics.jsonl`:

```json
{"date":"YYYY-MM-DD","sessions_7d":N,"unique_users_7d":N,"organic_sessions_7d":N,"organic_share_pct":N,"gsc_impressions_7d":N,"gsc_clicks_7d":N,"gsc_avg_ctr_pct":N,"gsc_avg_position":N,"guides_published":N,"guides_indexed":N}
```

This creates an append-only time series for trend analysis across runs.

### Update Strategy Master

Apply targeted diffs to `reports/seo/seo-strategy-master.md`:
1. Update section 1 (Current Performance Snapshot) with this week's numbers
2. Re-render section 3 (Active Hypotheses) from the hypothesis ledger
3. Move any scored hypotheses to section 4 (Winning Tactics) or section 5 (Dead Hypotheses)
4. Append a changelog entry to section 9

**Never rewrite the strategy master wholesale.** Only apply diffs, and always append to the changelog.

## Quality Checklist

Before saving the report, verify:

- [ ] Every recommendation names a specific guide and URL
- [ ] Every metric includes actual numbers, not vague language
- [ ] Week-over-week comparisons use percentages
- [ ] No em dashes
- [ ] No AI cliches
- [ ] No generic praise or vague recommendations
- [ ] GSC section clearly marked as unavailable if credentials not set
- [ ] Report saved to the correct path with today's date
- [ ] Aligns with `identity` keyword strategy and positioning
