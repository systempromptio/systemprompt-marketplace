---
name: reddit-monitor
description: "Daily multi-channel social-engagement briefing for AI governance positioning. Scans Reddit (daily) plus X/Twitter and forums (weekly), filters for AI governance / compliance / shadow-AI conversations aligned with the systemprompt ICP, and outputs a prioritised action list. Designed for daily /loop. Load identity and brand-voice first."
metadata:
  version: "1.1.0"
  git_hash: "5079c7a"
---

# Social Monitor (reddit-monitor)

Daily social-engagement briefing for systemprompt.io. Scans Reddit as the primary channel and sweeps X/Twitter and relevant forums on a weekly cadence. Output is a prioritised **action list** of concrete places to engage today, plus drafted replies ready for human review. Designed for daily execution via `/loop 1d`.

The skill name is kept as `reddit-monitor` for compatibility with existing `/loop` entries and the `reddit-reply` follow-up skill. It is, in practice, a multi-channel social monitor.

## Dependencies

**Load `identity` and `brand-voice` before this skill.** Identity defines what we say and to whom (AI governance infrastructure for CTOs at 20-500 person orgs). Brand voice defines how we sound. This skill handles channel discovery, scoring, and reply drafting.

## Channels and Cadence

| Channel | Scope | Cadence | Runs today? |
|---------|-------|---------|-------------|
| Reddit Tier A + B | Governance and practitioner subreddits | Daily | Always |
| Reddit Tier C | Broad signal subreddits | Weekly (Monday) | If today is Monday |
| X / Twitter | Keyword + author streams | Weekly (Wednesday) | If today is Wednesday |
| Forums (HN, Lobsters, LinkedIn, MLOps, ISACA) | High-leverage governance threads | Weekly (Friday) | If today is Friday |

On the first run after install, run **all** channels regardless of weekday so the user gets a full picture. After that, follow the cadence.

## Reddit Targets

### Tier A: governance and decision-makers (daily, highest priority)

| Subreddit | Focus | Tone |
|-----------|-------|------|
| r/cto | Build vs. buy, infrastructure decisions, team governance | Formal, strategic |
| r/ExperiencedDevs | Senior ICs handling AI rollout standards across teams | Technical, no-nonsense |
| r/ITManagers | Shadow AI, enforcement, audit trails, policy | Practical, governance-literate |
| r/sysadmin | Endpoint AI, policy enforcement, compliance headaches | Dry, operational |
| r/cybersecurity | Prompt injection, MCP risk, data exfiltration via AI tools | Rigorous, threat-model-aware |
| r/msp | Managed service providers reselling governance to SMEs | Business, margin-aware |
| r/compliance | Regulated orgs, EU AI Act, SOC2, audit trails | Formal, regulation-literate |
| r/devops | AI ops, pipeline governance, observability | Technical, pragmatic |
| r/mlops | Model lifecycle, evaluation, governance tooling | Deeply technical |

### Tier B: practitioner and technical (daily, where governance pain surfaces)

| Subreddit | Focus | Tone |
|-----------|-------|------|
| r/ClaudeAI | Claude-specific workflows, standardisation, team pain | Casual, fellow-user |
| r/AI_Agents | Multi-agent architecture, boundary enforcement | Technical, curious |
| r/LLMDevs | Prompt infra, eval, deployment | Technical |
| r/LocalLLaMA | Self-hosted, open-source ethos, sovereignty | Deeply technical, respect the ethos |
| r/PromptEngineering | Standardisation, prompt libraries, team patterns | Practitioner |
| r/RAG | Knowledge governance, access control, data lineage | Technical |

### Tier C: broad signal (weekly sweep, Monday only)

`r/artificial`, `r/singularity`, `r/OpenAI`, `r/Anthropic`, `r/SaaS`, `r/smallbusiness`, `r/Entrepreneur`. These are noisier and less on-ICP; scan for occasional high-signal threads but do not draft replies unless there is a clear governance angle.

## Part 1: Reddit Daily Scan

### Step 1.1: Fetch posts

**Use Reddit RSS, not JSON.** Reddit's `/new.json` endpoint is blocked for most automated clients with a "whoa there, pardner" network-policy page. The RSS endpoint returns an Atom feed and works reliably with a standard browser User-Agent.

For each subreddit in Tier A and Tier B (and Tier C on Mondays), fetch:

```
https://www.reddit.com/r/{subreddit}/new/.rss?limit=30
```

Fetch via `curl` in `bash` with an explicit User-Agent header (e.g. `-A "Mozilla/5.0 (compatible; systempromptbot/1.0)"`). `WebFetch` is blocked for `www.reddit.com` in some Claude Code environments, so `curl` is the primary path. Parallelise the fetches (`curl ... &` then `wait`) to stay under rate limits without serial delay; on large runs add a 1-2 second sleep between batches.

**Parsing:** each `<entry>` contains `<title>`, `<link href="...">`, `<content type="html">` (HTML-escaped body), `<author>`, and `<updated>`. Strip HTML tags from content for keyword filtering. There is no `score` or `num_comments` in RSS, that is a deliberate trade-off for reliability. Rank by keyword relevance and recency instead.

**Keyword filter (case-insensitive regex):** match posts whose title or body contains any of:
`ai`, `llm`, `gpt`, `chatgpt`, `claude`, `copilot`, `cursor`, `anthropic`, `openai`, `mcp`, `agent`, `prompt`, `shadow ai`, `rag`, `govern`, `polic`, `complian`, `audit`, `soc ?2`, `iso ?42001`, `eu ai`, `nist`, `endpoint`, `dlp`, `injection`, `standardi[sz]`, `rollout`, `observab`.

Discard posts that do not match. Everything that remains goes into Step 1.2.

### Step 1.2: Filter for governance relevance

Categorise each post. Skip posts that do not match.

| Category | Signals |
|----------|---------|
| Governance and Control | Team standards, observability, enforcement, permissions, multi-user AI |
| Shadow AI and Enforcement | Unsanctioned tools, discovery, policy, endpoint control, DLP |
| Compliance and Audit | EU AI Act, SOC2, ISO 42001, audit trails, regulated industries |
| Build vs. Buy | In-house AI infra vs. platforms, maintenance burden, roadmap risk |
| Agent Boundaries and Safety | Agent scope, permissioning, autonomous action risk, CLAUDE.md limits |
| MCP Security | MCP server trust, prompt injection via tools, scoping, sandboxing |
| Claude Workflow and Standardisation | Teams standardising Claude usage, shared skills, plugin distribution |

**Skip:**
- Pure memes, screenshots with no discussion
- Simple troubleshooting with an obvious answer
- Posts already answered thoroughly
- Posts older than the scan window

### Step 1.3: Score and rank

- **High:** post directly describes a problem systemprompt solves (governance, enforcement, compliance, standardisation, build-vs-buy) OR is a substantive technical discussion where we have genuine expertise.
- **Medium:** adjacent topic (Claude workflows, MCP, agent architecture) where we can add useful perspective.
- **Low:** tangentially related but there is something specific and valuable to contribute.

Select the **top 8 Reddit posts** for reply drafting. Prefer a mix of categories over clustering. Include 1 Tier A post at minimum.

Include **1 pure-person reply**: a post where someone is sharing a personal experience or venting, reply as a human not a brand. This keeps the engagement pattern natural.

### Step 1.4: Draft replies

**Structure:**
1. Open by engaging directly with the poster's specific situation. Reference their exact problem.
2. Provide value: concrete technical insight, useful perspective, or specific suggestion (2-4 sentences).
3. Close with a forward-looking thought, practical next step, or specific resource. Never close with a generic engagement question.

Typical length: 3-6 sentences. Longer only when warranted.

**Tone by subreddit:** match the tone column in the Tier A/B tables. r/cybersecurity and r/compliance want precise threat-model and regulation language. r/sysadmin wants dry, operational framing. r/LocalLLaMA wants respect for open-source sovereignty.

### Step 1.5: systemprompt mention rules

- ONLY mention systemprompt.io when the post is specifically about a problem systemprompt solves: governance, enforcement, standardisation, shadow-AI discovery, build-vs-buy, white-label AI for SaaS.
- **Maximum 30% of Reddit replies** may mention systemprompt. Flag each reply with `systemprompt mention: Yes/No`.
- When mentioned, it must be a natural part of the answer. Example: "systemprompt.io exists for this, it is self-hosted governance infrastructure that lets you enforce rules across every team using Claude instead of hoping CLAUDE.md files stay in sync." NOT: "Check out systemprompt.io for AI governance!"
- If the post does not involve a governance-adjacent problem, do not mention it. Period.

## Part 2: X / Twitter Weekly Sweep (Wednesdays)

No API access. Use public search URLs via `WebFetch`, or nitter mirrors if those fail.

### Keyword streams

Sample one or two posts per keyword (not exhaustive):
- `"AI governance"`, `"AI compliance"`, `"EU AI Act"`, `"shadow AI"`
- `"Claude enterprise"`, `"Claude Code"`, `"MCP security"`, `"AI audit trail"`, `"ISO 42001"`

### Author streams

Pull recent threads from governance-adjacent voices whose posts attract the right audience:
- `@jackclarkSF`, `@AnthropicAI`, `@simonw`, `@swyx`, `@AINowInstitute`, `@HelenToner`, `@dwarkesh_sp`
- CTO and VP-Eng voices as discovered (expand over time)

### Output

Select **3-5 reply-worthy threads** per weekly run. For each, produce the same draft-reply format as Reddit (open / value / close). Anti-sludge rules apply. No hashtags ever.

## Part 3: Forums Weekly Digest (Fridays)

| Forum | URL / entry point | Action type |
|-------|-------------------|-------------|
| Hacker News | `news.ycombinator.com/newest` + `/from?site=anthropic.com` + front-page keyword match | Reply / upvote / note |
| Lobsters | `lobste.rs/t/ai` + `/t/security` + `/t/practices` | Reply / note |
| MLOps Community | Public blog and newsletter threads (no private Slack quoting) | Note / reply on public posts |
| LinkedIn | Search "AI governance" + "Claude" from CTO/VP Eng authors | Reply with substance |
| ISACA public forums | Regulated-industry AI governance threads | Note / reply |
| CTO Craft | Public newsletter and blog replies | Note / reply |
| GitHub Discussions | Covered by `github-monitor`; link to it here for completeness | Cross-reference only |

Select **3-5 forum items** per weekly run. Hacker News is the highest-leverage single channel; one thoughtful HN reply on a trending thread beats a week of Reddit. Prioritise HN when a governance or Claude thread is live.

For each item, draft a reply or a one-line "why this matters and what to say" note if drafting a full reply is premature.

## Part 4: Daily Action List

Every run, emit a top-of-report **Action List** — a flat, prioritised checklist the user can work through in 30 minutes or less.

### Structure

```markdown
## Today's Action List

| # | Action | Channel | Target | Time | Mention |
|---|--------|---------|--------|------|---------|
| 1 | Reply to {poster} on {brief topic} | r/ITManagers | {permalink} | 10 min | Yes |
| 2 | Comment on HN thread about {topic} | HN | {url} | 15 min | No |
| ... |
```

### Rules

- Maximum **10 actions**. Less is fine if quality is low.
- Order by priority (High relevance + Tier A subreddit first, then HN, then others).
- Include at least **one Tier A Reddit item** if any scored High or Medium.
- On weekly-channel days, include at least one X or forum item.
- Each action must have: verb-first phrasing, channel, target URL, time estimate (5 / 10 / 15 min), `systemprompt mention: Yes/No`.
- Keep the 30% systemprompt-mention cap across the whole list, not per channel.
- Actions must map 1:1 to drafted replies below. If a reply is not drafted, the action is a "read-only / note" item.

## Anti-Sludge Rules (MANDATORY)

Applies to every drafted reply on every channel.

**Banned openings:**
- NO generic praise: "Great question", "Nice work", "Love this", "Awesome project"
- NO sludge greetings: "Hey there", "Thanks for sharing", "Fellow Claude user here", "As someone who..."
- NO opening with a question back to the poster

**Banned patterns:**
- NO em dashes anywhere. Use commas, periods, or parentheses.
- NO fabricated personal stories. Never "When I was building...", "I ran into this too", "In my experience..." unless Edward provided the actual story.
- NO AI cliches: revolutionize, game-changer, unlock, supercharge, seamlessly, cutting-edge, harness, next-generation, paradigm shift, disrupt, empower, leverage (as verb), reimagine, transform (without specifics)
- NO hashtags on any channel
- NO forced product mentions

**Quality standard:**
- Content must not read as AI-generated. Vary sentence length. Be specific.
- Each reply must be visibly personalised to the specific post.
- Read the reply as the poster. Would you find it genuinely helpful?

## Output Files

Write two files per run:

1. **Reddit section** (for `reddit-reply` compatibility):
   ```
   reports/reddit/daily/YYYY-MM-DD/reddit-monitor.md
   ```
   Contains the Reddit scan summary, categorised posts, and drafted Reddit replies in the legacy format.

2. **Combined action list** (new):
   ```
   reports/social/daily/YYYY-MM-DD/action-list.md
   ```
   Contains the Part 4 action list at the top, followed by the X and forum sections (if weekly cadence triggered), followed by a short Observations block.

Use today's date in both filenames.

## Report Template (action-list.md)

```markdown
# Social Monitor Action List

**Date:** {YYYY-MM-DD}
**Channels run today:** Reddit daily{, X weekly}{, Forums weekly}
**Subreddits scanned:** {N} | **Posts scanned:** {N} | **Reply targets:** {N}

---

## Today's Action List

{action table per Part 4}

---

## X / Twitter (weekly)

{3-5 threads with drafts, or "Not run today"}

---

## Forums (weekly)

{3-5 items with drafts or notes, or "Not run today"}

---

## Observations

- {Trending governance topics this period}
- {Subreddits with unusual activity}
- {Emerging pain points worth noting in future content}

---

See `reports/reddit/daily/{YYYY-MM-DD}/reddit-monitor.md` for the full Reddit scan and drafted replies.
```

## Quality Checklist

Before finalising, verify:

- [ ] No em dashes anywhere in the report or drafts
- [ ] No generic praise or sludge openings
- [ ] No fabricated personal stories
- [ ] No AI cliches
- [ ] No hashtags
- [ ] Nothing reads as AI-generated
- [ ] systemprompt mentioned in 30% or fewer replies, only where genuinely relevant
- [ ] Each reply directly addresses the specific post
- [ ] Tone matches the target channel
- [ ] Action list has at least one Tier A Reddit item (if any scored)
- [ ] On weekly-channel days, action list includes at least one X or forum item
- [ ] Aligns with `identity` (AI governance infrastructure, CTO-first)
- [ ] Aligns with `brand-voice` (value first, never pitch)
