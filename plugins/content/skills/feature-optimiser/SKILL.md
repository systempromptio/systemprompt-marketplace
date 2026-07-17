---
name: feature-optimiser
description: "Deterministically audit and optimise a published feature page on the register ladder: struggling-moment heroes with zero implementation jargon, mechanism evidence relocated to section bodies and dropdowns in the HashiCorp / Stripe / Tailscale register. Runs an 11-section quality audit plus register-ladder checks (hero jargon count, homepage narrative echo, struggling-moment opener, identifier-enumeration, established-not-indie voice) and applies 6 rewrite rules: claim verification, conversion clarity, brand discipline, and Technical-Marketing Synthesis (ten sub-checks: outcome headlines, jargon payoff scoped to sections/dropdowns, numbers with context, feature-to-outcome binding, narrative-vs-reference separation, skeptic test, named surfaces over coined metaphors, dropdown alignment, no Rust internals in narrative, dense sentences no filler). Penalises metaphor-stacking and marketing adjectives. Reads website analytics and GSC data per feature URL, produces a 90-point score delta (115 with analytics), commits changes, and updates the per-feature report. Load identity and brand-voice first."
metadata:
  version: "1.4.0"
  git_hash: "pending"
---

# Feature Optimiser

Run a **deterministic, data-driven audit and rewrite** on a single published feature page. This skill is the complete lifecycle tool for feature page quality: audit, fix, score, commit, log. Every decision is grounded in a quantitative rule, a code reference verification, or a 28-day Google Search Console signal. No vibes, no "use your judgement" gaps.

**Critical overrides (two, independently fatal):**

1. **Section 10 (CTA Effectiveness).** If Section 10 fails, the entire audit fails regardless of how many other sections pass. A feature page without a clear, effective call to action has no conversion value, regardless of how well it scores on technical criteria.
2. **Section 11 (Technical-Marketing Synthesis).** If three or more of the six Rule 6 sub-checks (6a-6f) fail, the entire audit fails. A feature page that reads as a jargon-stacked spec dump does not convert enterprise buyers, regardless of how well the claims verify or how clear the CTA is. The Secrets Management page is the canonical exemplar for what passing looks like.

## Dependencies

**Load `identity` and `brand-voice` before this skill.**

- `identity` -- positioning, ICP, messaging hierarchy, what the brand actually stands for
- `brand-voice` -- the cliche list, terminology rules, em-dash ban, and voice targets

## Source of Truth

Read these before starting:

- `/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md` -- pillar health, objectives, active hypotheses
- `/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json` -- canonical keyword registry with assigned pages, volumes, difficulty, target positions. Find the entry where the keyword matches this feature's topic to identify the primary keyword and its current metrics.
- The latest `reports/seo/daily/YYYY-MM-DD/daily-seo-brief.md` -- per-page CTR, impressions, position, quick-wins list
- `/var/www/html/systemprompt-web/reports/content/features/{slug}/feature-report.md` -- the per-feature report (search intent analysis, reference verification log, competitor audit, conversion baseline, action log, metadata rationale). If this file does not exist, create it from the template in the "Per-Feature Report Template" section below before proceeding. Populate with available data from keyword-targets.json and any GSC data pulled in Phase 0.

## Inputs

Caller must provide:
- **Feature slug** (e.g. `ai-governance`), OR the absolute path to the feature YAML file at `services/web/config/features/{slug}.yaml`

## Phases

The skill runs sequentially: **0 -> 1 -> 2 -> 2.5 -> 3**. Do not skip. If any phase aborts, exit cleanly without committing.

---

## Phase 0 -- Data Ingestion

Pull the 28-day Google Search Console query data for this specific feature URL. 28 days (not 7) so recent pages have enough signal and the result is not biased by a single bad week.

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

### Query for the feature's top 100 queries (28d)

```bash
TOKEN=$(cat /tmp/gsc_token)
SLUG=<slug>
START=$(date -d '28 days ago' +%Y-%m-%d)
END=$(date -d 'yesterday' +%Y-%m-%d)
mkdir -p /tmp/gsc-feature-queries

curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{
    \"startDate\": \"$START\",
    \"endDate\": \"$END\",
    \"dimensions\": [\"query\"],
    \"dimensionFilterGroups\": [{
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/features/$SLUG\"}]
    }],
    \"rowLimit\": 100
  }" > /tmp/gsc-feature-queries/$SLUG.json
```

### Query for the page-level aggregate

```bash
curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{
    \"startDate\": \"$START\",
    \"endDate\": \"$END\",
    \"dimensions\": [\"page\"],
    \"dimensionFilterGroups\": [{
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/features/$SLUG\"}]
    }],
    \"rowLimit\": 10
  }" > /tmp/gsc-feature-queries/$SLUG.page.json
```

Cache both files. If the feature has no rows, record `no_gsc_data: true` and proceed. Content rules still apply.

### Reference Inventory

Read the feature YAML file. For every `sections[].references[]` entry, verify the source code file exists at the stated path. Build a reference inventory:

```
reference_inventory = [
  {section: "...", file: "...", exists: true/false, line_anchor: "L12-L45", prose_accurate: pending}
]
```

### Build Working Set

- `page_metrics`: `{impressions, clicks, ctr, position}` from the page aggregate
- `top_queries`: sorted by impressions, filter `impressions >= 20` (signal floor)
- `reference_inventory`: every reference across all sections with existence status

### Initialise Feature Report

Read the per-feature report at `reports/content/features/{slug}/feature-report.md`. If it does not exist, create it from the template (see "Per-Feature Report Template" section below) and populate with:
- Primary keyword data from keyword-targets.json
- GSC data just pulled (impressions, clicks, CTR, position)
- Reference inventory from the YAML scan

This ensures every optimiser run has a feature report to work with, even for features created before this skill existed.

---

## Phase 1 -- 11-Section Audit

Run the full 11-section checklist against the target feature page. Record pass/fail per check. This phase writes nothing to disk. It produces a dict held in memory for Phase 2.5 scoring.

When Phase 1 produces a failing check, Phase 2 is responsible for fixing it only where the fix is covered by the rewrite rules below. Out-of-scope failures (e.g. missing source code files that need engineering work) are reported but not auto-fixed.

### Section 1: Why-What-How Structure Compliance

Every section on a feature page must follow strict Why-What-How ordering. This is not a suggestion. It is the structure that separates credible technical infrastructure marketing from generic SaaS copy.

- [ ] Every section opens with a concrete problem statement (the "Why")
- [ ] The "Why" names the actor, the moment, the failure mode. Example: "When a compliance officer audits agent behaviour at 2am, scattered logs across twelve services make root-cause analysis impossible."
- [ ] Every section has a one-sentence mechanism statement (the "What") using exact type/function names from the codebase. Example: "The AuditTrail type captures every tool invocation, model response, and governance decision in a single append-only log."
- [ ] Every section terminates in a verifiable code reference (the "How") pointing to a real file and line range
- [ ] No generic nouns ("the engine", "the platform", "the system") unless the actual codebase names them so. If the code calls it `GovernancePipeline`, the copy calls it `GovernancePipeline`.
- [ ] Why-What-How order is strictly followed. No section leads with "What" or "How" before establishing "Why".

### Section 2: Claim Verification (CRITICAL)

Every claim on a feature page must be anchored to source code. Feature pages are not blog posts. They describe what the software does, and every description must be verifiable.

- [ ] Every `sections[].references[]` points to a real, accessible file in the codebase
- [ ] Surrounding prose accurately describes what the referenced code does (read the actual file, compare to the claim)
- [ ] No claim overstates scope. "Handles all edge cases" must enumerate which edge cases, or be softened to "Handles {specific list}"
- [ ] Performance claims cite benchmarks or code measurements, not marketing estimates
- [ ] No references to deprecated or removed code paths
- [ ] **Every section has at least one reference.** CRITICAL: sections with zero references fail the entire audit. A feature section without a code reference is a marketing claim, not a feature description.

### Section 3: Conversion Clarity

Feature pages exist to convert visitors into users or conversations. Every element must serve that goal without being manipulative.

- [ ] Hero section follows formula: headline (6-10 words), subheadline (15-25 words), single CTA
- [ ] CTA text uses action verbs appropriate to audience. Enterprise visitors: "Schedule a deployment review". Individual developers: "Start building". Not "Learn more".
- [ ] Each value prop section answers one specific objection. The objection is identifiable. "Why should I trust a third-party governance layer?" is an objection. "Our product is great" is not.
- [ ] Page passes the Expert Density Test in the **section bodies** (not the hero): the mechanism-bearing paragraphs name a real surface (endpoint, table, trait, config key), cite a concrete mechanism, and state the operational boundary ("on your network", "before the tool process spawns", "before the response returns"). The hero is judged by Section 3R, not this check.
- [ ] No more than one primary CTA per section. Multiple CTAs create decision paralysis.
- [ ] Conversion path clear for all three personas: CTO (enterprise conversation), technical partner (integration discussion), individual developer (activation)

### Section 3R: Register Ladder (Charter, authoritative)

Governed by `/var/www/html/systemprompt-web/reports/content/features/copy-charter.md`. The hero leads with the reader's struggling moment and the ownership stake in plain language; mechanism evidence lives in the section bodies and dropdowns. Jargon is demoted, never deleted.

- [ ] **Hero jargon count.** No protocol or implementation noun appears in `headline`, `headline_highlight`, `subtitle`, or `highlights[].text`. Banned in the hero: OAuth, OAuth2, JWT, RBAC, Postgres/PostgreSQL, SQL, Rust type or trait names, `.rs` file names, column names, "resource server", "middleware", "IdP", "PDP", "AEAD". Product nouns (MCP, Claude Code) are allowed. Any banned noun in a hero field fails the check.
- [ ] **Homepage narrative echo present (exactly one).** The page echoes exactly one homepage phrase (rent vs own, "one binary", "governance you can prove", "evidence not screenshots", "stops working the day you stop paying", "still yours if you never pay us again", Run/Own/Build pillar language). Zero echoes fails; two or more (verbatim-spam) fails.
- [ ] **Struggling-moment opener.** The first paragraph of the first `sections[].content` opens on a concrete incident, audit, or renewal the reader recognises, in plain prose, not on a mechanism statement.
- [ ] **Only-ness / category-sameness.** The hero makes one claim only a self-hosted, source-available binary can make. If the headline could sit on a Datadog, LangSmith, or Credo AI feature page, it fails.
- [ ] **Identifier-enumeration check.** No list of three or more variable, env-var, or file names strung together in narrative prose as decoration (e.g. `ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, database URLs and OAuth tokens`). One representative concrete detail is fine; a padded list fails. Named identifiers belong in `references[]` and dropdown descriptions.
- [ ] **Established-not-indie voice.** No self-deprecating framing ("our Achilles heel", "if we disappear tomorrow", "happy to do a deal"), no head-counting, no "solo/indie/one-person", no fabricated scale. Institutional proof (due diligence at the largest tech companies, production deployments, USPTO registration, BSL 1.1, crates.io, load numbers) is used where present.
- Fail markers (pattern scan): any banned hero noun in `headline`/`headline_highlight`/`subtitle`/`highlights[].text`; zero or ≥2 homepage-phrase matches; first section paragraph opening on a backticked identifier or "The {Type} …" mechanism statement; ≥3 comma-separated backticked identifiers in one narrative sentence; any of the self-deprecating or head-counting strings above.

### Section 4: Technical Accuracy

- [ ] All code examples in the YAML are syntactically valid
- [ ] All type names, function names, module paths match the current codebase (grep to verify)
- [ ] Line-anchored references point to the correct lines (file content at those lines matches the described behaviour)
- [ ] Configuration examples use valid syntax for their stated format
- [ ] No placeholder values that look real (fake API keys, fake URLs, fake metrics)
- [ ] Version numbers and compatibility claims are current

### Section 5: Brand and Voice Compliance

- [ ] No marketing adjectives: "powerful", "seamless", "robust", "comprehensive", "cutting-edge", "enterprise-grade", "best-in-class", "world-class", "unparalleled", "transformative", "innovative", "next-generation", "state-of-the-art"
- [ ] No em dashes. Use commas, periods, or parentheses.
- [ ] No AI cliches: "revolutionize", "game-changer", "unlock", "supercharge", "seamlessly", "harness", "paradigm shift", "disrupt", "empower", "leverage" (as a verb), "reimagine"
- [ ] No second-person cheerleading: "You get full control", "You'll love how", "Imagine being able to". State what the software does. The reader decides if they love it.
- [ ] Active voice, present tense throughout. "The pipeline evaluates", not "The pipeline will be evaluating" or "Evaluations are performed by the pipeline".
- [ ] systemprompt.io never called a "platform". It is a library, infrastructure you own and extend. Correct terms: library, infrastructure, toolkit, framework.
- [ ] Correct Anthropic terminology: plugins not apps, skills not prompts, agents not bots, MCP servers not APIs
- [ ] One idea per sentence. No compound sentences joined with "and" that smuggle two distinct claims.

### Section 6: Competitive Positioning

- [ ] Competitive frame is build-vs-buy (not systemprompt vs other platforms). The question is "should I build this governance layer in-house or use existing infrastructure?"
- [ ] No direct competitor mentions by name in feature copy. No "unlike Platform X" or "better than Tool Y".
- [ ] Positioning communicates governance infrastructure, not consumer product. The reader should think "enterprise infrastructure" not "developer tool".
- [ ] Differentiators are specific and code-backed. "Self-hosted" is specific. "Better performance" without a benchmark is not.
- [ ] Page communicates why a CTO should trust this over building in-house. The answer must be specific: audit trail, governance pipeline, compliance integration, not "we're experts".

### Section 7: Visual Hierarchy and Readability

- [ ] Headline hierarchy correct. One `headline` (H1 equivalent), `sections[].heading` (H2 equivalent), items within sections (H3 equivalent). No skipped levels.
- [ ] No section exceeds 300 words without a visual break (sub-items, references, diagrams)
- [ ] Bullet points contain mechanisms, not padding. "Validates schema compliance for every tool invocation" is a mechanism. "Ensures quality and reliability" is padding.
- [ ] Before/after examples included where rewrites were made (in the artifact report, not in the YAML itself)
- [ ] YAML schema preserved. No structural key changes. The renderer expects specific keys.

### Section 8: SEO and Metadata

- [ ] `headline` + `headline_highlight` together form a complete title under 60 characters
- [ ] `description` under 160 characters with primary keyword in the first 100 characters
- [ ] `keywords` list is specific and relevant (not generic terms like "AI" or "software")
- [ ] Primary keyword appears in the headline
- [ ] Primary keyword appears in the description
- [ ] Slug not changed. Contract: anchor links and external references to `/features/{slug}` exist in the wild. Changing the slug breaks inbound links.

### Section 9: Enterprise Credibility Signals

- [ ] Page demonstrates genuine technical depth. A senior engineer reading the page should learn something about the architecture, not just get a sales pitch.
- [ ] Social proof elements are real. No fabricated testimonials, logos, or metrics. If there are no testimonials, there are no testimonials. Do not invent them.
- [ ] Page addresses build-vs-buy question implicitly through implementation depth. The level of detail in the feature description itself is the argument for "buy".
- [ ] Architecture and implementation details are exposed, not hidden behind marketing. Show the types, show the flow, show the code.
- [ ] Page would survive scrutiny from an engineer who clicks through to the source code references. Every reference must check out.

### Section 10: CTA Effectiveness (CRITICAL OVERRIDE)

**If Section 10 fails, the entire audit fails regardless of other scores.**

This is the conversion gate. A feature page that passes every quality check but fails to direct the visitor toward action is a documentation page, not a feature page.

- [ ] Primary CTA is present and clear. The page has an explicit call to action, not just information.
- [ ] CTA matches conversion path. Enterprise visitors get directed toward a conversation ("Schedule a 15-minute deployment review"). Individual developers get directed toward activation ("Install the CLI and run your first governance check").
- [ ] Evidence precedes the ask. The CTA appears after the feature has been demonstrated, not before. The reader has seen code references, architecture details, and specific mechanisms before being asked to act.
- [ ] No dead ends. Every section provides a path forward, either to the next section or to a CTA. No section ends with the reader having nowhere to go.
- [ ] CTA language is specific. Not "Learn more" but "Schedule a 15-minute deployment review". Not "Get started" but "Install the CLI in 60 seconds". Specificity builds trust.

### Section 11: Technical-Marketing Synthesis (CRITICAL OVERRIDE when 3+ sub-checks fail)

**If three or more of the ten sub-checks below fail, the entire audit fails regardless of other scores.**

This is the craft gate. A page can verify every claim, hit every keyword, and ship a perfect CTA, and still read as an API doc stapled to a pitch deck, or as a brand exercise stapled to a spec. Section 11 enforces the register: dense, metaphor-free, every claim tied to a named surface and a verifiable reference — the register a staff engineer, CISO, or platform lead reads in HashiCorp, Stripe, and Tailscale documentation. The primary exemplar is the `/v1/messages` Gateway hero in the feature-writer skill. The Secrets Management "Last Mile Secrets Delivery" section is the secondary exemplar for permissible-coinage cases only.

Six-check Section 11 (6a–6f) addresses copy clarity and outcome-binding. Sub-checks 6g–6j address naming discipline, navigation consistency, Rust-plumbing exclusion, and prose density. The bar: at most one invented coined title per page; industry terms (JWT, OAuth, RBAC, MCP) assumed known; sentences dense with named surfaces and guarantees stated as verbs.

**6a. Outcome Headlines (not mechanism)**
- [ ] Headline names the stake, not the implementation (or the mechanism *is* the outcome, as in "Secrets never enter the context window")
- [ ] A CISO reading only the headline can complete "without this, my organisation is exposed to ___"
- [ ] Subtitle extends the stake with a concrete behaviour or number, not a restatement of the mechanism
- Fail markers (pattern scan): headline matches `governed|unified|comprehensive|MCP-native|powerful|every-X-Yed` without an outcome clause

**6b. Jargon Payoff (in sections and dropdowns, not the hero)**
- [ ] **Scope:** this sub-check applies to `sections[].content` paragraphs 2+ and `items[].description` only. The hero (`headline`, `headline_highlight`, `subtitle`, `highlights[]`) must carry no implementation jargon at all. That is Section 3R, not a decode-it check. A hero with a technical term to decode has already failed the register ladder; do not "fix" it by adding a decoder, strip the term.
- [ ] Every acronym (OAuth2, HS256, JWT, RBAC, SIEM, RPC, etc.) in a section body or dropdown has a plain-English decoder within the same or next sentence
- [ ] Every Rust type or trait name in narrative body copy (as opposed to `references[]`) is followed by a sentence explaining what it does for the reader
- [ ] No stacked jargon lists (three or more technical terms in a row without interstitial decoding)
- Fail markers (pattern scan): any section-body or dropdown paragraph with a backticked identifier that is not followed within one sentence by a decoder clause starting with "means", "so", "this", "the effect", or equivalent. Jargon found in a hero field is a Section 3R failure, not a 6b decoder gap.

**6c. Numbers with Context (why this number, not another?)**
- [ ] Every numeric claim in body copy is followed within the same paragraph by a clause explaining why that number
- [ ] Rate limits, counts, thresholds, and tier multipliers have a sized-to / because / so-that clause adjacent
- [ ] Performance numbers (ms, req/s, percentages) cite what they were measured against
- Fail markers (pattern scan): any digit token not within ±2 sentences of the substrings "because", "so that", "sized to", "measured", "per", or a clause explaining intent

**6d. Feature-to-Outcome Binding (what breaks without this?)**
- [ ] Every `items[]` bullet binds the capability to a concrete failure mode or stake
- [ ] Bullet text answers "what goes wrong without this?" implicitly or explicitly
- [ ] No bullets that are bare capability names ("Role tiers", "Scoping", "Hooks")
- Fail markers (pattern scan): any `items[].title` or `items[].description` that is a noun phrase under 8 words with no verb and no stake

**6e. Narrative-vs-Reference Separation**
- [ ] Inline `ModuleName::function_name` references in narrative body copy only appear where naming the type *is* the mechanism the reader cares about
- [ ] Middleware names, internal plumbing types, and opaque trait names live in `references[]` entries with a description, not in narrative
- [ ] Narrative prose speaks in behaviour; references speak in code
- Fail markers (pattern scan): any backticked token in narrative containing `::` or snake_case that is not also named inline in a sentence describing its behaviour, with no matching entry in that section's `references[]`

**6f. Skeptic's "So What" Test**
- [ ] Every technical claim paragraph pre-answers at least one of CISO ("can I prove this in an audit?"), CTO ("does this replace what I'm building?"), or staff engineer ("can I verify this in source?")
- [ ] The pre-answer lives in the same paragraph as the claim, not three scrolls below
- [ ] A reader reaching the end of any technical paragraph cannot finish with an unanswered "so what?"
- Fail markers: paragraph lacks audit cite (log table / signature / query), build-vs-buy delta, or file+line reference

**6g. Named Surfaces Over Coined Metaphors**
- [ ] Every `sections[].title` names the real surface (endpoint, table, trait, config key), the industry term, or the operational boundary — **not** an invented metaphor
- [ ] At most one invented coined title appears on the page (metaphor-stacking fails)
- [ ] Any invented coinage is grounded in an industry-standard metaphor (supply chain's "last mile" for credential delivery, "blast radius" for IAM scoping) and the section's opening sentence collapses the metaphor to the real surface
- [ ] A reader scanning the sidebar can tell what each section does without opening it
- Pass examples: "`/v1/messages` on Your Infrastructure", "Per-Server OAuth Scoping", "Subprocess Credential Injection", "Per-Endpoint Rate Limits", "On-Host Audit Trail", "Air-Gap Deployment"
- Fail markers: more than one of "The Probe Wall", "Blast Doors", "The Fleet Manifest", "The Lifecycle Chokepoint", "The Executor Spine", "Transport-Agnostic Bearer" on the same page; any section title whose subject cannot be guessed by a reader who knows JWT/OAuth/RBAC/MCP/air-gap; any coined title whose opening paragraph does not name the real surface within the first sentence

**6h. Dropdown Alignment**
- [ ] The feature page `headline` matches the navigation `dropdown-link-label` verbatim (extended minimally with a coined highlight to hit the 6-10 word hero formula is allowed)
- [ ] The `subtitle` preserves the two or three anchor phrases from the navigation `dropdown-link-desc` (extended with feature-specific detail for the 15-25 word target)
- [ ] A reader clicking through from the nav sees consistent copy on landing, not a surprise rebrand
- Source of truth: `/var/www/html/systemprompt-web/services/web/config/navigation.yaml`. Find this feature under `links[].label`/`links[].description`; also check `/var/www/html/systemprompt-web/services/web/config/homepage.yaml` for the homepage card text
- Fail markers: headline that diverges from the dropdown label (e.g., dropdown "Secrets Management" but page "AI AGENT SECRETS MANAGEMENT"), or subtitle that drops the dropdown's anchor phrases entirely
- Exception: if the dropdown copy itself fails Rules 2 or 6a-6f, flag it for a separate menu-copy pass rather than aligning to bad copy

**6i. Plain-English Narrative (no Rust internals)**
- [ ] Rust-specific standard-library types (`std::process::Command`, `HashMap<...>`, `Arc<>`, `Box<>`, `Option<>`, `Result<>`, `Vec<>`, `Mutex<>`) do NOT appear in `sections[].content` paragraphs or `items[].description`
- [ ] Rust macros (`#[serde(flatten)]`, `#[derive(...)]`, `#[tokio::main]`) do NOT appear in narrative
- [ ] Function call syntax like `spawn()`, `::new()`, `::standard()`, `::browser_only()` does NOT appear in narrative (those belong in `references[].description`)
- [ ] Industry terminology (JWT, HS256, OAuth, MCP, RBAC, bearer, audience, issuer, scope) IS permitted in narrative — engineers recognise it regardless of language
- [ ] Plumbing stays in `references[]`; narrative speaks behaviour
- Fail markers: any backticked identifier in narrative that is a Rust-specific stdlib type, macro, or method syntax; any `crates/...` module path inline
- Calibration exemplar: the Secrets Management "Last Mile Secrets Delivery" body paragraphs describe subprocess launch, credential handoff, and audit logging in plain English. The function names (`spawn_server`, `Secrets::get`, `McpToolExecutor::execute`) live only in the references block

**6j. Natural Flow (no formulaic punctuation or mad-libs)**
- [ ] `sections[].content` paragraphs have zero colons outside reference descriptions (break into separate sentences rather than use colons to front-load)
- [ ] Content prose has zero semicolons (split into sentences)
- [ ] Content prose has zero em-dashes (Rule 5 already bans these)
- [ ] `items[].description` does NOT end with the formulaic "Without this, ___" pattern on every bullet — the stake should fall out of natural sentences for most bullets; use the explicit "without this" phrasing sparingly (zero-to-two per section) where it genuinely lands
- [ ] `sections[].references[].description` is ≤15 words per entry (longer descriptions break the UI layout)
- [ ] Varied sentence openings; no mechanical repetition of structure across items
- Fail markers: >1 colon per content paragraph, any semicolon, any em-dash, >2 "Without this" appendices per section, any reference description over 15 words

Record a pass/fail for each sub-check. If 3+ of the ten fail, Section 11 fails; if Section 11 fails, the audit fails.

---

## Phase 2 -- Deterministic Rewrite

Six hard rules. Each is mechanically enforceable.

**Handling features without GSC data:** When `no_gsc_data: true` (new or unindexed features), Phase 2 still applies all five rules. Only SEO metadata optimisation within Rule 5 is limited because it benefits from search data. No feature gets a free pass.

### Rule 1 -- Why-What-How Enforcement

For every section that failed Section 1 of the audit:

1. **Extract the implied problem.** Read the section content. Identify what problem the feature solves. If the section does not clearly state a problem, infer it from the feature's purpose and the code it references.
2. **Rewrite the opening** to name the actor, the moment, and the failure mode. Template: "When {actor} {does what} {at what moment}, {failure mode}."
3. **Identify the exact type or function** that addresses the problem. Read the referenced source code. Use the real name from the codebase, not a marketing synonym.
4. **Add or correct the reference.** Every section must terminate with a verifiable code reference. If no reference exists, find the relevant source file and add one. If the reference exists but the line numbers have shifted, update them.

Do not invent references. If no source code file supports a section's claims, flag `unverifiable_section: true` and soften the claims to match what can be verified.

### Rule 2 -- Adjective-to-Specific Replacement

Scan all editable fields (`headline`, `headline_highlight`, `subtitle`, `description`, `sections[].content`, `items[].title`, `items[].description`, `cta.description`, `cta.heading`) for banned adjectives.

**Ban list:**
`powerful`, `seamless`, `robust`, `comprehensive`, `cutting-edge`, `enterprise-grade`, `best-in-class`, `world-class`, `unparalleled`, `transformative`, `innovative`, `next-generation`, `state-of-the-art`, `scalable` (unless backed by benchmark), `flexible` (unless backed by configuration options list), `secure` (unless backed by specific security mechanism), `efficient` (unless backed by performance data)

**Replacement rules:**
- Replace each banned adjective with a number, a type name, or a concrete behaviour
- "Powerful governance" -> "Governance pipeline that evaluates 14 compliance rules per invocation"
- "Seamless integration" -> "Integration via a single `use systemprompt::governance` import"
- "Robust error handling" -> "Error handling that retries 3 times with exponential backoff before surfacing to the audit log"
- "Comprehensive audit trail" -> "Audit trail capturing tool invocations, model responses, and governance decisions"
- If no specific replacement is available, delete the adjective entirely. "Powerful governance pipeline" becomes "Governance pipeline".

### Rule 3 -- Reference Verification and Repair

For every entry in the `reference_inventory` built in Phase 0:

1. **Verify file exists** at the stated path. If not, search the codebase for the file (it may have moved). Update the path if found. Remove the reference if the file no longer exists.
2. **Verify line anchor accuracy.** Read the file at the referenced lines. Confirm the code at those lines matches what the prose describes. If lines have shifted (common after refactors), find the correct lines and update the anchor.
3. **Verify prose accuracy.** Read the surrounding section content. Does it accurately describe what the code does? If the prose says "validates schema compliance" but the code actually performs "type checking", update the prose to match the code. The code is the source of truth, not the copy.
4. **Add missing references.** For sections flagged with zero references in the audit, find the relevant source file and add a reference. Every section must have at least one.
5. **Soften unverifiable claims.** If a section makes claims that cannot be traced to source code, soften the language: "supports X" becomes "designed to support X" or is removed entirely.

### Rule 4 -- CTA and Conversion Optimisation

1. **Hero formula enforcement.** The hero section must contain: headline (6-10 words), subheadline (15-25 words), single CTA. Count the words. If out of range, rewrite to fit.
2. **Replace generic CTAs** with specific action language:
   - "Learn more" -> "Read the architecture walkthrough"
   - "Get started" -> "Install the CLI in 60 seconds"
   - "Contact us" -> "Schedule a 15-minute deployment review"
   - "Sign up" -> "Start your first governance pipeline"
   - "Try it free" -> "Run your first compliance check"
3. **Verify conversion path clarity.** For each persona (CTO, technical partner, individual developer), trace the path from hero to action. If any persona hits a dead end, add navigation.
4. **Ensure evidence precedes action.** The primary CTA must appear after at least two sections of feature evidence. Moving a CTA above the evidence violates trust.

### Rule 5 -- Brand and Voice Cleanup

1. **Strip cliches.** Same list as Section 5 audit. Every occurrence replaced or removed.
2. **Strip filler.** "In today's fast-paced world", "At the end of the day", "It goes without saying". Delete entirely.
3. **Replace em dashes** with commas, periods, or parentheses.
4. **Fix terminology.** plugins not apps, skills not prompts, agents not bots, MCP servers not APIs, library/infrastructure not platform.
5. **Enforce one idea per sentence.** Split compound sentences that smuggle two claims.
6. **Strip second-person cheerleading.** "You get full control" becomes "The operator retains full control" or simply describes the mechanism.
7. **Feature-specific ban list** (in addition to the global ban list): "solution", "leverage" (as verb), "utilize", "facilitate", "streamline", "optimize" (as marketing verb, allowed when describing actual code optimisation), "empower", "enable" (replace with specific mechanism).

### Rule 5R -- Register Ladder (Charter)

For every Section 3R check that failed, apply the matching rewrite. Read the charter and the homepage (`services/web/config/homepage.yaml`) first.

1. **Hero jargon strip.** Scan `headline`, `headline_highlight`, `subtitle`, `highlights[].text` for banned implementation nouns (OAuth, OAuth2, JWT, RBAC, Postgres, SQL, trait names, `.rs` file names, column names, "resource server", "middleware", "IdP", "PDP", "AEAD"). Do not decode them, remove them. Rewrite the hero to open on the struggling moment or ownership stake in plain language, echoing one homepage phrase. Relocate the stripped mechanism intact into a section body (paragraph 2+) or a dropdown, never delete it. Example: "Per-Server OAuth Scoping keeps each MCP token isolated" -> hero "One stolen key should open one door, not all of them", with the OAuth scoping detail moved to the section body.
2. **Homepage echo.** If zero homepage phrases are present, weave exactly one into the headline or subtitle. If two or more appear, keep the one that matches the page's stake and cut the rest.
3. **Struggling-moment opener.** If the first `sections[].content` paragraph opens on a mechanism statement, rewrite paragraph 1 to open on the concrete incident, audit, or renewal. Move the displaced mechanism to paragraph 2+.
4. **Identifier-enumeration.** Collapse any list of three or more variable/env/file names in narrative prose to one representative detail or "your API keys". Move the full list to a `references[]` entry or dropdown description.
5. **Established-voice.** Replace self-deprecating or head-counting phrasing with institutional proof (due diligence at the largest tech companies, production deployments, USPTO registration, BSL 1.1, crates.io, load numbers) or engineering-led framing. Never fabricate scale.

Relocation of already-verified evidence needs no re-verification. Nothing verified gets deleted.

### Rule 6 -- Technical-Marketing Synthesis

For every sub-check that failed Section 11, apply the matching rewrite. Apply in order 6a -> 6f so earlier rewrites do not create work for later ones.

**6a scan -> rewrite: Outcome Headlines**
- Scan: `headline` or `headline_highlight` contains any of `governed`, `unified`, `comprehensive`, `MCP-native`, `powerful`, `every-{noun}-{past-participle}` without an outcome clause, OR any banned implementation noun (see Rule 5R.1)
- Rewrite: regenerate to the struggling-moment / ownership-stake form with zero implementation jargon and one homepage echo. Ask "without this, the reader is exposed to ___" and lead with the answer. Keep within 6-10 words for headline plus highlight combined.
- Example: "Every tool call governed" -> "Stop it before it runs. Not report it after." "Per-Server OAuth Scoping" -> "One stolen key should open one door, not all of them"

**6b scan -> rewrite: Jargon Payoff (sections and dropdowns only)**
- Scope: applies to `sections[].content` paragraphs 2+, `items[].title`, and `items[].description`, never the hero. Jargon in a hero field is repaired by Rule 5R.1 (strip and relocate), not by adding a decoder.
- Scan: any backticked identifier, acronym, or technical term in the section bodies or dropdowns that is not followed within one sentence by a decoder clause ("means", "so", "the effect is", "which translates to")
- Rewrite: append a one-sentence decoder that ties the term to a reader concern (from `commons:brand-voice` preferred-language lists where possible). If the term is internal plumbing that does not merit a decoder, move it to a `references[]` entry and replace the inline mention with a behaviour description (see 6e).
- Example: "HS256 JWT signing" -> "HS256 signing means tokens verify locally in under a microsecond, with no external dependency"

**6c scan -> rewrite: Numbers with Context**
- Scan: any digit token in body copy (`sections[].content`, `items[].description`) that is not within ±2 sentences of any of: "because", "so that", "sized to", "measured", "budgeted for", "leaves headroom", "to catch", "because a loop", or an equivalent intent clause
- Rewrite: add a clause explaining the sizing rationale in the same paragraph. If the rationale is unknown, read the source code or configuration defaults to recover it; if still unknown, remove the number and soften to a qualitative claim.
- Example: "11 per-endpoint rates" -> "Eleven per-endpoint rates, sized to catch runaway agents without throttling normal use"

**6d scan -> rewrite: Feature-to-Outcome Binding**
- Scan: any `items[].title` that is a bare capability noun phrase under 8 words with no verb, OR any `items[].description` that describes *what the feature is* without describing *what breaks without it*
- Rewrite: append or lead with a failure-mode clause. Template: "{capability} — prevents {failure mode}" or "{capability}, so that {stake}".
- Example: "Six role tiers" -> "Six role tiers — prevents an analyst inheriting production database access from an overloaded admin role"

**6e scan -> rewrite: Narrative-vs-Reference Separation**
- Scan: any backticked token in narrative body copy containing `::` or snake_case that is not explicitly described as a mechanism in the same sentence (i.e. the sentence would not change meaning if the identifier were replaced with a behaviour phrase)
- Rewrite: move the identifier to a `references[]` entry with a one-line description. Replace the inline mention with a behaviour phrase ("the middleware that checks permissions", "the helper that spawns the subprocess"). Preserve the link to source via the references entry, not inline.
- Example: "Routed through `enforce_rbac_from_registry` middleware" -> "Every request passes a permission check before it reaches a handler. The middleware is named in the reference below." plus matching `references[]` entry.
- Exception: if the identifier *is* the mechanism (e.g. `spawn_server()` setting `ANTHROPIC_API_KEY` on a `Command`), leave it inline.

**6f scan -> rewrite: Skeptic's So What**
- Scan: any paragraph containing a technical claim that does not cite one of (a) an audit log table, signature, or query; (b) a build-vs-buy delta with specificity; (c) a file path and line range
- Rewrite: add a sentence pre-answering the matching buyer question. Choose CISO if the paragraph touches security, compliance, audit, or secrets; CTO if it touches control-plane consolidation, single-binary claims, or cost/consolidation; staff engineer if it describes internals.
- If no pre-answer is possible (the claim is not defensible), soften or cut the claim.

**6g scan -> rewrite: Named Surfaces Over Coined Metaphors**
- Scan: `sections[].title` fields. Count invented coined titles (metaphors that cannot be decoded without reading the section body). If the count exceeds 1, the page fails 6g until reduced.
- Rewrite: replace invented coinage with the real surface the section operates on. "Blast Doors" → "Per-Server OAuth Scoping". "The Lifecycle Chokepoint" → "Managed MCP Server Lifecycle". "The Probe Wall" → "Edge Scanner Rejection". "The Executor Spine" → "Subprocess Tool Execution".
- Prefer the protocol endpoint (`/v1/messages` Gateway, `audit_events` Table), the industry term (Per-Server OAuth Scoping, Subprocess Credential Injection, Per-Endpoint Rate Limits), or the operational boundary (Air-Gap Deployment, On-Host Audit Trail).
- Exception: one invented coined title per page is allowed when grounded in an industry-standard metaphor (supply chain's "last mile", "blast radius" from IAM) AND the opening sentence collapses the metaphor to the real surface. The rest of the section titles must name surfaces.
- Do not propagate invented coinage into `headline_highlight` or `highlights[]` unless the coinage survived the exception test above.

**6h scan -> rewrite: Dropdown Alignment**
- Load `/var/www/html/systemprompt-web/services/web/config/navigation.yaml`. Find the entry where `href == /features/{slug}`. Read the `label` and the `description`.
- Also load `/var/www/html/systemprompt-web/services/web/config/homepage.yaml`. Find the entry where `url == /features/{slug}`. Read the `title` and the `description`.
- Rewrite `headline` to match the dropdown label verbatim (or extend minimally with a coined highlight to hit 6-10 words). Example: dropdown label "Secrets Management" -> headline "SECRETS MANAGEMENT." + highlight "LAST MILE DELIVERY, NEVER IN THE PROMPT."
- Rewrite `subtitle` to preserve the anchor phrases from the dropdown description, extending as needed for the 15-25 word target. Example: dropdown description "Credentials are encrypted at rest and blocked from inference. Secrets never reach AI models." -> subtitle "Credentials for Claude agents are encrypted at rest and blocked from inference. API keys, tokens, and database URLs never reach AI models."
- If the dropdown copy is itself broken under the skill rules (banned adjectives, unverifiable claims), flag the navigation.yaml entry for a separate menu-copy pass in the artifact report. Do not align a well-rewritten feature page to poorly-written menu copy.

**6i scan -> rewrite: Plain-English Narrative (no Rust internals)**
- Scan `sections[].content` and `items[].description` for Rust-specific tokens: `std::` paths, standard generic types (`HashMap<`, `Arc<`, `Box<`, `Option<`, `Result<`, `Vec<`, `Mutex<`), Rust macros (`#[`), function call syntax with `()` or `::` other than when the function name IS the mechanism
- Rewrite: describe the behaviour in plain English. Move the Rust identifier to the matching `references[].description`.
- Example: "`spawn_server()` writes provider keys onto the child `Command` environment and fires `spawn()`" -> "the system launches the tool as a separate subprocess and hands the provider credentials to it as environment variables". The function name `spawn_server` moves to the reference for `spawner.rs (lines 26-120)`.
- Industry acronyms and protocol names remain inline (JWT, HS256, OAuth, MCP, RBAC, bearer, audience, issuer, scope) — decode them per 6b if they haven't been decoded yet.

**6j scan -> rewrite: Natural Flow**
- Scan content paragraphs for colons (>1 per paragraph), semicolons (any), em-dashes (any), and `items[].description` for "Without this" frequency (>2 per section).
- Scan `sections[].references[].description` for entries longer than 15 words.
- Rewrite colons to periods (break into two sentences). Rewrite semicolons to periods. Replace em-dashes with commas or periods (Rule 5). Trim formulaic "Without this, ___" appendices on every bullet to at most 2 per section; let the stake fall out of the sentence itself on other bullets. Trim reference descriptions to ≤15 words, preserving the function name and the core behavioural phrase.
- Vary sentence openings across items[] so the page does not read as a template fill-in.

After all ten sub-rewrites, re-scan the page. If any sub-check still fails, iterate once. If a second pass still fails, flag the offending section for manual review and mark `rule_6_{x}_unresolved: true` in the artifact report.

---

## Phase 2.5 -- Scoring

Every feature page gets a **90-point score** across ten dimensions (expandable to 115 when analytics data is available). Compute both pre- and post-rewrite. The delta is the proof of work.

### Rubric (90-point base)

| Dimension | Max | How to score |
|-----------|----:|-------------|
| Why-What-How compliance | 15 | `round(15 * (passing_sections / total_sections))` |
| Claim verification | 15 | `round(15 * (verified_refs / total_refs))` |
| Technical-marketing synthesis | 15 | `round(15 * (passing_sub_checks / 6))` where passing_sub_checks is the count of Section 11 sub-checks (6a-6f) that pass across the whole page |
| Conversion clarity | 10 | 2 points each: hero specification (operation + boundary + ≥3 concrete nouns), CTA quality (gated by evidence depth, names artefact), Expert Density Test (surface + mechanism + boundary in first 300 chars), conversion paths present, no dead ends |
| Technical accuracy | 10 | `round(10 * (valid_refs / total_refs))` |
| Brand/voice compliance | 8 | `max(0, 8 - adjective_count - cliche_count)` |
| Competitive positioning | 5 | 1 point each: build-vs-buy frame, no competitor names, governance-first positioning, code-backed differentiators, build-vs-buy implicit in depth |
| Visual hierarchy | 5 | 1 point each: correct heading hierarchy, visual breaks every 300 words, no padding bullets, before/after in report, YAML schema preserved |
| SEO metadata | 5 | 1 point each: title under 60 chars, description under 160 chars, keywords relevant, primary keyword in headline, primary keyword in description |
| Enterprise credibility | 2 | 1 point each: genuine technical depth, real social proof (no fabrication) |

### Analytics expansion (when data available, +25 points)

| Dimension | Max | How to score |
|-----------|----:|-------------|
| Conversion performance | 15 | Based on CTA click-through rate. `min(15, round(15 * (cta_ctr / 0.05)))` where 5% CTR is the benchmark |
| Page engagement | 10 | Based on bounce rate and time-on-page. `round(10 * (1 - bounce_rate) * min(1, avg_time_seconds / 120))` |

### Deterministic scoring formulas

**Why-What-How compliance (15 max):**
```
passing = sections where all 6 checks in Section 1 pass
total = total number of sections in the feature YAML
score = round(15 * (passing / total))
```
0 passing out of 5 sections = 0. 3 out of 5 = 9. 5 out of 5 = 15.

**Claim verification (15 max):**
```
verified = references where file exists AND prose matches code AND no overstatement
total = total references across all sections
score = round(15 * (verified / total))
```
If total is 0 (no references at all), score is 0 because Section 2 failed the entire audit.

**Technical-marketing synthesis (15 max):**
```
passing = count of Section 11 sub-checks (6a..6j, ten total) that pass across the whole page
score = round(15 * (passing / 10))
```
10 of 10 passing = 15. 7 of 10 = 11. 5 of 10 = 8. 3+ fails (i.e. 7 or fewer passing) = Section 11 fails (critical override; the audit fails even before scoring runs). If the audit has aborted because of Section 11's override, do not report a score; report the abort.

**Conversion clarity (10 max):**
2 points for each passing criterion:
- Hero follows formula (headline 6-10 words, subheadline 15-25 words, single CTA)
- CTA text uses specific action verbs (not generic "learn more")
- Expert Density Test passes (surface, mechanism, and operational boundary present in the first 300 characters of the hero)
- Conversion paths clear for all three personas
- No dead ends (every section has a path forward)

**Technical accuracy (10 max):**
```
valid = references where file exists AND line anchors correct AND code matches prose
total = total references
score = round(10 * (valid / total))
```

**Brand/voice compliance (8 max):**
```
violations = count of banned adjectives + count of cliches + count of em dashes
score = max(0, 8 - violations)
```
Each violation subtracts 1 point, floored at 0. Zero violations = 8.

**Competitive positioning (5 max):**
1 point for each:
- Build-vs-buy frame used (not product-vs-product)
- No competitor names in copy
- Governance infrastructure positioning (not consumer product)
- Differentiators backed by code references
- Build-vs-buy question answered implicitly through implementation depth

**Visual hierarchy (5 max):**
1 point for each:
- Heading hierarchy correct (H1 > H2 > H3 equivalent, no skips)
- No section exceeds 300 words without visual break
- Bullet points contain mechanisms, not padding
- Before/after examples documented in artifact report
- YAML schema preserved (no forbidden field changes)

**SEO metadata (5 max):**
1 point for each:
- `headline` + `headline_highlight` under 60 characters combined
- `description` under 160 characters
- `keywords` list contains specific, relevant terms
- Primary keyword appears in headline
- Primary keyword appears in description

**Enterprise credibility (2 max):**
1 point for each:
- Page demonstrates genuine technical depth (architecture details, type names, code flow)
- Social proof elements are real (no fabrication, no invented metrics)

### Score tiers (90-point scale)

- **78-90:** Top-tier feature page. No further action.
- **60-77:** Acceptable. Rewrite opportunities exist but page is not broken.
- **Below 60:** Failing. Priority candidate for rewrite.

When analytics expand the scale to 115:
- **100-115:** Top-tier. No further action.
- **80-99:** Acceptable.
- **Below 80:** Failing.

---

## Phase 3 -- Verify and Commit

After rewriting:

1. **Re-run the 11-section audit.** Sections 2 (claim verification), 3 (conversion clarity), 10 (CTA effectiveness), and 11 (Technical-Marketing Synthesis) must all pass. Other sections must be no worse than the baseline from Phase 1. If Section 11 still fails on re-audit, abort and roll back the YAML; report the specific sub-checks that could not be satisfied.
2. **Diff the YAML file.** If diff is empty or trivially whitespace-only, abort with `no_material_change`. Never commit a no-op.
3. **Recompute the score.** If `post_score < pre_score`, abort and roll back. This is a bug in the rules, not an improvement. Report the regression.
4. **Reference spot-check.** Pick 3 random references from the updated YAML. Verify each file exists and the line anchor is accurate. If any fail, abort.
5. **Schema validation.** Verify the YAML is valid and the renderer-expected keys are intact. Parse with a YAML parser. A syntax error means abort.
6. **Commit** with the structured message format below.
7. **Write the structured per-feature artifact report** to `reports/content/artifacts/optimiser/YYYY-MM-DD/{slug}.md`.
8. **Update the canonical feature report** at `reports/content/features/{slug}/feature-report.md`:
   - Append Action Log entry: date, "Optimised", "feature-optimiser", "Score {pre} -> {post}", link to artifact report, commit SHA
   - Update "Current Scores > Optimiser Score" with the new score breakdown table
   - Update "Current Scores > Revision Audit" with the Phase 1 section results
   - Update "Reference Verification Log" with the current reference inventory
   - Update Section 7 (metadata rationale) if headline/description/keywords were changed

### Commit message format

```
optimise feature/{slug}: {pre_score} -> {post_score} (scale 90)

- refs verified: {verified}/{total} ({dead_removed} dead removed, {anchors_updated} anchors updated)
- adjectives removed: {count}
- cliches removed: {count}
- cta: "{before}" -> "{after}"
- hero: headline {word_count} words, subheadline {word_count} words
- rule 6 sub-checks: {passing}/6 ({fail_list}, e.g. 6a,6c resolved)
- rule 6 rewrites: {headline_changed}, {jargon_decoded} decoders added, {numbers_contexted} numbers contexted, {bullets_bound} bullets bound, {refs_separated} identifiers moved to references
- gsc baseline: {impressions_28d} imp, {ctr}% CTR, position {position}
```

---

## Per-Feature Report Template

When a feature report does not exist, create it at `reports/content/features/{slug}/feature-report.md` using the following template. Populate what you can from keyword-targets.json and the feature's current YAML content:

```markdown
# Feature Report: {headline}

**Slug:** {slug}
**Path:** services/web/config/features/{slug}.yaml
**Created:** {YYYY-MM-DD}
**Last updated:** {YYYY-MM-DD}
**Primary keyword:** {keyword} (volume: {N}, difficulty: {N}, intent: {type})
**Status:** draft | published | needs-revision | optimised

## 1. Search Intent Analysis

### Who visits feature pages and why?
- **Primary intent:** {informational|commercial|navigational|transactional}
- **User profile:** {who is this person, what role, what problem brought them here}
- **What they need:** {the specific answer or outcome, e.g. "proof that this handles compliance at scale"}
- **Evidence:** {how we know: GSC queries, keyword intent data, referral sources}

### How have we addressed their intent?
- **Core value delivered:** {what the feature page gives them}
- **Unique perspective:** {what our page shows that competitors do not}
- **Evidence quality:** {are claims code-backed? are references verified?}
- **Trust signals:** {source code links, architecture details, real implementation}
- **Intent resolution verdict:** RESOLVED | PARTIALLY RESOLVED | NOT RESOLVED

### Keyword Map
| Keyword | Volume | Difficulty | Classification | Source | Status |
|---------|-------:|----------:|---------------|--------|--------|

## 2. Reference Verification Log

Every claim on this feature page must be traceable to source code. This section is the audit trail.

| Section | Reference Path | Exists? | Lines Accurate? | Prose Matches Code? | Last Verified |
|---------|---------------|:-------:|:---------------:|:-------------------:|:-------------:|

Rule: every reference is verified on every optimiser run. No stale entries.

## 3. Competitor Page Audit

| URL | Word count | Technical depth | Code references? | Strengths | Gaps we exploit |
|-----|----------:|:--------------:|:----------------:|-----------|----------------|

### Our Differentiation
{What this feature page exposes that competitor pages hide or cannot show}

## 4. Conversion Data Baseline

| Metric | Value | Date | Source |
|--------|------:|:----:|--------|
| Page views (28d) | | | Analytics |
| Bounce rate | | | Analytics |
| Avg time on page | | | Analytics |
| CTA click-through | | | Analytics |
| GSC impressions (28d) | | | GSC |
| GSC clicks (28d) | | | GSC |
| GSC CTR | | | GSC |
| GSC avg position | | | GSC |

## 5. Action Log

Every action on this feature page is recorded here. This is the audit trail. It must be complete.

| Date | Action | Skill | Details | Artifact Report | Commit |
|------|--------|-------|---------|----------------|--------|

Rules:
- Every skill run on this feature MUST append a row here
- Artifact reports are linked using relative paths
- Commit SHAs link to the actual code change
- This log is append-only. Rows are never edited or removed.

## 6. Current Scores

### Optimiser Score: pending/90

| Dimension | Score | Max |
|-----------|------:|----:|
| Why-What-How compliance | | 15 |
| Claim verification | | 15 |
| Technical-marketing synthesis | | 15 |
| Conversion clarity | | 10 |
| Technical accuracy | | 10 |
| Brand/voice compliance | | 8 |
| Competitive positioning | | 5 |
| Visual hierarchy | | 5 |
| SEO metadata | | 5 |
| Enterprise credibility | | 2 |

### Revision Audit: pending/11 sections passing

## 7. Title, Description and Keywords Rationale

### Current Headline
- **Value:** "{headline} {headline_highlight}"
- **Primary keyword:** {keyword} (volume: {N}, source: keyword-targets.json, date: {YYYY-MM-DD})
- **Rationale:** {why this headline was chosen}
- **Last changed:** {YYYY-MM-DD} by {skill}

### Current Description
- **Value:** "{description}"
- **Rationale:** {why this description, what search intent it addresses}
- **Last changed:** {YYYY-MM-DD} by {skill}

### Current Keywords
- **Value:** "{keywords}"
- **Rationale:** {each keyword justified by volume/difficulty data}
- **Last changed:** {YYYY-MM-DD} by {skill}

Rule: headline, description, and keywords must NOT be changed without GSC or keyword data justifying the change.

## 8. GSC Performance History

| Date | 28d Impressions | 28d Clicks | CTR | Avg Position |
|------|----------------:|-----------:|----:|-------------:|
```

---

## Output Format

Per-feature artifact report template:

```markdown
# Feature Optimiser Report: {headline}

**Feature:** `{path}`
**Slug:** `{slug}`
**Audited:** {YYYY-MM-DD}
**Mode:** optimise
**Commit:** {sha}

## Score: {post}/90 (was {pre}/90, {delta:+d})

| Dimension | Before | After | Max |
|-----------|-------:|------:|----:|
| Why-What-How compliance | {} | {} | 15 |
| Claim verification | {} | {} | 15 |
| Technical-marketing synthesis | {} | {} | 15 |
| Conversion clarity | {} | {} | 10 |
| Technical accuracy | {} | {} | 10 |
| Brand/voice compliance | {} | {} | 8 |
| Competitive positioning | {} | {} | 5 |
| Visual hierarchy | {} | {} | 5 |
| SEO metadata | {} | {} | 5 |
| Enterprise credibility | {} | {} | 2 |

## Rule 6 Sub-checks (Technical-Marketing Synthesis)

| Sub-check | Before | After | Rewrites applied |
|-----------|:------:|:-----:|-----------------|
| 6a Outcome Headlines | PASS/FAIL | PASS/FAIL | {headline change summary} |
| 6b Jargon Payoff | PASS/FAIL | PASS/FAIL | {decoders added} |
| 6c Numbers with Context | PASS/FAIL | PASS/FAIL | {numbers contexted} |
| 6d Feature-to-Outcome Binding | PASS/FAIL | PASS/FAIL | {bullets bound} |
| 6e Narrative-vs-Reference Separation | PASS/FAIL | PASS/FAIL | {identifiers moved} |
| 6f Skeptic's So What | PASS/FAIL | PASS/FAIL | {audience answers added} |

Sub-checks passing: {before_passing}/6 -> {after_passing}/6

## GSC Baseline

- 28-day impressions: {}
- 28-day clicks: {}
- 28-day CTR: {}%
- Avg position: {}

## Reference Verification

| Section | Reference | Exists? | Lines correct? | Prose accurate? | Action taken |
|---------|-----------|:-------:|:--------------:|:---------------:|-------------|

- Total references: {n}
- Verified: {n}
- Dead removed: {n}
- Anchors updated: {n}
- Added: {n}

## Adjective and Cliche Removal

| Line | Original | Replacement | Rule |
|-----:|----------|------------|------|

- Adjectives removed: {n}
- Cliches removed: {n}
- Em dashes replaced: {n}

## CTA Changes

**Primary CTA:**
- Before: "{}"
- After: "{}"

**Hero formula:**
- Headline: {word_count} words (target: 6-10)
- Subheadline: {word_count} words (target: 15-25)
- CTA count: {n} (target: 1)

## Why-What-How Rewrites

| Section | Had Why? | Had What? | Had How? | Action taken |
|---------|:--------:|:---------:|:--------:|-------------|

## SEO Metadata

**Title (headline + highlight):**
- Before: "{}" ({N} chars)
- After: "{}" ({N} chars)

**Description:**
- Before: "{}" ({N} chars)
- After: "{}" ({N} chars)

## Audit Results (Phase 1)

| Section | Result | Notes |
|---------|:------:|-------|
| 1. Why-What-How | PASS/FAIL | |
| 2. Claim verification | PASS/FAIL | |
| 3. Conversion clarity | PASS/FAIL | |
| 3R. Register ladder (hero jargon, homepage echo, struggling-moment opener, identifier enumeration, established voice) | PASS/FAIL | |
| 4. Technical accuracy | PASS/FAIL | |
| 5. Brand/voice | PASS/FAIL | |
| 6. Competitive positioning | PASS/FAIL | |
| 7. Visual hierarchy | PASS/FAIL | |
| 8. SEO metadata | PASS/FAIL | |
| 9. Enterprise credibility | PASS/FAIL | |
| 10. CTA effectiveness | PASS/FAIL | CRITICAL (fails audit on its own) |
| 11. Technical-marketing synthesis | PASS/FAIL | CRITICAL (fails audit if 3+ of 6a-6f fail) |

## Verification

- Schema valid: PASS | FAIL
- References spot-checked: PASS | FAIL
- Score improved: PASS | FAIL
- Critical sections (2, 3, 10, 11) pass: PASS | FAIL
- YAML parseable: PASS | FAIL
- Feature report updated: PASS | FAIL
```

---

## Schema Preservation Rules

Feature YAML files have a strict schema that the renderer depends on. Changing structural keys breaks the website.

### Allowed edit fields

These fields contain copy and can be rewritten:

- `headline` -- the main page title (H1 equivalent)
- `headline_highlight` -- the highlighted portion of the headline
- `subtitle` -- hero subheadline
- `description` -- meta description for SEO
- `keywords` -- keyword list for SEO
- `sections[].content` -- section body text
- `items[].title` -- item heading within a section
- `items[].description` -- item body text within a section
- `references[]` -- code references (path and line anchors can be updated)
- `cta.description` -- CTA body text
- `cta.heading` -- CTA headline

### Forbidden fields (never change)

These fields are structural. Changing them breaks routing, rendering, or external links:

- `slug` -- URL path component, referenced externally
- `icon` -- icon identifier for the renderer
- `hero_diagram` -- diagram configuration for the hero section
- `sections[].id` -- section identifier used for anchor links
- `related[]` -- related feature links (managed separately)

If a forbidden field contains a problem (e.g. a broken `hero_diagram`), report it in the artifact but do not modify it. File an engineering task instead.

---

## Anti-sludge Rules

- Every recommendation and action ties to a specific reference, a specific section in the YAML, or a specific query from GSC.
- No generic praise. No "this improves credibility." Say which section, which reference, which metric, and why.
- No em dashes in the report.
- No AI cliches in the report.
- The report is an audit trail, not marketing. It exists so a future reviewer can reproduce or reverse the rewrite.
- Every score has a formula. No "I gave it a 7 because it felt right."

## When NOT to Use This Skill

- Pages outside `/features/`. For guides use `guide-optimiser`. For documentation pages use `documentation-optimiser`.
- Feature pages that are not yet published (no YAML file exists). Use `feature-writer` to create first, then optimise.
- Structural changes to the feature YAML schema. That is engineering work, not copy optimisation.
