---
name: identity
description: "The foundational source of truth for what systemprompt.io is, who it serves, and how it goes to market. Load this skill before any other content skill. Defines product identity, ICP, go-to-market strategy, competitive positioning, and messaging hierarchy."
---

# systemprompt Identity

The single source of truth for what systemprompt is, who it serves, and how it goes to market. Every other systemprompt skill must align with this document. Load it first, always.

## What systemprompt Is

**One sentence:** systemprompt gives you control of Claude.

**Full definition:** systemprompt.io is AI governance infrastructure. It is the platform that lets organizations own, standardize, and control how Claude is used across their teams, their departments, and (through white-label deployment) their customers.

systemprompt is not a consumer app. It is not a prompt library. It is not an MCP server (though it includes one). It is infrastructure that other companies build on.

**The product has three faces:**

1. **For individual users:** A free tier that provides ownership and portability of your Claude plugins. Your skills, agents, and connectors stored securely in a third-party cloud, decoupled from any single ecosystem. Reusable, shareable, yours.

2. **For direct enterprise customers (SMEs):** Standardized AI implementation across the organization. Every team member uses Claude with the same knowledge, the same rules, the same processes. Full observability of what AI you have, how it is used, and where it is used. Role-based permissions and enforcement.

3. **For white-label partners (SaaS companies):** AI governance infrastructure deployed under their own brand. A custom-branded gateway (like the Dynapps Enterprise Intelligence Gateway) that lets SaaS companies offer AI governance to their own customers without building it themselves.

**The common thread across all three:** Ownership of your AI. You are firmly in control of what AI you have, how it is used, and where it is used, with full observability and permissions.

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

### Primary ICP: CTOs at Small and Medium Enterprises

The decision-maker is a CTO (or equivalent technical leader) at a company of 20 to 500 people that is already deploying Claude and starting to feel the pain of ungoverned, inconsistent AI usage.

**Key characteristics:**
- Already bought into AI (not skeptics, not evaluating whether to use AI at all)
- Experiencing the governance gap firsthand (inconsistent outputs, no observability, no standards)
- Technical enough to understand the value of infrastructure, not so large that they need 12 months of procurement
- Looking for a solution that works now, not a roadmap

**The moment of pain:** A CTO realizes that 30 people in their org are all using Claude differently, with different context, different quality, and no visibility into what is happening. They cannot enforce standards. They cannot share what works. They cannot audit anything. They need governance, and they need it without building it.

### Secondary ICP: SaaS Companies Seeking White-Label AI Governance

SaaS companies whose customers are asking for AI governance capabilities. These companies face a build-vs-buy decision: dedicate engineering resources to building AI governance (and maintaining it as the landscape evolves), or partner with systemprompt and deploy a white-labelled solution.

**The moment of pain:** A SaaS company's customers start asking "can we govern how our teams use AI through your platform?" and the SaaS company realizes building this would consume their engineering team for months, and by the time they ship it, the AI landscape will have moved.

### Tertiary: Individual Users (Awareness and Brand Building)

Individual Claude users who want ownership and portability of their plugins. These users matter for brand awareness and credibility, not for direct revenue. When a CTO Googles systemprompt after receiving a cold email, these users and their activity create the signal that this is a real, active platform.

## Go-to-Market Strategy

### Distribution Model: Partnership Into White-Label

systemprompt's primary go-to-market is not content marketing or inbound. It is direct, relationship-driven:

1. **Identify SaaS companies in the local network** that are already using Claude
2. **Implement systemprompt as their internal AI governance layer** (direct enterprise sale, reference implementation)
3. **The partner experiences the value firsthand** as an end user
4. **Propose white-label:** "You could offer this to your customers under your own brand"
5. **The partner becomes a distribution channel,** white-labelling systemprompt to their customer base

This solves the trust problem twice. The partner trusts the technology because they use it internally. Their customers trust it because it comes from a brand they already have a relationship with.

### Role of the Website (systemprompt.io)

The website's primary job is **enterprise credibility.** When a CTO who has received a cold email visits systemprompt.io to vet the company before taking a meeting, the site must communicate "this is an AI governance platform" within 10 seconds.

The website's secondary job is supporting the free tier for individual users, which builds visible activity and brand familiarity.

The website must NOT look like a consumer product. The first impression must be enterprise-grade AI governance infrastructure.

### Role of the Free Tier

The free tier is a **demonstration environment.** It proves the technology works. It creates visible user activity that signals a real, active platform. It gives individual users genuine value (ownership and portability of their plugins). But it is not the business model. It is a credibility engine.

### Channels

- **Primary:** Direct outreach (warm and cold) to CTOs at SMEs in local network
- **Secondary:** LinkedIn thought leadership (Edward's personal profile) building credibility in the AI governance space
- **Supporting:** Content (blog, guides) targeting AI governance search queries to establish authority
- **Supporting:** Free tier driving brand awareness and platform activity

## Competitive Positioning

### The Competitive Frame: Build vs. Buy

The primary competitor is not another platform. It is the internal engineering team that says "we can build this ourselves."

**The argument against building in-house:**
The AI landscape evolves so rapidly that internal governance tooling becomes a maintenance burden that never ends. Anthropic ships new features, plugin architectures, and capabilities continuously. An in-house solution requires a dedicated team tracking every change, rewriting integrations, and maintaining compatibility. systemprompt absorbs that complexity. The organization gets governance that evolves with the ecosystem, maintained by a team whose entire focus is staying current with the AI landscape.

**The one-line version:** You could build it yourself. But by the time you ship it, you will need to rebuild it.

### Secondary Competitors

- **Anthropic Enterprise plugins:** Enterprise-only, requires custom pricing and SSO/SAML. Does not serve SMEs. Does not offer white-label.
- **MCP directories** (mcpmarket.com, mcpservers.org): Discovery tools, not governance platforms. Different problem entirely.
- **Prompt management tools** (PromptHub, Braintrust, etc.): Developer-focused, prompt versioning in production. Different audience, different problem.

### Differentiation

- **Governance, not just management:** systemprompt enforces rules, permissions, and standards. It does not just store prompts.
- **White-label infrastructure:** No competitor offers brandable, deployable AI governance that SaaS companies can offer to their customers.
- **Continuous adaptation:** systemprompt evolves with the AI ecosystem so customers do not have to maintain governance tooling.
- **Accessible to non-technical users:** Enterprise governance that does not require a developer to configure or maintain.
- **Decoupled from any single ecosystem:** Portable, standards-based. No vendor lock-in.

## Messaging Hierarchy

### Tier 1: The Core Message
**"systemprompt gives you control of Claude."**

Use this as the anchor. Everything else is elaboration.

### Tier 2: Audience-Specific Messages

**To a CTO evaluating for their org:**
"Standardize how your organization uses Claude. Full observability, enforcement, and permissions across every team."

**To a SaaS company evaluating white-label:**
"Give your customers AI governance without building it yourself. Deploy under your own brand. We handle the infrastructure."

**To an individual user:**
"Own your Claude plugins. Portable, shareable, securely stored, not locked to any ecosystem."

### Tier 3: Supporting Messages

- "You could build it yourself. But by the time you ship it, you will need to rebuild it."
- "AI adoption without governance is chaos. systemprompt brings order."
- "The AI landscape moves too fast to maintain governance tooling in-house."
- "One platform. Your brand. Full control."

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
