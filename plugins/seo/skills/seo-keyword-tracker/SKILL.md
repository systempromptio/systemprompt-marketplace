---
name: seo-keyword-tracker
description: "Pulls DataForSEO keyword data, updates keyword-targets.json, refreshes keyword-research.md, discovers new keywords, and seeds hypotheses. Monthly full refresh + daily lightweight cross-reference in seo-monitor. Load identity first."
metadata:
  version: "1.0.0"
---

# SEO Keyword Tracker

Keyword intelligence layer for the SEO system. Owns the canonical keyword targets, pulls live search data from DataForSEO, and feeds daily actions into the hypothesis ledger.

## Dependencies

Load `identity` first. It defines ICP, positioning, and which keyword clusters matter.

## Two Run Modes

### Monthly Full Refresh (`/loop 30d` or manual)

Pulls fresh DataForSEO data for all tracked keywords, discovers new keywords, updates all data files, and generates a full keyword report. Cost: ~$0.60.

### Daily Cross-Reference (called by `seo-monitor`)

No API calls. Reads `keyword-targets.json` and cross-references with today's GSC data to surface keyword movements, new ranking queries, and content gaps. Zero cost.

---

## Data Files

All files live in `/var/www/html/systemprompt-web/reports/seo/`.

### 1. `data/keyword-targets.json` (canonical keyword registry)

The single source of truth for which keywords we track and which guides own them. Every content skill reads this file.

```json
{
  "_meta": {
    "description": "Canonical tracked keywords",
    "last_updated": "YYYY-MM-DD",
    "last_updated_by": "seo-keyword-tracker",
    "dataforseo_pull_date": "YYYY-MM-DD",
    "total_keywords": N,
    "total_addressable_volume": N
  },
  "keywords": [
    {
      "keyword": "claude code vs cursor",
      "volume": 6600,
      "difficulty": 0,
      "cpc": 57.43,
      "trend_3mo_pct": 112,
      "intent": "commercial",
      "cluster": "comparison",
      "assigned_guide": "claude-code-vs-cursor",
      "classification": "primary|secondary|brand-adjacent",
      "target_position": 3,
      "opportunity_score": 81.1,
      "status": "covered|gap|needs-data|weak-targeting",
      "notes": "..."
    }
  ]
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| keyword | string | Exact search query |
| volume | int/null | Monthly search volume (DataForSEO) |
| difficulty | int/null | Keyword difficulty 0-100 (DataForSEO) |
| cpc | float/null | Cost per click USD (DataForSEO) |
| trend_3mo_pct | int/null | 3-month volume trend percentage |
| intent | string | informational, commercial, transactional |
| cluster | string | Keyword cluster name |
| assigned_guide | string/null | Slug of the guide targeting this keyword |
| classification | string | primary (H1/title), secondary (covered in body), brand-adjacent |
| target_position | int/null | Target Google position |
| opportunity_score | float/null | Composite score (volume * (100-difficulty) * trend_factor / 10000) |
| status | string | covered, gap, needs-data, weak-targeting |
| notes | string | Free text |

**Status values:**
- `covered`: Guide exists and targets this keyword in title/H1
- `gap`: No guide targets this keyword yet (content to create)
- `needs-data`: Keyword added but no DataForSEO data pulled yet
- `weak-targeting`: Guide exists but keyword is not in title/H1

### 2. `data/keyword-snapshots.jsonl` (append-only history)

One JSON line per keyword per refresh. Enables trend tracking across months.

```json
{"date":"2026-04-16","keyword":"claude code vs cursor","volume":6600,"difficulty":0,"cpc":57.43,"trend_3mo_pct":112,"prev_volume":5400,"volume_change_pct":22.2}
```

Appended by the monthly full refresh. Never edited. This is how we track whether keywords are growing or shrinking over time.

### 3. `keyword-research.md` (human-readable report)

Updated on each monthly refresh. Contains:
- Executive summary with key findings
- Tier 1/2/3 keyword tables with volume, difficulty, trend, assigned guide
- Cluster analysis with health ratings
- Hypergrowth and declining keyword lists
- Zero-volume keywords to retire
- New keyword discoveries

This is the file Ed reads. The JSON files are machine-readable for other skills.

---

## Monthly Full Refresh Procedure

### Step 1: Pull Search Volume for All Tracked Keywords

Read `data/keyword-targets.json` to get the keyword list. Pull fresh search volume data:

```bash
curl -s -X POST "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live" \
  -H "Authorization: Basic ZWRAdHlpbmdzaG9lbGFjZXMuY29tOjBmOThlODg1YmZlN2RlMWQ0" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["claude code vs cursor", "claude code cost", "...all tracked keywords..."],
    "location_code": 2840,
    "language_code": "en"
  }]'
```

Response contains: `search_volume`, `competition`, `cpc`, `monthly_searches` (array of 12 months for trend calculation).

### Step 2: Pull Keyword Suggestions for New Discovery

Use the "keywords for site" endpoint to discover what Google associates with systemprompt.io:

```bash
curl -s -X POST "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_site/live" \
  -H "Authorization: Basic ZWRAdHlpbmdzaG9lbGFjZXMuY29tOjBmOThlODg1YmZlN2RlMWQ0" \
  -H "Content-Type: application/json" \
  -d '[{
    "target": "systemprompt.io",
    "location_code": 2840,
    "language_code": "en"
  }]'
```

Also pull suggestions for our top 5 keywords:

```bash
curl -s -X POST "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live" \
  -H "Authorization: Basic ZWRAdHlpbmdzaG9lbGFjZXMuY29tOjBmOThlODg1YmZlN2RlMWQ0" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["claude code vs cursor", "claude code cost", "anthropic marketplace", "claude agent sdk", "how to use claude code"],
    "location_code": 2840,
    "language_code": "en"
  }]'
```

### Step 3: Pull Keyword Difficulty

```bash
curl -s -X POST "https://api.dataforseo.com/v3/dataforseo_labs/google/bulk_keyword_difficulty/live" \
  -H "Authorization: Basic ZWRAdHlpbmdzaG9lbGFjZXMuY29tOjBmOThlODg1YmZlN2RlMWQ0" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["...all tracked + newly discovered keywords..."],
    "location_code": 2840,
    "language_code": "en"
  }]'
```

### Step 4: Update Data Files

**4a. Update keyword-targets.json:**
- For each existing keyword: update volume, difficulty, cpc, trend_3mo_pct
- Calculate new opportunity_score: `volume * (100 - difficulty) * (1 + trend_3mo_pct/100) / 10000`
- For newly discovered keywords with volume > 50: add to the keywords array with `status: "gap"` if no guide exists, `status: "needs-data"` otherwise
- Update `_meta.dataforseo_pull_date` and `_meta.last_updated`

**4b. Append to keyword-snapshots.jsonl:**
- One line per keyword with today's date, current volume, difficulty, and delta from previous snapshot
- Calculate `volume_change_pct` from previous snapshot (search by keyword in the file)

**4c. Rewrite keyword-research.md:**
- Full regeneration with current data
- Same structure as existing report (tiers, clusters, trends, gaps)
- Include comparison to previous month's data from snapshots

### Step 5: Generate Actions

For each change detected, create an actionable output:

**New high-value keywords (volume > 200, difficulty < 30, no assigned guide):**
- Log as hypothesis in the SEO hypothesis ledger (S-###)
- Draft: "Create guide targeting '{keyword}' ({volume}/mo, difficulty {difficulty})"

**Volume spikes (>50% increase from previous month):**
- Flag in the report as "breakout keyword"
- If assigned guide exists, recommend optimizing title/meta to better target this keyword
- If no guide, escalate to content pipeline

**Volume declines (>30% decrease from previous month):**
- Flag as "declining keyword"
- If assigned guide depends on this keyword as primary, recommend finding a replacement keyword

**Difficulty drops (keyword became easier to rank for):**
- Flag as "new opportunity"
- If we have a guide but rank poorly, recommend content refresh

**Status changes:**
- Keywords that move from `gap` to `covered` (new guide published)
- Keywords that move from `needs-data` to scored (first data pull)

### Step 6: Update Strategy Master

Apply diffs to `reports/seo/seo-strategy-master.md`:
- Update section 8 (Content Pipeline) with new gap keywords
- Add changelog entry to section 9

---

## Daily Cross-Reference (no API calls)

Called by `seo-monitor` during each daily run. This is how keyword data drives daily actions.

### Procedure

1. **Read keyword-targets.json** to get the tracked keyword list with assigned guides.

2. **Cross-reference with today's GSC query data:**
   - For each GSC query, check if it matches a tracked keyword
   - Report position changes for tracked keywords (GSC avg position vs target_position)
   - Flag tracked keywords with zero GSC impressions (not indexed or not ranking)
   - Flag GSC queries with >50 impressions that don't match any tracked keyword (discovery)

3. **Generate the "Keyword Movements" section** for the daily report:

```markdown
## Keyword Movements

### Tracked Keywords in GSC

| Keyword | Target Pos | GSC Pos | GSC Imp | GSC Clicks | Trend | Guide |
|---------|-----------|---------|---------|------------|-------|-------|
| claude code github actions | 5 | 9.6 | 74 | 1 | -- | github-actions |

### Tracked Keywords Missing from GSC

| Keyword | Volume | Assigned Guide | Published | Days Since |
|---------|--------|---------------|-----------|-----------|
| self-hosted AI governance | TBD | self-hosted-ai-governance | 2026-04-21 | -- |

### Untracked Queries with Impressions

| Query | Impressions | Clicks | Position | Action |
|-------|------------|--------|----------|--------|
| failed to install anthropic marketplace | 75 | 1 | 7.0 | Consider adding to keyword-targets.json |
```

4. **Surface daily actions:**
   - Any tracked keyword that dropped >2 positions WoW: "Investigate ranking drop for '{keyword}'"
   - Any tracked keyword with >500 impressions and <1% CTR: "Rewrite title/meta for '{keyword}' guide"
   - Any untracked query with >30 impressions: "Add '{query}' to keyword-targets.json and assign a guide"
   - Any `status: "gap"` keyword with volume >200 and difficulty <30: "Create content for '{keyword}'"

---

## How This Drives Content

### Before Writing a New Guide

The `guide-writer` skill reads `keyword-targets.json` to:
1. Select the primary keyword (highest opportunity_score among `status: "gap"` keywords in the target cluster)
2. Select 2-3 secondary keywords from the same cluster
3. Validate that the primary keyword has volume > 0 and difficulty < 50
4. Set the title to include the primary keyword verbatim

### Before Optimizing an Existing Guide

The `guide-optimiser` skill reads `keyword-targets.json` to:
1. Find the primary keyword assigned to the guide
2. Check if the current title contains the keyword verbatim
3. Cross-reference with GSC data to see which queries actually drive impressions
4. If the high-CTR GSC queries differ from the assigned keyword, recommend updating the keyword assignment

### Content Pipeline Prioritization

The hypothesis ledger + keyword targets together determine what to write next:

1. Sort `status: "gap"` keywords by `opportunity_score` descending
2. Filter to keywords with `volume > 200` and `difficulty < 40`
3. The top keyword becomes the next guide to write
4. Log as S-### hypothesis: "If we publish a guide targeting '{keyword}' then gsc_page_{slug}_impressions_7d > 0 within 21d"

---

## How This Drives Daily Analysis

The seo-monitor daily run includes these keyword-driven sections:

1. **Keyword Health Dashboard**: For each cluster, how many tracked keywords are ranking page 1, page 2, or not at all
2. **Keyword Movements**: Position changes WoW for tracked keywords (from GSC data, not DataForSEO)
3. **Gap Report**: Keywords with `status: "gap"` sorted by opportunity score
4. **Actions**: 1-3 keyword-specific actions per day, each tied to an S-### hypothesis

---

## How This Tracks Progress

### Weekly (in seo-monitor report)

- Count of tracked keywords ranking page 1 vs total tracked
- Average position across all tracked keywords with GSC data
- Keywords gained/lost page 1 this week
- CTR by keyword (from GSC)

### Monthly (in keyword-research.md)

- Volume changes for all tracked keywords (from DataForSEO snapshots)
- New keywords discovered
- Keywords retired (zero volume confirmed across 2+ months)
- Cluster health changes (strength ratings up/down)
- Content gap closure rate (how many gaps were filled since last month)

### Quarterly (in seo-strategy-master.md)

- Progress toward 30/60/90 objectives
- Hypothesis pass/fail rate for SEO actions
- Pillar strength trend (from keyword coverage + ranking data)
- Winning and dead hypotheses aggregated

---

## Reporting Consistency

Every output follows the same pattern:

1. **Data** (numbers, tables, no adjectives)
2. **Diagnosis** (what the numbers mean, one sentence)
3. **Action** (what to do, with S-### hypothesis ID)
4. **Metric** (how to measure success)
5. **Window** (when to check back)

No run of this skill or seo-monitor should produce a report without at least one action item tied to a hypothesis.

---

## Anti-Sludge Rules

- Never report a keyword movement without the actual numbers (position X to Y, volume N)
- Never recommend creating content without checking if volume > 0
- Never flag a "declining keyword" without comparing to at least 2 months of data
- Always include the DataForSEO pull date so we know how stale the data is
- The `dataforseo_pull_date` in keyword-targets.json must be updated on every refresh
- If DataForSEO API returns an error, surface it in the report, do not silently skip

---

## Cost Management

DataForSEO charges per API call:

| Endpoint | Cost per call | Our usage |
|----------|--------------|-----------|
| Search volume (batch) | ~$0.10 per 700 keywords | 1x/month |
| Keywords for site | ~$0.05 | 1x/month |
| Keywords for keywords | ~$0.10 per 5 seeds | 1x/month |
| Bulk keyword difficulty | ~$0.10 per 700 keywords | 1x/month |

**Monthly total: ~$0.40-0.60.** Annual: ~$5-7. The daily cross-reference uses zero API calls (GSC data only).
