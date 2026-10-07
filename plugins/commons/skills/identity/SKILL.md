---
name: identity
description: "The foundational source of truth for what systemprompt.io is, who it serves, and how it goes to market. Load this skill before any other content skill. Defines product identity, ICP, partner-led go-to-market, competitive positioning, vocabulary, and messaging hierarchy."
metadata:
  version: "4.0.0"
  git_hash: "a5b0f4d"
---

# systemprompt.io Identity

The single source of truth for what systemprompt.io is, who it serves, and how it goes to market. Every other systemprompt.io skill must align with this document. Load it first, always.

Upstream source: `/var/www/html/systemprompt-web/reports/pivot/positioning.md` (approved 2026-10-07) and `/var/www/html/systemprompt-web/reports/pivot/handbook.md` (pillars, value model, KPIs, tiers, exam blueprints). If this skill and positioning.md disagree, positioning.md wins. Copy facts from the handbook; never invent KPIs, controls or numbers.

## What systemprompt.io Is

**One sentence:** systemprompt.io is the software for AI architecture: one governed runtime that connects an organisation's people and agents to models, tools and data, delivered and supported by certified partners worldwide.

**Short form:** The software for AI architecture, delivered by certified partners.

**Two sentences for a buyer:** Your organisation wants its people and agents to use AI across the systems that run the business, under controls the security team can defend. systemprompt.io is the software that makes that possible, and a certified partner designs, implements and operates it with you.

**Two sentences for a partner:** AI implementation is a services business with a software core. systemprompt.io gives your consultancy the software, the method (three tracks, seven pillars) and the certification that lets you sell, design and build governed AI inside enterprise customers.

**What it is:** AI architecture software. A runtime and control plane installed inside the customer's environment.

**How it is sold:** exclusively through a global network of certified partners. Customers find a certified partner. Partners certify their people on three tracks and earn tiers and pillar specialisations. There is no direct sales motion.

systemprompt.io is not a consumer app. It is not a prompt library. It is not an MCP server (though it includes governed MCP access). It is not sold as a library, framework, platform or open-source project.

## What the Software Does (Capabilities)

The product capability list. Use these as supporting proof, never as the lead:

- **Identity.** Every request is bound to a person or agent identity. OIDC SSO and roles. Default-deny authorisation.
- **Gateway.** One gateway to model providers with routing, quotas, policy and safety screening. Provider choice: Anthropic, OpenAI, Google and other compatible providers are named only in lists of supported providers.
- **Governed MCP tool access.** Tools served by governed MCP servers with least-privilege scopes.
- **Agents.** Agents run on the runtime under the same identity and policy.
- **Skills and marketplaces.** Skills, plugins and agents distributed through scoped marketplaces.
- **Audit.** Audit records correlated by trace id, stored in the customer's database.
- **Runs inside the customer's environment.** One runtime plus PostgreSQL, in the customer's cloud or on premises, secrets in the customer's key management. Say this once per page at most, as a property, never as the headline.

**What it does not govern:** activity that bypasses the gateway, governed MCP servers and runtime agents is outside the governance boundary. A certified partner pairs the software with network controls that close it. Every certified person must be able to say this.

## Proof Points That Remain True

- Technical due diligence at some of the largest technology companies in the world.
- Production deployments.
- Registered copyright on the software.

Never invent customer names, counts, percentages or "hours saved".

## The Method: Three Tracks, Seven Pillars

**The three tracks** are the three jobs on every AI implementation. Everyone starts with **Foundation** (SP-FND), then certifies for the job they do.

| Track | Owns | Produces | Credential(s) |
|---|---|---|---|
| **Sales** | WHY | Opportunity Brief | Certified Sales Consultant (SP-SAL) |
| **Business Analyst** | WHAT | Solution Blueprint | Certified Functional Consultant (SP-CON) + Pillar Specialist endorsements |
| **Development** | HOW | Working implementation, then Architecture Pack | Certified Technical Implementer (SP-TIM), then Certified Solution Architect (SP-ARC) |

**The seven pillars** are the business outcome areas: Revenue & Growth, People & Performance, Engineering Productivity, Governance Security & Compliance, Customer Operations, AI FinOps & Platform Operations, Knowledge & Content.

**The one-sentence rule:** a credential says what a person can be trusted to do on a customer engagement, not how much training they have consumed.

**How an engagement works:** Opportunity Brief, then Solution Blueprint, then working implementation, then measured at 30, 60 and 90 days.

**Partner tiers** (organisation level): Registered, Silver, Gold, Platinum. Partners also earn **pillar specialisations**. Commercial terms are in the partner agreement and are never published.

## The Value Model

**Data source + implementation + control = expected benefit, then lever, then KPI, then value.**

**The five levers:** Revenue, Performance, Efficiency, Cost control, Risk.

Value is always measured against the customer's own baseline. Every pillar names leading and lagging KPIs; the partner baselines them before configuration and measures at 30, 60 and 90 days. We never quote a vendor percentage. Never call it an "ROI calculator".

## Vocabulary

Use these words exactly.

| Term | Meaning | Never |
|---|---|---|
| **systemprompt.io** | the company and the software | SystemPrompt, System Prompt |
| **the software** / **the runtime** / **AI architecture software** | the product | library, framework, platform, open-source project, template |
| **certified partner** | a consultancy or integrator in the programme | reseller (unless describing the partner_type field), vendor |
| **partner network** | all certified partners together | ecosystem, marketplace (reserved for skill marketplaces in the product) |
| **the three tracks** | Sales, Business Analyst, Development: the three jobs on every AI implementation | the three pillars |
| **the seven pillars** | the business outcome areas listed above | domains, verticals, modules |
| **Foundation** | the shared entry certification everyone takes first | Associate, L1 |
| **credential** | an individual certification | badge (except "Pillar Specialist endorsement") |
| **tier** | partner organisation level: Registered, Silver, Gold, Platinum | level |
| **pillar specialisation** | a partner-organisation badge for a pillar | |
| **Opportunity Brief**, **Solution Blueprint**, **Architecture Pack** | the three deliverables, one per track | proposal, spec |
| **value model** | data source + implementation + control = expected benefit, lever, KPI, value | ROI calculator |
| **the five levers** | Revenue, Performance, Efficiency, Cost control, Risk | |

## ICP (Ideal Customer Profile)

Two audiences. Every page and every piece of content serves one or both.

### ICP 1: Consultancies, system integrators and AI practices (partners)

**Who:** practice leads, alliance leads, managing partners and delivery heads at consultancies, system integrators and AI practices who want a certified AI implementation practice.

**The moment of pain:** their clients ask for governed AI across the business. The firm has smart people but no repeatable method, no software core and no credential that tells a client "these people can be trusted on this engagement".

**What they get:** the software, the method (three tracks, seven pillars), certification for their people, tiers and pillar specialisations, partner directory listing and inbound lead sharing at higher tiers.

**CTA:** Become a partner, `/partners/apply`.

### ICP 2: Enterprise buyers who engage a certified partner

**Who:** CIO, CISO, COO, CRO, CFO, CHRO at organisations that want a governed AI implementation with a measurable KPI.

**The moment of pain:** AI is everywhere and governed nowhere. Security is blocking adoption, the board asks what AI spend buys, or one department has a burning workflow nobody can safely automate.

**What they get:** a certified partner who runs discovery, designs the solution, implements and supports it, and measures value against their own baseline.

**Where to start:** the pillar with the clearest baseline and an executive who owns the KPI. Security blocking AI: Governance. Board asking what AI spend buys: FinOps. One burning workflow: start there and land Governance controls alongside it.

**CTA:** Find a certified partner, `/partners/find`.

Engineers still matter: they should find mechanism evidence and documentation lower on every page, but they are not the lead audience and not a separate funnel.

## Go-to-Market Strategy

**Partner-led. No direct sales motion.** systemprompt.io does not sell the software directly to end customers. Certified partners sell, design, implement and support it.

1. Recruit consultancies, system integrators and AI practices into the partner programme.
2. Partners certify their people: Foundation, then Sales, Business Analyst and Development tracks.
3. Partners progress through tiers (Registered, Silver, Gold, Platinum) on certified people, live deployments and referenceable customers, and earn pillar specialisations.
4. Enterprise buyers find a certified partner, who runs discovery and a pilot, then delivers and measures.

**Exactly two CTAs, everywhere:**

- **Become a partner** → `/partners/apply` (header button, partner-facing pages, final CTA on every page).
- **Find a certified partner** → `/partners/find` (hero secondary, pillar pages, customer-facing pages).

Pillar and track pages may add a contextual third link ("See the certification"). No "Book a call", no "Request a demo", no "Start free". The recorded demo stays at `/features/demo` as "Watch the software in action".

### Role of the Website

Every page splits by audience. A buyer gets the outcome and the "find a partner" route from the hero and first section. A partner finds the track, credential and "become a partner" route. An engineer still finds mechanism evidence and documentation links lower down.

### Channels

- **Primary:** partner recruitment (consultancies, SIs, AI practices).
- **Supporting:** LinkedIn thought leadership from Edward's personal profile on AI architecture, the paradigm shifts and the value model.
- **Supporting:** content and SEO that bring buyers and partners to the pillar, track and partner pages.

## Competitive Positioning

The frame is no longer build vs. buy for engineers. The frame is: AI implementation done by people certified to do it, on software designed for governed AI, measured against the customer's baseline, versus ad hoc pilots, tool sprawl and vendor percentages.

**One-liner:** Other vendors sell you a tool and leave the implementation to you. systemprompt.io is the software plus a certified partner network that designs, implements and measures it.

Secondary context (do not lead with competitor names):

- **Single-vendor enterprise AI suites:** tied to one provider. systemprompt.io is provider-neutral and governs people and agents across providers.
- **Governance toolkits:** require assembly by the customer. systemprompt.io arrives through a partner with a method and a credential.
- **SaaS governance products:** post-hoc analysis outside the customer's environment. systemprompt.io enforces at request time inside it.

## Messaging Hierarchy

### Tier 1: The Core Message
**"The software for AI architecture, delivered by certified partners."**

Homepage register: "AI architecture, delivered." Highlight: "Software, method and certified partners for governed AI inside your business."

### Tier 2: Audience-Specific Messages

**To a consultancy or SI:**
"AI implementation is a services business with a software core. Get the software, the method and the certification to sell, design and build governed AI inside enterprise customers."

**To a CIO or COO:**
"Your people and agents using AI across the systems that run the business, designed and implemented by a certified partner, measured against your own baseline."

**To a CISO:**
"Every request identity-bound, default-deny authorisation, audit correlated by trace id, running inside your environment. A certified partner designs the controls with you and can state exactly what the software does not govern."

**To a CFO:**
"Value measured against your own baseline at 30, 60 and 90 days. No vendor percentages."

### Tier 3: Supporting Messages

- "Three tracks. Seven pillars."
- "Three tracks. One implementation."
- "Seven pillars. One runtime."
- "Sales owns why. Business Analyst owns what. Development owns how."
- "Start with work, not AI."
- "Governance is an operating boundary, not another dashboard."
- "A credential says what a person can be trusted to do on a customer engagement."

## What the Name Means

"System prompt" is the foundational instruction that controls how an AI behaves. The name signals that the software operates at the foundational layer of AI architecture.

## Rules for All Content

1. **Lead with AI architecture delivered by certified partners**, not ownership, not self-hosting, not the binary.
2. **Brand name is always lowercase `systemprompt.io`.** Never SystemPrompt or System Prompt.
3. **Exactly two CTAs:** Become a partner, Find a certified partner.
4. **Say "three tracks" and "seven pillars"** exactly; never confuse the two.
5. **The product noun is "software" or "runtime".** Never library, framework, platform, open-source project or template.
6. **Never reference** the template repo, cloning, BSL, MIT, source-available, a free tier, crates.io, cargo or install commands in public copy.
7. **No numbers except the programme's own** (question counts, lab durations, tier thresholds) and the customer's-own-baseline framing.
8. **Never fabricate evidence.** No invented statistics, customer stories, or anecdotes. Use placeholders.
9. **Never use hashtags.**
10. **Never use em dashes.**
11. **Avoid AI cliches** (see brand-voice banned list).
12. **Provider neutrality:** name Anthropic, OpenAI, Google and others only in lists of supported providers.
13. **Content must not read as AI-generated.** Vary sentence length. Use specific details. No corporate voice.
