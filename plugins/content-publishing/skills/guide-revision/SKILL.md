---
name: guide-revision
description: "Deterministic quality audit for published guides. Runs a checklist of binary pass/fail checks covering facts, links, code, structure, SEO, readability, and interlinking. Load identity first."
metadata:
  version: "1.0.0"
  git_hash: "0000000"
---

# Guide Revision Audit

Run a deterministic quality audit on a published guide. Every check is binary (pass/fail) with specific criteria. No subjective assessments. Output a structured report with exact line references and fixes.

## Dependencies

**Load `identity` before this skill.** The identity skill provides positioning context, keyword targets, and messaging hierarchy needed to evaluate SEO alignment and brand compliance.

## Source of Truth

Read the SEO Content Strategy Master Plan at `/var/www/html/systemprompt-web/services/content/guides/seo-content-strategy-master/index.md` for keyword targets, cluster map, and interlinking strategy. Reference this document when checking SEO alignment and interlinking requirements.

## How to Use

1. Identify the guide to audit (provide the file path or slug)
2. Read the full guide content
3. Read the SEO Content Strategy Master Plan for cluster and interlinking context
4. Run each of the 8 audit sections below
5. Generate the structured report
6. Save to `reports/guide-revision-{slug}-{YYYY-MM-DD}.md`

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
- [ ] Positions systemprompt as governance infrastructure when mentioned (not consumer tool)
- [ ] Competitive frame is build-vs-buy (not systemprompt vs other platforms)
- [ ] Any systemprompt.io promotion is contextual and disclosed, not disguised as neutral advice

### Section 8: Actionability and Completeness

- [ ] A reader with stated prerequisites can complete the guide's goal without external help
- [ ] Every "how to" section has exact steps, not vague direction ("configure your settings" without showing how)
- [ ] Error scenarios and common mistakes are addressed
- [ ] "After reading this" outcomes are all achievable by following the guide
- [ ] Guide does not end abruptly (has a conclusion with next steps or related resources)
- [ ] If the guide recommends a tool or approach, it shows the actual implementation (not just "use X")

## Output Format

Generate a structured markdown report with the following format:

```markdown
# Guide Revision Report: {guide title}

**Guide:** `{file path}`
**Audited:** {YYYY-MM-DD}
**Overall Score:** {N}/8 sections passing

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

... (repeat for all 8 sections)
```

Save the report to `reports/guide-revision-{slug}-{YYYY-MM-DD}.md`.

A section passes only if ALL checks within it pass.
