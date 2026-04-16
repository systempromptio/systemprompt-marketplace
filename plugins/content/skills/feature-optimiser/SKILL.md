---
name: feature-optimiser
description: "Deterministically audit and optimise a published feature page. Runs a 10-section quality audit, applies 5 rewrite rules for claim verification, conversion clarity, and brand discipline. Reads website analytics and GSC data per feature URL, produces a 75-point score delta (100 with analytics), commits changes, and updates the per-feature report. Load identity and brand-voice first."
metadata:
  version: "1.0.0"
  git_hash: "7f3e532"
---

# Feature Optimiser

Run a **deterministic, data-driven audit and rewrite** on a single published feature page. This skill is the complete lifecycle tool for feature page quality: audit, fix, score, commit, log. Every decision is grounded in a quantitative rule, a code reference verification, or a 28-day Google Search Console signal. No vibes, no "use your judgement" gaps.

**Critical rule:** Section 10 (CTA Effectiveness) is a critical override. If Section 10 fails, the entire audit fails regardless of how many other sections pass. A feature page without a clear, effective call to action has no conversion value, regardless of how well it scores on technical criteria.

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

## Phase 1 -- 10-Section Audit

Run the full 10-section checklist against the target feature page. Record pass/fail per check. This phase writes nothing to disk. It produces a dict held in memory for Phase 2.5 scoring.

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
- [ ] Page passes the 10-Second Rule: a CTO landing after a cold email understands "serious AI governance infrastructure" within 10 seconds of scanning the hero and first section
- [ ] No more than one primary CTA per section. Multiple CTAs create decision paralysis.
- [ ] Conversion path clear for all three personas: CTO (enterprise conversation), technical partner (integration discussion), individual developer (activation)

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

---

## Phase 2 -- Deterministic Rewrite

Five hard rules. Each is mechanically enforceable.

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

---

## Phase 2.5 -- Scoring

Every feature page gets a **75-point score** across nine dimensions (expandable to 100 when analytics data is available). Compute both pre- and post-rewrite. The delta is the proof of work.

### Rubric (75-point base)

| Dimension | Max | How to score |
|-----------|----:|-------------|
| Why-What-How compliance | 15 | `round(15 * (passing_sections / total_sections))` |
| Claim verification | 15 | `round(15 * (verified_refs / total_refs))` |
| Conversion clarity | 10 | 2 points each: hero formula, CTA quality, 10-second rule, conversion paths, no dead ends |
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

**Conversion clarity (10 max):**
2 points for each passing criterion:
- Hero follows formula (headline 6-10 words, subheadline 15-25 words, single CTA)
- CTA text uses specific action verbs (not generic "learn more")
- 10-second rule passes (CTO understands the value prop within 10 seconds)
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

### Score tiers (75-point scale)

- **65-75:** Top-tier feature page. No further action.
- **50-64:** Acceptable. Rewrite opportunities exist but page is not broken.
- **Below 50:** Failing. Priority candidate for rewrite.

When analytics expand the scale to 100:
- **85-100:** Top-tier. No further action.
- **70-84:** Acceptable.
- **Below 70:** Failing.

---

## Phase 3 -- Verify and Commit

After rewriting:

1. **Re-run the 10-section audit.** Sections 2, 3, and 10 must pass (claim verification, conversion clarity, CTA effectiveness). Other sections must be no worse than the baseline from Phase 1.
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
optimise feature/{slug}: {pre_score} -> {post_score}

- refs verified: {verified}/{total} ({dead_removed} dead removed, {anchors_updated} anchors updated)
- adjectives removed: {count}
- cliches removed: {count}
- cta: "{before}" -> "{after}"
- hero: headline {word_count} words, subheadline {word_count} words
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

### Optimiser Score: pending/75

| Dimension | Score | Max |
|-----------|------:|----:|
| Why-What-How compliance | | 15 |
| Claim verification | | 15 |
| Conversion clarity | | 10 |
| Technical accuracy | | 10 |
| Brand/voice compliance | | 8 |
| Competitive positioning | | 5 |
| Visual hierarchy | | 5 |
| SEO metadata | | 5 |
| Enterprise credibility | | 2 |

### Revision Audit: pending/10 sections passing

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

## Score: {post}/75 (was {pre}/75, {delta:+d})

| Dimension | Before | After | Max |
|-----------|-------:|------:|----:|
| Why-What-How compliance | {} | {} | 15 |
| Claim verification | {} | {} | 15 |
| Conversion clarity | {} | {} | 10 |
| Technical accuracy | {} | {} | 10 |
| Brand/voice compliance | {} | {} | 8 |
| Competitive positioning | {} | {} | 5 |
| Visual hierarchy | {} | {} | 5 |
| SEO metadata | {} | {} | 5 |
| Enterprise credibility | {} | {} | 2 |

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
| 4. Technical accuracy | PASS/FAIL | |
| 5. Brand/voice | PASS/FAIL | |
| 6. Competitive positioning | PASS/FAIL | |
| 7. Visual hierarchy | PASS/FAIL | |
| 8. SEO metadata | PASS/FAIL | |
| 9. Enterprise credibility | PASS/FAIL | |
| 10. CTA effectiveness | PASS/FAIL | CRITICAL |

## Verification

- Schema valid: PASS | FAIL
- References spot-checked: PASS | FAIL
- Score improved: PASS | FAIL
- Critical sections (2, 3, 10) pass: PASS | FAIL
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
