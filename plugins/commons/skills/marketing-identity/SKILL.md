---
name: marketing-identity
description: "Lead-generation positioning for systemprompt.io. Defines the ICP for the template-based funnel, where they live online, the template hook, and the rules every outreach draft must follow. Load FIRST before any marketing skill."
metadata:
  version: "0.2.0"
  git_hash: "pending"
---

# Marketing Identity — Lead-Gen Layer

Single source of truth for **who we're chasing and with what hook**. Every marketing-related skill loads this first. This skill complements `commons:identity` (brand-level positioning) with the distribution-and-lead-gen layer it omits.

## Upstream Sources of Truth (read before drafting)

Load these once per session in order:

1. `commons:identity` — brand positioning, voice, banned words, 4-segment ICP definitions (ICP 1: Enterprise Security, ICP 2: Mid-Market, ICP 3: White-Label, ICP 4: Individual)
2. `/var/www/html/systemprompt-web/reports/marketing/drafts/midmarket-value-prop.md` — **ICP 2 detailed value prop, the lead-gen target**
3. `/var/www/html/systemprompt-web/reports/marketing/drafts/enterprise-value-prop.md` — ICP 1 detailed value prop (content audience, **not** outreach target)
4. `/var/www/html/systemprompt-web/COMPETITOR_ANALYSIS.md` — positioning wedges (provable governance, single binary, own-it)
5. `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — current strategy state (read-only here, written by `marketing-strategy-master` skill)

If any file is missing, stop and tell Ed.

## The Lead Definition

A **lead** = someone who clones `systempromptio/systemprompt-template`, runs it, and gives feedback (any channel: GH Issue labelled `feedback`, email to `hello@systemprompt.io`, DM reply, form submission).

Activation requires **all three**: clone + run + feedback. Clones alone are not leads. Feedback without a run is not a lead.

## Primary Lead-Gen ICP (ICP2)

VP Eng / Head of AI / CTO / Platform Eng lead at a **50–500-person** company that has already decided to standardise on Claude Code. Their pain: fragmented usage, no shared knowledge, no visibility, no governance — and they don't want to build infrastructure themselves.

**What they say out loud:**
- "How do we standardise Claude Code across teams?"
- "I can't tell who's using it or what it costs."
- "We need shared skills / prompts / MCP servers."
- "Our security team is asking about agent governance."

**Where they live online (in rough priority order — validate with data, do not assume):**

| Channel | Sub-segment | Signal |
|---|---|---|
| Reddit | r/ClaudeAI, r/mcp, r/LocalLLaMA, r/ExperiencedDevs, r/devops, r/selfhosted | Standardisation, governance, cost questions |
| GitHub | `awesome-claude-code`, `awesome-mcp`, Anthropic cookbooks, plugin registries, `modelcontextprotocol/*` discussions | Ecosystem discovery, contribution threads |
| crates.io / docs.rs | Rust AI/MCP crates | **Already a referrer to systemprompt-core** — active surface |
| LinkedIn | Head of AI / VP Eng / Platform Eng at 50–500-emp cos | Public signals: job posts mentioning Claude, posts about AI rollout |
| X (Twitter) | MCP/AI-eng community, Simon Willison orbit, Anthropic devrel | Thread engagement, quote-tweets |
| Discord | Anthropic, MCP | Slow, but high-trust |
| Newsletters (target) | Latent Space, Ben's Bites, TLDR AI, Pragmatic Engineer | Placement goals, not owned |

**Not a target for outreach** (content only): CISOs, Fortune-100 procurement, consumer AI users.

## The Template Hook

All distribution must drive to one of:

1. **Primary CTA:** `https://github.com/systempromptio/systemprompt-template` — "clone the template, own the binary, see your team's AI usage by Friday"
2. **Secondary CTA:** `https://github.com/systempromptio/systemprompt-core` — for Rust/crate audiences
3. **Tertiary CTA:** `https://systemprompt.io/` — for high-funnel awareness posts

Never link to multiple CTAs in one post. Pick one per hypothesis.

**The one-liner:** *"A single Rust binary that turns your team's scattered Claude Code usage into a governed, shared, measured capability. Clone the template. Own it."*

## Hypothesis Format (mandatory for every action)

Every logged action must include:

```
[H-###] If we {verb + specific action} on {channel} targeting {ICP-subsegment},
        then {metric} will {direction} by {Δ or target} within {window}.
        Reason: {insight or prior evidence}.
```

Example:

```
[H-012] If we post a teardown of "Microsoft AGT vs one-binary governance" on r/mcp,
        then systemprompt-template unique cloners (7d) will increase from baseline 47
        to ≥70 within 7 days. Reason: r/mcp audience is pre-qualified and actively
        comparing governance options (COMPETITOR_ANALYSIS §2.1).
```

Ambiguous metrics ("more engagement", "better reach") are rejected — the skill must pick a metric from `lead-tracker`'s output.

## Rules for Every Draft

Inherits everything from `commons:brand-voice`, plus:

1. **No em dashes.** Commas, parens, periods, or restructure.
2. **No banned cliches** (see commons:identity list). Extra banned in outreach: *"reach out," "touch base," "circle back," "exciting news," "game-changer," "excited to share."*
3. **Never fabricate traction.** No made-up stars, clones, customer quotes. Use real numbers from `lead-tracker` or omit.
4. **One CTA per post.** One link.
5. **Specificity beats enthusiasm.** "47 unique cloners in 14d, referrers are crates.io and docs.rs" is better than "growing fast."
6. **It's a library, not a platform or framework.**
7. **Brand is `systemprompt.io`** — always lowercase.
8. **No hashtags on any platform.**
9. **Ed posts everything himself.** Drafts must be copy-paste ready, no placeholders like `{name}` unless it's a personalised DM and the placeholder is in square brackets at the top of the file for Ed to replace manually.
10. **Every draft is tagged with its `[H-###]`** in a footer comment so `hypothesis-ledger` can track it.
