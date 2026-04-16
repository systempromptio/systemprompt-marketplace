---
name: guide-optimiser
description: "Deterministically audit and optimise a published guide. Runs a 14-section quality audit, applies 7 rewrite rules for value density, brand discipline, search-intent alignment, and CTR. Reads 28-day GSC query data per URL, produces a 100-point score delta across 11 dimensions, commits changes, and updates the per-guide report. Handles guides without GSC data. Load identity and brand-voice first."
metadata:
  version: "3.0.0"
  git_hash: "8e40a90"
---

# Guide Optimiser

Run a **deterministic, data-driven audit and rewrite** on a single published guide. This skill is the complete lifecycle tool for guide quality: audit, fix, score, commit, log. Every decision is grounded in a quantitative rule or a 28-day Google Search Console signal. No vibes, no "use your judgement" gaps.

**Critical rule:** Section 14 (Search Intent Resolution) is a critical override. If Section 14 fails, the entire audit fails regardless of how many other sections pass. A guide that does not resolve the searcher's intent has no value, regardless of how well it scores on technical criteria.

## Dependencies

**Load `identity` and `brand-voice` before this skill.**

- `identity` — positioning, ICP, messaging hierarchy, what the brand actually stands for
- `brand-voice` — the cliche list, terminology rules, em-dash ban, and voice targets

## Source of Truth

Read these before starting:

- `/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md` — pillar health, objectives, active hypotheses
- `/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json` — canonical keyword registry with assigned guides, volumes, difficulty, target positions. Find the entry where `assigned_guide` matches this guide's slug to identify the primary keyword and its current metrics.
- The latest `reports/seo/daily/YYYY-MM-DD/seo-monitor.md` — per-guide CTR, impressions, position, quick-wins list
- `/var/www/html/systemprompt-web/reports/seo/data/hypothesis-ledger.md` — check if an S-### hypothesis exists for this guide's title/meta rewrite. If yes, note the hypothesis ID in your output so we can score it later.
- `/var/www/html/systemprompt-web/reports/content/guides/{slug}/guide-report.md` — the per-guide report (search intent analysis, FAQ mappings, external resources, asset inventory, action log, metadata rationale). If this file does not exist, create it from the template in the "Per-Guide Report Template" section below before proceeding. Populate with available data from keyword-targets.json and any GSC data pulled in Phase 0.

## Inputs

Caller must provide:
- **Guide slug** (e.g. `getting-started-anthropic-marketplace`), OR the absolute path to the guide's `index.md`

## Phases

The skill runs sequentially: **0 -> 1 -> 2 -> 2.5 -> 3**. Do not skip. If any phase aborts, exit cleanly without committing.

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

Cache both files. If the guide has no rows, record `no_gsc_data: true` and proceed — content rules still apply.

Build the working set:
- `top_queries`: sorted by impressions, filter `impressions >= 20` (signal floor)
- `mandatory_queries`: `top_queries` where `impressions >= 20` (the set that drives Rule 4)
- `page_metrics`: `{impressions, clicks, ctr, position}` from the page aggregate

### Initialise Guide Report

Read the per-guide report at `reports/content/guides/{slug}/guide-report.md`. If it does not exist, create it from the template (see "Per-Guide Report Template" section below) and populate with:
- Primary keyword data from keyword-targets.json
- GSC data just pulled (impressions, clicks, CTR, position)
- Any existing FAQ, resource, and asset data extractable from the guide's current content

This ensures every optimiser run has a guide report to work with, even for guides created before this upgrade.

---

## Phase 1 — 14-Section Audit

Run the full 14-section checklist against the target guide. Record pass/fail per check. This phase writes nothing to disk — it produces a dict held in memory for Phase 2.5 scoring.

When Phase 1 produces a failing check, Phase 2 is responsible for fixing it only where the fix is covered by the rewrite rules below. Out-of-scope failures (e.g. broken external links pointing to 404s) are reported but not auto-fixed.

### Section 1: Frontmatter Completeness

- [ ] `title` present and under 60 characters
- [ ] `description` present and under 160 characters
- [ ] `description` starts with a verb, not "This guide" or "In this article"
- [ ] `slug` present, lowercase, hyphenated, 3-6 words, contains primary keyword
- [ ] `keywords` present with 5-10 comma-separated phrases
- [ ] `author` present
- [ ] `published_at` and `updated_at` present and valid dates
- [ ] `image` path present and follows `/files/images/blog/{slug}.png` pattern
- [ ] `after_reading_this` has 3 specific, measurable outcomes (not vague "understand X")
- [ ] `links` array has at least 2 reference links with titles and full URLs
- [ ] `public` is explicitly set
- [ ] `kind` and `category` are set

### Section 2: Claim Verification

For every specific claim in the guide:

- [ ] Performance claims (percentages, times, costs) have methodology or source
- [ ] Technical behaviour claims (caching, context isolation, API behaviour) cite official documentation
- [ ] Product integration claims (connectors, tools) are verified to exist
- [ ] Pricing/cost data includes "as of {date}" and links to pricing page
- [ ] No unattributed quotes or testimonials
- [ ] Claims about what "teams" or "CTOs" do are either sourced or clearly framed as the author's observation

Flag each unverified claim with exact line number and suggested fix: add source, add "[as of date]", reframe as observation, or remove.

### Section 3: Link Audit

- [ ] Every external link uses a full URL (not just domain)
- [ ] Every external link has descriptive anchor text (not "click here" or bare URLs)
- [ ] Links to Anthropic docs point to current, non-deprecated pages
- [ ] Internal links to other guides use relative paths (`/guides/{slug}`)
- [ ] Guide links to all related guides recommended by the SEO strategy interlinking map
- [ ] No orphan guide (must link to at least 2 other guides AND be linked from at least 2)
- [ ] `links` frontmatter references are real, accessible URLs
- [ ] No links to placeholder or example domains

### Section 4: Code and Command Verification

- [ ] Every code block specifies a language (```rust, ```json, ```bash, etc.)
- [ ] Every code example is complete enough to run (not fragments that assume context)
- [ ] Every CLI command is correct for the stated tool version
- [ ] File paths in code examples are realistic and consistent within the guide
- [ ] OS-specific commands note alternatives for other platforms (macOS, Linux, Windows)
- [ ] Config examples (JSON, YAML) are valid syntax
- [ ] No placeholder values that look real (e.g., fake API keys, fake URLs)
- [ ] Prerequisites for running code are stated (language version, dependencies, installed tools)

### Section 5: Structure and Readability

- [ ] Exactly one H1 (the title)
- [ ] H2 sections follow a logical progression (problem, solution, examples, conclusion)
- [ ] No H2 section exceeds 800 words without H3 sub-sections
- [ ] No paragraph exceeds 5 sentences
- [ ] Sentence length varies (mix of short punchy and longer explanatory)
- [ ] No wall of text: visual break (heading, code block, list, or table) every 300 words max
- [ ] Opening section (first 150 words) clearly states what the reader will get and why it matters
- [ ] Guide answers the search query implied by its title within the first 500 words
- [ ] Conclusion has specific takeaways (not just "now you know X")
- [ ] No section repeats a point already made in another section

### Section 6: SEO and Metadata Optimisation

**Title optimisation:**
- [ ] Title under 60 characters (Google truncation threshold)
- [ ] Title contains the primary keyword naturally (not stuffed)
- [ ] Title is action-oriented or specific ("Build X", "How to X", "X vs Y"), not generic ("A Guide to X")
- [ ] Title accurately represents the content (no clickbait, no overpromise)

**Description optimisation:**
- [ ] Description is 130-160 characters (sweet spot for SERP display)
- [ ] Description starts with a verb or action ("Learn", "Build", "Configure", "Compare")
- [ ] Description includes primary keyword in first 100 characters
- [ ] Description tells the reader what they will be able to DO, not what the article covers
- [ ] Description is unique (not duplicated from another guide)

**Keywords optimisation:**
- [ ] Primary keyword from SEO strategy matches frontmatter keywords field
- [ ] Keywords field contains 5-10 distinct phrases (not just variations of one term)
- [ ] Long-tail keywords from SEO strategy are included
- [ ] Keywords include both British and American spelling variants where search volume warrants it
- [ ] No keyword in the list is irrelevant to the actual content

**Content keyword placement:**
- [ ] Primary keyword appears in: title, first paragraph, at least one H2, description, slug
- [ ] Primary keyword density is natural (max 1x per 200 words, no stuffing)
- [ ] Long-tail keywords appear naturally in H2/H3 headings or body text
- [ ] Guide answers "People Also Ask" questions related to its primary keyword

**Slug and URL:**
- [ ] Slug is 3-6 words, lowercase, hyphenated
- [ ] Slug contains primary keyword or close variant
- [ ] Slug has no stop words unless they aid readability

**Cluster alignment:**
- [ ] Guide is assigned to the correct cluster per SEO strategy
- [ ] Guide links to its cluster's pillar page
- [ ] `category` and `tags` accurately reflect the content topic

**Structured data readiness:**
- [ ] `after_reading_this` outcomes are specific enough for HowTo schema
- [ ] `links` array contains authoritative external references
- [ ] `image` path is set and the image file exists

### Section 7: Brand and Voice Compliance

- [ ] No em dashes (use commas, periods, parentheses)
- [ ] No hashtags
- [ ] No AI cliches (revolutionize, game-changer, unlock, supercharge, seamlessly, cutting-edge, harness, next-generation, paradigm shift, disrupt, empower, leverage as verb, reimagine)
- [ ] No fabricated personal stories or "When I was building..." narratives
- [ ] No generic filler ("Let's dive in", "Without further ado", "In today's fast-paced world")
- [ ] Uses correct Anthropic terminology (plugins not apps, skills not prompts, agents not bots, MCP servers not APIs)
- [ ] **Zero occurrences** of `systemprompt`, `systemprompt.io`, or `systempromptio` (case-insensitive) in guide body content. Run `grep -ci 'systemprompt' body_content` to verify. **Exceptions:** founder-narrative guides (`the-growth-chart-nobody-shows-you`, `building-on-quicksand-claude-breaking-changes`), or guides where the product IS the topic.
- [ ] No product CTAs of any kind in body content
- [ ] No "we recommend", "our solution", "try our", or first-person product language
- [ ] Competitive frame is build-vs-buy (not product vs other platforms)

### Section 8: Actionability and Completeness

- [ ] A reader with stated prerequisites can complete the guide's goal without external help
- [ ] Every "how to" section has exact steps, not vague direction ("configure your settings" without showing how)
- [ ] Error scenarios and common mistakes are addressed
- [ ] "After reading this" outcomes are all achievable by following the guide
- [ ] Guide does not end abruptly (has a conclusion with next steps or related resources)
- [ ] If the guide recommends a tool or approach, it shows the actual implementation (not just "use X")

### Section 9: External Resources

Every guide must link to authoritative external sources that substantiate its claims and provide further reading. These resources demonstrate that the guide is built on research, not opinion.

- [ ] At least 5 distinct external resource links in the guide body (not counting frontmatter `links` array)
- [ ] All external links point to primary sources (official documentation, research papers, RFCs, GitHub repositories, specification documents), not blog posts summarising documentation
- [ ] External links are contextually placed inline where relevant (not dumped in a "resources" or "further reading" section at the end)
- [ ] External links are to current, live pages (not 404, not deprecated, not archived)
- [ ] No external links to competitor products presented as recommendations
- [ ] External resources are recorded in the per-guide report's "External Resources Audit" section

### Section 10: Homemade Visual Assets

Every guide must include original visual assets based on real data. Charts, tables, and graphs make content more useful and harder to replicate. They also signal to readers (and search engines) that the content is original research, not a rewrite.

- [ ] At least 2 homemade visual assets in the guide (SVG charts, data tables with real data, comparison graphs, architecture diagrams)
- [ ] Each visual asset cites a real data source (pricing page, benchmark results, API documentation, research paper, official statistics)
- [ ] Visual assets contain real data, not placeholder or illustrative numbers
- [ ] SVG charts and diagrams are well-formed and render correctly
- [ ] Data tables have proper markdown formatting (headers, column alignment)
- [ ] Every visual asset is wrapped with copy and share buttons for external sharing:
  - [ ] Copy button (using `<sp-copy-button>` web component) copies asset content to clipboard
  - [ ] Share button copies a permalink URL with backlink to `systemprompt.io/guides/{slug}#{asset-anchor}`
  - [ ] Source attribution line citing the data source is visible
- [ ] Visual assets are recorded in the per-guide report's "Homemade Asset Inventory" section with their data sources

### Section 11: FAQ and Long-Tail Keyword Validation

FAQs drive structured data in search results. Every FAQ must be grounded in actual search behaviour, not invented questions.

- [ ] At least 4 FAQ entries in frontmatter
- [ ] Each FAQ question maps to a documented long-tail keyword (from `keyword-targets.json` or GSC query data)
- [ ] FAQ-to-keyword mapping is recorded in the per-guide report's "FAQ and Long-Tail Keyword Match" section
- [ ] FAQ answers are self-contained (useful without reading the full guide)
- [ ] FAQ answers include specific numbers, steps, or data points (not vague generalities)
- [ ] No FAQ question is generic or unresearchable (e.g., "What is X?" must have keyword volume backing it)

### Section 12: Topic Research Evidence

Every guide must demonstrate that its topic was researched before writing. This section validates the per-guide report's research sections.

- [ ] Per-guide report exists at `reports/content/guides/{slug}/guide-report.md`
- [ ] Search Intent Analysis section is complete:
  - [ ] Intent classification (informational/commercial/navigational/transactional) with evidence
  - [ ] User profile: who is searching, what role, what problem they have
  - [ ] What they need: the specific answer or outcome they seek
  - [ ] Evidence: how we know (GSC queries, keyword intent data, SERP analysis)
- [ ] Keyword map with primary, secondary, and long-tail keywords, each with volume and source date
- [ ] Competing content audit with at least 3 competitor URLs analysed (word count, strengths, gaps)
- [ ] Differentiation statement: what this guide offers that competing content does not
- [ ] All keyword volumes cite their source (keyword-targets.json pull date or GSC date range)

### Section 13: Metadata Rationale and Action Traceability

The title, description, and keywords of every guide must be backed by data, and every change to them must be traceable. This prevents repeated edits without evidence.

- [ ] Guide report Section 7 (Title, Description and Keywords Rationale) is complete
- [ ] Title rationale cites keyword volume data with source and date
- [ ] Description rationale explains which search intent it addresses
- [ ] Keywords rationale justifies each keyword with volume/difficulty data
- [ ] Every metadata change in the guide's history has a corresponding Action Log entry
- [ ] Every Action Log entry that produced an artifact links to it using a relative path
- [ ] No metadata was changed without GSC data or keyword volume evidence justifying the change
- [ ] Title/description "Last changed" date is present and accurate

### Section 14: Search Intent Resolution (CRITICAL OVERRIDE)

This is the most important section. **If Section 14 fails, the entire audit result is FAIL regardless of how many other sections pass.** A guide that does not resolve the searcher's intent is not a world-class resource, no matter how well-structured or SEO-optimised it is.

The assessment here is structured but requires judgement. Each check must be supported by specific evidence from the guide and the per-guide report.

- [ ] **Intent match:** The documented search intent (from the guide report) matches what the content actually delivers. If the report says users want "empirical cost reduction strategies," the guide must contain specific, tested strategies with measured outcomes, not general advice.
- [ ] **Quick resolution:** The guide answers the title's implied question within the first 300 words. A reader who arrived from Google should know within 30 seconds that this page will solve their problem.
- [ ] **Complete resolution:** A reader searching the primary keyword finds their question fully answered, not just discussed. "How to reduce Claude Code costs" must contain actual cost reduction techniques with expected savings, not just an explanation of how pricing works.
- [ ] **Actionable value:** The guide provides specific steps, real numbers, working code, or clear recommendations. Every strategy and recommendation must be something the reader can act on immediately.
- [ ] **Empirical evidence:** Strategies and recommendations are backed by evidence (benchmarks, measurements, documented behaviour, official sources), not presented as unsupported assertions. "This saves 40% on token costs" must cite where that number comes from.
- [ ] **Competitive superiority:** The guide is demonstrably better than the competing content documented in the guide report. It must go deeper, be more accurate, or provide unique value that competitors miss.
- [ ] **Trust signals:** The content shows WHY readers can trust it. Methodology is stated. Sources are cited. Real numbers have provenance. The reader understands the basis for every claim.
- [ ] **Unique perspective:** The guide offers something no other resource does. This is documented in the guide report's differentiation statement and must be visible in the content itself.

---

## Phase 2 — Deterministic Rewrite

Seven hard rules. Each is mechanically enforceable.

**Handling guides without GSC data:** When `no_gsc_data: true` (new or unindexed guides), Phase 2 still applies Rules 1, 2, 5, and 7 (brand cleanup, length floor, cliche/voice, external resources). Only Rule 3 (title/meta CTR rewrite), Rule 4 (query alignment), and Rule 6 (FAQ/GSC alignment) are skipped because they need search data. No guide gets a free pass.

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
- "systemprompt.io's governance pipeline evaluates" -> "a governance pipeline evaluates"
- "At systemprompt we believe" -> delete entire phrase, keep the underlying claim
- "systemprompt is the only self-hosted" -> "self-hosted deployments that" (reframe as category, not product)
- First-person marketing ("we built X to solve Y") -> stripped entirely

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

### Rule 3 — Title and meta description rewrite (CTR-driven, with rationale tracking)

**If the guide has no GSC data** (new, not indexed, `no_gsc_data: true` from Phase 0): **leave title and meta alone**. A rewrite without signal is guessing. Note `title_meta_skipped_no_signal` in the report.

**Before rewriting, check the guide report's Section 7 (metadata rationale):**
- Read the "Last changed" date for the title and description.
- **Hard rule:** if the title or description was last changed less than 28 days ago AND the previous hypothesis (S-###) has not matured (check `hypothesis-ledger.md` for `window_end` date), do NOT change it again. Wait for the data to come in. Note `title_meta_skipped_hypothesis_pending: {S-###}` in the report.
- Read the previous rationale so you understand why the current values were chosen.

**If the guide has GSC data and the 28-day cooldown has passed:** rewrite both. Use the following hard rules.

**Title rules:**
- 50-60 characters hard cap (Google truncates above 60)
- Must start with a strong verb or comparison frame: `How to ...`, `Build ...`, `Configure ...`, `X vs Y`, `N ways to ...`, `Install ...`, `Deploy ...`
- Must contain the guide's primary keyword (frontmatter `keywords[0]` or derived from the top GSC query)
- Must include a specificity hook: a number, a year (`2026`), an outcome, or a differentiator
- **Banned**: colon sandwich (`Foo: The Complete Guide to X`), bracketed tags (`[2026 Guide]`), "Ultimate", "Definitive", "Complete"
- Must accurately represent the content — no clickbait, no overpromise

**Meta description rules:**
- 130-160 characters hard cap
- Starts with a verb (`Learn`, `Compare`, `Configure`, `Build`, `Deploy`, `Troubleshoot`)
- Primary keyword in the first 100 characters
- Tells the reader what they will be able to DO, not what the article covers
- Unique across the site — grep `services/content/guides/*/index.md` for collision before writing

**Selection of primary keyword:** from the Phase-0 GSC data, the top query (by impressions, signal >= 20) *is* the primary keyword if it matches the guide's topic. Otherwise fall back to `keywords[0]` in frontmatter. Cross-check: the chosen primary keyword must appear in at least two top-20 GSC queries, or the signal is too narrow.

**Do not rewrite titles on breakout performers.** If the guide's current CTR is already within 80% of the position-expected CTR (see Phase 2.5 CTR curve), the title is working. Leave it. Only rewrite the meta description in this case.

**After rewriting, update the guide report's Section 7:**
- Record the new title/description values
- Record the rationale: which GSC data justified the change (impressions, CTR, position, top queries)
- Record the S-### hypothesis ID (create one in the hypothesis ledger if a title rewrite was made)
- Record the previous values and their rationale (so the change can be reversed if the hypothesis fails)
- Update "Last changed" date to today

### Rule 4 — Query-to-content alignment (search intent)

**Skipped when `no_gsc_data: true`.** Without search data, query alignment cannot be grounded.

For each query in `mandatory_queries` (Phase 0, impressions >= 20, 28 days):

1. **Verbatim presence check**: grep the guide body (case-insensitive) for the exact query string. If absent, it must be added naturally — as an H2, an H3, a lead sentence, or an FAQ question. Never keyword-stuff.

2. **Intent classification** (deterministic mapping):
   - Starts with `how to`, `how do I` -> how-to intent -> needs numbered steps
   - Contains `vs`, `versus`, `or`, `difference between` -> comparison intent -> needs table
   - Contains `error`, `failed`, `not working`, `broken`, `cannot`, `issue` -> troubleshooting intent -> needs troubleshooting block
   - Ends with `?` or starts with `what`, `why`, `when` -> question intent -> needs FAQ answer
   - Contains `best`, `top`, `list of` -> listicle intent -> needs enumerated list
   - Contains `example`, `tutorial`, `guide`, `setup` -> instructional intent -> needs step-by-step
   - Otherwise: informational -> needs an H2 or H3 explaining it

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

**Punctuation:** em dashes `—` -> replace with commas, periods, or parentheses (brand-voice rule)

**Other:** hashtags, fabricated "when I was building this" stories (unless founder-narrative exception), vague "teams say" / "companies report" / "studies show" without a source

Run a final pass against `brand-voice` skill's full cliche list and Anthropic terminology rules (plugins not apps, skills not prompts, agents not bots, MCP servers not APIs).

### Rule 6 — FAQ and GSC long-tail alignment

**Skipped when `no_gsc_data: true`.** Without search data, FAQ alignment cannot be grounded.

After Phase 0 produces the GSC query data:

1. **Extract question-form queries** from GSC data: any query containing `how`, `what`, `why`, `when`, `can`, `does`, `is`, or ending with `?`.
2. **Cross-reference with existing FAQ questions** in the guide's frontmatter.
3. **For any GSC question-query with >= 20 impressions that has no matching FAQ:** add it as a new FAQ entry with a complete, specific answer (2-4 sentences, includes numbers where applicable). The FAQ question should use the GSC query phrasing verbatim or as a natural variant.
4. **For any existing FAQ question that matches no GSC query AND no keyword-targets.json keyword:** flag for removal or replacement. Do not remove without flagging — the FAQ may be too new for GSC data.
5. **Update the guide report's "FAQ and Long-Tail Keyword Match" table** with all current mappings, noting which are GSC-validated and which are keyword-targets-only.

### Rule 7 — External resource and shareable asset enforcement

1. **External resources:** Count distinct external links in the guide body (exclude frontmatter, exclude internal links). If count < 5:
   - Identify additional relevant primary sources from the guide's topic domain (official documentation, research papers, specifications, GitHub repositories).
   - Add them as inline links in contextually appropriate locations where they support specific claims. Do not dump them in a "resources" section.
   - Update the guide report's "External Resources Audit" section.

2. **Homemade visual assets:** Count SVG elements, markdown data tables (with real data, not just structural tables), embedded charts, and architecture diagrams. If count < 2:
   - Flag `needs_visual_assets: true` in the report.
   - Do NOT generate placeholder assets. List specific data sources that could be used to create real assets (e.g., "Anthropic pricing page data could power a cost comparison chart," "benchmark results from the guide's code examples could populate a performance table").
   - Update the guide report's "Homemade Asset Inventory" section.

3. **Shareable asset compliance:** For each visual asset found, check that it is wrapped with:
   - A copy button (using `<sp-copy-button>` web component)
   - A share button with permalink backlink to `systemprompt.io/guides/{slug}#{asset-anchor}`
   - A source attribution line
   - If missing, flag `needs_share_buttons: true` in the report.

---

## Phase 2.5 — Scoring

Every guide gets a **100-point score** across eleven dimensions. Compute both pre- and post-rewrite. The delta is the proof of work.

**Handling guides without GSC data:** When `no_gsc_data: true`, GSC-dependent dimensions (Search traffic, CTR performance) score `N/A` and the max drops to 75. Query coverage gets a neutral score of 8 (cannot be penalised without signal). All other dimensions score normally.

### Rubric

| Dimension | Max | Data source |
|-----------|----:|-------------|
| Search traffic | 15 | GSC 28d impressions for this URL |
| CTR performance | 10 | GSC 28d CTR vs position-expected CTR |
| Query coverage | 15 | Fraction of top-20 queries where verbatim+intent are covered |
| Content depth | 10 | Word count vs floor |
| Value density | 8 | Brand-mention budget adherence |
| SEO hygiene | 8 | Frontmatter title/meta/slug/keywords rules |
| Structural integrity | 8 | Audit sections 3, 4, 5, 8 (links/code/structure/actionability) |
| FAQ keyword match | 8 | Fraction of FAQs matched to researched long-tail keywords |
| External resources | 8 | Distinct external resource links in body >= 5 |
| Homemade assets | 5 | Shareable visual assets with cited sources >= 2 |
| Search intent resolution | 5 | Guide report intent analysis complete + content addresses it |

### Deterministic scoring rules

**Search traffic (15 max):**
```
score = min(15, round(3 * log10(max(impressions_28d, 1))))
```
1 imp -> 0, 100 -> 6, 1k -> 9, 10k -> 12, 100k -> 15.

**CTR performance (10 max):**
```
ctr_curve = {1:0.25, 2:0.15, 3:0.11, 4:0.08, 5:0.06, 6:0.045,
             7:0.03, 8:0.023, 9:0.018, 10:0.015}
# positions 11-20 -> 0.01
expected = ctr_curve[round(position)]
score = min(10, round(10 * (actual_ctr / expected)))
```
A guide hitting 50% of expected CTR scores 5. No GSC data -> `N/A`, max drops to 75.

**Query coverage (15 max):**
```
eligible = top_queries with impressions >= 20
score = round(15 * (queries_with_verbatim_AND_intent / len(eligible)))
```
If `len(eligible) == 0`, score is a neutral 8 — cannot be penalised without signal.

**Content depth (10 max):**
```
floor = 5000 if pillar else 3500
score = 10 if words >= floor else round(10 * (words / floor))
```

**Value density (8 max):**
```
budget = min(3, words // 1500)
score = max(0, 8 - max(0, brand_mentions - budget))
```
Each brand mention over budget subtracts 1 point, floored at 0.

**SEO hygiene (8 max):** 1.6 points per pass: title length, meta length, slug quality, keyword list populated, meta uniqueness.

**Structural integrity (8 max):** 2 points per passing audit section (links, code, structure, actionability).

**FAQ keyword match (8 max):**
```
matched = FAQs with documented keyword match (in guide report or GSC-validated)
total = total FAQ count (minimum 1 to avoid division by zero)
score = round(8 * (matched / total))
```
4/4 matched = 8. 2/4 = 4. 0/4 = 0.

**External resources (8 max):**
```
count = distinct external resource links in guide body
score = min(8, round(8 * (count / 5)))
```
5+ = 8. 3 = 5. 1 = 2. 0 = 0.

**Homemade assets (5 max):**
```
count = shareable visual assets (SVGs + data tables + charts) with cited sources and share buttons
score = min(5, round(5 * (count / 2)))
```
2+ = 5. 1 = 3. 0 = 0.

**Search intent resolution (5 max):**
- 5 points if: guide report has completed "Search Intent Analysis" section (all fields populated with evidence) AND the guide's first 500 words address the documented intent AND the intent resolution verdict is "RESOLVED".
- 3 points if: guide report exists but intent analysis is partial or verdict is "PARTIALLY RESOLVED".
- 0 points if: no guide report, no intent analysis, or verdict is "NOT RESOLVED".

### Score tiers

- **85-100:** Top-tier asset. No further action.
- **70-84:** Acceptable. Rewrite opportunities exist but guide is not broken.
- **Below 70:** Failing. Priority candidate for rewrite.

### Commit message format

```
optimise {slug}: {pre_score} -> {post_score}

- brand mentions: {before} -> {after} (budget {budget})
- word count: {before} -> {after} (floor {floor})
- query coverage: {before}/{total} -> {after}/{total}
- FAQ keyword match: {matched}/{total}
- external resources: {count}/5
- title: "{before}" -> "{after}"
- meta: rewritten for {reason}
- gsc baseline: {impressions_28d} imp, {ctr}% CTR, position {position}
```

---

## Phase 3 — Verify and Commit

After rewriting:

1. **Word count** — must be >= floor. If not, report as `needs_content_investment` and abort commit.
2. **Brand-mention count** — must be within budget. Re-grep to verify.
3. **Re-run the 14-section audit.** Sections 1, 6, 7 must all pass. Other sections must be no worse than the baseline from Phase 1.
4. **Title and meta lengths** — validate hard caps.
5. **Meta description uniqueness** — grep all other guides' descriptions, confirm no collision.
6. **Diff the guide file.** If diff is empty or trivially whitespace-only, abort with `no_material_change`. Never commit a no-op.
7. **Recompute the score.** If `post_score < pre_score`, abort and roll back — this is a bug in the rules, not an improvement. Report the regression.
8. **Commit** with the message format above.
9. **Write the structured per-guide artifact report** to `reports/content/artifacts/optimiser/YYYY-MM-DD/{slug}.md`.
10. **Update the canonical guide report** at `reports/content/guides/{slug}/guide-report.md`:
    - Append Action Log entry: date, "Optimised", "guide-optimiser", "Score {pre} -> {post}", link to artifact report, hypothesis ID (if title/meta changed), commit SHA
    - Update "Current Scores > Optimiser Score" with the new score breakdown table
    - Update "Current Scores > Revision Audit" with the Phase 1 section results
    - Update "FAQ and Long-Tail Keyword Match" table with any new mappings from Rule 6
    - Update "External Resources Audit" with current resource inventory
    - Update "Homemade Asset Inventory" with current asset inventory
    - Update Section 7 (metadata rationale) if title/description/keywords were changed (with new rationale, previous values, S-### hypothesis ID)
    - Append a GSC performance snapshot row to Section 8 with today's data

---

## Per-Guide Report Template

When a guide report does not exist, create it at `reports/content/guides/{slug}/guide-report.md` using the following template. Populate what you can from keyword-targets.json and the guide's current content:

```markdown
# Guide Report: {title}

**Slug:** {slug}
**Path:** services/content/guides/{slug}/index.md
**Created:** {YYYY-MM-DD}
**Last updated:** {YYYY-MM-DD}
**Primary keyword:** {keyword} (volume: {N}, difficulty: {N}, intent: {type})
**Status:** draft | published | needs-revision | optimised

## 1. Search Intent Analysis

### Who is searching and why?
- **Primary intent:** {informational|commercial|navigational|transactional}
- **User profile:** {who is this person, what role, what problem}
- **What they need:** {the specific answer or outcome they are seeking}
- **Evidence:** {how we know: GSC queries, keyword intent data, SERP analysis}

### How have we addressed their intent?
- **Core value delivered:** {what the guide gives them that resolves their search}
- **Unique perspective:** {what we offer that no other resource does}
- **Evidence quality:** {are strategies empirical? are claims backed by data?}
- **Trust signals:** {methodology stated, sources cited, real numbers with provenance}
- **Intent resolution verdict:** RESOLVED | PARTIALLY RESOLVED | NOT RESOLVED

### Keyword Map
| Keyword | Volume | Difficulty | Classification | Source | Status |
|---------|-------:|----------:|---------------|--------|--------|

### Competing Content Audit
| URL | Word count | Strengths | Gaps we exploit |
|-----|----------:|-----------|----------------|

### Our Differentiation
{What this guide offers that nothing else does, with evidence}

## 2. FAQ and Long-Tail Keyword Match

| FAQ Question | Matched Keyword | Volume | Source | Validated? |
|-------------|----------------|-------:|--------|:----------:|

Rule: every FAQ must map to a researched keyword. No guessing.

## 3. External Resources Audit

| # | URL | Type | Relevance | In Guide? |
|---|-----|------|-----------|:---------:|

Minimum: 5 primary-source external resources.

## 4. Homemade Asset Inventory

| # | Type | Description | Data Source | Location |
|---|------|------------|------------|---------|

Minimum: 2 visual assets (SVG chart, data table, graph) with cited real data sources.

## 5. Action Log

Every action on this guide is recorded here. Every entry links to the artifact report and hypothesis ID where applicable. This is the audit trail. It must be complete.

| Date | Action | Skill | Details | Artifact Report | Hypothesis | Commit |
|------|--------|-------|---------|----------------|------------|--------|

Rules:
- Every skill run on this guide MUST append a row here
- Artifact reports are linked using relative paths
- Hypothesis IDs (S-###) cross-reference the SEO hypothesis ledger
- Commit SHAs link to the actual code change
- This log is append-only. Rows are never edited or removed.

## 6. Current Scores

### Optimiser Score: pending/100

### Revision Audit: pending/14 sections passing

## 7. Title, Description and Keywords Rationale

### Current Title
- **Value:** "{title}"
- **Primary keyword:** {keyword} (volume: {N}, source: keyword-targets.json, date: {YYYY-MM-DD})
- **Rationale:** {why this title was chosen, linked to keyword data or CTR evidence}
- **Last changed:** {YYYY-MM-DD} by {skill} (action: {S-### hypothesis ID or "initial"})
- **CTR at time of change:** {N}% (position {N})

### Current Description
- **Value:** "{description}"
- **Rationale:** {why this description, what search intent it addresses}
- **Last changed:** {YYYY-MM-DD} by {skill} (action: {S-### or "initial"})

### Current Keywords
- **Value:** "{keywords}"
- **Rationale:** {each keyword justified by volume/difficulty data from keyword-targets.json}
- **Last changed:** {YYYY-MM-DD} by {skill}

Rule: title, description, and keywords must NOT be changed without GSC or keyword data justifying the change. Every change must reference an S-### hypothesis ID or cite specific volume/CTR evidence. This prevents repeated edits without data backing.

## 8. GSC Performance History

| Date | 28d Impressions | 28d Clicks | CTR | Avg Position |
|------|----------------:|-----------:|----:|-------------:|
```

## Output Format

Per-guide artifact report template:

```markdown
# Guide Optimiser Report: {title}

**Guide:** `{path}`
**Slug:** `{slug}`
**Audited:** {YYYY-MM-DD}
**Mode:** optimise
**Commit:** {sha}

## Score: {post}/100 (was {pre}/100, {delta:+d})

| Dimension           | Before | After | Max |
|---------------------|-------:|------:|----:|
| Search traffic      | {} | {} | 15 |
| CTR performance     | {} | {} | 10 |
| Query coverage      | {} | {} | 15 |
| Content depth       | {} | {} | 10 |
| Value density       | {} | {} | 8 |
| SEO hygiene         | {} | {} | 8 |
| Structural          | {} | {} | 8 |
| FAQ keyword match   | {} | {} | 8 |
| External resources  | {} | {} | 8 |
| Homemade assets     | {} | {} | 5 |
| Search intent       | {} | {} | 5 |

## GSC Baseline

- 28-day impressions: {}
- 28-day clicks: {}
- 28-day CTR: {}%
- Avg position: {}
- Expected CTR at this position: {}%
- CTR gap: {}

## Query Coverage Matrix

{table from Rule 4}

## FAQ Keyword Alignment

| FAQ Question | Matched Keyword | Volume | Source | GSC-validated? |
|-------------|----------------|-------:|--------|:--------------:|

## Brand Mentions

- Before: {n}
- After: {n}
- Budget: {n}
- Removed instances:
  1. Line {N}: "{excerpt}" -> removed
  2. ...

## External Resources

- Count in body: {n}/5 minimum
- Added: {list of URLs added, or "none"}

## Homemade Assets

- Count: {n}/2 minimum
- Share buttons present: YES/NO
- Needs visual assets: {true/false}

## Content Changes

- Word count: {before} -> {after} (floor {floor})
- Sections added: {list}
- Sections rewritten: {list}

## Title and Meta

**Title:**
- Before: "{}"
- After: "{}"
- Length: {N} -> {N} chars
- Rationale: {GSC data justification}
- Hypothesis: {S-### or "no change"}

**Meta description:**
- Before: "{}"
- After: "{}"
- Length: {N} -> {N} chars

## Audit Results (Phase 1)

{pass/fail by all 14 sections}

## Verification

- Brand mentions within budget: PASS | FAIL
- Word count floor met: PASS | FAIL
- Title length: PASS | FAIL
- Meta length: PASS | FAIL
- Meta uniqueness: PASS | FAIL
- Score improved: PASS | FAIL
- Audit sections 1/6/7: PASS | FAIL
- Guide report updated: PASS | FAIL
```

## Anti-sludge rules

- Every recommendation and action ties to a specific line number or a specific query from GSC.
- No generic praise. No "this improves SEO" — say *which* metric and *why*.
- No em dashes in the report.
- No AI cliches in the report.
- The report is an audit trail, not marketing. It exists so a future reviewer can reproduce or reverse the rewrite.

## When NOT to use this skill

- Guides with `public: false` — internal-only, no public SEO value.
- Pages outside `/guides/` — this skill is guide-specific. For feature pages use `feature-copywriter`.
