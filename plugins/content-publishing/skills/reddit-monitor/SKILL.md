---
name: reddit-monitor
description: "Monitor target subreddits for reply opportunities, filter for relevance to AI governance and Claude workflows, and draft personalized replies. Designed for daily /loop. Load identity and brand-voice first."
metadata:
  version: "1.0.2"
  git_hash: "bc2a4a3"
---

# Reddit Monitor

Scan target subreddits, find high-value reply opportunities, and draft personalized replies. Designed for daily execution via `/loop 1d`. Output is a structured report with links and draft replies ready for human review.

## Dependencies

**Load `identity` and `brand-voice` before this skill.** Identity defines what we say and to whom. Brand voice defines how we sound. This skill handles Reddit discovery and reply drafting.

## Subreddits

| Priority | Subreddit | Typical Tone | Focus |
|----------|-----------|-------------|-------|
| Primary | r/ClaudeAI | Casual, technical, fellow-user | Claude usage, plugins, skills, workflows |
| Primary | r/Anthropic | Technical, product-focused | Anthropic products, API, enterprise features |
| Secondary | r/artificial | Mixed technical and general | Broader AI trends, governance, adoption |
| Secondary | r/SaaS | Business-oriented | SaaS tooling, AI for business, team workflows |
| Secondary | r/CTO | Formal, strategic | Infrastructure decisions, team governance, build vs. buy |
| Secondary | r/LocalLLaMA | Deeply technical, open-source ethos | Local models, self-hosted AI, model comparisons |

## Step 1: Fetch Posts

For each subreddit, fetch recent posts using Reddit's public JSON API:

```
https://www.reddit.com/r/{subreddit}/new.json?t=day&limit=50
```

Use `WebFetch` if available, otherwise fall back to `bash curl`. Add a 2-second delay between subreddit requests to respect rate limits.

On weekly runs (or first run), use `?t=week` instead of `?t=day`.

From each post, extract: `title`, `selftext`, `url`, `permalink`, `author`, `created_utc`, `score`, `num_comments`, `subreddit`.

## Step 2: Filter for Relevance

Categorise each post into one of these categories. Skip posts that do not match any category.

| Category | Signals |
|----------|---------|
| Plugin/Setup | Claude plugins, skills, installation, configuration, team standardisation |
| MCP Servers | MCP protocol, server setup, tool configuration, MCP security |
| Agents | Agent architecture, multi-agent systems, agent workflows, Agent SDK |
| Marketplace | Sharing, distributing, or discovering AI tools, plugins, skills |
| AI Governance | Team AI adoption, standards, control, observability, compliance |
| Build vs. Buy | Building AI infrastructure in-house vs. using platforms, maintenance burden |
| General Workflow | Claude Code productivity, prompting, project setup, best practices |

**Skip these posts:**
- Pure memes or screenshots with no discussion
- Simple troubleshooting with obvious answers ("Claude won't load", "API key not working")
- Posts already answered thoroughly by multiple commenters
- Posts older than the scan window

## Step 3: Score and Rank

Assign a relevance score to each post:

**High**: Post directly discusses a problem systemprompt solves (governance, plugin distribution, team standardisation) OR is a substantive technical discussion where we have genuine expertise to contribute.

**Medium**: Post touches on adjacent topics (Claude workflows, MCP, agent architecture) where we can add useful perspective.

**Low**: Post is tangentially related but we can still contribute something specific and valuable.

Select the **top 10** highest-scoring posts for reply drafting. Prefer a mix of categories over clustering in one topic.

**Include 1-2 pure person replies.** Not every reply should be about content or products. Find 1-2 posts where someone is sharing a personal experience, asking for encouragement, or just venting about AI tooling. Reply as a human being, not as a brand. This makes the overall reply pattern look natural and avoids the appearance of only engaging when there is something to promote.

## Step 4: Draft Replies

### Reply Structure

1. **Open** by directly engaging with the poster's specific situation. Reference their exact problem, question, or observation.
2. **Provide value** with actionable technical insight, a useful perspective, or a concrete suggestion (2-4 sentences).
3. **Close** with a forward-looking thought, practical next step, or specific resource. Never close with a generic engagement question.

Typical length: 3-6 sentences. Go longer only when the topic genuinely warrants depth.

### Tone by Subreddit

- **r/ClaudeAI**: Casual, first-person where authentic. Short paragraphs. Fellow-user energy.
- **r/Anthropic**: Slightly more formal, product-aware. Acknowledge Anthropic's roadmap where relevant.
- **r/artificial**: Accessible but informed. Broader AI context welcome.
- **r/SaaS**: Business language. ROI, efficiency, team workflows. Less code, more outcomes.
- **r/CTO**: Formal, strategic. Infrastructure thinking. Governance and standards language.
- **r/LocalLLaMA**: Deeply technical. Respect the open-source ethos. Never dismissive of local models.

### systemprompt Mention Rules

- ONLY mention systemprompt.io when the post is specifically about a problem systemprompt solves: plugin distribution, team governance, skill marketplaces, standardising Claude usage across teams.
- **Maximum 3 out of 10 replies** may mention systemprompt (30% cap). Flag each reply with "systemprompt mention: Yes/No" in the report.
- When mentioned, it must be a natural part of the answer. Example: "systemprompt.io was built around this use case, it lets teams standardise and distribute plugins as installable packages." NOT: "Check out systemprompt.io for all your AI governance needs!"
- If the post does not involve a problem systemprompt solves, do not mention it. Period.

### Anti-Sludge Rules (MANDATORY)

Every reply must pass these checks. No exceptions.

**Banned openings:**
- NO generic praise: "Great question!", "Nice work!", "This is really interesting!", "Love this!", "Awesome project!"
- NO sludge greetings: "Hey there!", "Thanks for sharing!", "Fellow Claude user here!", "As someone who..."
- NO opening with a question back to the poster

**Banned patterns:**
- NO em dashes anywhere. Use commas, periods, or parentheses.
- NO fabricated personal stories or analogies presented as real experiences. Never write "When I was building...", "I ran into this too...", or "In my experience..." unless Edward provides the actual story. Use generic examples or clearly hypothetical scenarios instead.
- NO AI cliches: revolutionize, game-changer, unlock, supercharge, seamlessly, cutting-edge, harness, next-generation, paradigm shift, disrupt, empower, leverage (as verb), reimagine, transform (without specifics)
- NO hashtags
- NO forced product mentions. If systemprompt is not genuinely relevant to the post, do not shoehorn it in.

**Quality standard:**
- Content must NOT read as AI-generated. Vary sentence length. Be specific. Include observations only someone building in this space would make.
- Each reply must be visibly personalised to the specific post. A reply that could apply to any similar post is too generic.
- Read the reply as if you are the poster. Would you find it genuinely helpful, or would you scroll past it?

## Step 5: Generate Report

Output the report in this format:

```markdown
# Reddit Monitor Report

**Date:** {YYYY-MM-DD}
**Window:** Last 24 hours | Last 7 days
**Subreddits:** r/ClaudeAI, r/Anthropic, r/artificial, r/SaaS, r/CTO, r/LocalLLaMA
**Posts scanned:** {N} | **Relevant:** {N} | **Reply targets:** {N}

---

## Reply Targets

### 1. "{Post Title}"
- **Subreddit:** r/{subreddit}
- **URL:** https://reddit.com{permalink}
- **Category:** {category}
- **Relevance:** High | Medium
- **systemprompt mention:** Yes | No

**Draft reply:**

> {The drafted reply text, properly formatted}

---

(repeat for each target)

## Summary

| Category | Posts Found |
|----------|-----------|
| Plugin/Setup | {N} |
| MCP Servers | {N} |
| Agents | {N} |
| Marketplace | {N} |
| AI Governance | {N} |
| Build vs. Buy | {N} |
| General Workflow | {N} |

## Observations

- {Trending topics or recurring themes this period}
- {Subreddits with unusually high or low activity}
- {Emerging questions or pain points worth noting}
```

**Save the report to:**

```
reports/reddit/YYYY-MM-DD/reddit-monitor.md
```

Use today's date in the filename.

## Quality Checklist

Before finalising the report, verify every reply against:

- [ ] No em dashes
- [ ] No generic praise or sludge openings
- [ ] No fabricated personal stories or analogies
- [ ] No AI cliches
- [ ] No hashtags
- [ ] Does not read as AI-generated
- [ ] systemprompt mentioned in 30% or fewer replies
- [ ] systemprompt only mentioned where genuinely relevant
- [ ] Each reply directly addresses the specific post content
- [ ] Tone matches the target subreddit
- [ ] Aligns with `identity` positioning (governance infrastructure)
- [ ] Aligns with `brand-voice` Reddit strategy (value first, never pitch)
