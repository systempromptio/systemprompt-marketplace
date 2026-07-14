---
name: identity
description: "The foundational source of truth for what systemprompt.io is, who it serves, and how it goes to market. Load this skill before any other content skill. Defines product identity, ICP, go-to-market strategy, competitive positioning, and messaging hierarchy."
metadata:
  version: "2.1.0"
  git_hash: "41ef419"
---

# systemprompt Identity

The single source of truth for what systemprompt is, who it serves, and how it goes to market. Every other systemprompt skill must align with this document. Load it first, always.

## What systemprompt Is

**One sentence:** systemprompt gives you control of every AI client your organisation uses.

**Full definition:** systemprompt.io is AI governance infrastructure. It lets organizations own, standardize, and control how AI is used (Claude, Codex, Gemini, or in-house agents) across their teams, their departments, and (through white-label deployment) their customers. Provider support is verified in source: Anthropic, OpenAI, and Gemini providers plus a /v1 gateway that routes to any compatible upstream. Claude remains the best-supported client and the main SEO surface, but positioning is provider-neutral, Claude-aware: lead with governing every AI client, name Claude as one of them.

systemprompt is not a consumer app. It is not a prompt library. It is not an MCP server (though it includes one). It is infrastructure that other companies build on.

**The product has four faces:**

1. **For enterprise security teams:** A governance pipeline that integrates with existing security infrastructure. SIEM-compatible structured JSON audit logs, role-based access control with six tiers, end-to-end request tracing, and provable compliance for every AI agent interaction. Runs on-premises, air-gapped if needed, no data leaves the perimeter.

2. **For mid-market engineering teams (SMEs):** Standardized AI implementation across the organization. A centralised skill marketplace, shared knowledge base, usage analytics, and cost visibility. Every team member uses AI with the same knowledge, the same rules, the same processes, whichever client they run. Full observability of what AI you have, how it is used, and where it is used.

3. **For individual users:** A free tier that provides ownership and portability of your Claude plugins. Your skills, agents, and connectors stored securely in a third-party cloud, decoupled from any single ecosystem. Reusable, shareable, yours.

4. **For white-label partners (SaaS companies):** AI governance infrastructure deployed under their own brand. A custom-branded gateway (like the Dynapps Enterprise Intelligence Gateway) that lets SaaS companies offer AI governance to their own customers without building it themselves.

**The common thread across all four:** Ownership of your AI. You are firmly in control of what AI you have, how it is used, and where it is used, with full observability and permissions.

## What the Product Actually Is (Technical)

These are the concrete proof points that content skills should draw from when specificity is needed:

- **Single compiled Rust binary** (~50 MB). No runtime dependencies beyond PostgreSQL. One artifact to deploy, audit, and secure.
- **Air-gap capable.** Self-hosted, no phone-home, no telemetry. Runs entirely inside the customer's perimeter.
- **4-layer synchronous governance pipeline.** Every AI tool call passes through scope check, secret scan (35+ patterns), blocklist evaluation, and rate limiting before execution. Real-time enforcement, not retroactive analysis.
- **16 event hooks.** Sessions, tool calls, prompts, configuration changes, permission grants/denials, and subagent lifecycle, all captured as structured JSONB in PostgreSQL.
- **SIEM-compatible structured JSON logs.** Direct ingestion by Splunk, ELK, Datadog, Sumo Logic, or any log aggregator. No custom adapters.
- **Transport-layer MCP governance.** Governance sits at the protocol layer (MCP transport), not as a proxy bolted on top. Every client, every model, every tool inherits the policy.
- **Source-available licensing.** The customer owns the binary, the codebase, and the deployment.

## What systemprompt Is NOT

- It is not just an MCP server (the platform is much broader)
- It is not competing with Anthropic (it works with the Anthropic ecosystem, making it governable)
- It is not a developer tool (built for organizations, accessible to non-technical users)
- It is not a consumer product (the free tier exists to demonstrate the technology and build brand awareness, not as the core business)
- It is not a prompt template library (it is governance infrastructure)

## The Core Narrative

Every organization using Claude faces the same problem: AI adoption without governance is chaos. Different team members get different results. Knowledge disappears between sessions. There are no standards, no observability, no enforcement. The bigger the organization, the worse it gets.

Some try to build governance in-house. This is a trap. The AI landscape moves so fast that whatever you build today will need rewriting in three months. Anthropic ships new features, new plugin architectures, new capabilities constantly. Maintaining internal AI governance tooling means dedicating engineering resources to a problem that never stops moving.

systemprompt solves this permanently. Organizations get a governance layer that evolves with the ecosystem. When Anthropic ships something new, systemprompt supports it. When new governance requirements emerge, systemprompt handles them. The organization stays current without maintaining a single line of governance code.

**The value proposition is not the platform. It is freedom from maintaining the platform yourself.**

## ICP (Ideal Customer Profile)

systemprompt serves four audiences. **ICP 1 is the content and credibility audience. ICP 2 is the primary sales and outreach target.** This distinction matters: downstream marketing, CRM, and outreach skills must respect it.

### ICP 1: Enterprise Security (Content and Credibility Audience)

**Buyer:** CISO, Security Engineering Lead, VP Security at companies of 1,000+ employees with dedicated security teams.

**Entry point:** Governance pipeline, SIEM integration, audit trails, secret detection.

**The moment of pain:** Security teams discover that AI agents are a blind spot in the SOC. Agents make tool calls, access external APIs, and process sensitive data with no centralised record. SIEM systems have no visibility. There is no policy enforcement on AI tool calls, no audit trail for compliance, and no secret protection. The CISO asks "what are our AI agents doing?" and nobody can answer.

**What they say:** "We need visibility into AI agent activity." "Our SIEM has a blind spot." "We need provable governance, not a dashboard."

**Value frame:** Defence, compliance, provable governance. systemprompt is a control, not a feature.

**Vocabulary:** governance pipeline, SIEM integration, RBAC, transport-layer governance, end-to-end request trace, audit trail, secret detection, air-gap, policy enforcement, provable governance.

**Outreach rule:** This is a content and credibility audience. Do not cold-email CISOs. Build authority through governance-focused content that security leaders find when they search for AI agent governance solutions.

### ICP 2: Mid-Market Claude Code (Primary Outreach Target)

**Buyer:** VP Engineering, Head of AI, CTO, Platform Engineering Lead at companies of 50 to 500 employees that have already standardised on Claude Code.

**Entry point:** Skill marketplace, plugin management, usage dashboard, cost visibility.

**The moment of pain:** A CTO realises that 30 people in their org are all using Claude differently, with different context, different quality, and no visibility into what is happening. Knowledge is siloed in individual developers. There is no centralised skill library. No one knows what AI costs per department. There is no way to enforce standards. They need governance, and they need it without building it.

**What they say:** "How do we standardise Claude Code across teams?" "I can't tell who's using it or what it costs." "We need shared skills and MCP servers." "Our security team is starting to ask about agent governance."

**Value frame:** Enablement, productivity, knowledge sharing, cost visibility. systemprompt turns fragmented individual AI usage into a governed, shared, measured capability.

**Vocabulary:** centralised skill library, usage analytics, cost attribution, role-based distribution, shared knowledge base, adoption metrics, governed by default.

**Outreach rule:** This is the primary sales and outreach target. Direct, relationship-driven engagement. The template hook ("clone the template, own the binary, see your team's AI usage by Friday") is calibrated for this audience.

### ICP 3: SaaS White-Label Partners

SaaS companies whose customers are asking for AI governance capabilities. These companies face a build-vs-buy decision: dedicate engineering resources to building AI governance (and maintaining it as the landscape evolves), or partner with systemprompt and deploy a white-labelled solution.

**The moment of pain:** A SaaS company's customers start asking "can we govern how our teams use AI through your platform?" and the SaaS company realizes building this would consume their engineering team for months, and by the time they ship it, the AI landscape will have moved.

### ICP 4: Individual Users (Awareness and Brand Building)

Individual Claude users who want ownership and portability of their plugins. These users matter for brand awareness and credibility, not for direct revenue. When a CTO Googles systemprompt after receiving a cold email, these users and their activity create the signal that this is a real, active platform.

## Go-to-Market Strategy

### Distribution Model: Partnership Into White-Label

systemprompt's primary go-to-market is direct, relationship-driven:

1. **Identify SaaS companies in the local network** that are already using Claude
2. **Implement systemprompt as their internal AI governance layer** (direct enterprise sale, reference implementation)
3. **The partner experiences the value firsthand** as an end user
4. **Propose white-label:** "You could offer this to your customers under your own brand"
5. **The partner becomes a distribution channel,** white-labelling systemprompt to their customer base

This solves the trust problem twice. The partner trusts the technology because they use it internally. Their customers trust it because it comes from a brand they already have a relationship with.

Content and SEO are supporting channels that build credibility and inbound discovery. They are not the primary growth engine. The primary motion is direct, relationship-driven outreach. Content exists to ensure that when a prospect researches systemprompt after a direct touch, they find authoritative, governance-focused material. Content also serves ICP 1 (enterprise security), where direct outreach is not appropriate but search-driven discovery is.

### Role of the Website (systemprompt.io)

The website's primary job is **enterprise credibility.** When a CTO who has received a cold email visits systemprompt.io to vet the company before taking a meeting, the site must communicate "this is an AI governance platform" within 10 seconds. When a CISO searches for AI agent governance solutions, the site must demonstrate technical depth and security-first infrastructure.

The website's secondary job is supporting the free tier for individual users, which builds visible activity and brand familiarity.

The website must NOT look like a consumer product. The first impression must be enterprise-grade AI governance infrastructure.

### Role of the Free Tier

The free tier is a **demonstration environment.** It proves the technology works. It creates visible user activity that signals a real, active platform. It gives individual users genuine value (ownership and portability of their plugins). But it is not the business model. It is a credibility engine.

### Channels

- **Primary:** Direct outreach (warm and cold) to CTOs at SMEs in local network (ICP 2)
- **Secondary:** LinkedIn thought leadership (Edward's personal profile) building credibility in the AI governance space (ICP 1 and ICP 2)
- **Supporting:** Content (blog, guides) targeting AI governance search queries for enterprise security credibility (ICP 1) and Claude Code standardisation queries for mid-market discovery (ICP 2)
- **Supporting:** Free tier driving brand awareness and platform activity (ICP 4)

## Competitive Positioning

### The Competitive Frame: Build vs. Buy

The primary competitor is not another platform. It is the internal engineering team that says "we can build this ourselves."

**The argument against building in-house:**
The AI landscape evolves so rapidly that internal governance tooling becomes a maintenance burden that never ends. Anthropic ships new features, plugin architectures, and capabilities continuously. An in-house solution requires a dedicated team tracking every change, rewriting integrations, and maintaining compatibility. systemprompt absorbs that complexity. The organization gets governance that evolves with the ecosystem, maintained by a team whose entire focus is staying current with the AI landscape.

**The one-line version:** You could build it yourself. But by the time you ship it, you will need to rebuild it.

### Secondary Competitors

- **Anthropic Enterprise plugins:** Enterprise-only, requires custom pricing and SSO/SAML. Does not serve SMEs. Does not offer white-label.
- **Microsoft Agent Governance Toolkit:** A toolkit, not a platform. Requires assembly. Does not offer a single-binary deployment.
- **Rubrik Agent Govern:** SaaS, not self-hosted. Post-hoc analysis, not synchronous enforcement. No air-gap capability.
- **MCP directories** (mcpmarket.com, mcpservers.org): Discovery tools, not governance platforms. Different problem entirely.
- **Prompt management tools** (PromptHub, Braintrust, etc.): Developer-focused, prompt versioning in production. Different audience, different problem.

### Differentiation

- **Governance, not just management:** systemprompt enforces rules, permissions, and standards. It does not just store prompts.
- **One binary, complete stack:** A single ~50 MB Rust binary consolidates what others assemble from multiple services.
- **White-label infrastructure:** No competitor offers brandable, deployable AI governance that SaaS companies can offer to their customers.
- **Continuous adaptation:** systemprompt evolves with the AI ecosystem so customers do not have to maintain governance tooling.
- **Accessible to non-technical users:** Enterprise governance that does not require a developer to configure or maintain.
- **Self-hosted, air-gap capable:** The binary runs inside the customer's perimeter. No data leaves. No vendor dependency at runtime.
- **Decoupled from any single ecosystem:** Portable, standards-based. No vendor lock-in.

## Messaging Hierarchy

### Tier 1: The Core Message
**"systemprompt gives you control of every AI client your organisation uses."**

Use this as the anchor. Everything else is elaboration.

### Tier 2: Audience-Specific Messages

**To a CISO or security leader evaluating governance:**
"Every AI agent request traced end-to-end. SIEM-compatible audit logs. RBAC at the transport layer. One binary, your infrastructure, provable governance."

**To a CTO evaluating for their org:**
"Standardize how your organization uses AI. Full observability, enforcement, and permissions across every team and every client."

**To a SaaS company evaluating white-label:**
"Give your customers AI governance without building it yourself. Deploy under your own brand. We handle the infrastructure."

**To an individual user:**
"Own your Claude plugins. Portable, shareable, securely stored, not locked to any ecosystem."

### Tier 3: Supporting Messages

- "You could build it yourself. But by the time you ship it, you will need to rebuild it."
- "AI adoption without governance is chaos. systemprompt brings order."
- "The AI landscape moves too fast to maintain governance tooling in-house."
- "One platform. Your brand. Full control."
- "Same binary. Same features. Different story."

## Pricing Context

- **Free tier:** Up to 10 skills. Demonstrates the technology. Builds brand awareness.
- **Pro ($15/month):** Unlimited skills, team workspaces, analytics. For individuals and very small teams who want more.
- **Enterprise (custom):** White-label gateways, SSO/SAML, HTTP hooks, policy enforcement, SLA. The core revenue driver.

## What the Name Means

"System prompt" is a technical term in AI. It is the foundational instruction that controls how an AI behaves. The name is an asset: it signals to CTOs and technical leaders that this platform operates at the foundational layer of AI control. It communicates authority and depth to the people who matter most (the primary ICP).

## Rules for All Content

All content created using any systemprompt skill must align with this identity document. Specifically:

1. **Lead with governance and control,** not memory or persistence
2. **Position as infrastructure,** not as a consumer product
3. **Speak to CTOs first,** individual users second
4. **The free tier is a demonstration environment,** not the product
5. **The competitive frame is build vs. buy,** not systemprompt vs. other platforms
6. **White-label is the strategic direction,** but content should lead with direct enterprise value (white-label follows naturally once trust is established)
7. **Never fabricate evidence.** No invented statistics, customer stories, or anecdotes. Use placeholders.
8. **Never use hashtags.** On any platform.
9. **Never use em dashes.** Use commas, periods, parentheses, or restructure.
10. **Avoid AI cliches.** Banned: revolutionize, game-changer, unlock, supercharge, seamlessly, harness the power of, next-generation, cutting-edge, paradigm shift, disrupt, empower, leverage (as verb), transform (without specifics), reimagine.
11. **Use Anthropic terminology.** Plugins, skills, agents, connectors, MCP servers, Claude Cowork. Not apps, extensions, bots, integrations, APIs, the desktop app.
12. **Content must not read as AI-generated.** Vary sentence length. Use specific details. Include observations only a real person in this space would make. No corporate voice.
