---
name: reddit-post-composer
description: "Drafts genuine, non-marketing Reddit POSTS (top-level submissions) for systemprompt.io. Reads the qualified subreddit list from reddit-audience-finder, matches the sub's moderation rules and tone, and produces value-first drafts (data drops, lessons learned, calls for input). Refuses to draft without real data. Invoked on-demand, not daily. Load social-identity and brand-voice first."
metadata:
  version: "1.0.0"
  git_hash: "d9ea667"
---

# Reddit Post Composer

Drafts Reddit **posts** (top-level submissions), not comments. Comments are `reddit-monitor` + `reddit-reply`. This skill writes the thing that shows up in the sub's feed.

**Not a daily skill.** Invoked when Ed has something genuinely worth posting: a real number, a real failure, a real question where input would move the product forward. If there is no underlying reality, the skill refuses to draft. Fabrication is the one unrecoverable error in subs like r/mcp (which bans AI-generated slop on sight).

## Dependencies

1. `social-media:social-identity` — voice + banned patterns + 30% mention cap
2. `commons:brand-voice` — tone rules
3. `commons:identity` — ICP and positioning

The audience list (`reports/social/reddit/audience/subreddits.json`) must exist. If not, instruct the user to run `reddit-audience-finder` and abort.

## Inputs

Three required inputs from the user:

1. **Target subreddit** — must be in the audience list at Tier A or Tier B. If the user names a Tier C or Drop sub, refuse and suggest the nearest Tier-A/B alternative in the same bucket.
2. **Topic** — what Ed actually wants to say, in one or two sentences.
3. **Underlying data or experience** — the real thing behind the post. One of:
   - Numbers we measured (downloads, sessions, blocks, latencies)
   - A failure we experienced and diagnosed (not hypothetical)
   - A decision we're actively stuck on and want input on

If input 3 is missing or abstract, **refuse to draft**. Respond with: "No underlying data — I won't draft a post that's just an opinion framed as expertise. Come back with the number, the failure, or the specific decision."

## Step 1: Load subreddit context

From `reports/social/reddit/audience/subreddits.json`, pull the record for the target sub:

- `subscribers`, `tier`, `score`
- `tone`, `mention_tolerance`, `key_rules`

Also load the cached `hot.json` from the latest `reddit-audience-finder` run (or refetch if older than 3 days) and sample the top 10 posts. This is the reference for native format — title length, selftext length, whether links in body are normalised, whether the community prefers data or narrative.

## Step 2: Select post type

Pick ONE of three formats. The sub's tone and recent hot posts determine which works.

### A) Data Drop

For subs that reward numbers: r/LLMDevs, r/LocalLLaMA, r/mlops, r/devops, r/cybersecurity, r/ClaudeAI.

- **Title:** surprising number + context, specific. "We ran 10,000 Claude Code sessions through tool-call hooks. Here's what got blocked."
- **Body (400–900 words):**
  - Setup (2 paragraphs): what we measured, why, the environment
  - Findings (3–5 paragraphs): the numbers, with specifics
  - Interpretation (1–2 paragraphs): what this means, caveats
  - Open question to the sub (1 line): what would you expect to see?
- **Links:** never in body. If one belongs, first comment with one sentence of context.

### B) Lesson Learned

For subs that reward post-mortems: r/ExperiencedDevs, r/devops, r/cto, r/ITManagers, r/sysadmin.

- **Title:** specific failure. "We shipped a policy hook that blocked 40% of legitimate Claude requests. Here's how we got it wrong."
- **Body (500–1,200 words):**
  - Context (1–2 paragraphs): what we were trying to do, the setup
  - What we shipped (1 paragraph): concrete, with code or config if relevant
  - What broke (2–3 paragraphs): the failure, how it surfaced, what the telemetry said
  - Why we got it wrong (2 paragraphs): the wrong assumption, not vague "oops"
  - What we changed (1 paragraph): the fix, with the new approach
  - What we're still unsure about (1 paragraph): the honest open problems
- **Links:** none in body. Sub rules govern first-comment policy.

### C) Call for Input

For subs that reward peer consultation: r/cto, r/ExperiencedDevs, r/devops, r/compliance, r/AI_Agents.

- **Title:** a specific question, not a generic ask. "How are you enforcing tool-call policy for Claude Code across 30+ devs without destroying their flow?"
- **Body (300–600 words):**
  - Our setup (1 paragraph): team size, current state, constraints
  - What we've tried (1–2 paragraphs): specific approaches, why each fell short
  - Where we're stuck (1 paragraph): the actual open question
  - What we've ruled out (1 paragraph): so respondents don't suggest those
  - The specific input we want (2 lines): not "any thoughts?", but e.g. "has anyone built centralised CLAUDE.md policy with per-repo overrides without the sync pain?"
- **Must actually want input.** If the answer is already known and the post is a disguised pitch, abort.

## Step 3: Apply sub-specific rules

Read the `key_rules` field from `subreddits.json`. Apply these enforcement patterns (add new patterns as they appear):

| Rule pattern | Enforcement |
|---|---|
| "No self-promotion" / "No commercial" / "permaban" | Zero product mentions in body. Link in first comment only, and only if the rule explicitly allows. Otherwise no link at all. |
| "1/10 self-promotion ratio" (r/LLMDevs, r/AI_Agents, r/LocalLLaMA) | Product mention allowed only if this is post #10 in a 10-post history on this sub. Otherwise drop it. |
| "Links in comments, not posts" (r/AI_Agents) | Strip all links from body. Move to first comment. |
| "<3 months = megathread only" (r/selfhosted) | If systemprompt's first public release is younger than 3 months, redirect to the current New Project Megathread. Do not submit to main feed. |
| "3+ years experience" (r/ExperiencedDevs) | Voice must reflect senior IC reality, not beginner framing. If the post could be asked by a junior, abort. |
| "Competitor posts need homework" (r/ClaudeAI) | If the draft compares systemprompt to another tool, include our own evaluation with concrete data. Opinion-only comparisons get removed. |
| "No AI-generated slop" (r/mcp) | Strict. Vary sentence length (mix 6-word and 25-word sentences). Zero AI-prose markers. Use `showcase` flair if showing our work. |
| "Disclose purpose" (r/LLMDevs) | If the post is seeking input that feeds product decisions, say so in the body. |
| "Provide sources" (r/LLMDevs) | Every numeric claim needs a source or a note that the data is internal. |
| "Use relevant post flair" (r/ClaudeAI, r/ExperiencedDevs) | Recommend a flair in the draft. |

## Step 4: Draft

Write the post. Run through anti-sludge gate:

- No em dashes
- No hashtags
- No AI clichés (revolutionize, leverage verb, supercharge, unlock, seamlessly, harness, cutting-edge, next-generation, paradigm shift, disrupt, empower, reimagine)
- No sludge openings ("Fellow {X}...", "Wanted to share...", "Hey everyone...")
- No fabricated data
- No generic closers ("Thoughts?", "What do you all think?") — calls-for-input close with a specific question instead
- Vary sentence length. Mix short and long.

## Step 5: Mention audit

Count product mentions. Apply tolerance from `subreddits.json`:

| Mention tolerance | Max inline mentions | First-comment link |
|---|---|---|
| 1 | 0 | Not permitted |
| 2 | 0 | Permitted only if sub rules explicitly allow |
| 3 | 1 (final paragraph only) | Permitted, one sentence |
| 4 | 1 (final paragraph only) | Permitted |
| 5 | 1 inline + 1 first-comment link | Permitted |

If the draft exceeds the budget, rewrite until it fits. Mention-budget violations are the most common reason posts get removed from governance-adjacent subs.

## Step 6: Output

Save to:

```
reports/social/reddit/drafts/YYYY-MM-DD-{subreddit}-{slug}.md
```

`{slug}` is a lowercase-hyphen 3–6 word summary of the post.

File format:

```markdown
# Reddit Post Draft

**Subreddit:** r/{sub}
**Tier:** A/B | **Mention tolerance:** {n}/5
**Post type:** data-drop | lesson-learned | call-for-input
**Proposed flair:** {if applicable}
**Mention budget used:** {inline}/1 inline, first-comment link: {yes/no}
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

## Why this post, this sub, now

Three bullets:
- What signal in the sub triggered this (specific hot thread or recurring question)
- What real data or experience we're drawing from (must be concrete)
- What response we expect (engagement, a specific discussion, or pipeline signal)

---

## Sub-specific rule compliance

Inline checklist — what rule applied, how the draft satisfies it.

- r/{sub} rule: "{rule}" — satisfied by {specific choice in the draft}
- ...

---

## Pre-submit checklist (for Ed)

- [ ] Read 10 most-upvoted posts from this sub in the last 7 days — our draft matches the native format
- [ ] Zero AI-clichés, em dashes, hashtags (anti-sludge gate passed)
- [ ] Every numeric claim is real (not fabricated)
- [ ] Mention budget respected per this sub's tolerance
- [ ] Link (if any) placed in first comment only
- [ ] Appropriate flair selected
- [ ] If r/selfhosted and project <3 months old, target is the megathread not the main feed
- [ ] If r/ClaudeAI and this is a comparison, our own evaluation data is included

---

## Expected log entry (H-###)

If this post is shipped as a seeded hypothesis, log format:

- **Channel:** reddit / r/{sub}
- **Action:** top-level post, type={type}
- **Hypothesis:** {metric} will rise from {baseline} to {target} within {window} days
- **Metric:** {specific metric to watch}
- **Window end:** {date}

(Ed fills in the actual hypothesis and metric when queuing the post in `commons:marketing-hypothesis-ledger`.)
```

## What the composer refuses to do

- Draft a post without real underlying data or experience
- Submit to a sub below Tier B
- Exceed the mention budget for the sub's tolerance
- Produce identical content for multiple subs (every draft is native to its sub)
- Generate "thought leadership" with no verifiable content behind it
- Write in a voice that doesn't match the sub (e.g. casual ClaudeAI voice in r/cto)

## Quality checklist

- [ ] Subreddit loaded from audience list (Tier A or B only)
- [ ] Real data/experience provided by user (not abstract)
- [ ] Post-type matches sub culture per Step 2 table
- [ ] All applicable sub-specific rules enforced per Step 3 table
- [ ] Anti-sludge gate passed
- [ ] Mention budget respected per tolerance (Step 5)
- [ ] Draft file saved with correct date, sub, slug
- [ ] Pre-submit checklist populated for Ed's review
