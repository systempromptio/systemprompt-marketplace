---
name: seo-monitor
description: "Daily SEO performance review. Analyses content traffic, engagement, and search performance across published guides using internal analytics and Google Search Console. Generates actionable reports. Designed for daily /loop. Load identity first."
metadata:
  version: "1.0.1"
  git_hash: "4b835fd"
---

# SEO Monitor

Daily performance review of all published content. Pulls internal analytics and Google Search Console data, cross-references with the content inventory, and generates an actionable report. Designed for `/loop 1d`.

## Dependencies

**Load `identity` before this skill.** Identity defines positioning, ICP, and keyword strategy context. This skill handles performance measurement and recommendations.

## Source of Truth

**Read the SEO Content Strategy Master Plan before running this skill:**

```
/var/www/html/systemprompt-web/services/content/guides/seo-content-strategy-master/index.md
```

This document (also available at `/guides/seo-content-strategy-master/` on the site) is the single source of truth for:
- Complete guide inventory with primary keywords, long-tail keywords, and search intent
- Keyword cluster map (which guides belong to which clusters and their pillar pages)
- Content gap analysis (high-priority topics not yet covered)
- Internal linking strategy (which guides should link to which)
- SEO metadata standards (title length, description format, slug conventions)
- Performance tracking benchmarks (100+ organic sessions/month within 90 days, page 1 within 90 days)
- Content refresh triggers (ranking drop, traffic decline, product updates)
- Suggested future publishing schedule with target dates and priorities
- Competitive benchmarking targets

Use this document to evaluate whether each guide is hitting its keyword targets, whether clusters are strengthening, and whether gap-filling content is being published on schedule.

## Overview

This skill runs five steps:

1. Read the SEO strategy and inventory all published guides
2. Pull internal analytics (systemprompt CLI)
3. Pull Google Search Console data (if configured)
4. Analyse performance against strategy targets
5. Generate and save a structured report

## Step 1: Read Strategy and Inventory Content

First, read the SEO Content Strategy Master Plan at `/var/www/html/systemprompt-web/services/content/guides/seo-content-strategy-master/index.md`. Extract:
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
4. Store the key:

```
Tool: manage_secrets
Action: set
Key: GSC_SERVICE_ACCOUNT_KEY
Value: <paste the full JSON key contents>
```

### Retrieving the Key

```
Tool: get_secrets
Keys: GSC_SERVICE_ACCOUNT_KEY
```

### Authentication

Generate a JWT and exchange it for an access token. The service account JSON contains `client_email`, `private_key`, and `token_uri`.

```bash
# Extract fields from the service account key
CLIENT_EMAIL=$(echo "$GSC_SERVICE_ACCOUNT_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin)['client_email'])")
PRIVATE_KEY=$(echo "$GSC_SERVICE_ACCOUNT_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin)['private_key'])")

# Generate JWT (header.payload.signature)
# Header: {"alg":"RS256","typ":"JWT"}
# Payload: {"iss":CLIENT_EMAIL,"scope":"https://www.googleapis.com/auth/webmasters.readonly","aud":"https://oauth2.googleapis.com/token","iat":NOW,"exp":NOW+3600}

# Use python3 to generate and sign the JWT:
ACCESS_TOKEN=$(python3 -c "
import json, time, base64, hashlib
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# Load key
key_data = json.loads('''$GSC_SERVICE_ACCOUNT_KEY''')
email = key_data['client_email']
private_key = key_data['private_key']

# Build JWT
now = int(time.time())
header = base64.urlsafe_b64encode(json.dumps({'alg':'RS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
payload = base64.urlsafe_b64encode(json.dumps({
    'iss': email,
    'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
    'aud': 'https://oauth2.googleapis.com/token',
    'iat': now,
    'exp': now + 3600
}).encode()).rstrip(b'=').decode()

# Sign with RSA (requires cryptography or jwt library)
try:
    import jwt
    token = jwt.encode({
        'iss': email,
        'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
        'aud': 'https://oauth2.googleapis.com/token',
        'iat': now,
        'exp': now + 3600
    }, private_key, algorithm='RS256')
except ImportError:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
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
resp = json.loads(urlopen(req).read())
print(resp['access_token'])
")
```

### Querying Search Analytics

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

## Step 4: Analyse Performance

Cross-reference all three data sources (inventory, internal analytics, GSC) to build a complete picture.

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

## Step 5: Generate and Save Report

Save the report to:

```
/var/www/html/systemprompt-marketplace/reports/seo-monitor-{YYYY-MM-DD}.md
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

**Source:** [SEO Content Strategy Master Plan](/guides/seo-content-strategy-master/)

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
