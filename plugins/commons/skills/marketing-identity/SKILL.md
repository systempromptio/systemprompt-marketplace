---
name: marketing-identity
description: "Lead-generation positioning for systemprompt.io after the partner pivot. Defines the two funnels (partner programme for consultancies, find-a-partner for enterprise buyers), where each audience lives online, the hooks, and the rules every outreach draft must follow. Load FIRST before any marketing skill."
metadata:
  version: "1.0.0"
  git_hash: "2c36b10"
---

# Marketing Identity: Lead-Gen Layer

Single source of truth for **who we're chasing and with what hook**. Every marketing-related skill loads this first. This skill complements `commons:identity` (brand-level positioning) with the distribution-and-lead-gen layer.

## Upstream Sources of Truth (read before drafting)

Load these once per session in order:

1. `commons:identity`: positioning, vocabulary, the two ICPs, the two CTAs
2. `/var/www/html/systemprompt-web/reports/pivot/positioning.md`: approved pivot positioning (wins on any conflict)
3. `/var/www/html/systemprompt-web/reports/pivot/handbook.md`: pillars, value model, KPIs, tiers (copy facts from here, never invent)
4. `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md`: current strategy state (read-only here, written by `marketing-strategy-master`)

If any file is missing, stop and tell Ed.

## The Lead Definition

Two kinds of lead, tracked separately:

- **Partner lead:** a consultancy, system integrator or AI practice that submits a partner application at `/partners/apply`, or replies to outreach asking how the programme works. Qualified when the firm has a delivery practice and named people who would certify.
- **Buyer lead:** an enterprise buyer who submits a request at `/partners/find`. Qualified when they name a workflow, an executive owner and a likely pillar. Buyer leads are routed to certified partners; we do not sell to them directly.

Page views, follows and likes are not leads.

## Funnel 1 (primary): Partner programme for consultancies

**Who:** practice leads, alliance leads, managing partners and delivery heads at consultancies, system integrators and AI practices.

**What they say out loud:**
- "Our clients want governed AI and we have no repeatable method."
- "We need an AI practice that is more than prompt workshops."
- "How do we prove our people can deliver this?"

**The hook:** *"AI implementation is a services business with a software core. Get the software, the method (three tracks, seven pillars) and the certification to sell, design and build governed AI inside your enterprise clients."*

**CTA:** Become a partner → `https://systemprompt.io/partners/apply`

## Funnel 2: Find a certified partner, for enterprise buyers

**Who:** CIO, CISO, COO, CRO, CFO, CHRO at organisations that want a governed AI implementation with a measurable KPI.

**What they say out loud:**
- "Security keeps blocking our AI rollout."
- "The board asks what our AI spend buys."
- "We have one workflow that is drowning and nobody can safely automate it."

**The hook:** *"Governed AI across the systems that run your business, designed and implemented by a certified partner and measured against your own baseline."*

**CTA:** Find a certified partner → `https://systemprompt.io/partners/find`

Buyers are a content and inbound audience. Do not cold-email executives at enterprise buyers; build authority through pillar content they find when they search.

## Where They Live Online (validate with data, do not assume)

| Channel | Audience | Signal |
|---|---|---|
| LinkedIn | Practice and alliance leads at consultancies and SIs; CIO/CISO/COO at buyers | AI practice launches, hiring for AI consultants, posts about AI rollout and governance |
| Consultancy and SI communities | Partner-ecosystem groups, AI practice leaders | Practice building, certification, delivery method |
| Industry newsletters and events | Both | AI architecture, governance, FinOps, operating model |
| Search (pillar and track pages) | Both | Pillar outcome queries, AI governance queries, AI certification queries |

**Never use as funnels:** GitHub repos, crates.io, docs.rs, install pages or the template repo. Those are not CTAs any more.

## CTA Rule

All distribution drives to exactly one of the two CTAs:

1. **Become a partner** → `/partners/apply` (partner-facing content)
2. **Find a certified partner** → `/partners/find` (buyer-facing content)

Pillar and track content may use "See the certification" as a contextual link. Never "Book a call", "Request a demo", "Start free", "clone the template" or a GitHub link. One CTA per post.

## Hypothesis Format (mandatory for every action)

Every logged action must include:

```
[H-###] If we {verb + specific action} on {channel} targeting {ICP-subsegment},
        then {metric} will {direction} by {Δ or target} within {window}.
        Reason: {insight or prior evidence}.
```

Example:

```
[H-112] If we post a breakdown of "Sales owns why, Business Analyst owns what,
        Development owns how" on LinkedIn targeting practice leads at SIs,
        then /partners/apply submissions (14d) will increase from baseline [N]
        to ≥[N+2] within 14 days. Reason: the three-track split answers the
        "how do we staff an AI practice" question directly.
```

Ambiguous metrics ("more engagement", "better reach") are rejected. Pick a metric from `lead-tracker`'s output.

## Rules for Every Draft

Inherits everything from `commons:brand-voice`, plus:

1. **No em dashes.** Commas, parens, periods, or restructure.
2. **No banned words** (see commons:brand-voice pivot banned list). Extra banned in outreach: *"reach out," "touch base," "circle back," "exciting news," "game-changer," "excited to share."*
3. **Qualify, never offer a call.** Ask the question that qualifies (practice size, delivery capability, workflow, executive owner, pillar). Never offer a call, meeting or demo. Route to the CTA.
4. **No unsubscribe footer.** Outreach is personal 1:1 from Ed.
5. **Never fabricate traction.** No made-up partner counts, customer quotes or percentages. Use real numbers from `lead-tracker` or omit.
6. **One CTA per post.** One link.
7. **Specificity beats enthusiasm.**
8. **The product is "the software" or "the runtime".** Never library, platform, framework, template or open-source project.
9. **Brand is `systemprompt.io`**, always lowercase.
10. **Say "three tracks" and "seven pillars"** exactly.
11. **No hashtags on any platform.**
12. **Ed posts everything himself.** Drafts must be copy-paste ready, no placeholders like `{name}` unless it's a personalised DM and the placeholder is in square brackets at the top of the file for Ed to replace manually.
13. **Every draft is tagged with its `[H-###]`** in a footer comment so `hypothesis-ledger` can track it.
