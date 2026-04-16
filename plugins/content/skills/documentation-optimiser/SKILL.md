---
name: documentation-optimiser
description: "Deterministically audit and optimise a published documentation page. Runs a 10-section quality audit, applies 5 rewrite rules for structure, terminology, link health, and completeness. Reads website analytics and GSC data per doc URL, produces a 75-point score delta (100 with analytics), commits changes, and updates the per-doc report. Load identity and brand-voice first."
metadata:
  version: "1.0.0"
  git_hash: "0000000"
---

# Documentation Optimiser

Run a **deterministic, data-driven audit and rewrite** on a single published documentation page. This skill is the complete lifecycle tool for documentation quality: audit, fix, score, commit, log. Every decision is grounded in a quantitative rule or a measurable signal. No vibes, no "use your judgement" gaps.

**Critical rule:** Section 10 (Search Appearance and Discoverability) is a critical override. If Section 10 fails, the entire audit fails regardless of how many other sections pass. Documentation that cannot be found has no value, regardless of how well it scores on technical criteria.

## Dependencies

**Load `identity` and `brand-voice` before this skill.**

- `identity` -- positioning, ICP, messaging hierarchy, what the brand actually stands for
- `brand-voice` -- the cliche list, terminology rules, em-dash ban, and voice targets

## Source of Truth

Read these before starting:

- The documentation page itself at `/var/www/html/systemprompt-web/services/content/documentation/{slug}/index.md`
- All pages linked from this doc (verify they exist on disk or resolve via HTTP)
- `/var/www/html/systemprompt-web/reports/content/documentation/{slug}/doc-report.md` -- the per-doc report (accuracy log, link health, terminology compliance, action log, current scores). If this file does not exist, create it from the template in the "Per-Doc Report Template" section below before proceeding. Populate with available data from the documentation page and any GSC data pulled in Phase 0.

## Inputs

Caller must provide:
- **Documentation slug** (e.g. `getting-started`), OR the absolute path to the doc's `index.md`

## Phases

The skill runs sequentially: **0 -> 1 -> 2 -> 2.5 -> 3**. Do not skip. If any phase aborts, exit cleanly without committing.

---

## Phase 0 -- Data Ingestion

Pull Google Search Console query data, run automated checks, and build the working set.

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

### Query for the doc's top 100 queries (28d)

```bash
TOKEN=$(cat /tmp/gsc_token)
SLUG=<slug>
START=$(date -d '28 days ago' +%Y-%m-%d)
END=$(date -d 'yesterday' +%Y-%m-%d)
mkdir -p /tmp/gsc-doc-queries

curl -s -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Asystemprompt.io/searchAnalytics/query" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{
    \"startDate\": \"$START\",
    \"endDate\": \"$END\",
    \"dimensions\": [\"query\"],
    \"dimensionFilterGroups\": [{
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/documentation/$SLUG\"}]
    }],
    \"rowLimit\": 100
  }" > /tmp/gsc-doc-queries/$SLUG.json
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
      \"filters\": [{\"dimension\": \"page\", \"operator\": \"contains\", \"expression\": \"/documentation/$SLUG\"}]
    }],
    \"rowLimit\": 10
  }" > /tmp/gsc-doc-queries/$SLUG.page.json
```

Cache both files. If the doc has no rows, record `no_gsc_data: true` and proceed. Content rules still apply.

### Automated Link Health Check

For every internal and external link in the documentation page:

1. **Internal links:** Verify the target file exists on disk. Check that the path resolves to a real page under `/var/www/html/systemprompt-web/`.
2. **External links:** Issue an HTTP HEAD request. Record status code. Flag 4xx and 5xx as broken.
3. Record results in `link_inventory` with columns: `url`, `type` (internal/external), `anchor_text`, `status`, `line_number`.

### Terminology Scan

Scan the entire document against the terminology table:

| Incorrect | Correct |
|-----------|---------|
| prompt, template, instruction set | Skill |
| bot, assistant, AI helper | Agent |
| app, extension, add-on, package | Plugin |
| integration, bridge, adapter | Connector |
| API, service, endpoint (when referring to MCP) | MCP server |
| AI management, AI administration | AI governance |

Record each violation with line number, incorrect term, and correct replacement in `terminology_violations`.

### Build Working Set

Assemble the following data structures in memory:

- `page_metrics`: `{impressions, clicks, ctr, position}` from the page aggregate (or `no_gsc_data: true`)
- `top_queries`: sorted by impressions, filter `impressions >= 20` (signal floor)
- `link_inventory`: every link in the doc with type, status, anchor text, line number
- `terminology_violations`: every terminology violation with line number, incorrect term, correct term

### Initialise Doc Report

Read the per-doc report at `reports/content/documentation/{slug}/doc-report.md`. If it does not exist, create it from the template (see "Per-Doc Report Template" section below) and populate with:
- GSC data just pulled (impressions, clicks, CTR, position)
- Link inventory from the health check
- Terminology violations found
- Any existing metadata extractable from the doc's current content

This ensures every optimiser run has a doc report to work with, even for documentation created before this skill existed.

---

## Phase 1 -- 10-Section Audit

Run the full 10-section checklist against the target documentation page. Record pass/fail per check. This phase writes nothing to disk. It produces a dict held in memory for Phase 2.5 scoring.

When Phase 1 produces a failing check, Phase 2 is responsible for fixing it only where the fix is covered by the rewrite rules below. Out-of-scope failures (e.g. broken external links pointing to third-party 404s) are reported but not auto-fixed.

### Section 1: Structure Adherence

- [ ] Breadcrumb navigation present
- [ ] Exactly one H1 (page title, clear and descriptive)
- [ ] Introduction paragraph present (2-3 sentences: what and why)
- [ ] "After Reading This" / learning outcomes present (3-5 bullet points)
- [ ] Prerequisites listed (or explicitly "none")
- [ ] Main content uses H2 sections with progressive complexity
- [ ] Code/configuration examples present where relevant
- [ ] Troubleshooting section present with common issues
- [ ] Related pages / next steps section present with cross-links
- [ ] Heading hierarchy strictly H1 > H2 > H3 (no H4+, no skipped levels)
- [ ] H2 headings are action-oriented ("Creating a Skill" not "Skill Creation")
- [ ] All headings use sentence case

### Section 2: Accuracy

- [ ] All CLI commands correct and produce described output
- [ ] All configuration examples valid syntax (YAML, JSON, TOML)
- [ ] All API endpoints and parameters current
- [ ] Version numbers and compatibility claims accurate
- [ ] No references to deprecated features or removed pages
- [ ] Code examples complete and runnable (not fragments)
- [ ] Prerequisites stated (language version, dependencies, tools)
- [ ] File paths realistic and consistent

### Section 3: Completeness

- [ ] Introduction clearly states what page covers and why it matters
- [ ] Learning outcomes specific and measurable (not "understand X" but "configure X to do Y")
- [ ] Every step in procedure included (no gaps)
- [ ] Every configuration field documented (type, required/optional, default, description)
- [ ] Error scenarios and failure modes addressed
- [ ] Edge cases documented where relevant
- [ ] Reader can accomplish stated goal without external help

### Section 4: Terminology Compliance

- [ ] "Skill" not "prompt", "template", "instruction set"
- [ ] "Agent" not "bot", "assistant", "AI helper"
- [ ] "Plugin" not "app", "extension", "add-on", "package"
- [ ] "Connector" not "integration", "bridge", "adapter"
- [ ] "MCP server" not "API", "service", "endpoint" (when referring to MCP)
- [ ] "AI governance" not "AI management", "AI administration"
- [ ] No marketing language in documentation (no persuasion, no benefit-selling)

### Section 5: Link Health

- [ ] All internal links resolve to existing pages (no 404s)
- [ ] All external links current and accessible
- [ ] Anchor text descriptive (not "click here" or bare URLs)
- [ ] Cross-links to related documentation pages present
- [ ] No links to placeholder or example domains
- [ ] Breadcrumb links correct

### Section 6: Code Example Validity

- [ ] Every code block specifies a language identifier
- [ ] YAML examples syntactically valid
- [ ] JSON examples syntactically valid
- [ ] Bash/CLI commands correct for stated tool version
- [ ] Configuration examples include comments explaining non-obvious fields
- [ ] No placeholder values that look real (fake API keys, URLs)
- [ ] OS-specific commands note alternatives where they differ

### Section 7: Prerequisite Clarity

- [ ] Prerequisites listed at top, before procedural content
- [ ] Each prerequisite specific (version numbers, tools, permissions)
- [ ] Prerequisites distinguish "must have" vs "recommended"
- [ ] Links to prerequisite setup instructions where they exist
- [ ] Assumed knowledge level stated

### Section 8: Troubleshooting Coverage

- [ ] Troubleshooting section exists (or justified as unnecessary for reference-only pages)
- [ ] Each item follows Symptom / Cause / Solution format
- [ ] Common failure modes from the feature's domain covered
- [ ] Error messages quoted exactly as user would see them
- [ ] Solutions specific and actionable (not "check your configuration")

### Section 9: Learning Outcomes Quality

- [ ] 3-5 learning outcomes present
- [ ] Each outcome specific and measurable
- [ ] Each achievable by following page's content
- [ ] Outcomes use action verbs ("Configure X", "Deploy Y", "Diagnose Z"), not passive ("Understand X")
- [ ] Outcomes align with documented search intent

### Section 10: Search Appearance and Discoverability (CRITICAL OVERRIDE)

**If Section 10 fails, the entire audit result is FAIL regardless of how many other sections pass.** Documentation that cannot be found has no value, regardless of how well it scores on technical criteria.

- [ ] **Title is discoverable:** H1 contains terms users would search for
- [ ] **Meta description exists:** under 160 chars, tells reader what they will learn to DO
- [ ] **Frontmatter keywords present:** mapping to real search terms
- [ ] **Quick answer:** Page answers title's implied question within first 300 words
- [ ] **Internal search findability:** Title and intro contain vocabulary users would use (including common incorrect terms as context, e.g. mentioning "API" in a paragraph about MCP servers so searches for "API" still find the page)

---

## Phase 2 -- Deterministic Rewrite

Five hard rules. Each is mechanically enforceable.

**Handling docs without GSC data:** When `no_gsc_data: true`, all five rules still apply. Unlike guides, documentation rewrites do not depend on search traffic data. GSC data enhances scoring but does not gate rewrites.

### Rule 1 -- Structure Enforcement

Add missing structural sections. Fix heading hierarchy. Convert headings to action-oriented form.

**Missing sections:** For each required section from the Section 1 audit that is absent, add it:
- **Introduction:** 2-3 sentences stating what the page covers and why the reader needs it. No preamble, no "welcome to" language.
- **Learning outcomes:** 3-5 bullet points. Each starts with an action verb ("Configure", "Deploy", "Diagnose"). Each is specific and measurable. Each is achievable by following the page's content.
- **Prerequisites:** List every tool, version, permission, and dependency required. If none, state "None" explicitly. Distinguish "must have" from "recommended".
- **Troubleshooting:** Minimum 3 items in Symptom / Cause / Solution format. Source symptoms from the feature's known failure modes, error messages in the codebase, and GSC error-style queries if available.
- **Related pages / next steps:** Minimum 3 cross-links to other documentation pages. Use descriptive anchor text.

**Heading hierarchy fix:**
- Demote any heading that skips a level (H1 followed by H3 becomes H1 > H2 > H3)
- Promote any heading that is deeper than H3 (H4+ becomes H3)
- No skipped levels anywhere in the document

**Action-oriented headings:**
- Convert noun-phrase headings to action-oriented form: "Skill Creation" becomes "Creating a Skill", "Configuration" becomes "Configuring the Plugin", "Authentication" becomes "Authenticating with the API"
- Exception: pure reference headings that name a thing ("CLI Commands", "Environment Variables") are acceptable

**Sentence case enforcement:**
- All headings use sentence case ("Getting started with plugins" not "Getting Started With Plugins")
- Exception: proper nouns retain capitalisation ("Configuring Claude Code" not "Configuring claude code")

### Rule 2 -- Terminology Correction

Automated find-and-replace for all terminology violations identified in Phase 0. Fully mechanical. No judgement required.

| Incorrect term | Correct term | Context |
|---------------|-------------|---------|
| prompt | Skill | When referring to a systemprompt skill file |
| template | Skill | When referring to a systemprompt skill file |
| instruction set | Skill | When referring to a systemprompt skill file |
| bot | Agent | When referring to an AI agent |
| assistant | Agent | When referring to an AI agent (not Claude assistant) |
| AI helper | Agent | When referring to an AI agent |
| app | Plugin | When referring to a systemprompt plugin |
| extension | Plugin | When referring to a systemprompt plugin (not VS Code extensions) |
| add-on | Plugin | When referring to a systemprompt plugin |
| package | Plugin | When referring to a systemprompt plugin (not npm/cargo packages) |
| integration | Connector | When referring to a systemprompt connector |
| bridge | Connector | When referring to a systemprompt connector |
| adapter | Connector | When referring to a systemprompt connector |
| API | MCP server | When referring to a Model Context Protocol server |
| service | MCP server | When referring to a Model Context Protocol server (not cloud services generally) |
| endpoint | MCP server | When referring to a Model Context Protocol server (not HTTP endpoints generally) |
| AI management | AI governance | Always |
| AI administration | AI governance | Always |

**Context sensitivity:** The "Context" column is critical. "API" is only replaced when it refers to an MCP server, not when discussing REST APIs generally. "Extension" is only replaced when it refers to a systemprompt plugin, not VS Code extensions. Apply the replacement only when the context matches.

**Process:**
1. For each violation in `terminology_violations` from Phase 0, apply the replacement.
2. Re-scan after replacement to catch any cascading issues (e.g. "the prompt template" becoming "the Skill Skill").
3. Record every replacement in the artifact report with line number, before, and after.

### Rule 3 -- Link Repair

Fix broken and substandard links identified in Phase 0.

**Broken internal links:**
- If the target page has moved, update the link to the new path
- If the target page has been deleted and the link is non-essential, remove the link and inline any critical context that was being delegated
- If the target page has been deleted and the link is essential, flag `needs_content_review: true` and note the missing dependency

**Broken external links:**
- If a permanent redirect (301) exists, update to the final URL
- If the page is gone (404, 410), remove the link. If the link supported a claim, flag the claim for re-sourcing
- Do not silently remove links that substantiate technical claims

**Anchor text fixes:**
- Replace "click here" with descriptive text: "click here for the CLI reference" becomes "the CLI reference"
- Replace bare URLs with descriptive anchor text
- Ensure every anchor text describes what the reader will find at the destination

**Cross-link additions:**
- If the doc references a concept that has its own documentation page, add a link
- Minimum 3 internal cross-links per documentation page
- Use relative paths for internal links (`/documentation/{slug}`)

### Rule 4 -- Code Example Validation

Fix code examples identified as problematic in Phase 1 Sections 2 and 6.

**Language identifiers:**
- Every fenced code block must specify a language: ```yaml, ```json, ```bash, ```rust, ```toml, etc.
- If the language is ambiguous, infer from content (YAML has colons and indentation, JSON has braces, TOML has brackets and equals signs)

**Syntax validation:**
- YAML: parse with a YAML parser or verify structure manually (consistent indentation, valid key-value pairs, no tabs)
- JSON: verify balanced braces, proper quoting, no trailing commas
- Bash: verify command exists and flags are valid for the stated tool version
- TOML: verify section headers and key-value syntax

**Explanatory comments:**
- Add comments to configuration examples explaining non-obvious fields
- Comments should explain WHY, not WHAT (not `# set the port` but `# default 8080, must match reverse proxy config`)

**OS-specific alternatives:**
- If a command differs across macOS, Linux, and Windows, note the alternatives
- At minimum, note when a command is Linux/macOS-only

**Placeholder cleanup:**
- Replace fake API keys (`sk-abc123`) with clearly marked placeholders (`YOUR_API_KEY_HERE`)
- Replace fake URLs with `example.com` domain or clearly marked placeholders
- Never leave a value that could be mistaken for a real credential

### Rule 5 -- Completeness Gap Fill

Fill gaps identified in Phase 1 Section 3.

**Missing learning outcomes:**
- Add 3-5 outcomes if absent
- Each starts with an action verb
- Each is specific: "Configure a plugin manifest with required fields and optional metadata" not "Understand plugins"
- Each is achievable by following the page's content

**Missing troubleshooting items:**
- Add minimum 3 items in Symptom / Cause / Solution format
- Source symptoms from: the feature's error messages in the codebase, common user mistakes for this type of configuration, GSC error-style queries if available
- Each solution must be specific and actionable: "Add `version: 2` to the manifest header" not "Check your configuration"

**Incomplete procedures:**
- If a procedure has gaps (e.g. "create the file" without showing the file content), fill them
- Every step must be complete enough that the reader can execute it without guessing

**SME review flag:**
- If a gap cannot be filled without domain expertise (e.g. undocumented API behaviour, unclear error conditions), flag the specific item as `needs_sme_review: true` in the report
- Do NOT invent technical details. Flag and move on.

---

## Phase 2.5 -- Scoring

Every documentation page gets a **75-point score** (expandable to 100 when analytics are available). Compute both pre- and post-rewrite. The delta is the proof of work.

### Rubric (75-point base)

| Dimension | Max | Formula |
|-----------|----:|---------|
| Structure adherence | 15 | `round(15 * (passing_checks / 12))` (12 checks in Section 1) |
| Accuracy | 15 | `round(15 * (valid_items / total_items))` from Sections 2 + 6 |
| Completeness | 10 | `round(10 * (passing_checks / 7))` (7 checks in Section 3) |
| Terminology compliance | 8 | `max(0, 8 - violation_count)` |
| Link health | 8 | `round(8 * (healthy_links / total_links))` |
| Prerequisite clarity | 5 | 1 point per passing check in Section 7 (5 checks) |
| Troubleshooting coverage | 5 | 1 point per passing check in Section 8 (5 checks, max 5) |
| Learning outcomes quality | 5 | 1 point per passing check in Section 9 (5 checks) |
| Search appearance | 4 | 1 point per passing check in Section 10 (excluding the critical override, 4 remaining checks) |

### Analytics expansion (100-point scale)

When website analytics and GSC data are available, add:

| Dimension | Max | Formula |
|-----------|----:|---------|
| Page engagement | 15 | Based on bounce rate + time-on-page. `score = round(15 * (1 - bounce_rate) * min(1, avg_time_seconds / 180))`. 3+ minutes with low bounce = 15. High bounce or < 30s = 0-3. |
| Search traffic | 10 | Based on GSC impressions. `score = min(10, round(2 * log10(max(impressions_28d, 1))))`. 1 imp = 0, 100 = 4, 1k = 6, 10k = 8, 100k = 10. |

When analytics are not available, max score is 75 and these two dimensions are marked `N/A`.

### Score tiers

- **65-75:** Top-tier documentation (or 85-100 with analytics). No further action.
- **50-64:** Acceptable (or 70-84 with analytics). Rewrite opportunities exist but doc is functional.
- **Below 50:** Failing (or below 70 with analytics). Priority candidate for rewrite.

### Deterministic scoring detail

**Structure adherence (15 max):**
```
checks = [breadcrumb, single_h1, intro_paragraph, learning_outcomes, prerequisites,
          h2_progressive, code_examples, troubleshooting, related_pages,
          heading_hierarchy, action_headings, sentence_case]
score = round(15 * (sum(checks) / 12))
```

**Accuracy (15 max):**
```
items = cli_commands + config_examples + api_endpoints + version_claims +
        deprecation_refs + code_completeness + prerequisites + file_paths
score = round(15 * (valid_items / max(total_items, 1)))
```
Count every verifiable item in the doc. Each is valid or invalid.

**Completeness (10 max):**
```
checks = [intro_states_coverage, outcomes_measurable, no_procedure_gaps,
          fields_documented, errors_addressed, edge_cases, self_sufficient]
score = round(10 * (sum(checks) / 7))
```

**Terminology compliance (8 max):**
```
score = max(0, 8 - violation_count)
```
Each violation subtracts 1 point. 8+ violations = 0.

**Link health (8 max):**
```
score = round(8 * (healthy_links / max(total_links, 1)))
```
A link is "healthy" if it resolves (internal: file exists, external: 2xx or 3xx status).

**Prerequisite clarity (5 max):**
```
checks = [listed_at_top, each_specific, must_vs_recommended, links_to_setup, knowledge_level]
score = sum(checks)  # 1 point each, max 5
```

**Troubleshooting coverage (5 max):**
```
checks = [section_exists, symptom_cause_solution, failure_modes, exact_errors, actionable_solutions]
score = sum(checks)  # 1 point each, max 5
```

**Learning outcomes quality (5 max):**
```
checks = [three_to_five_present, specific_measurable, achievable, action_verbs, aligned_intent]
score = sum(checks)  # 1 point each, max 5
```

**Search appearance (4 max):**
```
checks = [title_discoverable, meta_under_160, keywords_present, answers_within_300_words]
score = sum(checks)  # 1 point each, max 4
```
Note: the 5th check (internal search findability) is the critical override and does not contribute to the numeric score. It gates the entire audit.

### Commit message format

```
optimise-doc {slug}: {pre_score} -> {post_score}

- structure: {before}/{12} -> {after}/{12}
- accuracy: {valid}/{total} items verified
- terminology: {violation_count} violations (was {before_count})
- links: {healthy}/{total} healthy (was {before_healthy}/{before_total})
- completeness: {before}/{7} -> {after}/{7}
- sections added: {list}
- sections rewritten: {list}
```

---

## Phase 3 -- Verify and Commit

After rewriting:

1. **Re-run the 10-section audit.** Section 10 must pass (critical override). Other sections must be no worse than the baseline from Phase 1.
2. **Diff the markdown.** If diff is empty or trivially whitespace-only, abort with `no_material_change`. Never commit a no-op.
3. **Recompute the score.** If `post_score < pre_score`, abort and roll back. This is a bug in the rules, not an improvement. Report the regression.
4. **Commit** with the message format above.
5. **Write the structured per-doc artifact report** to `reports/content/artifacts/optimiser/YYYY-MM-DD/{slug}.md`.
6. **Update the canonical doc report** at `reports/content/documentation/{slug}/doc-report.md`:
   - Append Action Log entry: date, "Optimised", "documentation-optimiser", "Score {pre} -> {post}", link to artifact report, commit SHA
   - Update "Current Scores > Optimiser Score" with the new score breakdown table
   - Update "Current Scores > Revision Audit" with the Phase 1 section results
   - Update "Link Health Snapshot" with current link inventory
   - Update "Terminology Compliance Snapshot" with current violation count (should be 0 after Rule 2)
   - Update "Accuracy Verification Log" with any items verified or flagged

---

## Per-Doc Report Template

When a doc report does not exist, create it at `reports/content/documentation/{slug}/doc-report.md` using the following template. Populate what you can from the documentation page and Phase 0 data:

```markdown
# Doc Report: {title}

**Slug:** {slug}
**Path:** services/content/documentation/{slug}/index.md
**URL:** /documentation/{slug}
**Created:** {YYYY-MM-DD}
**Last updated:** {YYYY-MM-DD}
**Primary keyword:** {keyword}
**Status:** draft | published | needs-revision | optimised

## 1. Documentation Purpose and Audience

### What does this page document?
- **Feature/concept:** {what this page covers}
- **Target audience:** {who needs this: developer, admin, decision-maker}
- **Expected outcome:** {what the reader can do after reading}
- **Prerequisites assumed:** {what background knowledge is expected}

## 2. Accuracy Verification Log

Every verifiable claim in this documentation page is tracked here. Each item is verified or flagged on each optimiser run.

| # | Claim/Item | Type | Status | Last verified | Notes |
|---|-----------|------|--------|--------------|-------|

Types: CLI command, config example, API endpoint, version claim, file path, code example.
Status: verified, unverified, flagged, needs-sme-review.

## 3. Link Health Snapshot

| # | URL | Type | Anchor Text | Status | Line | Last checked |
|---|-----|------|------------|--------|------|-------------|

Types: internal, external.
Status: healthy (2xx), redirect (3xx), broken (4xx), error (5xx), not-found (file missing).

## 4. Terminology Compliance Snapshot

| # | Line | Found | Should be | Status |
|---|------|-------|----------|--------|

Status: fixed, outstanding.

After a clean optimiser run, this table should be empty (all violations fixed).

## 5. Action Log

Every action on this documentation page is recorded here. This is the audit trail. It must be complete.

| Date | Action | Skill | Details | Artifact Report | Commit |
|------|--------|-------|---------|----------------|--------|

Rules:
- Every skill run on this doc MUST append a row here
- Artifact reports are linked using relative paths
- Commit SHAs link to the actual code change
- This log is append-only. Rows are never edited or removed.

## 6. Current Scores

### Optimiser Score: pending/75 (or /100 with analytics)

| Dimension | Score | Max |
|-----------|------:|----:|
| Structure adherence | - | 15 |
| Accuracy | - | 15 |
| Completeness | - | 10 |
| Terminology compliance | - | 8 |
| Link health | - | 8 |
| Prerequisite clarity | - | 5 |
| Troubleshooting coverage | - | 5 |
| Learning outcomes quality | - | 5 |
| Search appearance | - | 4 |
| Page engagement | N/A | 15 |
| Search traffic | N/A | 10 |

### Revision Audit: pending/10 sections passing
```

---

## Output Format

Per-doc artifact report template:

```markdown
# Documentation Optimiser Report: {title}

**Doc:** `{path}`
**Slug:** `{slug}`
**URL:** `/documentation/{slug}`
**Audited:** {YYYY-MM-DD}
**Mode:** optimise
**Commit:** {sha}

## Score: {post}/75 (was {pre}/75, {delta:+d})

| Dimension              | Before | After | Max |
|------------------------|-------:|------:|----:|
| Structure adherence    | {}     | {}    | 15  |
| Accuracy               | {}     | {}    | 15  |
| Completeness           | {}     | {}    | 10  |
| Terminology compliance | {}     | {}    | 8   |
| Link health            | {}     | {}    | 8   |
| Prerequisite clarity   | {}     | {}    | 5   |
| Troubleshooting        | {}     | {}    | 5   |
| Learning outcomes      | {}     | {}    | 5   |
| Search appearance      | {}     | {}    | 4   |
| Page engagement        | N/A    | N/A   | 15  |
| Search traffic         | N/A    | N/A   | 10  |

## GSC Baseline

- 28-day impressions: {} (or "no data")
- 28-day clicks: {}
- 28-day CTR: {}%
- Avg position: {}

## Link Health Summary

- Total links: {n}
- Healthy: {n}
- Broken: {n}
- Fixed in this run: {n}
- Broken links:
  1. Line {N}: `{url}` -- {status} -- {action taken}
  2. ...

## Terminology Corrections

- Violations found: {n}
- Violations fixed: {n}
- Corrections:
  1. Line {N}: "{before}" -> "{after}"
  2. ...

## Structure Changes

- Sections added: {list}
- Sections rewritten: {list}
- Headings fixed: {list of heading changes}
- Heading hierarchy violations resolved: {n}

## Code Example Fixes

- Language identifiers added: {n}
- Syntax errors fixed: {n}
- Comments added: {n}
- Placeholder values cleaned: {n}

## Completeness Gap Fills

- Learning outcomes added: {list}
- Troubleshooting items added: {list}
- Procedure gaps filled: {list}
- Items flagged needs_sme_review: {list}

## Audit Results (Phase 1)

| Section | Name | Before | After |
|--------:|------|--------|-------|
| 1 | Structure adherence | {pass/fail} | {pass/fail} |
| 2 | Accuracy | {pass/fail} | {pass/fail} |
| 3 | Completeness | {pass/fail} | {pass/fail} |
| 4 | Terminology compliance | {pass/fail} | {pass/fail} |
| 5 | Link health | {pass/fail} | {pass/fail} |
| 6 | Code example validity | {pass/fail} | {pass/fail} |
| 7 | Prerequisite clarity | {pass/fail} | {pass/fail} |
| 8 | Troubleshooting coverage | {pass/fail} | {pass/fail} |
| 9 | Learning outcomes quality | {pass/fail} | {pass/fail} |
| 10 | Search appearance (CRITICAL) | {pass/fail} | {pass/fail} |

## Verification

- Section 10 passes: PASS | FAIL
- Score improved: PASS | FAIL
- Diff is non-trivial: PASS | FAIL
- No audit regressions: PASS | FAIL
- Doc report updated: PASS | FAIL
```

## Anti-sludge rules

- Every recommendation and action ties to a specific line number or a specific data point.
- No generic praise. No "this improves discoverability." Say WHICH metric and WHY.
- No em dashes in the report.
- No AI cliches in the report.
- The report is an audit trail, not marketing. It exists so a future reviewer can reproduce or reverse the rewrite.

## When NOT to use this skill

- Pages outside `/documentation/`. For guides use `guide-optimiser`. For feature pages use `feature-optimiser`.
- Draft documentation not yet published (`public: false` or missing from the documentation directory).
- Pages that are pure API reference auto-generated from code. Those have their own generation pipeline.
