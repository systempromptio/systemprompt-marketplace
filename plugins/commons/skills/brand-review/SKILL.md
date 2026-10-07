---
name: brand-review
description: "Review any content against systemprompt.io's identity, brand voice, and governance infrastructure positioning before publishing. Pre-publish quality gate for blog posts, docs, website copy, and marketing content."
metadata:
  version: "2.0.0"
  git_hash: "a8d5b1e"
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
3. **Target audience** (partners: consultancies, SIs, AI practices; or enterprise buyers: CIO, CISO, COO, CRO, CFO, CHRO; engineers reading mechanism evidence)

## Review Checklist

### Identity Alignment
- Does the content position systemprompt.io as the software for AI architecture, delivered by certified partners (not a library, framework, platform, template or open-source project)?
- Does it lead with partner-delivered AI architecture (not ownership, self-hosting or the binary)? Is "runs inside your environment" used at most once, as a property?
- Is the go-to-market partner-led (no direct sales motion, no free tier, no template, no white-label as the route to market)?
- Does it speak to the stated target audience (partner or buyer), with the buyer route, partner route and engineer evidence in the right places?

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
- **Pivot banned list:** grep for every term in brand-voice rule 10: `open source`, `open-source`, `source-available`, `BSL`, `Business Source`, `MIT licen`, `template repo`, `systemprompt-template`, `clone the`, `cargo `, `crates.io`, `brew install`, `docker run`, `helm install`, `1-click deploy`, `evaluate on your laptop`, `Book a call`, `book a call`, `Evaluate the template`, `founder`, `solo`, `indie`, `platform` (except the `self-hosted-ai-platform` slug and "AI FinOps & Platform Operations"), `framework`, `SystemPrompt`, `powerful`, `seamless`, `robust`, `comprehensive`, `cutting-edge`, `enterprise-grade`, `next-generation`, `revolutionize`, `game-changer`, `unlock`, `supercharge`, `leverage`, `harness`, `transform`, `empower`, `delve`. Any hit is High severity
- **"library" as product noun:** replace with "software" or "runtime"
- **Numbers:** any percentage, "X hours saved" or invented count? Only the programme's own numbers and customer's-own-baseline framing are allowed
- **Provider neutrality:** providers named only in lists of supported providers
- **Engagement bait:** Any "Comment YES," "Like for Part 2," "Tag someone" patterns? Remove

### Messaging Hierarchy
- Does the content reinforce the core message ("The software for AI architecture, delivered by certified partners")?
- Does it align with at least one messaging pillar (AI architecture delivered; three tracks, seven pillars; governance as the operating boundary; value against your own baseline)?
- **Two-CTA rule:** are the only CTAs "Become a partner" (`/partners/apply`) and "Find a certified partner" (`/partners/find`), plus "See the certification" on track and pillar pages only? Any "Book a call", "Request a demo", "Start free", clone, GitHub or install CTA is High severity

### Terminology
- Correct Anthropic terms used (skill, agent, connector, plugin, MCP server, Claude Cowork)?
- "the software" or "the runtime" (not platform, library, framework, tool, app, template)?
- **Three tracks / seven pillars naming rule:** tracks are Sales, Business Analyst, Development; pillars are the seven outcome areas; never swapped, never "domains", "verticals" or "modules"?
- Identity vocabulary table respected (certified partner, partner network, Foundation, credential, tier, pillar specialisation, Opportunity Brief, Solution Blueprint, Architecture Pack, value model, the five levers)?
- Brand name lowercase `systemprompt.io`?

### Channel-Specific Checks

**LinkedIn:**
- Hook in first two lines (under 210 characters)?
- Mobile-optimized formatting?
- No external links in body?
- No product pitch unless naturally part of a story?
- Content funnel position appropriate (70/20/10)?
- Speaks to partners or buyers as intended?

**Blog:**
- SEO metadata present?
- Primary keyword in first 100 words?
- Heading structure correct?
- Content routes to one of the two CTAs?

**Email outreach:**
- Subject under 50 characters?
- Peer-to-peer tone (not vendor-to-customer)?
- References something specific about the recipient?
- One clear CTA, and it is one of the two CTAs?
- Qualifies rather than offering a call? No unsubscribe footer?

**Email nurture/onboarding:**
- From Edward personally?
- One clear purpose?
- Not pushy or fake-urgent?

**Landing page:**
- Headline communicates AI architecture delivered by certified partners in under 10 words?
- Buyer gets outcome and "Find a certified partner" in hero and first section; partner finds track, credential and "Become a partner"; engineer finds mechanism evidence lower down?
- CTAs limited to the two CTAs (plus "See the certification" on track and pillar pages)?

### AI Detection Risk
- Formulaic patterns ("In today's world," "Let's dive in," "Here's the thing")?
- Varied sentence structure?
- Specific point of view that could only come from someone delivering AI architecture?
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
