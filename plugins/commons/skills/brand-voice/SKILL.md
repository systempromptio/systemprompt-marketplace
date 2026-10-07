---
name: brand-voice
description: "Apply and enforce the systemprompt.io brand voice, style guide, and messaging pillars across all content. Always load identity first. Use when reviewing content for brand consistency, drafting content, or checking terminology compliance."
metadata:
  version: "4.0.0"
  git_hash: "2c36b10"
---

# systemprompt Brand Voice

Source of truth for tone, style, and language across all systemprompt.io content. Always load the systemprompt Identity skill first for product definition, ICP, and strategic positioning.

## Dependency

**Load `identity` before this skill.** This skill governs how we sound. The identity skill governs what we say and to whom.

## Brand Personality

systemprompt's voice belongs to Edward: a technical practitioner who has been building in the AI infrastructure space and speaks from direct experience. Not a company broadcasting. Not a marketing team. A person who understands the governance problem because he has watched organizations struggle with it firsthand.

The voice carries authority on AI governance without being academic. It is the CTO's peer, not their vendor.

## Voice Attributes

### Authoritative
- **We are**: confident in our domain, speaking from real experience building AI governance infrastructure, precise about what works and what does not
- **We are not**: arrogant, dismissive of alternatives, making claims we cannot back up
- **This sounds like**: "Every organization using Claude hits the same wall. Different people, different results, no visibility into any of it. That is a governance problem, and it has a governance solution."
- **This also sounds like**: "35 secret patterns scanned at the transport layer. Not a policy document. An actual control."
- **This does NOT sound like**: "We are the leading AI governance platform transforming how enterprises use AI."

### Practical
- **We are**: specific, grounded in real implementation, showing not telling, focused on what the CTO needs to hear
- **We are not**: theoretical, vague, full of empty promises
- **This sounds like**: "Pick the workflow with a baseline and an executive who owns the KPI. Measure it at 30, 60 and 90 days. No vendor percentages."
- **This also sounds like**: "Sales owns why. Business Analyst owns what. Development owns how. A certified partner brings all three to your first workflow."
- **This does NOT sound like**: "Our platform leverages cutting-edge technology to optimize your AI workflow."

### Sophisticated
- **We are**: intelligent without being academic, nuanced about the build-vs-buy decision, respectful of the CTO's technical depth
- **We are not**: dumbed-down, condescending, oversimplified
- **This sounds like**: "The trap is not building it. The trap is maintaining it. Anthropic ships new capabilities every few weeks. Your governance layer needs to evolve with them, or it becomes a liability."
- **This also sounds like**: "The CISO does not care about your skill library. They care that every agent request is traceable, every tool call is logged, and the whole thing runs inside their perimeter."
- **This does NOT sound like**: "AI governance is super easy now! Anyone can set it up!"

### Infrastructure-Minded
- **We are**: thinking at the infrastructure layer, talking about systems and standards, focused on what scales
- **We are not**: feature-focused, demo-driven, selling individual capabilities
- **This sounds like**: "systemprompt is not a tool your team uses. It is the layer underneath that ensures every tool works the way your organization needs it to."
- **This also sounds like**: "MCP is the governance surface. Govern at the protocol layer and every client, every model, every tool inherits the policy."
- **This does NOT sound like**: "Check out our cool new skill editor with drag-and-drop!"

## Tone Adaptation by Audience

**Speaking to consultancies and system integrators (partners, identity ICP 1):** Practice-builder to practice-builder. Business of delivery: method, credentials, tiers, pillar specialisations, what their clients are asking for. Lead to "Become a partner".

**Speaking to enterprise buyers (CIO, CISO, COO, CRO, CFO, CHRO; identity ICP 2):** Outcome first, then the certified partner who delivers it, then mechanism evidence lower down. Lead to "Find a certified partner". The CISO and CTO registers below still apply when the buyer is security or engineering.

**Speaking to CISOs and security leaders (enterprise security, ICP 1):** Defence-in-depth framing. Compliance and audit language. Reference SIEM, SOC, RBAC naturally. The tone is a security engineer presenting a control to the CISO, not a vendor pitching a product. Technical precision matters more than narrative. Lead with what is provable, not what is promised. No marketing superlatives.

**Speaking to CTOs and engineering leaders (mid-market, ICP 2):** Peer-to-peer. Technical confidence. Focus on governance, observability, standards, and the build-vs-buy calculus. No hand-holding. Enablement and productivity framing, grounded in specific capabilities (skill marketplace, usage dashboard, cost attribution).


## CRITICAL RULES (non-negotiable)

### 1. NEVER fabricate evidence or personal stories
Never invent statistics, quotes, anecdotes, customer stories, personal narratives, or specific examples. This includes made-up "I built...", "I learned...", or "When I was..." stories. Never fabricate analogies presented as real experiences.

Use generic, clearly hypothetical examples ("A 200-person SaaS company rolling out Claude...") or placeholders:
- `[INSERT: specific example from Edward]`
- `[INSERT: customer quote or observation]`
- `[INSERT: specific metric or data point]`

### 2. NEVER use hashtags
On any platform. In any context. Ever.

### 3. NEVER use em dashes
Use commas, periods, parentheses, or restructure the sentence instead.

### 4. Avoid AI cliches
Banned: revolutionize, game-changer, unlock, supercharge, seamlessly, harness the power of, the future of, next-generation, cutting-edge, paradigm shift, disrupt, empower, leverage (as verb), transform (without specifics), reimagine.

### 5. Content must not appear AI-generated
- Vary sentence length deliberately (mix short punchy with longer explanatory)
- Use specific details instead of generic claims
- Include observations that only someone building AI governance infrastructure would make
- Avoid perfectly parallel structures (real writing is slightly asymmetric)
- No corporate voice. Write like a technical practitioner talking to a peer.
- Read the content aloud. If it sounds like a press release, rewrite it.

### 6. Use Anthropic's terminology
- Plugins (not "apps" or "extensions" or "add-ons")
- Skills (not "prompts" or "templates")
- Agents (not "bots" or "assistants")
- Connectors (not "integrations" or "bridges")
- MCP servers (not "APIs" or "services")
- Claude Cowork (not "the desktop app")
- systemprompt.io, the software, or the runtime (never "the systemprompt platform", "library", "framework", "template", "tool", or "app")

### 7. Lead with AI architecture delivered by certified partners
Every piece of content reinforces the core message: the software for AI architecture, delivered by certified partners. Not ownership, not self-hosting, not the binary. "Runs inside your environment" is a property, used once per page at most, never the headline.

### 8. Three tracks, seven pillars (naming rule)
- **The three tracks** are Sales, Business Analyst, Development. They are jobs. Never call them pillars.
- **The seven pillars** are Revenue & Growth, People & Performance, Engineering Productivity, Governance Security & Compliance, Customer Operations, AI FinOps & Platform Operations, Knowledge & Content. They are outcome areas. Never call them tracks, domains, verticals or modules.
- Spell the names exactly. Use the identity vocabulary table for Foundation, credential, tier, pillar specialisation, Opportunity Brief, Solution Blueprint, Architecture Pack, value model and the five levers.

### 9. Two CTAs only
- **Become a partner** → `/partners/apply`
- **Find a certified partner** → `/partners/find`
- Track and pillar pages may add "See the certification". Nothing else: no "Book a call", "Request a demo", "Start free", "Clone the template", GitHub or install links.

### 10. Pivot banned list
Banned everywhere in public copy (grep before publishing): `open source`, `open-source`, `source-available`, `BSL`, `Business Source`, `MIT licen`, `template repo`, `systemprompt-template`, `clone the`, `cargo `, `crates.io`, `brew install`, `docker run`, `helm install`, `1-click deploy`, `evaluate on your laptop`, `Book a call`, `book a call`, `Evaluate the template`, `founder`, `solo`, `indie`, `platform` (except the `self-hosted-ai-platform` slug and the pillar name "AI FinOps & Platform Operations"), `framework`, `SystemPrompt`, em dashes, `powerful`, `seamless`, `robust`, `comprehensive`, `cutting-edge`, `enterprise-grade`, `next-generation`, `revolutionize`, `game-changer`, `unlock`, `supercharge`, `leverage`, `harness`, `transform`, `empower`, `delve`.
- **"library" as the product noun is banned.** Use "software" or "runtime". ("It's a library, not a framework" in engineering docs describes code architecture and is not website copy.)
- **No numbers** except the programme's own (question counts, lab durations, tier thresholds) and the customer's-own-baseline framing. No percentages, no "X hours saved".
- **Provider neutrality:** Anthropic, OpenAI, Google and others appear only in lists of supported providers.

## Preferred Language

Use these phrases when they are accurate. They are tested, specific, and grounded in the actual product. Vary them. If the same phrase appears more than once in a single piece of content, find an alternative.

**Enterprise security context (ICP 1):**
- provable governance
- governance pipeline
- transport-layer governance
- end-to-end request trace
- SIEM-compatible audit logs
- air-gap capable
- "a control, not a feature"
- "runs inside your perimeter"

**Mid-market enablement context (ICP 2):**
- centralised skill library
- usage analytics
- cost attribution
- role-based distribution
- shared knowledge base
- adoption metrics
- "governed by default"

**Cross-ICP (always appropriate):**
- the software for AI architecture
- certified partner, partner network
- three tracks, seven pillars
- "Sales owns why. Business Analyst owns what. Development owns how."
- value model, the five levers, measured against your own baseline
- "governance is an operating boundary, not another dashboard"
- "start with work, not AI"
- runs inside your environment (once per page at most)

## Content Framing by ICP

Same binary. Same features. Different story. Use this table to calibrate framing before drafting.

| ICP | Lead with | Proof points | Emotional register |
|-----|-----------|-------------|-------------------|
| 1: Enterprise Security | Defence, compliance, audit | SIEM integration, 35+ secret patterns, air-gap, RBAC, 16 event hooks | Rigorous, measured, precise |
| 2: Mid-Market | Enablement, productivity, cost | Usage dashboard, shared skills, cost attribution, role-based distribution | Practical, peer-to-peer, direct |
| Partners (consultancies, SIs) | Practice, method, credential | Three tracks, seven pillars, tiers, pillar specialisations | Practice-builder to practice-builder |

Do not mix ICP frames in a single piece of content. A blog post targeting CISOs should not detour into skill marketplace features. A LinkedIn post about Claude Code standardisation should not lead with SIEM integration.

## Messaging Pillars (in priority order)

1. **AI architecture, delivered** - The software for AI architecture, delivered by certified partners. (All audiences. This is the lead pillar everywhere.)
2. **Three tracks, seven pillars** - The method: the three jobs on every implementation and the seven outcome areas. (Partners first, buyers second.)
3. **Governance as the operating boundary** - Identity-bound requests, default-deny authorisation, audit correlated by trace id, inside your environment. (CISOs and engineers.)
4. **Value against your own baseline** - The value model and the five levers, measured at 30, 60 and 90 days. (CFOs, COOs and every buyer.)

## LinkedIn Strategy

### Algorithm Context (2025-2026)
- Dwell time (how long people spend reading) is a primary signal
- Comments are worth approximately 8x likes for distribution
- External links reduce reach by approximately 60%
- First 60 to 90 minutes of engagement are critical
- Content from personal profiles outperforms company pages

### ICP Routing
- **Primary audience:** ICP 2 (mid-market CTOs, VP Eng). The 70/20/10 funnel is calibrated for this audience.
- **Growing audience:** ICP 1 (enterprise security). Governance and compliance thought leadership. Always top-of-funnel (trust-building, no product pitch). This content also builds credibility with ICP 2 ("if security teams take them seriously, this is real infrastructure").

### Content Funnel (70/20/10)
- **70% Top of funnel**: Trust-building. Observations about AI governance challenges in organizations. How teams actually adopt AI vs how they think they do. No product mention. Goal: be the person CTOs follow for AI governance insight.
- **20% Middle of funnel**: Thought leadership with positioning. The build-vs-buy decision. What good AI governance looks like. systemprompt may be mentioned as context, not as a pitch.
- **10% Bottom of funnel**: Direct product content. Reference implementations, use cases, partnership announcements. Only after trust is established.

### Post Structure
1. **Hook** (first line): Contrarian take on AI governance, surprising observation about how organizations use AI, or bold claim about where the market is heading. Must earn the "see more" click.
2. **Body** (3-5 short paragraphs): One idea per paragraph. Short sentences. Mobile-formatted. Specific details that demonstrate infrastructure-level thinking.
3. **Closing**: Strong final statement, specific observation, or direct call to action. Never end with a generic engagement question.

### LinkedIn Rules
- NEVER include external links in the post body
- Keep text posts under 1,300 characters
- Post 2 to 3 times per week
- Respond to every comment within the first 90 minutes
- Personal observations and contrarian takes outperform generic advice
- NEVER end posts with generic engagement questions ("What do you think?", "Have you experienced this?", "How does your team handle this?")
- End with a strong statement, a specific insight, or a direct CTA (link in first comment)

## Reddit Strategy

### ICP Routing
- **ICP 2 (mid-market):** r/ClaudeAI, r/mcp, r/LocalLLaMA, r/ExperiencedDevs, r/devops, r/selfhosted. Standardisation, cost, and workflow discussions.
- **ICP 1 (enterprise security):** r/cybersecurity, r/netsec, r/compliance. Match the rigour of these communities. Only contribute when you have genuine security infrastructure insight.

### Rules
- Lead with value. Never pitch
- Match subreddit tone exactly
- Share genuine experiences building AI governance infrastructure
- Only mention systemprompt if directly relevant and helpful
- Be a helpful community member first, a vendor never

## Blog/SEO Strategy

### ICP Routing
- **ICP 1 content:** Targets governance, compliance, and AI security search queries. "AI agent governance tools compared," "AI agent audit trail SIEM," "AI agent secret detection." These build enterprise credibility.
- **ICP 2 content:** Targets Claude Code standardisation queries. "Claude Code organisation rollout," "Claude Code cost optimisation," "Claude Code GitHub Actions." These drive mid-market discovery.
- **Do not mix audiences in a single post.** A governance deep-dive and a Claude Code how-to serve different searchers with different intent.

### Rules
- Long-form, comprehensive content (1,500 to 3,000 words)
- Target keywords that Anthropic's documentation does not cover
- Every blog post answers a specific question a CTO or CISO would search for
- Include practical, actionable insights (not just theory)
- Dual distribution: publish on blog, create standalone LinkedIn version

## Email Strategy
- All emails from Edward personally
- Short, conversational, one clear action per email
- Subject lines under 50 characters
- Plain text with minimal formatting
- Treat the reader as a technical peer
- **Partner outreach only.** Outreach goes to consultancies, SIs and AI practices. Do not cold-email enterprise executives; they are a content and inbound audience routed to "Find a certified partner".
- Qualify, never offer a call. No unsubscribe footer.
