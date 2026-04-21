---
name: reddit-post
description: "Drafts Reddit posts for developer audiences (ICP: principal engineers). Two registers: Practitioner Story (community subs, viral post formula) and Technical Merit (r/rust, r/ExperiencedDevs, engineering subs). Refuses to draft without a surprise hook (Register 1) or real benchmark data (Register 2). Load social-identity and brand-voice first."
metadata:
  version: "1.0.0"
  git_hash: "a4cd51d"
---

# Reddit Post — Developer Audience

Drafts Reddit **top-level posts** targeted at developers, with two distinct registers calibrated to different sub cultures and reading modes. This is not the general-purpose `reddit-post-composer`. Use that for community and outreach posts. Use this when the audience is people who will read your source before trusting your claims.

**Not a daily skill.** Only invoke when there is something real to post: a benchmark you ran, a failure you diagnosed, an architectural decision worth explaining. If there is no underlying reality, this skill refuses to draft.

---

## Dependencies

1. `social-media:social-identity` — voice rules, banned patterns, mention cap
2. `commons:brand-voice` — tone
3. `commons:identity` — ICP and positioning

---

## ICP: Principal Engineer

The intended reader has 5–15 years of production experience. They have been burned by tools that oversold and underdelivered. They read source code before trusting a README. They review infrastructure proposals for their team. They will downvote anything that reads like a pitch, a README, or a blog post dressed up as a Reddit post.

They engage with:
- A specific problem stated precisely, with no throat-clearing
- Evidence the author has actually run the system (numbers with methodology, failures with diagnosis)
- Honest tradeoffs — what the thing doesn't do, what it costs
- Architectural reasoning — not "we chose Rust for performance" but "we use sqlx `query!` macros because column renames caught at compile time vs. runtime panics at 3am"

They do not engage with:
- Feature lists unanchored to problems
- Benchmarks without tool name and concurrency
- Any sentence that could appear on a landing page
- "Rust is fast"
- Vague safety claims

---

## Two Registers

### Register 1: Practitioner Story

**Subreddits:** r/ClaudeCode, r/ClaudeAI, r/mcp, r/LocalLLaMA (community subs where context > credentials)

**When to use:** You have a real-world deployment story, a counterintuitive result, or something the sub hasn't seen before. The viral benchmark is authenticity, not polish.

**Structure:**

1. **Opener (1 sentence):** First-person service context. Establish who you are in terms of what you do, not what you've built.
   - Works: "I run a small consultancy helping companies deploy Claude Code across their teams."
   - Fails: "We built a governance platform for Claude Code." (product-first, not practitioner-first)
   - Fails: "Excited to share what we've been working on." (announcement energy)

2. **The problem (2–3 sentences):** State what people actually ask for, in the words they'd use. No product vocabulary, no category names.
   - Works: "The first thing every org asks for is governance. Who is using Claude, what are they doing with it, are sessions actually productive, where are tokens going."
   - Fails: "Enterprises require centralized AI governance with audit trail and RBAC."

3. **What you did (2–3 paragraphs):** The facts of what was built or deployed. Specific features are fine here once the problem is established. Include one number that feels real (not a marketing number — a specific count, a latency, a rate).

4. **The surprise hook (1 paragraph):** The one thing nobody expected. This is the post's engine. Without it, don't post in Register 1. The hook should come after credibility is established, not in the opener.
   - Worked example from viral post: gamification. 119 achievements, XP ranks, leaderboard. Nobody opening a governance post expects that. The comments went there.
   - Other hooks that work: a counterintuitive finding ("the tool they used most wasn't what we expected"), a reversal ("we built the restrictive version first — here's why we deleted it"), an odd constraint ("it has to run air-gapped, which ruled out everything we'd normally reach for")

5. **Honest about what's missing (1–2 sentences):** Not modesty performance — actual gaps. "A lot is being built as we go." "The achievement system is still WIP." This signals authenticity. Developers can tell the difference between a gap and a lie.

6. **Engagement hook (1 sentence):** Low-friction and specific. DM offer, question you actually want answered, link in first comment. Not "Thoughts?" Not "Check it out at [link]."

**Register 1 refusal condition:** If you cannot identify a genuine surprise hook — something the sub has not seen in the last 30 days — do not draft. A post without a hook is noise.

---

### Register 2: Technical Merit

**Subreddits:** r/rust, r/ExperiencedDevs, r/devops, r/LLMDevs, r/selfhosted (subs where technical depth is the price of admission)

**When to use:** You have real benchmark data, a specific architectural decision worth defending, or a failure with a diagnosed root cause.

**Structure:**

1. **Opener (1 sentence):** The architectural problem. No intro, no context-setting. If a principal engineer needs three sentences to understand what problem is being solved, you've lost them.
   - Works: "Every AI agent framework I evaluated required at least three services to govern tool calls. Here's why we ended up with one Rust binary."
   - Works: "We needed compile-time guarantees that a UserId couldn't be passed where a SessionId was expected. Here's what that cost us."
   - Fails: "I wanted to share our experience building AI governance infrastructure."
   - Fails: "We've been working on something interesting."

2. **The problem, precisely (2–3 paragraphs):** What you were trying to solve and why existing solutions failed. Specific failure modes, not category criticism. "We evaluated X, it required Redis for session state which ruled out air-gapped deployments" is better than "existing tools are complex."

3. **WHY Rust (1–2 paragraphs, required for r/rust):** Must name specific language features and explain why they were necessary for this problem. The bar is: could this paragraph only have been written by someone who actually built the thing?

   Permitted claims (with the required specificity):
   - `sqlx::query!` macros: "Every SQL query is checked against the live schema at compile time. When we renamed a column in a migration, six queries failed to compile before any code shipped to prod."
   - Newtype IDs: `UserId`, `SessionId`, `AgentName` are distinct types. "You cannot pass a `SessionId` where the function signature expects `&UserId`. The compiler prevents the class of bug where two UUIDs get swapped at a function boundary."
   - `tokio::spawn` for audit writes: "The audit INSERT is fire-and-forget. Governance response doesn't block on the DB write. That's the source of the 6ms figure — the caller gets an allow/deny before the row is committed."
   - Serde boundary discipline: "JSON is untyped at exactly one point — the HTTP boundary. `serde` deserializes directly into typed structs. No raw maps pass between layers."

   Forbidden claims:
   - "Rust is fast" (too vague)
   - "Memory safety" without the specific alternative you avoided
   - "Zero-cost abstractions" as a conclusion rather than an explanation
   - Any claim that could appear in a Rust marketing page

4. **WHY single binary (1 paragraph):** The operational argument, not the technical one. This is for the PE who owns the deployment decision.
   - "One binary, one `just start`, PostgreSQL. No Kubernetes, no Redis, no sidecar. For the orgs we deploy this for, that's the difference between a week of infra work and an afternoon."
   - Include what you gave up to get there (e.g., horizontal scaling constraints, plugin isolation tradeoffs).

5. **The benchmark (1 paragraph, required):** Format: `[tool] / [n requests] / [concurrency] / [what was measured] → [result]`. No result without methodology.
   - Works: "hey / 500 requests / 50 concurrent / governance endpoint (JWT + scope check + 3 rules + async audit) → 3,300 req/s, p50 4ms, p99 18ms on a 4-core dev machine."
   - Works: "Single request cold: 6.1ms wall time (curl, localhost). Breakdown: JWT validation ~0.5ms, rule evaluation ~1ms, tokio::spawn audit (non-blocking) — remainder is HTTP overhead."
   - Fails: "3,300 req/s with sub-5ms governance overhead." (no methodology)
   - Fails: "Extremely fast in our testing." (not a number)

6. **What it doesn't do (1 paragraph):** Two or three honest limitations. PEs will think of them anyway. Addressing them preempts the "but what about X" comments and demonstrates you've thought past the happy path.

7. **No CTA in body.** If the sub permits links in comments, put the repo link in the first comment with one sentence of context. If not, nothing.

**Register 2 refusal condition:** If there are no real benchmark numbers (tool, concurrency, result), do not draft. An architecture post without data is a blog post, not a Reddit post.

---

## Viral Post Reference (r/ClaudeCode, Register 1)

Immortalized for pattern extraction. Each paragraph annotated with the mechanic it uses.

```
Title: We've installed Claude Code governance for enterprise clients - here's the free version

[PRACTITIONER OPENER]
I run a small consultancy helping companies deploy Claude Code across their teams.

[PROBLEM IN READER'S LANGUAGE — no jargon, real questions orgs ask]
The first thing every org asks for is governance. Who is using Claude, what are they
doing with it, are sessions actually productive, and where are tokens going. (Restricting
use, sharing plugins by department etc)

[CONTEXT + TRANSITION TO FREE — explains the post's reason for existing]
My smaller clients kept asking for the same thing but couldn't justify enterprise pricing.
So we've published a cloud based free version (will eventually have a paid tier, not even
enforced right now as we don't know if it's even worth implementing).

[SPECIFIC FEATURES — listed concisely, after credibility established]
Session quality scores (Q1-Q5), usage patterns over time, tool diversity tracking, skill
adoption rates, workflow bottleneck detection. It also comes with a skill and agent
marketplace so teams standardise how they work with Claude instead of everyone doing
their own thing.

[SURPRISE HOOK — buried mid-post after credibility, not in the opener]
Then we added a competitive layer. APM tracking, 119 achievements, XP ranks, and a
leaderboard. Turns out developers engage way more with governance tooling when there's
gamification on top.

[LOW-FRICTION ENGAGEMENT + HONEST IMPERFECTION]
DM for lifetime premium (even thought doesn't not even enforced yet, removes limits, adds
team features). Happy to give just in case we ever charge and to get feedback from early
adopters!

[HONEST ABOUT LIMITATIONS]
A lot is being built as we go, Claude installation and tracking is quite stable as is
ported from Enterprise product, but the achievement and reports etc are still wip.
```

**What to replicate:**
- Practitioner framing in sentence 1 (service context, not product context)
- Problem stated as questions the reader's clients ask, not as product categories
- Surprise hook mid-post, not in title or opener
- Numbers that feel measured (119 achievements — odd enough to be real)
- Typos and "as we go" language left in — authenticity signal, not an error

**What not to replicate:**
- The lack of technical depth (works in r/ClaudeCode, fatal in r/rust or r/ExperiencedDevs)
- "Happy to answer questions" as a closer (replace with a specific question)

---

## Anti-patterns for developer audiences

These fail in addition to the standard anti-sludge gate from `social-identity`:

| Pattern | Why it fails | Replacement |
|---|---|---|
| "Rust is fast" | PE reads this as "I don't know what I measured" | Name the measurement: tool, concurrency, endpoint, result |
| "We chose Rust for memory safety" | Safety is a default claim, not a reason | Name the specific unsafe alternative avoided and why it mattered here |
| Leading with features | Features without a problem are a brochure | Open with the problem the features solve |
| "Zero-cost abstractions" as a conclusion | It's a Rust tagline, not an argument | Show what it cost in other languages and what you got for free |
| Benchmark without methodology | Can't be verified, looks made up | Always: tool / n / concurrency / what measured / result |
| README-in-post | PEs can read the README | Post what's NOT in the README: decisions, failures, tradeoffs |
| Any comparison without your own data | Gets removed in most subs | Either skip comparisons or include your own test run |
| "Happy to answer questions" | Passive, low-information | Ask the specific thing you want input on |

---

## Output

Save to:

```
reports/social/reddit/drafts/YYYY-MM-DD-{subreddit}-{slug}.md
```

File format (identical to reddit-post-composer):

```markdown
# Reddit Post Draft

**Subreddit:** r/{sub}
**Register:** Practitioner Story | Technical Merit
**Tier:** A/B | **Mention tolerance:** {n}/5
**Status:** DRAFT — awaiting Ed review

---

## Title

{title}

---

## Body

{body}

---

## First comment (if any)

{one sentence + link, or "none"}

---

## Register compliance

- Register 1: Surprise hook identified: {yes/no} — {what it is}
- Register 2: Benchmark included with methodology: {yes/no} — {tool / n / c / result}
- WHY Rust paragraph: {specific features named} / {forbidden claims used: none}

---

## Pre-submit checklist (for Ed)

- [ ] Register 1: Surprise hook is present and placed mid-post (not opener)
- [ ] Register 2: Benchmark has tool name, request count, concurrency, result
- [ ] Register 2: WHY Rust names specific language features, not vague claims
- [ ] No forbidden anti-patterns (see table above)
- [ ] Anti-sludge gate passed (no em dashes, no AI clichés)
- [ ] Mention budget respected per sub tolerance
- [ ] Link in first comment only (not in body)
- [ ] Every number is real and verifiable

---

## Expected log entry (H-###)

- **Channel:** reddit / r/{sub}
- **Register:** {1 or 2}
- **Hypothesis:** {metric} will rise from {baseline} to {target} within {window}d
- **Metric:** {specific metric}
- **Window end:** {date}
```

---

## Refusal conditions

- No surprise hook identified (Register 1): refuse, explain what hook would unlock the draft
- No real benchmark data (Register 2): refuse, list what numbers are needed
- Sub below Tier B: refuse, redirect to nearest Tier A/B sub in the same bucket
- Mention budget would be exceeded: rewrite until it fits, or refuse if rewrite is impossible
- Any benchmark presented without tool + concurrency: refuse to include it, ask for methodology
