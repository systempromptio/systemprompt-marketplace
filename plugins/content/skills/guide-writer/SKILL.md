---
name: guide-writer
description: "Write deep, researched long-form technical guides. Data-driven topic research, evidence-backed strategies, long-tail FAQ mapping, 5+ external resources, 2+ homemade visual assets, and per-guide report state management. No brand references in body content."
metadata:
  version: "3.0.2"
  git_hash: "dc0c940"
---

# Guide Writer

Write deep, accurate, long-form technical guides that rank because they deserve to. Every guide must be the best available resource on its topic. No brand mentions in the content body. The content sells itself through quality, depth, and practical value.

Every guide must demonstrate WHY readers can trust it: methodology is stated, sources are cited, evidence is presented throughout. Nothing by guessing. Every decision is backed by keyword data, search intent analysis, or competitive research.

## Dependencies

**Load `identity` first** to understand the topic domain and audience. Do NOT load `brand-voice` — guides must read as independent editorial content, not brand collateral.

## Output Locations

- **Guide:** `/var/www/html/systemprompt-web/services/content/guides/{slug}/index.md`
- **Guide report:** `/var/www/html/systemprompt-web/reports/content/guides/{slug}/guide-report.md`

Both files are committed together. The guide report is the living state document for this guide's lifecycle.

## Research-First Workflow

Every guide follows this sequence. Do not skip steps. Steps 1 through 1.9 produce the per-guide report. Step 2 produces the outline. Step 3 produces the draft. Step 4 verifies. Each step builds on the evidence gathered in previous steps.

### Step 1: Research the Topic

Before writing a single word:

1. **Search the web** for the top 5 existing articles on the topic. Read them. Identify what they cover, what they miss, and where they are wrong or outdated. Record these in the guide report's Competing Content Audit table.
2. **Read primary sources** — official documentation, API references, changelogs, GitHub issues, RFCs. Every technical claim must trace back to a primary source.
3. **Test code examples** — if the guide includes code, verify it works. Run it. If you cannot run it, state that explicitly and mark examples as untested.
4. **Identify the gap** — what does this guide offer that nothing else does? If you cannot answer this, the guide should not be written. Record this as the differentiation statement in the guide report.

### Step 1.5: Check Keyword Targets

Before outlining, read the keyword target data:

```
/var/www/html/systemprompt-web/reports/seo/data/keyword-targets.json
```

1. **Find the primary keyword** for this guide. Look for entries where `assigned_guide` matches the planned slug, or find `status: "gap"` keywords in the relevant cluster.
2. **Select 2-3 secondary keywords** from the same cluster with `classification: "secondary"` or unassigned keywords that fit the topic.
3. **Validate demand:** the primary keyword must have `volume > 0`. If volume is null (`status: "needs-data"`), note this and proceed, but flag that keyword data should be pulled before publishing.
4. **Record in frontmatter:** set the guide's `keywords` field to include the primary keyword first, then secondaries.
5. **Title must contain the primary keyword** verbatim or a close variant. If the primary keyword is "claude code cost" and the title is "Token Optimization for AI Coding", the title fails this check.

If no keyword-targets.json entry exists for this guide's topic, check the latest `reports/seo/keyword-research.md` for the keyword universe, or flag for a `seo-keyword-tracker` refresh.

### Step 1.6: Document Topic Research Evidence

Create the per-guide report at `reports/content/guides/{slug}/guide-report.md` using the template from the `guide-optimiser` skill. Fill in:

1. **Search Intent Analysis:**
   - **Primary intent:** classify as informational, commercial, navigational, or transactional based on the keyword intent field in keyword-targets.json
   - **User profile:** who is this person? What role? What problem are they trying to solve? Be specific ("a senior engineer evaluating Claude Code vs Cursor for their team's daily workflow"), not generic ("developers interested in AI tools")
   - **What they need:** the specific answer or outcome they are seeking. Not "information about X" but "a side-by-side comparison with real benchmarks they can use to justify a tool choice to their CTO"
   - **Evidence:** cite the keyword intent data, SERP features observed during Step 1 research, and any GSC query patterns from related guides in the same cluster

2. **Keyword Map:** populate with the primary keyword, 2-3 secondary keywords, and any long-tail keywords identified. Include volume, difficulty, and source date for each.

3. **Competing Content Audit:** the top 5 URLs from Step 1 with word counts, strengths, and the specific gaps this guide will exploit.

4. **Differentiation statement:** what this guide offers that nothing else does. This must be specific and evidence-based, not "we go deeper" but "no existing guide includes actual token-level cost measurements across different conversation lengths."

**Pass/fail:** If you cannot complete the Search Intent Analysis with evidence (who, why, what they need, how we know), the guide is not ready to write. Stop and research further.

### Step 1.7: Map FAQs to Long-Tail Keywords

Before outlining, build the FAQ plan:

1. Pull all keywords from `keyword-targets.json` where `cluster` matches this guide's cluster and `classification` is `"secondary"`, or where the keyword contains question words (`how`, `what`, `why`, `when`, `can`, `does`, `is`).
2. Pull any GSC query data from related guides in the same cluster (check the latest `reports/seo/daily/YYYY-MM-DD/daily-seo-brief.md` for query data on cluster siblings).
3. Build the FAQ-to-keyword mapping table in the guide report's Section 2. Every planned FAQ question must match a researched long-tail keyword.
4. **Minimum 4 FAQs, each mapped to a keyword with documented volume.** If volume data is missing for a keyword, flag with `status: "needs-data"` but proceed.
5. Record the mapping in the guide report.

**Pass/fail:** If fewer than 4 FAQ-keyword mappings can be established, flag the guide as `needs_keyword_research: true` and run `seo-keyword-tracker` to pull fresh data before continuing.

### Step 1.8: Plan External Resources and Homemade Assets

Before outlining, identify the evidence base:

**External resources (minimum 5):**
- Identify at least 5 external resources that will be linked in the guide body (not just the frontmatter `links` array).
- Must be primary sources: official documentation, research papers, RFCs, GitHub repositories, specification documents, pricing pages, benchmark reports.
- Must NOT be blog posts or tutorials summarising documentation.
- Must be relevant to the guide's specific topic, not generic "learn more about AI" links.
- Record them in the guide report's "External Resources Audit" section with their type and relevance.

**Homemade visual assets (minimum 2):**
- Plan at least 2 original visual assets: SVG charts, comparison tables with real data, data-driven graphs, architecture diagrams.
- Each must cite a real data source (pricing page with URL, benchmark results with methodology, API documentation with numbers, research paper with DOI or URL).
- Record planned assets in the guide report's "Homemade Asset Inventory" section with their data sources.
- **Every visual asset must be shareable.** Each chart, table, or graph must be wrapped in a container that includes:
  - A **copy button** (using the existing `<sp-copy-button>` web component) that copies the asset's content (data, SVG markup, or formatted table) to the clipboard
  - A **share button** that copies a permalink URL back to the guide section containing the asset, formatted as `https://systemprompt.io/guides/{slug}#{asset-anchor}`. This backlink drives external traffic back to the site when shared.
  - A source attribution line citing the data source

**Pass/fail:** If 5 external primary-source resources cannot be identified before writing, the research is insufficient. If 2 data-driven visual assets cannot be planned with cited sources, the topic needs more quantitative depth. Go back to Step 1 and research further.

### Step 1.9: Document Title, Description, and Keywords Rationale

Before finalising the frontmatter, record in the guide report's Section 7:

- **Title rationale:** why this specific title, which keyword data supports it, the primary keyword volume and source date. Example: "Title contains 'claude code vs cursor' (volume: 6,600, source: keyword-targets.json, 2026-04-16). Starts with comparison frame to match comparison intent."
- **Description rationale:** what search intent it addresses, why this specific phrasing. Example: "Description tells the reader they will get benchmark comparisons and workflow analysis, matching the commercial/comparison intent of the primary keyword."
- **Keywords rationale:** each keyword justified by volume/difficulty data from keyword-targets.json with date. Example: "Primary: 'claude code vs cursor' (6,600/mo, diff 38). Secondary: 'cursor alternative' (1,200/mo, diff 25)."
- Mark all as "initial" with today's date and action "initial" (no S-### hypothesis).

This creates the baseline rationale that prevents future optimiser runs from changing metadata without knowing what evidence backed the original choices.

### Step 2: Build an Outline

Structure the guide around the reader's actual questions (documented in the Search Intent Analysis), not around a topic taxonomy. The outline must:

- Start with the answer (not background)
- Progress from immediately useful to deeply technical
- Include at least one section that no competing article covers (from the differentiation statement)
- Identify where tables, code blocks, or diagrams will appear
- **Identify where each of the 5+ external resource links will be placed** (which section, which claim they support)
- **Identify where each homemade visual asset will appear** (which section, what data it presents)
- **Show which H2/H3 headings correspond to FAQ questions** and their matched long-tail keywords

### Step 3: Write the Draft

Follow the structure and quality rules below.

**Additional requirements for the draft:**
- Every FAQ in the frontmatter must use the long-tail keyword phrase from the FAQ-keyword mapping as/in the question (or a natural variant that preserves the keyword verbatim).
- At least 5 external resource links must appear in the body text (inline, contextually placed where they support a claim or provide depth).
- At least 2 homemade visual assets must be included in the body, each citing its data source and wrapped with copy/share buttons for external sharing (with backlinks to systemprompt.io).
- Content must demonstrate WHY readers can trust it: methodology is stated for any measurements, sources are cited for any claims, evidence is presented for any recommendations. The reader must understand the basis for every assertion.

### Step 4: Verify

- Every link must resolve to a real page
- Every code block must specify a language and be syntactically valid
- Every claim with a number must cite a source
- Every section must add information the previous section did not contain
- Read the guide as a skeptical senior engineer — would you trust it? Would you bookmark it?
- **Verify the search intent documented in the guide report is resolved:** does the guide actually deliver what the Search Intent Analysis says the reader needs?

## Content Quality Standards

### Depth Requirements

- **Minimum 4,000 words** of substantive content (excluding frontmatter and code blocks) for non-pillar guides. The top-performing guides on the site are 5,000-6,000 words.
- **Pillar guides: minimum 5,000 words.** Pillar list: `claude-code-vs-cursor`, `self-hosted-ai-governance`, `getting-started-anthropic-marketplace`, `claude-code-mcp-servers-extensions`, `claude-code-daily-workflows`, `claude-code-organisation-rollout`.
- **Reference guide `claude-code-vs-cursor`: target 9,000-11,000 words** (approximately 45 minutes of reading material). This is the flagship comparison resource and must be exhaustive.
- **No filler.** Every sentence must contain information or insight. Cut any sentence that restates what the previous sentence said. Cut any sentence that could apply to any topic ("In today's fast-paced world...").
- **Go deeper than the docs.** Official documentation describes what a feature does. Guides explain when to use it, when not to, what goes wrong, and what the docs leave out.
- **Include real numbers.** Token counts, latency measurements, cost comparisons, performance benchmarks. Approximate numbers with methodology beat vague claims.

### Accuracy Requirements

- **Primary sources only.** Link to official documentation, not blog posts that summarise documentation.
- **Date all data.** Pricing, model capabilities, API behaviour — anything that changes must include "as of {month} {year}" and a source link.
- **Distinguish fact from opinion.** Benchmarks and documented behaviour are facts. Recommendations and preferences are opinions. Never present opinions as facts.
- **No fabricated examples.** Every code example must work. Every configuration example must be valid. Every CLI command must produce the described output. If you are uncertain, test it or mark it as untested.
- **Correct errors in sources.** If official documentation is wrong or outdated, say so explicitly and explain the actual behaviour. This is how guides become authoritative.

### Writing Quality

- **Write for senior engineers.** Assume the reader knows their stack, has shipped production systems, and can smell filler. Do not explain what an API is. Do not explain what a terminal is.
- **Be specific.** "Reduces costs" is filler. "Reduces input token costs by 40% on conversations longer than 50K tokens" is information.
- **Use concrete examples.** Abstract explanations followed by concrete examples is the pattern. Never abstract without concrete.
- **British English.** Organisation, optimise, realise, colour.
- **No AI cliches.** No "delve", "leverage", "harness the power of", "in today's landscape", "it's worth noting that", "game-changer", "seamlessly". Write like a human who knows the subject.
- **No em dashes.** Use commas, full stops, or parentheses.
- **No hashtags.** Ever.

## Guide Structure

### Frontmatter

```yaml
---
title: "Clear title with primary keyword, under 60 characters"
description: "Meta description, under 160 characters, includes primary keyword"
author: "Edward Burton"
slug: "url-slug-with-keyword"
keywords: "primary keyword, secondary keyword 1, secondary keyword 2"
kind: "guide"
category: "category-slug"
public: true
tags: ["relevant-tag-1", "relevant-tag-2"]
published_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
image: "/files/images/blog/slug.png"
after_reading_this:
  - "Specific outcome 1"
  - "Specific outcome 2"
  - "Specific outcome 3"
links:
  - title: "Primary source title"
    url: "https://primary-source-url"
  - title: "Second source title"
    url: "https://second-source-url"
faq:
  - question: "Exact long-tail keyword phrase someone would search for"
    answer: "Complete, specific answer in 2-4 sentences with numbers where applicable."
  - question: "Second search question matching a researched keyword"
    answer: "Complete answer with specific data points."
---
```

**FAQ rules:** Include 4-6 FAQ entries. Each must match a researched long-tail keyword from the FAQ-keyword mapping in the guide report. Answers must be self-contained (useful without reading the guide) and include specific numbers or steps. FAQs are structured data that appear in search results — they must be accurate and valuable standalone.

### Body Structure

1. **Quick Answer** (first 200 words): Immediately answer the question implied by the title. Numbered steps or a summary table. The reader who stops here should still get value.

2. **Deep Sections** (3-6 H2 sections, 600-1200 words each):
   - One core idea per section
   - Open with what the reader will learn in this section
   - Include at least one of: code block, table, numbered steps, or comparison
   - End with the practical takeaway
   - Include external resource links inline where they support claims
   - Include homemade visual assets where they clarify data

3. **Conclusion** (75-100 words): What to do next. No summary of what was covered. Link to related guides.

### Structural Rules

- No paragraph exceeds 5 sentences
- No H2 section exceeds 1,000 words without H3 subsections to break it up
- A visual break (heading, code block, list, table) every 300 words maximum
- The guide must begin answering the title's implied question within the first 300 words
- Every H2 must be a question or action phrase that someone would search for

## No Brand References in Body Content

The body of the guide must contain **zero occurrences** of `systemprompt`, `systemprompt.io`, or `systempromptio` (case-insensitive). This is absolute. Run a grep check to verify before publishing.

This means:
- No "How {product} helps" sections
- No product CTAs in the body
- No "we recommend" or "our solution" language
- No links to product pages within the guide body
- No first-person marketing ("we built X to solve Y")
- No positioning language ("our platform", "our governance infrastructure")

The guide stands alone as authoritative technical content. Product association happens through the site context (header, footer, author bio), not through the prose.

**Only exception:** if the guide's topic IS specifically about the product (e.g., "Getting Started with Anthropic Marketplace"), then references to that product are the content, not promotion.

## SEO Integration

- One primary keyword, 2-4 secondary keywords per guide (from keyword-targets.json)
- Primary keyword in: title, first paragraph, one H2 subheading, meta description, URL slug
- Target questions that official documentation does not answer
- Answer "People Also Ask" questions — these become H2 headings and FAQ entries
- Internal links to at least 2 related guides from the same cluster
- Reference the interlinking map at `/var/www/html/systemprompt-web/reports/seo/interlinking-strategy.md`

## Code Standards

- Every code example must be complete enough to run. State prerequisites (language version, dependencies, environment variables).
- Note OS-specific commands with alternatives for macOS, Linux, and Windows where they differ.
- Every code block must specify a language identifier.
- Configuration examples (JSON, YAML, TOML) must be syntactically valid.
- No placeholder values that look real (no fake API keys, no fake URLs that resolve).
- Long code blocks (>30 lines) must have inline comments explaining non-obvious lines.

## Citation Standards

- Every specific claim (performance numbers, technical behaviour, pricing, model capabilities) must cite an official source using an inline markdown link.
- Pricing or cost data must include "as of {month} {year}" and link to the pricing page.
- If multiple sources disagree, acknowledge the discrepancy and state which source you trust and why.
- Do not cite blog posts or tutorials as authoritative sources for technical facts. Cite documentation, papers, or source code.

## Guide Types

### Technical Implementation Guides
Step-by-step content for deploying, configuring, or operating specific tools and systems. Highest word count. Most code examples.

### Decision Guides
Compare approaches, tools, or architectures. Must include a comparison table with specific criteria. Must state a clear recommendation with reasoning.

### Operational Guides
How to run, monitor, and maintain systems in production. Focus on what goes wrong and how to fix it. Include troubleshooting sections.

### Concept Guides
Explain a technical concept in depth. Must go beyond what the official docs cover. Include diagrams or worked examples that build intuition.

## Quality Gate

Before publishing, the guide must pass all of these:

**Content fundamentals:**
- [ ] Minimum 4,000 words of substantive content (5,000 for pillar guides, 9,000-11,000 for claude-code-vs-cursor)
- [ ] Every code block is syntactically valid and specifies a language
- [ ] Every numerical claim cites a source with a date
- [ ] FAQ entries answer real search queries with specific numbers
- [ ] At least 2 internal links to related guides
- [ ] Visual break every 300 words maximum
- [ ] Passes the skeptical senior engineer test: would they bookmark this?

**SEO and metadata:**
- [ ] Title is under 60 characters and contains the primary keyword
- [ ] Meta description is under 160 characters and contains the primary keyword
- [ ] Title, description, and keywords rationale documented in guide report (Section 7)

**Brand compliance:**
- [ ] Zero product references in body content (grep check: `grep -ci 'systemprompt' body_content` returns 0)
- [ ] No "we recommend", "our solution", "try our" language

**Research evidence:**
- [ ] Per-guide report created at `reports/content/guides/{slug}/guide-report.md`
- [ ] Search Intent Analysis complete with evidence (who is searching, why, what they need, how we know)
- [ ] Unique perspective documented: what this guide offers that nothing else does
- [ ] Competing content audit with at least 3 competitor URLs analysed

**Data-driven content:**
- [ ] At least 4 FAQs, each mapped to a researched long-tail keyword with documented volume
- [ ] At least 5 external resources linked in body (primary sources, not blog summaries)
- [ ] At least 2 homemade visual assets (SVG chart, data table, graph) with cited data sources
- [ ] Every visual asset has copy and share buttons (share button embeds backlink to systemprompt.io/guides/{slug}#{anchor})

**Trust and value:**
- [ ] Content demonstrates trustworthiness: methodology stated, sources cited, evidence presented throughout
- [ ] Strategies and recommendations are empirical and evidence-backed
- [ ] Search intent resolution: the guide demonstrably answers what searchers are looking for (based on documented intent analysis)

**State management:**
- [ ] Action logged in per-guide report with date, word count, and commit SHA
- [ ] Guide and guide report committed together

## Post-Write: Update Guide Report

After the quality gate passes:

1. Update the guide report:
   - Append Action Log entry: date, "Created", "guide-writer", word count, no artifact report, no hypothesis, commit SHA
   - Set status to "published"
   - Confirm Section 7 (metadata rationale) is complete
   - Confirm Sections 1-4 (research evidence, FAQs, resources, assets) are populated
2. Commit both the guide (`services/content/guides/{slug}/index.md`) and the guide report (`reports/content/guides/{slug}/guide-report.md`) together in the same commit.
