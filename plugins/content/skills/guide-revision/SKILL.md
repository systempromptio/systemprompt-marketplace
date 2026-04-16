---
name: guide-revision
description: "Deterministic quality audit for published guides. 14-section checklist covering facts, links, code, structure, SEO, brand, external resources, visual assets, FAQ keyword validation, topic research evidence, metadata rationale, and search intent resolution (critical override). Load identity first."
metadata:
  version: "2.0.0"
  git_hash: "c24c577"
---

# Guide Revision Audit

Run a deterministic quality audit on a published guide. Every check is binary (pass/fail) with specific criteria. Output a structured report with exact line references and fixes.

**Critical rule:** Section 14 (Search Intent Resolution) is a critical override. If Section 14 fails, the entire audit fails regardless of how many other sections pass. A guide that does not resolve the searcher's intent has no value, regardless of how well it scores on technical criteria.

## Dependencies

**Load `identity` before this skill.** The identity skill provides positioning context, keyword targets, and messaging hierarchy needed to evaluate SEO alignment and brand compliance.

## Source of Truth

Read these before starting:

- `/var/www/html/systemprompt-web/reports/seo/seo-strategy-master.md` — pillar health, objectives, cluster map, interlinking strategy
- `/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json` — keyword assignments, volumes, difficulty, target positions
- `/var/www/html/systemprompt-web/reports/content/guides/{slug}/guide-report.md` — the per-guide report (search intent analysis, FAQ mappings, external resources, asset inventory, action log, metadata rationale). If this file does not exist, create it from the template in the "Per-Guide Report" section below before proceeding. Populate with whatever data is available from keyword-targets.json.

## How to Use

1. Identify the guide to audit (provide the file path or slug)
2. Read the full guide content
3. Read the per-guide report (or create it if missing)
4. Read the SEO Strategy Master for cluster and interlinking context
5. Run each of the 14 audit sections below
6. Generate the structured report
7. Save to `reports/content/artifacts/revision/YYYY-MM-DD/guide-revision-{slug}.md`
8. Update the per-guide report: append action log entry and update current scores

## Audit Sections

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
- [ ] Description tells the reader what they will be able to DO, not just what the article covers
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

Generate a structured markdown report with the following format:

```markdown
# Guide Revision Report: {guide title}

**Guide:** `{file path}`
**Audited:** {YYYY-MM-DD}
**Overall Score:** {N}/14 sections passing
**Critical Override (Section 14):** PASS/FAIL

## Guide Report Status

- Guide report exists: YES/NO
- Guide report path: `reports/content/guides/{slug}/guide-report.md`
- Guide report last updated: {date}
- Action logged: YES/NO

## Summary

Top 3 critical issues to fix first:
1. {issue with section reference}
2. {issue with section reference}
3. {issue with section reference}

## Section 1: Frontmatter Completeness - {PASS/FAIL}

| Check | Result | Details |
|-------|--------|---------|
| title under 60 chars | PASS/FAIL | {current length or issue} |
| ... | ... | ... |

{For each failing check, include the exact line number and a specific fix.}

## Section 2: Claim Verification - {PASS/FAIL}

{List each claim found, its line number, and whether it passes or fails.}

... (repeat for all 14 sections)
```

Save the report to `reports/content/artifacts/revision/YYYY-MM-DD/guide-revision-{slug}.md`.

A section passes only if ALL checks within it pass.

## Post-Audit: Update Guide Report

After generating the audit report:

1. **Update the per-guide report** at `reports/content/guides/{slug}/guide-report.md`:
   - Append an Action Log entry: date, "Revised", "guide-revision", "{N}/14 sections passing", link to artifact report, no hypothesis, no commit (audit-only)
   - Update "Current Scores > Revision Audit" with the new section results
2. Save the detailed audit artifact to `reports/content/artifacts/revision/YYYY-MM-DD/guide-revision-{slug}.md` (existing behaviour)
