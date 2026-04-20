---
name: reddit-monitor
description: "Daily Reddit-only opportunity scanner. Reads the qualified subreddit list from reddit-audience-finder, fetches hot and new threads from each, scores each thread for engagement value, and outputs a ranked action list with draft reply hooks. Reply follow-ups are handled by reddit-reply. Load social-identity, identity, and brand-voice first."
metadata:
  version: "2.0.0"
  git_hash: "pending"
---

# Reddit Monitor (opportunity scanner)

Daily Reddit-only skill. Scans the subreddits qualified by `reddit-audience-finder` and outputs a ranked list of engagement opportunities — threads where a substantive reply is achievable today. Designed for `/loop 1d`.

This skill replaces the previous multi-channel monitor. X/Twitter and forums are handled elsewhere. Keep the concern pure: Reddit opportunities, Reddit drafts.

Fresh top-level posts are handled by `reddit-post-composer`. Comment follow-ups are handled by `reddit-reply`. This skill is the bridge between audience and action.

## Dependencies

Load in order:

1. `social-media:social-identity` — voice + banned patterns + 30% mention cap
2. `commons:identity` — ICP and positioning
3. `commons:brand-voice` — tone rules

If `reports/social/reddit/audience/subreddits.json` does not exist, instruct the user to run `reddit-audience-finder` first and abort.

## Reddit data access

Use `curl` in `bash` with a browser User-Agent. `WebFetch` may be blocked for `www.reddit.com` in some environments.

```bash
UA="Mozilla/5.0 (compatible; systempromptbot/1.0)"
curl -s -A "$UA" "https://www.reddit.com/r/$SUB/hot.json?limit=25"
curl -s -A "$UA" "https://www.reddit.com/r/$SUB/new.json?limit=25"
```

Parallelise across subs with `&` + `wait`. Sleep 0.3s between batches.

## Cadence

| Tier | Frequency |
|---|---|
| Tier A | Every run (daily) |
| Tier B | Every run (daily) |
| Tier C | Monday only |

Tier assignments come from `reports/social/reddit/audience/subreddits.json`. Never hard-code a sub list in this skill.

## Step 1: Load audience

Read `reports/social/reddit/audience/subreddits.json`. If older than 120 days, emit a warning: the list is likely stale, recommend re-running `reddit-audience-finder`.

## Step 2: Fetch hot + new for each qualified sub

For each Tier A, B, and (on Monday) C sub, pull both endpoints. `hot.json` catches peaked threads; `new.json` catches threads before they saturate.

Merge, dedupe by post ID, and keep the following fields per thread:

- `permalink`, `url`, `title`, `selftext[:800]`
- `num_comments`, `score`, `upvote_ratio`
- `created_utc`, `author`
- `subreddit`
- `link_flair_text`

Discard threads older than 48 hours unless `num_comments >= 100` and the conversation is still moving.

## Step 3: Relevance filter (drop most threads)

Keep a thread only if title OR selftext matches a governance-adjacent keyword:

`ai, llm, gpt, chatgpt, claude, copilot, cursor, anthropic, openai, mcp, agent, prompt, shadow ai, rag, govern, polic, complian, audit, soc ?2, iso ?42001, eu ai, nist, endpoint, dlp, injection, standardi[sz], rollout, observab, self-host, air-gap, cost, policy, permission, skill, plugin, hook`

Discard everything else. Typical retention: 8–15% of fetched threads.

## Step 4: Score each surviving thread (0–100)

Four dimensions, 25 points each:

### D1: Topical fit (25)

| Signal | Points |
|---|---|
| Thread is about governance/compliance/audit/shadow-AI/standardisation | 25 |
| Thread is about Claude Code / MCP / agents at team scale | 20 |
| Thread is Claude / LLM technical discussion | 12 |
| Thread is adjacent (AI ops, dev infra) | 6 |
| Tangential | 0 |

### D2: Opportunity freshness (25)

| `num_comments` | Points |
|---|---|
| 2–20 | 25 (still readable, we can land early) |
| 20–80 | 18 (saturating but not drowned) |
| 80–200 | 10 |
| > 200 | 5 (we'll be buried) |
| 0–1 | 12 (maybe too early, low engagement signal) |

### D3: Poster quality (25)

Proxy from selftext:

| Signal | Points |
|---|---|
| Poster describes specific setup (team size, tools, numbers) | 25 |
| Poster asks a clear technical question | 18 |
| Poster is venting with useful context | 12 |
| Poster is asking vague "best way to..." | 5 |
| Poster is self-promoting or low-effort | 0 |

### D4: Our authority (25)

Can we add value the thread doesn't already have? Check comments via `{permalink}.json` if uncertain. Avoid threads where the answer is already given thoroughly.

| Signal | Points |
|---|---|
| We have direct experience (governance infra, Claude at team scale, MCP transport) AND the good answer is missing | 25 |
| We have adjacent experience | 15 |
| We have a fresh angle others haven't taken | 10 |
| We'd be restating existing top comment | 0 |

Sum to a total. Select the top **8 threads** for the action list. Enforce variety:

- At least 1 Tier-A thread if any scored ≥ 50
- No more than 3 threads from the same sub
- Mix post-types (technical, venting, strategic)

## Step 5: Draft reply hooks

For each selected thread, draft a reply. Hook, not essay.

**Structure (3–6 sentences):**

1. Open with the poster's specific situation. Reference their exact setup or problem.
2. Provide value: concrete technical insight, specific suggestion, or a relevant distinction (2–4 sentences).
3. Close with a forward-looking thought, a specific next step, or a tangible resource. Never a generic engagement question.

**Tone matching (from subreddits.json `tone` field):**

- `r/cto`, `r/compliance` — formal, strategic, regulation-literate
- `r/ExperiencedDevs`, `r/devops` — technical, no-nonsense
- `r/sysadmin` — dry, operational
- `r/cybersecurity` — rigorous, threat-model-aware
- `r/ITManagers`, `r/msp` — business-practical, margin-aware
- `r/ClaudeAI`, `r/AI_Agents` — casual fellow-user, evidence-valued
- `r/LocalLLaMA`, `r/selfhosted` — deeply technical, respect for open-source sovereignty
- `r/LLMDevs`, `r/RAG` — practitioner, sources-required

## Step 6: Mention cap (30%)

Across the final action list, no more than **30% of drafts** may mention systemprompt.io. A mention only happens when the thread is specifically about a problem systemprompt solves: governance, enforcement, standardisation, shadow-AI discovery, build-vs-buy, self-hosted AI infra for teams.

Flag each action: `mention: Yes` or `mention: No`.

When mentioned, make it a natural part of the answer, not an insertion: "systemprompt.io is self-hosted governance for this — one binary, you run it, Claude tool-calls go through your policy hooks before execution." Never: "Check out systemprompt.io!"

## Step 7: Anti-sludge gate

Applies to every drafted reply.

**Banned openings:**
- "Great question", "Nice work", "Love this", "Fellow Claude user here", "Hey there", "Thanks for sharing"
- Any opening that is a question back to the poster

**Banned patterns:**
- Em dashes anywhere (use commas, periods, parentheses)
- Fabricated personal stories (no "I ran into this too" unless Ed actually did)
- AI clichés: revolutionize, game-changer, unlock, supercharge, seamlessly, harness, cutting-edge, next-generation, paradigm shift, disrupt, empower, leverage (verb), reimagine, transform
- Hashtags
- Forced product mentions

**Quality standard:**
- Reply must not read as AI-generated. Vary sentence length. Be specific.
- Each reply is visibly personalised to the specific post — reference a concrete detail they wrote.
- Read the reply as the poster. Would you find it genuinely helpful or is it sludge?

## Step 8: Output

Write two files per run.

### 1. `reports/social/reddit/daily/YYYY-MM-DD/opportunities.md`

The scored opportunity list. Structure:

```markdown
# Reddit Opportunities — YYYY-MM-DD

**Tiers scanned:** A ({N} subs), B ({N} subs){, C ({N} subs) if Monday}
**Threads fetched:** {N} | **Passed relevance filter:** {N} | **Selected:** {top 8}
**Mention count:** {X}/{total} drafts ({percent}%, cap 30%)
**Audience list age:** {days since reddit-audience-finder last ran}

---

## Top 8 opportunities

| # | Score | Sub | Title (truncated) | Comments | Mention | Time |
|---|---|---|---|---|---|---|
| 1 | 86 | r/ITManagers | Network manager building AI assistant... | 9 | Yes | 10 min |
| ... |

---

## Drafted replies

### 1. r/ITManagers — "New Network Manager trying to build an AI assistant"

- **Permalink:** {full URL}
- **Score breakdown:** topical_fit=20, freshness=25, poster_quality=18, authority=23 → total 86
- **Poster context:** {one-line summary of what they actually said}
- **Our angle:** {the specific value we add}
- **systemprompt mention:** Yes / No
- **Draft:**

> {3–6 sentence reply}

- **Post-reply action:** log to hypothesis ledger as H-### if this is a seeded experiment

{repeat for each of 8}
```

### 2. `reports/social/reddit/daily/YYYY-MM-DD/reddit-monitor.md`

Kept for `reddit-reply` compatibility. Same content as `opportunities.md` in the legacy format the reply skill expects. Both files until `reddit-reply` is updated to read `opportunities.md`.

## Quality checklist

- [ ] `reports/social/reddit/audience/subreddits.json` loaded successfully
- [ ] Audience list is < 120 days old (else warning logged)
- [ ] Tier-A subs always scanned; Tier-C only on Mondays
- [ ] Every selected thread has a dimensions breakdown
- [ ] No thread repeats across drafts (check by permalink)
- [ ] No more than 3 drafts from one sub
- [ ] Mention cap ≤ 30% across the list
- [ ] Anti-sludge gate passes on every draft
- [ ] Tone matches the sub's tone field
- [ ] Both output files written with today's date
