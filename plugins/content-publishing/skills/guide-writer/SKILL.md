---
name: guide-writer
description: "Write deep, researched long-form technical guides. Optimised for content quality, accuracy, and reader value. No brand references in the content body."
metadata:
  version: "2.0.0"
  git_hash: "626cd59"
---

# Guide Writer

Write deep, accurate, long-form technical guides that rank because they deserve to. Every guide must be the best available resource on its topic. No brand mentions in the content body. The content sells itself through quality, depth, and practical value.

## Dependencies

**Load `identity` first** to understand the topic domain and audience. Do NOT load `brand-voice` — guides must read as independent editorial content, not brand collateral.

## Output Location

Guides are saved to: `/var/www/html/systemprompt-web/services/content/guides/{slug}/index.md`

## Research-First Workflow

Every guide follows this sequence. Do not skip steps.

### Step 1: Research the Topic

Before writing a single word:

1. **Search the web** for the top 5 existing articles on the topic. Read them. Identify what they cover, what they miss, and where they are wrong or outdated.
2. **Read primary sources** — official documentation, API references, changelogs, GitHub issues, RFCs. Every technical claim must trace back to a primary source.
3. **Test code examples** — if the guide includes code, verify it works. Run it. If you cannot run it, state that explicitly and mark examples as untested.
4. **Identify the gap** — what does this guide offer that nothing else does? If you cannot answer this, the guide should not be written.

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

### Step 2: Build an Outline

Structure the guide around the reader's actual questions, not around a topic taxonomy. The outline must:

- Start with the answer (not background)
- Progress from immediately useful to deeply technical
- Include at least one section that no competing article covers
- Identify where tables, code blocks, or diagrams will appear

### Step 3: Write the Draft

Follow the structure and quality rules below.

### Step 4: Verify

- Every link must resolve to a real page
- Every code block must specify a language and be syntactically valid
- Every claim with a number must cite a source
- Every section must add information the previous section did not contain
- Read the guide as a skeptical senior engineer — would you trust it?

## Content Quality Standards

### Depth Requirements

- **Minimum 4,000 words** of substantive content (excluding frontmatter and code blocks). The top-performing guides on the site are 5,000-6,000 words.
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
  - question: "Exact question someone would search for"
    answer: "Complete, specific answer in 2-4 sentences with numbers where applicable."
  - question: "Second search question"
    answer: "Complete answer."
---
```

**FAQ rules:** Include 4-6 FAQ entries. Each must answer a real search query. Answers must be self-contained (useful without reading the guide) and include specific numbers or steps. FAQs are structured data that appear in search results — they must be accurate and valuable standalone.

### Body Structure

1. **Quick Answer** (first 200 words): Immediately answer the question implied by the title. Numbered steps or a summary table. The reader who stops here should still get value.

2. **Deep Sections** (3-6 H2 sections, 600-1200 words each):
   - One core idea per section
   - Open with what the reader will learn in this section
   - Include at least one of: code block, table, numbered steps, or comparison
   - End with the practical takeaway

3. **Conclusion** (75-100 words): What to do next. No summary of what was covered. Link to related guides.

### Structural Rules

- No paragraph exceeds 5 sentences
- No H2 section exceeds 1,000 words without H3 subsections to break it up
- A visual break (heading, code block, list, table) every 300 words maximum
- The guide must begin answering the title's implied question within the first 300 words
- Every H2 must be a question or action phrase that someone would search for

## No Brand References in Body Content

The body of the guide must not mention or promote any product, service, or company as a recommendation. This includes:

- No "How {product} helps" sections
- No product CTAs in the body
- No "we recommend" or "our solution" language
- No links to product pages within the guide body

The guide stands alone as authoritative technical content. Product association happens through the site context (header, footer, author bio), not through the prose.

Exception: if the guide's topic is specifically about a product (e.g., "Getting Started with X"), then references to that product are the content, not promotion.

## SEO Integration

- One primary keyword, 2-4 secondary keywords per guide
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

- [ ] Minimum 4,000 words of substantive content
- [ ] Every code block is syntactically valid and specifies a language
- [ ] Every numerical claim cites a source with a date
- [ ] No product recommendations or brand mentions in the body
- [ ] FAQ entries answer real search queries with specific numbers
- [ ] At least 2 internal links to related guides
- [ ] Title is under 60 characters and contains the primary keyword
- [ ] Meta description is under 160 characters and contains the primary keyword
- [ ] Visual break every 300 words maximum
- [ ] Passes the skeptical senior engineer test: would they bookmark this?
