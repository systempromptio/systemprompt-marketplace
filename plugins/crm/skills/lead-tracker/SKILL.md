---
name: lead-tracker
description: "Daily CRM and funnel measurement. Pulls GitHub Traffic API for systemprompt-core and systemprompt-template (14d retention, MUST run daily), website analytics via systemprompt CLI, and external feedback signals. Emits 1d/7d/31d funnel deltas and a dated report. Source of truth for every hypothesis metric."
metadata:
  version: "0.3.1"
  git_hash: "d9ea667"
---

# Lead Tracker

The measurable truth. Runs daily. Pulls every signal we have into a single funnel report and updates the persistent leads database. Every `hypothesis-ledger` metric resolves here.

## Why This Must Run Daily

**GitHub Traffic API retains only 14 days.** If this skill does not run at least once every 14 days, historical clone/view data is lost forever. Production cadence is daily via `/loop`. Missing one day is recoverable; missing a week is not.

## Dependencies

Load `commons:marketing-identity` first (for ICP context on referrer analysis). This skill does not depend on `commons:marketing-strategy-master` — it is upstream of it.

## CRITICAL: Profile must be `systemprompt-prod` for analytics reads

**Before running any `systemprompt analytics *` command**, verify the active profile is `systemprompt-prod`. The `local` profile reads a dev database that does not receive real traffic, so every analytics number will be silently wrong. This is the single biggest footgun in this skill.

**Step 0 of every run:**

```bash
# Check the active profile
systemprompt admin session list --json 2>&1 | grep -A1 '"is_active": true' | head -3

# If it is not systemprompt-prod, switch:
systemprompt admin session switch systemprompt-prod

# Confirm
systemprompt admin session list 2>&1 | grep -A2 systemprompt-prod
```

Expected output of the list command should show `"name": "systemprompt-prod"`, `"is_active": true`, and a non-expired `session_status` (e.g. `23h 59m remaining`). If the session is expired, tell Ed to log back in (`systemprompt cloud auth login` or equivalent) and stop — do NOT fall back to `local`.

**Rule of thumb (from memory):**

- `systemprompt-prod` = reading production analytics, GSC, content stats, sessions, traffic, costs. **This skill.**
- `local` = running jobs, writing to local dev DB, testing schema changes, publishing content pipeline dry-runs. **NOT this skill.**

After finishing the run, this skill does **not** switch back to local. If Ed needs local afterwards, he switches manually. Auto-switching back would mask which profile is active in any follow-up command.

Every report this skill writes must include a top-line `profile: systemprompt-prod` marker so a reader can instantly verify the data source.

## Data Sources & Verified Commands

All commands below were validated against the real `systempromptio/systemprompt-core` and `systempromptio/systemprompt-template` GitHub repos and the production `systemprompt` CLI as of 2026-04-15. They are copy-paste ready. **All `systemprompt analytics *` commands assume the active profile is `systemprompt-prod` — see the section above.**

### 1. GitHub Traffic API — `systempromptio/systemprompt-core`

Requires `gh` CLI authenticated with an account that has push/admin on the repo (Ed's `Ejb503` account has admin). Traffic endpoints 403 for anyone else.

```bash
# Views (14d window)
gh api repos/systempromptio/systemprompt-core/traffic/views

# Clones (14d window) — unique cloners is the HONEST signal; raw clones is bot-noisy
gh api repos/systempromptio/systemprompt-core/traffic/clones

# Top referrers (14d window) — the only way we learn distribution channels
gh api repos/systempromptio/systemprompt-core/traffic/popular/referrers

# Top paths (14d window) — what visitors actually looked at
gh api repos/systempromptio/systemprompt-core/traffic/popular/paths
```

Expected shapes (confirmed):

```jsonc
// views
{ "count": 112, "uniques": 8, "views": [ {"timestamp":"2026-04-01T00:00:00Z","count":0,"uniques":0}, ... ] }

// clones
{ "count": 128, "uniques": 47, "clones": [ {"timestamp":"...","count":17,"uniques":12}, ... ] }

// referrers
[ {"referrer":"github.com","count":44,"uniques":3}, {"referrer":"crates.io","count":4,"uniques":2}, ... ]

// paths
[ {"path":"/systempromptio/systemprompt-core","title":"Overview","count":17,"uniques":3}, ... ]
```

### 2. GitHub Traffic API — `systempromptio/systemprompt-template`

Same four calls, different repo:

```bash
gh api repos/systempromptio/systemprompt-template/traffic/views
gh api repos/systempromptio/systemprompt-template/traffic/clones
gh api repos/systempromptio/systemprompt-template/traffic/popular/referrers
gh api repos/systempromptio/systemprompt-template/traffic/popular/paths
```

**Anomaly flag**: if any single day in `clones[].count` exceeds `5 * median(clones[].count for non-zero days)`, flag as `probable_automation` in the report and note the raw count separately. On 2026-04-14 the template saw 959 raw clones from 119 unique cloners — a clear CI/bot spike.

### 3. GitHub Stars & Forks (point-in-time deltas)

```bash
# Current counts
gh api repos/systempromptio/systemprompt-core --jq '{stars: .stargazers_count, forks: .forks_count, watchers: .subscribers_count}'
gh api repos/systempromptio/systemprompt-template --jq '{stars: .stargazers_count, forks: .forks_count, watchers: .subscribers_count}'

# Stargazers with timestamps (for per-day attribution)
gh api "repos/systempromptio/systemprompt-core/stargazers" -H "Accept: application/vnd.github.star+json" --paginate
gh api "repos/systempromptio/systemprompt-template/stargazers" -H "Accept: application/vnd.github.star+json" --paginate
```

**Current baseline (2026-04-15):** core 1 star, template 1 star (both self-stars by Ejb503). Exclude self-stars from the delta calculation.

### 4. GitHub Issues — feedback leads (interim path)

Neither repo has Discussions enabled. Until that changes, **feedback leads are captured as Issues with label `feedback`**.

```bash
# All issues with the feedback label (open + closed)
gh api "repos/systempromptio/systemprompt-core/issues?state=all&labels=feedback&per_page=100" \
  --jq '.[] | {number, title, state, user: .user.login, created_at, body_excerpt: (.body[:160])}'

gh api "repos/systempromptio/systemprompt-template/issues?state=all&labels=feedback&per_page=100" \
  --jq '.[] | {number, title, state, user: .user.login, created_at, body_excerpt: (.body[:160])}'
```

Exclude authors `Ejb503` and `dependabot[bot]` from the leads count. Each remaining issue from a new user = one lead. Store in `leads.json` keyed by `{repo}#{number}`.

If label `feedback` does not yet exist on a repo, this call returns `[]` — that is expected, not an error.

### 5. Pull Requests (a weaker signal — track separately)

External PRs are activation signals too. Exclude dependabot.

```bash
gh api "repos/systempromptio/systemprompt-core/pulls?state=all&per_page=50" \
  --jq '[.[] | select(.user.login != "Ejb503" and .user.login != "dependabot[bot]") | {number, title, state, user: .user.login, created_at}]'

gh api "repos/systempromptio/systemprompt-template/pulls?state=all&per_page=50" \
  --jq '[.[] | select(.user.login != "Ejb503" and .user.login != "dependabot[bot]") | {number, title, state, user: .user.login, created_at}]'
```

### 6. Website Analytics — systemprompt CLI

Confirmed working commands (local profile, `--json` always):

```bash
# High-level dashboard — conversations, requests, sessions, costs
systemprompt analytics overview --since 7d --json

# Session stats — THIS is the main "website traffic" signal
systemprompt analytics sessions stats --since 7d --json
systemprompt analytics sessions stats --since 31d --json
systemprompt analytics sessions trends --since 7d --json

# Traffic sources — where visitors come from
systemprompt analytics traffic sources --since 7d --json
systemprompt analytics traffic sources --since 31d --json
systemprompt analytics traffic geo --since 7d --json
systemprompt analytics traffic devices --since 7d --json
systemprompt analytics traffic bots --since 7d --json

# Content performance — what's actually read
systemprompt analytics content top --limit 20 --since 7d --json
systemprompt analytics content top --limit 20 --since 31d --json
systemprompt analytics content stats --since 7d --json
systemprompt analytics content trends --since 7d --json
```

Confirmed shapes (2026-04-15, 7d window):

```jsonc
// sessions stats
{ "data": { "sessions_created_in_period": 165, "unique_users": 107, "avg_duration_seconds": 389,
            "avg_requests_per_session": 2.28, "conversion_rate": 0.0 } }

// traffic sources (top 5 shown, real data)
// github.com 30%, systemprompt.io 6%, www.producthunt.com, www.bing.com, com.slack...
// Use .data.sources[] and sum into named buckets.

// content top (each row)
// { content_id, slug, title, source: "guides|documentation|about", views, unique_visitors,
//   avg_time_seconds, trend: "up|stable|down" }
```

**Session-expired warning:** if any command prints `session_status: expired`, tell Ed to re-authenticate to the `systemprompt-prod` profile. Do NOT fall back to `local` — the data will be silently wrong.

**Wrong-profile warning:** if the active profile is `local`, STOP. Running analytics against `local` produces silently incorrect numbers because the local DB does not receive real traffic (Ed occasionally syncs prod→local, so `local` contains a frozen point-in-time snapshot from whenever the last sync happened). You must switch to `systemprompt-prod` before continuing. This is not optional.

### 7. Google Search Console

Service account key lives at **`/var/www/html/systemprompt-web/gsc.json`** (NOT in the marketplace repo). Confirmed working 2026-04-15 with service account `gsc-559@gen-lang-client-0891438583.iam.gserviceaccount.com` against site `sc-domain:systemprompt.io`.

Follow the exact GSC bash pattern from `seo:daily-seo-brief` SKILL.md (JWT → access token → POST to Search Analytics), but with the correct key path.

**What to pull every run** (7-day window, compared against prior 7d):

```bash
GSC_KEY_FILE="/var/www/html/systemprompt-web/gsc.json"

# Get access token (full bash block is in seo:daily-seo-brief SKILL.md — copy from there)

# Top queries (dimension: query)
curl -s -X POST "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"startDate": "'$(date -d '7 days ago' +%Y-%m-%d)'", "endDate": "'$(date -d 'yesterday' +%Y-%m-%d)'", "dimensions": ["query"], "rowLimit": 100}'

# Top pages (dimension: page)
curl -s -X POST "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"startDate": "'$(date -d '7 days ago' +%Y-%m-%d)'", "endDate": "'$(date -d 'yesterday' +%Y-%m-%d)'", "dimensions": ["page"], "rowLimit": 100}'

# Query x page pairing (for quick-win title/meta analysis)
curl -s -X POST "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"startDate": "'$(date -d '7 days ago' +%Y-%m-%d)'", "endDate": "'$(date -d 'yesterday' +%Y-%m-%d)'", "dimensions": ["query", "page"], "rowLimit": 500}'
```

**Metrics to emit** into the JSON tail (each gets a whitelist entry in `hypothesis-ledger`):

```
gsc_impressions_7d         gsc_impressions_prev_7d       gsc_impressions_31d
gsc_clicks_7d              gsc_clicks_prev_7d            gsc_clicks_31d
gsc_avg_ctr_7d             gsc_avg_position_7d
gsc_top_query_{slug}_clicks_7d        (for each of the top 15 queries)
gsc_top_page_{slug}_impressions_7d    (for each of the top 15 pages)
gsc_top_page_{slug}_ctr_7d
gsc_top_page_{slug}_position_7d
```

**Quick-win detection rule:** flag any page with `impressions > 1000 AND ctr < 0.02 AND position < 10` as a title/meta rewrite opportunity. Forward these to `content:guide-optimiser` as hypothesis candidates.

### 8. crates.io Downloads

Public API, no auth. **Signal decomposition is critical here** — raw crates.io download counts are dominated by publish-day automation (docs.rs rebuilds, crates.io mirror bots, cargo-binstall probes). An empirical analysis of the `systemprompt` main crate on 2026-04-17 showed:

- 598 lifetime downloads across 86 days and 42 versions
- **80% (479) fell on 24 publish days** — automated build/mirror fetches
- **20% (119) fell on 20 non-publish days** — the only genuine user-cache-miss signal

Tracking only the main crate's *lifetime* count inflates by ~5x. Tracking the *family total* (all 30 systemprompt-* crates) inflates by a further 55x — almost entirely transitive-dep fetches from systemprompt's own CI. **Use non-publish-day baselines as the headline, not lifetime totals.**

#### Fetch: two endpoints, one crate

The main crate is `systemprompt`. Sub-crates are diagnostic only.

```bash
UA='User-Agent: systempromptio-lead-tracker (ed@tyingshoelaces.com)'

# Daily download counts (last 90 days, split by version)
curl -s -H "$UA" "https://crates.io/api/v1/crates/systemprompt/downloads" > /tmp/crates-dl.json

# Version publish dates (all 42+ versions)
curl -s -H "$UA" "https://crates.io/api/v1/crates/systemprompt/versions" > /tmp/crates-versions.json

# Family snapshot (diagnostic, not for headlines)
curl -s -H "$UA" "https://crates.io/api/v1/crates?q=systemprompt&per_page=50" > /tmp/crates-family.json
```

#### Derivation: non-publish baseline

```python
# Pseudocode — implement in whichever language the skill runs in
dl = json.load(open('/tmp/crates-dl.json'))
per_day = {}
for row in dl['version_downloads'] + dl.get('meta', {}).get('extra_downloads', []):
    per_day[row['date']] = per_day.get(row['date'], 0) + row['downloads']

versions = json.load(open('/tmp/crates-versions.json'))['versions']
publish_dates = {v['created_at'][:10] for v in versions}

today = date.today().isoformat()

# Headline metrics
main_crate_lifetime = sum(per_day.values())                                             # vanity only
main_crate_1d_today = per_day.get(today, 0)
is_today_publish_day = today in publish_dates
main_crate_non_publish_7d = sum(c for dt, c in per_day.items()
                                if dt >= (today - 7d) and dt not in publish_dates)
main_crate_non_publish_28d = sum(c for dt, c in per_day.items()
                                 if dt >= (today - 28d) and dt not in publish_dates)
n_np_days_28d = len([dt for dt in per_day if dt >= (today - 28d) and dt not in publish_dates])
main_crate_non_publish_28d_mean = main_crate_non_publish_28d / n_np_days_28d
```

#### Emit to JSON tail

Headline metrics (**promoted — these drive master brief Section 1**):

- `crates_main_non_publish_7d` — clean downloads in the last 7 days, publish-days excluded. Primary velocity signal. May be small (0–5 typical); that's fine.
- `crates_main_non_publish_28d` — same over 28 days. Reduces noise from the 7d-window problem (publish cadence swallows most 7d windows right now).
- `crates_main_non_publish_28d_mean` — per-day mean on non-publish days (last 28d). Trend marker; watch for sustained crossings above ~15/day.
- `crates_main_is_today_publish_day` — boolean. When true, the Section 1 narrative must say "today is a publish day, 1d count is noise" rather than showing the publish spike as velocity.
- `core_referrer_crates_io_14d_uniques` — **already captured elsewhere**; re-surface it here as the companion metric. This is the highest-quality crates.io signal: humans who clicked from the crate page to github.

Diagnostic metrics (**demoted — footer only, never headline**):

- `crates_main_lifetime` — 598 today. Vanity.
- `crates_main_1d_today` — raw 1d count including publish automation.
- `crates_family_count` — 30 today.
- `crates_family_lifetime` — 32,512 today. **Do not headline.** Explains library surface area, not intent.
- `crates_family_top_crate` — e.g. systemprompt-identifiers.
- `per_crate[]` — top-10 by lifetime for drill-down.

#### Anomaly detection

Flag any **non-publish-day** with downloads > `3 * (28d non-publish mean)` as `CRATES_MAIN_NON_PUBLISH_SPIKE` — this represents a possible real-user adoption event (someone setting up fresh CI against a pinned version, or a crawler hit worth investigating). Example: 2026-03-19 had 32 downloads on a non-publish day when the mean was ~6 — real anomaly, worth server-log investigation.

#### Error handling

If the API returns 5xx or the parse fails, emit all `crates_main_*` and `crates_family_*` fields as `null`, not 0, and add a loud row to Anomalies / Flags.

### 9. LinkedIn / X / Reddit — manual paste-in

No API access yet. Report section prompts Ed to paste impressions counts from the three platforms for the last 24 h. Accepts `{platform}: {impressions}` one per line or `"skip"`.

## Output 1 — The Dated Report

```
/var/www/html/systemprompt-web/reports/marketing/daily/YYYY-MM-DD/lead-tracker.md
```

Reports live in the **web repo**, not the marketplace. The convention matches how `seo:daily-seo-brief` writes to `web/reports/seo/daily/YYYY-MM-DD/daily-seo-brief.md`. All daily output goes in `reports/{domain}/daily/YYYY-MM-DD/`.

Structure:

```markdown
# Lead Tracker Report

**Date:** {YYYY-MM-DD}
**Run by:** lead-tracker v{version}
**Profile:** **systemprompt-prod** (required — see skill dependencies)
**GSC:** {available | not configured}
**Session status:** {time remaining | EXPIRED — re-authenticate to systemprompt-prod}

---

## Funnel Snapshot

| Stage | 1d | 7d | 31d | 30d target | % of target |
|---|---|---|---|---|---|
| Awareness: web sessions | {N} | {N} | {N} | — | — |
| Awareness: repo views (core+template, unique) | {N} | {N} | {N} | — | — |
| Download: **unique cloners** (core+template combined) | {N} | {N} | {N} | 50/wk | {%} |
| Download: raw clones (w/ automation flag) | {N} | {N} | {N} | — | — |
| Activation: feedback leads (new) | {N} | {N} | {N} | 5 | {%} |
| Qualified: conversations (manual input) | {N} | {N} | {N} | 3 | {%} |

### Deltas vs previous period

| Metric | This 7d | Prev 7d | Δ | Δ% |
|---|---|---|---|---|
| template_cloners_7d | {N} | {N} | {±} | {±%} |
| core_cloners_7d | {N} | {N} | {±} | {±%} |
| web_sessions_7d | {N} | {N} | {±} | {±%} |
| leads_new_7d | {N} | {N} | {±} | {±%} |

## Anomalies / Flags

- {date}: template raw clones = 959 from 119 uniques → `probable_automation` flagged
- {any session-expired warnings}
- {any 403/401 from gh api}

## Referrers (14d, ranked)

### systemprompt-template
| Referrer | Count | Unique |
|---|---|---|
| github.com | 24 | 3 |
| systemprompt.io | 12 | 2 |

### systemprompt-core
| Referrer | Count | Unique |
|---|---|---|
| github.com | 44 | 3 |
| crates.io | 4 | 2 |
| docs.rs | 3 | 1 |
| systemprompt.io | 1 | 1 |

## Top Repo Paths (14d)
(both repos, top 5 each — reveals what visitors actually explore)

## Crates.io Downloads

**Main-crate signal (headline):**

| Metric | Value | Interpretation |
|--------|------:|:--------------|
| Non-publish 7d downloads | {N} | Clean velocity over rolling week (0 is possible when publish cadence is high) |
| Non-publish 28d downloads | {N} | Clean velocity over 28d — less noisy than 7d |
| Non-publish 28d mean/day | {N.N} | Baseline user pull rate; watch for sustained >15 |
| Today is a publish day? | {yes/no} | If yes, ignore today's raw 1d count |
| crates.io → github referrer uniques (14d) | {N} | Highest-quality crate-surface intent signal |

**Diagnostic (not a headline):**

| Metric | Value |
|--------|------:|
| Main crate lifetime | {N} |
| Family crates count | {N} |
| Family lifetime (all transitive) | {N} |
| Top family member by lifetime | {name} ({N}) |

Per-crate table (top-10 by lifetime, drill-down):

| Crate | Lifetime | Non-publish recent | Version |
|-------|---------:|-------------------:|:--------|
| {name} | {N} | {N} | {x.y.z} |

If the API call fails, emit `null` for all `crates_*` fields and add a loud row to Anomalies / Flags — never substitute 0.

## Website Top Content (7d)
| Slug | Source | Views | Unique | Avg time | Trend |
|---|---|---|---|---|---|
| claude-skills-non-technical-teams | guides | ... | ... | 138s | stable |

## Website Traffic Sources (7d)
| Source | Sessions | % |
|---|---|---|

## New Leads Since Last Run
(from Issues labelled `feedback`, excluding Ejb503 and dependabot)
| Repo | # | User | Title | Created |
|---|---|---|---|---|

## In-Flight Hypotheses (reading hypothesis-ledger)
List all `IN-FLIGHT` hypotheses with their baseline, metric, current value, and window_end. Flags ones due for scoring today.

## Machine-Readable Tail

```json
{
  "run_at": "YYYY-MM-DDTHH:MM:SSZ",
  "metrics": {
    "template_cloners_1d": 0, "template_cloners_7d": 0, "template_cloners_31d": 0,
    "template_views_1d": 0,   "template_views_7d": 0,   "template_views_31d": 0,
    "template_stars_delta_7d": 0,
    "core_cloners_1d": 0,     "core_cloners_7d": 0,     "core_cloners_31d": 0,
    "core_views_1d": 0,       "core_views_7d": 0,       "core_views_31d": 0,
    "core_stars_delta_7d": 0,
    "web_sessions_7d": 0,     "web_sessions_31d": 0,
    "web_unique_users_7d": 0, "web_unique_users_31d": 0,
    "web_traffic_github_7d": 0,
    "leads_new_7d": 0, "leads_new_31d": 0, "leads_total": 0,
    "qualified_convos_7d": 0, "qualified_convos_31d": 0,
    "crates_main_non_publish_7d": 0,
    "crates_main_non_publish_28d": 0,
    "crates_main_non_publish_28d_mean": 0.0,
    "crates_main_is_today_publish_day": false,
    "crates_main_lifetime": 0,
    "crates_main_1d_today": 0,
    "crates_family_count": 0,
    "crates_family_lifetime": 0,
    "crates_family_top_crate": "",
    "per_crate": [
      { "name": "systemprompt", "downloads": 0, "recent_downloads": 0, "version": "0.0.0" }
    ]
  }
}
```
```

The JSON tail is what `hypothesis-ledger` reads to pull baselines and score metrics. Field names MUST match the metric whitelist in `hypothesis-ledger`.

## Output 2 — Persistent Leads Database

```
{project_root}/reports/marketing/data/leads.json
(e.g. /var/www/html/systemprompt-web/reports/marketing/data/leads.json)
```

Schema:

```json
{
  "leads": [
    {
      "id": "systemprompt-template#7",
      "source": "github-issue",
      "user": "externaldev42",
      "first_seen": "2026-04-20",
      "stage": "feedback_given",
      "url": "https://github.com/systempromptio/systemprompt-template/issues/7",
      "notes": "Tried the template, hit DB connection error on Docker.",
      "attributed_to_hypothesis": "H-012"
    }
  ],
  "last_updated": "YYYY-MM-DDTHH:MM:SSZ"
}
```

Stages: `cloner` (unique cloner only) → `feedback_given` (posted an Issue with `feedback` label or emailed) → `qualified` (replied to follow-up, booked a call) → `sandbox` (active trial) → `converted`. Only `feedback_given` and above count as LEADS per the lead definition.

## Output 3 — Append to Funnel History

```
{project_root}/reports/marketing/data/funnel-history.jsonl
(e.g. /var/www/html/systemprompt-web/reports/marketing/data/funnel-history.jsonl)
```

One JSON line per daily run, just the `metrics` object plus `run_at`. This is the 14-day-retention workaround: once we append a day, we never lose it regardless of what the GitHub Traffic API decides to forget.

## Run Modes

```
lead-tracker                # Full daily run → writes all 3 outputs
lead-tracker latest         # Print the most recent report (no fetch)
lead-tracker metric {name}  # Print just one metric from latest report (used by hypothesis-ledger)
lead-tracker history {N}    # Print last N days from funnel-history.jsonl as a table
```

## Anti-Sludge Rules

- **Unique cloners is the headline.** Raw clones are bot-noisy. Every funnel table leads with unique cloners.
- **Exclude self-activity.** Ejb503 stars, Ejb503 issues, Ejb503 PRs, dependabot PRs — all excluded from lead counts.
- **Never silently fail.** If `gh` is unauthenticated, GSC key missing, systemprompt session expired, or an API call 4xx/5xx's, the report surfaces the failure in "Anomalies / Flags" with the exact command that failed. Do not substitute zeros for missing data.
- **Never invent numbers.** If a metric can't be computed, the JSON tail reports `null`, not `0`.
- **Daily or bust.** The first line of the report reports days-since-last-run. If >1, warn loudly.
