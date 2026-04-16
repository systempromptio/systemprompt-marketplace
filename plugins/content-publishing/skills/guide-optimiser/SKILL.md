---
name: guide-optimiser
description: "Deterministically optimise a published guide for value density, brand discipline, search-intent alignment, and CTR. Reads 28-day GSC query data per URL, enforces quantitative brand-mention and length rules, rewrites titles and meta descriptions against CTR data, and produces a 100-point score delta. Load identity and brand-voice first."
metadata:
  version: "1.0.0"
---

# Guide Optimiser

Run a **deterministic, data-driven rewrite** on a single published guide. This skill is the action counterpart to `guide-revision` (which is audit-only). Every decision is grounded in a quantitative rule or a 28-day Google Search Console signal. No vibes, no "use your judgement" gaps.

## Dependencies

**Load `identity` and `brand-voice` before this skill.**

- `identity` — positioning, ICP, messaging hierarchy, what the brand actually stands for
- `brand-voice` — the cliche list, terminology rules, em-dash ban, and voice targets

This skill reuses the 8-section audit checklist from `guide-revision` verbatim during Phase 1. Do not duplicate that checklist here — read the file at `plugins/content-publishing/skills/guide-revision/SKILL.md` when you need it.

## Source of Truth

Read these before starting:

- `/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md` — pillar health, objectives, active hypotheses
- `/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json` — canonical keyword registry with assigned guides, volumes, difficulty, target positions. Find the entry where `assigned_guide` matches this guide's slug to identify the primary keyword and its current metrics.
- The latest `reports/seo/YYYY-MM-DD/seo-monitor.md` — per-guide CTR, impressions, position, quick-wins list
- `/var/www/html/systemprompt-web/reports/seo/data/hypothesis-ledger.md` — check if an S-### hypothesis exists for this guide's title/meta rewrite. If yes, note the hypothesis ID in your output so we can score it later.

## Inputs

Caller must provide:
- **Guide slug** (e.g. `getting-started-anthropic-marketplace`), OR the absolute path to the guide's `index.md`
- Optional: `audit_only: true` — compute the score without rewriting (used for corpus re-baselining)

## Phases

The skill runs sequentially: **0 → 1 → 2 → 2.5 → 3**. Do not skip. If any phase aborts, exit cleanly without committing.

---

## Phase 0 — GSC Query Ingestion

Pull the 28-day Google Search Console query data for this specific guide URL. 28 days (not 7) so recent guides have enough signal and the result isn't biased by a single bad week.

### Authenticate

Use the service account at `/var/www/html/systemprompt-web/gsc.json`. Read scope is `https://www.googleapis.com/auth/webmasters.readonly`.

```bash
python3 <<'PY' > /tmp/gsc_token
import json, time, base64
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from pathlib import Path

key = json.loads(Path('/var/www/html/systemprompt-web/gsc.json').read_text())
now = int(time.time())
claims = {
    'iss': key['client_email'],
    'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
    'aud': 'https://oauth2.googleapis.com/token',
    'iat': now, 'exp': now + 3600,
}
try:
    import jwt as pyjwt
    token = pyjwt.encode(claims, key['private_key'], algorithm='RS256')
except ImportError:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    h = base64.urlsafe_b64encode(json.dumps({'alg':'RS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
    p = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b'=').decode()
    pk = serialization.load_pem_private_key(key['private_key'].encode(), password=None)
    sig = pk.sign(f'{h}.{p}'.encode(), padding.PKCS1v15(), hashes.SHA256())
    token = f'{h}.{p}.{base64.urlsafe_b64encode(sig).rstrip(b"=").decode()}'

data = urlencode({'grant_type':'urn:ietf:params:oauth:grant-type:jwt-bearer','assertion':token}).encode()
resp = json.loads(urlopen(Request('https://oauth2.googleapis.com/token', data=data, method='POST')).read())
print(resp['access_token'], end='')
PY
```

### Query for the guide's top 100 queries (28d)

```bash
TOKEN=$(cat /tmp/gsc_token)
SLUG=<slug>
START=$(date -d '28 days ago' +%Y-%m-%d)
END=$(date -d 'yesterday' +%Y-%m-%d)
mkdir -p /tmp/gsc-guide-queries

curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{
    \"startDate\": \"$START\",
    \"endDate\": \"$END\",
    \"dimensions\": [\"query\"],
    \"dimensionFilterGroups\": [{
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/guides/$SLUG\"}]
    }],
    \"rowLimit\": 100
  }" > /tmp/gsc-guide-queries/$SLUG.json
```

### Query for the page-level aggregate (for CTR scoring)

```bash
curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{
    \"startDate\": \"$START\",
    \"endDate\": \"$END\",
    \"dimensions\": [\"page\"],
    \"dimensionFilterGroups\": [{
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/guides/$SLUG\"}]
    }],
    \"rowLimit\": 10
  }" > /tmp/gsc-guide-queries/$SLUG.page.json
```

Cache both files. If the guide has no rows, record `no_gsc_data: true` and proceed — content rules still apply, only CTR scoring and title rewrites are skipped.

Build the working set:
- `top_queries`: sorted by impressions, filter `impressions >= 20` (signal floor)
- `mandatory_queries`: `top_queries` where `impressions >= 20` (the set that drives Rule 4)
- `page_metrics`: `{impressions, clicks, ctr, position}` from the page aggregate

---

## Phase 1 — Audit

Run the full `guide-revision` 8-section checklist against the target guide. Record pass/fail per check. This phase writes nothing to disk — it produces a Python dict (or equivalent) held in memory for Phase 2.5 scoring.

When Phase 1 produces a failing check, Phase 2 is responsible for fixing it only where the fix is covered by the rules below. Out-of-scope failures (e.g. broken external links pointing to 404s) are reported but not auto-fixed.

---

## Phase 2 — Deterministic Rewrite

Five hard rules. Each is mechanically enforceable.

### Rule 1 — Brand-mention discipline

The core ask: guides are littered with brand references that dilute value density.

**Definition of a brand mention:** any occurrence of `systemprompt`, `systemprompt.io`, or `systempromptio` (case-insensitive) in the guide **body**. Exclude:
- Frontmatter (`---` to `---`)
- The final "About / Further reading / Next steps" block (last H2 or H3 of the guide, whichever is last)
- Code blocks that legitimately import or reference the crate (e.g. `use systemprompt::...`, `cargo add systemprompt`)
- The `links` frontmatter array

**Topic terms are NOT brand mentions** — `Claude`, `Anthropic`, `Claude Code`, `MCP`, `Cursor`, `Copilot`, `LangChain` are topics. Leave them.

**Budget:**
- Hard cap: **max 3 brand mentions per guide body**, AND
- Density cap: **max 1 mention per 1,500 words of body**
- Whichever is stricter wins

**Earn-it test for each remaining mention:** would the paragraph be strictly weaker without it? If removing the mention leaves the paragraph intact, remove it.

**Replacement rules:**
- "systemprompt.io's governance pipeline evaluates" → "a governance pipeline evaluates"
- "At systemprompt we believe" → delete entire phrase, keep the underlying claim
- "systemprompt is the only self-hosted" → "self-hosted deployments that" (reframe as category, not product)
- First-person marketing ("we built X to solve Y") → stripped entirely

**Exception:** founder-narrative guides are exempt from Rule 1. Current list:
- `the-growth-chart-nobody-shows-you`
- `building-on-quicksand-claude-breaking-changes`

These can reference the brand freely because the guide *is* the founder's story.

### Rule 2 — Length floor

- **Non-pillar guides:** minimum 3,500 words body
- **Pillar guides:** minimum 5,000 words body

**Pillar list** (from `seo-strategy-master.md`):
- `claude-code-vs-cursor`
- `self-hosted-ai-governance`
- `getting-started-anthropic-marketplace`
- `claude-code-mcp-servers-extensions`
- `claude-code-daily-workflows`
- `claude-code-organisation-rollout`

If the guide is below the floor after Rule-1 stripping, **add substantive content**:
- A missing troubleshooting section (grounded in real errors, often in the GSC query log as error queries)
- A worked example with realistic input and output
- A common-pitfalls block
- A comparison table if the guide is comparing things
- Expanded FAQ answers driven by GSC question-style queries

**Never pad.** No restating points, no synonym chains, no "in summary" repetition. If the guide can't honestly reach the floor, flag it as `needs_content_investment: true` in the report and stop at the word count you can justify — better to under-deliver length than to lie with filler.

If the guide is **already above 5,000 words and dense**, do not expand it further. The length rule is a floor, not a target.

### Rule 3 — Title and meta description rewrite (CTR-driven)

**If the guide has no GSC data** (new, not indexed, `no_gsc_data: true` from Phase 0): **leave title and meta alone**. A rewrite without signal is guessing. Note `title_meta_skipped_no_signal` in the report.

**If the guide has GSC data:** rewrite both. Use the following hard rules.

**Title rules:**
- 50–60 characters hard cap (Google truncates above 60)
- Must start with a strong verb or comparison frame: `How to …`, `Build …`, `Configure …`, `X vs Y`, `N ways to …`, `Install …`, `Deploy …`
- Must contain the guide's primary keyword (frontmatter `keywords[0]` or derived from the top GSC query)
- Must include a specificity hook: a number, a year (`2026`), an outcome, or a differentiator
- **Banned**: colon sandwich (`Foo: The Complete Guide to X`), bracketed tags (`[2026 Guide]`), "Ultimate", "Definitive", "Complete"
- Must accurately represent the content — no clickbait, no overpromise

**Meta description rules:**
- 130–160 characters hard cap
- Starts with a verb (`Learn`, `Compare`, `Configure`, `Build`, `Deploy`, `Troubleshoot`)
- Primary keyword in the first 100 characters
- Tells the reader what they will be able to DO, not what the article covers
- Unique across the site — grep `services/content/guides/*/index.md` for collision before writing

**Selection of primary keyword:** from the Phase-0 GSC data, the top query (by impressions, signal ≥20) *is* the primary keyword if it matches the guide's topic. Otherwise fall back to `keywords[0]` in frontmatter. Cross-check: the chosen primary keyword must appear in at least two top-20 GSC queries, or the signal is too narrow.

**Do not rewrite titles on breakout performers.** If the guide's current CTR is already within 80% of the position-expected CTR (see Phase 2.5 CTR curve), the title is working. Leave it. Only rewrite the meta description in this case.

### Rule 4 — Query-to-content alignment (search intent)

For each query in `mandatory_queries` (Phase 0, impressions ≥20, 28 days):

1. **Verbatim presence check**: grep the guide body (case-insensitive) for the exact query string. If absent, it must be added naturally — as an H2, an H3, a lead sentence, or an FAQ question. Never keyword-stuff.

2. **Intent classification** (deterministic mapping):
   - Starts with `how to`, `how do I` → how-to intent → needs numbered steps
   - Contains `vs`, `versus`, `or`, `difference between` → comparison intent → needs table
   - Contains `error`, `failed`, `not working`, `broken`, `cannot`, `issue` → troubleshooting intent → needs troubleshooting block
   - Ends with `?` or starts with `what`, `why`, `when` → question intent → needs FAQ answer
   - Contains `best`, `top`, `list of` → listicle intent → needs enumerated list
   - Contains `example`, `tutorial`, `guide`, `setup` → instructional intent → needs step-by-step
   - Otherwise: informational → needs an H2 or H3 explaining it

3. **Format match check**: does the guide contain the format the intent demands? If the top query is "failed to install anthropic marketplace" (troubleshooting intent), the guide must contain a clearly labelled troubleshooting section. If not, add one.

4. **Position in document**: high-impression queries should appear in the first 500 words or in a heading — not buried.

Produce a **query coverage matrix** in the report:

```markdown
| Query | 28d Impressions | 28d CTR | In body? | In heading? | Intent covered? | Action |
|-------|----------------:|--------:|:--------:|:-----------:|:---------------:|--------|
| anthropic marketplace | 724 | 1.1% | yes | no | yes | Add H2 with exact phrasing |
| failed to install anthropic marketplace | 364 | 1.1% | no | no | no | Add troubleshooting section |
```

Every row with a `no` triggers a rewrite action. This is how the skill ensures the guide "accurately, precisely, and informatively provides value based on the keywords that are actually driving search traffic."

### Rule 5 — Cliche, filler, and voice cleanup

Strip:

**Cliches:** `revolutionize`, `game-changer`, `unlock`, `supercharge`, `seamlessly`, `cutting-edge`, `harness`, `next-generation`, `paradigm shift`, `disrupt`, `empower`, `leverage` (as a verb), `reimagine`, `robust`, `comprehensive`, `world-class`, `best-in-class`, `unparalleled`, `transformative`

**Filler transitions:** `Let's dive in`, `Without further ado`, `In today's fast-paced world`, `In this guide, we will`, `This article will cover`, `By the end of this guide`, `As we've seen`, `It goes without saying`, `At the end of the day`

**Punctuation:** em dashes `—` → replace with commas, periods, or parentheses (brand-voice rule)

**Other:** hashtags, fabricated "when I was building this" stories (unless founder-narrative exception), vague "teams say" / "companies report" / "studies show" without a source

Run a final pass against `brand-voice` skill's full cliche list and Anthropic terminology rules (plugins not apps, skills not prompts, agents not bots, MCP servers not APIs).

---

## Phase 2.5 — Scoring

Every guide gets a **100-point score** across seven dimensions. Compute both pre- and post-rewrite. The delta is the proof of work.

### Rubric

| Dimension | Max | Data source |
|-----------|----:|-------------|
| Search traffic | 20 | GSC 28d impressions for this URL |
| CTR performance | 15 | GSC 28d CTR vs position-expected CTR |
| Query coverage | 20 | Fraction of top-20 queries where verbatim+intent are covered |
| Content depth | 15 | Word count vs floor |
| Value density | 10 | Brand-mention budget adherence |
| SEO hygiene | 10 | Frontmatter title/meta/slug/keywords rules |
| Structural integrity | 10 | Audit sections 3, 4, 5, 8 (links/code/structure/actionability) |

### Deterministic scoring rules

**Search traffic (20 max):**
```
score = min(20, round(4 * log10(max(impressions_28d, 1))))
```
1 imp → 0, 100 → 8, 1k → 12, 10k → 16, 100k → 20.

**CTR performance (15 max):**
```
ctr_curve = {1:0.25, 2:0.15, 3:0.11, 4:0.08, 5:0.06, 6:0.045,
             7:0.03, 8:0.023, 9:0.018, 10:0.015}
# positions 11-20 → 0.01
expected = ctr_curve[round(position)]
score = min(15, round(15 * (actual_ctr / expected)))
```
A guide hitting 50% of expected CTR scores 7.5. No GSC data → `N/A`, max drops to 85.

**Query coverage (20 max):**
```
eligible = top_queries with impressions >= 20
score = round(20 * (queries_with_verbatim_AND_intent / len(eligible)))
```
If `len(eligible) == 0`, score is a neutral 10 — cannot be penalised without signal.

**Content depth (15 max):**
```
floor = 5000 if pillar else 3500
score = 15 if words >= floor else round(15 * (words / floor))
```

**Value density (10 max):**
```
budget = min(3, words // 1500)
score = max(0, 10 - max(0, brand_mentions - budget))
```
Each brand mention over budget subtracts 1 point, floored at 0.

**SEO hygiene (10 max):** 2 points per pass: title length, meta length, slug quality, keyword list populated, meta uniqueness.

**Structural integrity (10 max):** 2.5 points per passing audit section (links, code, structure, actionability).

### Score tiers

- **85–100:** Top-tier asset. No further action.
- **70–84:** Acceptable. Rewrite opportunities exist but guide is not broken.
- **Below 70:** Failing. Priority candidate for rewrite.

### Commit message format

```
optimise {slug}: {pre_score} → {post_score}

- brand mentions: {before} → {after} (budget {budget})
- word count: {before} → {after} (floor {floor})
- query coverage: {before}/{total} → {after}/{total}
- title: "{before}" → "{after}"
- meta: rewritten for {reason}
- gsc baseline: {impressions_28d} imp, {ctr}% CTR, position {position}
```

---

## Phase 3 — Verify and Commit

After rewriting:

1. **Word count** — must be ≥floor. If not, report as `needs_content_investment` and abort commit.
2. **Brand-mention count** — must be within budget. Re-grep to verify.
3. **Re-run the guide-revision audit.** Sections 1, 6, 7 must all pass. Other sections must be no worse than the baseline from Phase 1.
4. **Title and meta lengths** — validate hard caps.
5. **Meta description uniqueness** — grep all other guides' descriptions, confirm no collision.
6. **Diff the guide file.** If diff is empty or trivially whitespace-only, abort with `no_material_change`. Never commit a no-op.
7. **Recompute the score.** If `post_score < pre_score`, abort and roll back — this is a bug in the rules, not an improvement. Report the regression.
8. **Commit** with the message format above.
9. **Write the structured per-guide report** to `reports/guide-optimiser/YYYY-MM-DD/{slug}.md` (not committed — `reports/` is gitignored). Include:
   - Audit results (Phase 1)
   - Query coverage matrix (Rule 4)
   - Brand-mention before/after and list of removed instances
   - Scorecard (Phase 2.5)
   - Before/after title and meta
   - Word count delta
   - Git commit SHA

## Audit-only mode

If the caller passes `audit_only: true`, run Phases 0, 1, and 2.5 only. Produce the scorecard and report. Do not rewrite, do not commit. Used for corpus re-baselining and drift tracking.

## Output Format

Per-guide report template:

```markdown
# Guide Optimiser Report: {title}

**Guide:** `{path}`
**Slug:** `{slug}`
**Audited:** {YYYY-MM-DD}
**Mode:** optimise | audit_only
**Commit:** {sha or "audit only"}

## Score: {post}/100 (was {pre}/100, {delta:+d})

| Dimension         | Before | After | Max |
|-------------------|-------:|------:|----:|
| Search traffic    | {} | {} | 20 |
| CTR performance   | {} | {} | 15 |
| Query coverage    | {} | {} | 20 |
| Content depth     | {} | {} | 15 |
| Value density     | {} | {} | 10 |
| SEO hygiene       | {} | {} | 10 |
| Structural        | {} | {} | 10 |

## GSC Baseline

- 28-day impressions: {}
- 28-day clicks: {}
- 28-day CTR: {}%
- Avg position: {}
- Expected CTR at this position: {}%
- CTR gap: {}

## Query Coverage Matrix

{table from Rule 4}

## Brand Mentions

- Before: {n}
- After: {n}
- Budget: {n}
- Removed instances:
  1. Line {N}: "{excerpt}" → removed
  2. ...

## Content Changes

- Word count: {before} → {after} (floor {floor})
- Sections added: {list}
- Sections rewritten: {list}

## Title and Meta

**Title:**
- Before: "{}"
- After: "{}"
- Length: {N} → {N} chars

**Meta description:**
- Before: "{}"
- After: "{}"
- Length: {N} → {N} chars

## Audit Results (Phase 1)

{pass/fail by section}

## Verification

- Brand mentions within budget: PASS | FAIL
- Word count floor met: PASS | FAIL
- Title length: PASS | FAIL
- Meta length: PASS | FAIL
- Meta uniqueness: PASS | FAIL
- Score improved: PASS | FAIL
- Guide revision sections 1/6/7: PASS | FAIL
```

## Anti-sludge rules

- Every recommendation and action ties to a specific line number or a specific query from GSC.
- No generic praise. No "this improves SEO" — say *which* metric and *why*.
- No em dashes in the report.
- No AI cliches in the report.
- The report is an audit trail, not marketing. It exists so a future reviewer can reproduce or reverse the rewrite.

## When NOT to use this skill

- Guides that are founder narratives — use sparingly, Rule 1 exempts them but the other rules still apply.
- Guides with `public: false` — internal-only, no public SEO value.
- Guides under 7 days old — too new for meaningful GSC data.
- Pages outside `/guides/` — this skill is guide-specific. For feature pages use `feature-copywriter`.
