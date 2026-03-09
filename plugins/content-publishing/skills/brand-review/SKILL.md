---
name: brand-review
description: "Review any content against systemprompt.io's identity, brand voice, and governance infrastructure positioning before publishing. Pre-publish quality gate for blog posts, docs, website copy, and marketing content."
---

# systemprompt.io Brand Review

Review content against systemprompt's identity and brand voice before publishing. This skill checks that content aligns with the governance infrastructure positioning, speaks to the right audience, and follows all style rules.

## Dependencies

**Load `identity` and `brand-voice` before this skill.** Identity defines what we say. Brand voice defines how we sound. This skill verifies compliance with both.

## Trigger

User asks to review, check, or audit content before publishing.

## Inputs

1. **Content to review** (pasted text, file, or URL)
2. **Channel** (LinkedIn, Reddit, blog, email outreach, email nurture, documentation, landing page)
3. **Target audience** (CTOs/enterprise, SaaS partners, individual users)

## Review Checklist

### Identity Alignment
- Does the content position systemprompt as AI governance infrastructure (not a consumer tool, not a prompt library, not just an MCP server)?
- Does it lead with governance and control (not memory or persistence)?
- Does the competitive frame reference build-vs-buy (not systemprompt vs. other platforms)?
- Is the free tier positioned as a demonstration environment (not the core product)?
- Does it speak to the stated target audience (CTO, partner, or individual)?

### Voice and Tone
- Does it match the four voice attributes (authoritative, practical, sophisticated, infrastructure-minded)?
- Is the tone appropriate for the target audience (peer-to-peer for CTOs, opportunity framing for partners, warmer for individuals)?
- Does it sound like Edward writing, not a company broadcasting?
- Does it read as human-written, not AI-generated?

### Critical Rule Compliance
- **Fabricated evidence:** Any statistics, anecdotes, or observations not confirmed by Edward? Flag with "[UNVERIFIED]"
- **Hashtags:** Any hashtags anywhere? Remove them
- **Em dashes:** Any em dashes? Suggest restructured alternatives
- **AI cliches:** Check against banned list (revolutionize, unlock, leverage, seamless, cutting-edge, etc.)
- **Engagement bait:** Any "Comment YES," "Like for Part 2," "Tag someone" patterns? Remove

### Messaging Hierarchy
- Does the content reinforce the core message ("systemprompt gives you control of Claude")?
- Does it align with at least one messaging pillar (control/governance, build-vs-buy, infrastructure, ownership)?
- Is white-label mentioned only where appropriate (not in top-of-funnel content)?

### Terminology
- Correct Anthropic terms used (skill, agent, connector, plugin, MCP server, Claude Cowork)?
- "The systemprompt platform" (not tool, app, marketplace)?
- AI governance infrastructure (not persistence layer, memory tool)?

### Channel-Specific Checks

**LinkedIn:**
- Hook in first two lines (under 210 characters)?
- Mobile-optimized formatting?
- No external links in body?
- No product pitch unless naturally part of a story?
- Content funnel position appropriate (70/20/10)?
- Speaks to CTOs and technical leaders?

**Blog:**
- SEO metadata present?
- Primary keyword in first 100 words?
- Heading structure correct?
- Content serves enterprise pipeline (linkable in CTO outreach)?

**Email outreach:**
- Subject under 50 characters?
- Peer-to-peer tone (not vendor-to-customer)?
- References something specific about the recipient?
- One clear CTA?

**Email nurture/onboarding:**
- From Edward personally?
- One clear purpose?
- Not pushy or fake-urgent?

**Landing page:**
- Headline communicates AI governance in under 10 words?
- Enterprise credibility within first 10 seconds?
- CTA appropriate for audience (demo/meeting for enterprise, free signup for individuals)?

### AI Detection Risk
- Formulaic patterns ("In today's world," "Let's dive in," "Here's the thing")?
- Varied sentence structure?
- Specific point of view that could only come from someone building AI governance?
- Distinctly Edward's voice?

## Output

### Summary
- Overall alignment score: Strong / Needs Work / Off-Brand
- Identity alignment: Aligned / Partially aligned / Misaligned
- Top strength
- Top priority fix

### Issues Found

| Issue | Location | Severity | Fix |
|-------|----------|----------|-----|
| [specific issue] | [quote or line reference] | High/Medium/Low | [specific revision] |

### Revised Sections
For the top 3 to 5 issues, show before/after with the specific fix applied.

## After Review

Ask: "Would you like me to apply all fixes and give you a clean version, focus on high-severity issues only, or review additional content?"
