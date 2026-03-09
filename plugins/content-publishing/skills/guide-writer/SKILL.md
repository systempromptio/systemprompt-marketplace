---
name: guide-writer
description: "Write technical how-to guides for systemprompt.io focused on AI governance, Claude deployment, and the plugin ecosystem. Guides serve dual purpose: SEO authority and linkable material for enterprise CTO outreach."
version: "1.0.0"
git_hash: "0000000"
---

# systemprompt Guide Writer

Write technical how-to guides for systemprompt.io. Guides serve two purposes: building SEO authority on AI governance topics, and providing linkable material that Edward can include in CTO outreach emails to demonstrate expertise.

## Dependencies

**Load systemprompt-identity and systemprompt-brand-voice before this skill.** Guides must align with the governance infrastructure positioning and speak to the CTO audience.

## Output Location

Guides are saved to: `/var/www/html/systemprompt-web/services/content/guides/{slug}/index.md`

## Guide Strategy

Every guide should answer a specific question that a CTO deploying Claude would search for. The guide demonstrates systemprompt's depth of knowledge about AI governance, and naturally positions the platform as the solution.

Guides are not product documentation. They are authority content that happens to feature systemprompt where relevant.

## Guide Types

### 1. AI Governance Guides
Questions CTOs ask about governing AI usage across their organisation.
- "How to standardise Claude usage across a team"
- "AI governance checklist for SMEs"
- "How to control AI plugin usage in your organisation"

### 2. Build-vs-Buy Guides
Content that addresses the primary competitive frame.
- "Building AI governance in-house: what to expect"
- "The hidden costs of internal AI tooling"
- "When to buy vs. build AI infrastructure"

### 3. Technical Implementation Guides
Step-by-step content for Claude deployment and governance.
- "How to deploy Claude skills across an organisation"
- "Setting up role-based AI permissions"
- "Claude plugin governance: a CTO's guide"

### 4. White-Label and Partner Guides
Content targeting SaaS companies considering AI governance for their customers.
- "Adding AI governance to your SaaS product"
- "White-label AI: what SaaS companies need to know"

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
public: true
tags: ["ai-governance", "relevant-tag"]
published_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
image: "/files/images/blog/slug.png"
after_reading_this:
  - "Outcome 1"
  - "Outcome 2"
  - "Outcome 3"
---
```

### Body Structure
- **Introduction** (100 to 150 words): State the problem. Include primary keyword. Establish why this matters for someone governing AI at their organisation.
- **Body** (3 to 5 sections with H2 subheadings): One core idea per section. Practical, specific, actionable. Include code examples or configuration examples where relevant.
- **How systemprompt helps** (optional, 1 section): Where natural, show how systemprompt addresses the governance challenge discussed. Never forced. If the guide does not naturally lead here, omit this section entirely.
- **Conclusion** (75 to 100 words): Key takeaways. CTA appropriate for the audience.

## SEO Integration

- One primary keyword, 2 to 3 secondary keywords per piece
- Primary keyword in: title, first paragraph, one subheading, meta description, URL slug
- Target AI governance keywords Anthropic's documentation does not cover
- Answer "People Also Ask" questions where relevant
- Internal links to related systemprompt content

## Writing Rules

- Write for a technically competent CTO audience. Do not oversimplify.
- Be specific and practical. Every guide should leave the reader with something actionable.
- Use real examples. If examples require Edward's input, use placeholders.
- Guides must work as standalone content.
- Include internal links to related systemprompt content.
- Follow all brand voice rules (no hashtags, no em dashes, no AI cliches, no fabricated evidence).
- British English (realise, optimise, organisation).
- Content must not read as AI-generated.

## CRITICAL RULES

- Guides serve the enterprise pipeline. Every guide should be something Edward could link in an outreach email.
- Never fabricate examples, statistics, or case studies.
- Follow the identity and brand voice skills.
- Position systemprompt as governance infrastructure, not a consumer tool.
