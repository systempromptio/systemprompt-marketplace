---
name: linkedin-engine
description: "Daily interactive LinkedIn session: feed posts, DM outreach, prospect research, engagement tracking, and performance review. Human-in-the-loop. Designed for daily /loop."
metadata:
  version: "1.1.0"
  git_hash: "0000000"
---

# LinkedIn Engine

Daily interactive LinkedIn session for Ed. This is not an automation skill. It is a structured conversation that runs every day, covering content, outreach, engagement, and measurement. Ed executes every action manually. The skill provides drafts, tracks performance, manages the pipeline, and holds Ed accountable to the strategy.

Designed for daily execution via `/loop 1d marketing:linkedin-engine`.

## Dependencies (load in order)

1. `social-media:social-identity` — platform voice, engagement rules, banned patterns
2. `marketing:marketing-identity` — ICP, hook, channel rules
3. `commons:brand-voice` — LinkedIn-specific voice, algorithm context, post structure
4. `commons:identity` — product positioning for content pillars

Also read on first run:
- `/var/www/html/systemprompt-web/reports/marketing/drafts/enterprise-value-prop.md` — enterprise positioning and proof points
- `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — current phase, weekly theme, channel priorities

## Data Locations

All LinkedIn data lives under `/var/www/html/systemprompt-web/reports/marketing/data/linkedin/`:

```
data/linkedin/
  drafts/           LI-001.md, LI-002.md, ...  (draft queue)
  prospects.md      Prospect tracking table
  performance.jsonl Daily performance log (append-only)
  strategy.md       Living LinkedIn strategy doc (updated weekly)
```

Create this directory structure on first run if it does not exist.

## Run Modes

```
linkedin-engine                  # Full daily interactive session (default)
linkedin-engine draft            # Batch-generate a week of posts
linkedin-engine review           # Review and approve today's post
linkedin-engine track            # Performance check-in only
linkedin-engine dm               # DM outreach session only
linkedin-engine research         # Prospect research session
linkedin-engine weekly           # Full weekly review and planning
```

---

## LinkedIn Strategy (Researched, April 2026)

### Algorithm Reality

LinkedIn's 2026 "Depth Score" algorithm fundamentally changed content distribution:

- **Dwell time is king.** The algorithm measures how long users engage with content, not just whether they clicked. Long-form text that earns reading time outperforms short hot takes.
- **Personal profiles get 5-7x the organic reach of company pages.** Ed's personal profile is the primary distribution surface, not a company page.
- **External links reduce reach by ~60%.** Never put links in the post body. Links go in the first comment.
- **Comments are worth ~8x likes.** Content that provokes thoughtful comments gets exponentially more distribution.
- **AI-pattern content gets ~47% less reach.** Posts that read as AI-generated are actively suppressed. Every draft must be rewritten in Ed's voice before posting.
- **Carousels (PDF uploads) get 6.6% average engagement** — highest of any format. Use for frameworks, comparisons, and technical breakdowns.
- **First 60-90 minutes of engagement are critical.** Ed must be available to respond to comments immediately after posting.
- **3-5 hashtags maximum.** More than 5 correlates with 68% reduced reach. Prefer 0-3.
- **Zero-click content wins.** Provide the full value natively in the feed. Do not tease with "read more at my blog."

### Content Pillars (5)

Derived from the enterprise value prop and ICP pain points:

| # | Pillar | Angle | Example hook |
|---|--------|-------|-------------|
| 1 | **The visibility gap** | Your SOC has a blind spot. AI agents make tool calls, access APIs, process sensitive data — and none of it appears in your SIEM. | "Your security team monitors every API call in production. Except the ones made by AI agents." |
| 2 | **Governance is infrastructure** | AI governance is not a checklist or a policy doc. It is a runtime system that evaluates every tool call before execution. | "A governance policy that is not enforced at the tool-call level is a PDF, not a control." |
| 3 | **Own the binary** | Self-hosted, air-gapped, source-available. No data leaves your network. No vendor has access. | "We hand over a compiled binary and walk away. Your infrastructure. Your data. Your audit trail." |
| 4 | **The build trap** | You could build AI governance in-house. By the time you ship v1, the landscape has moved. | "I have talked to three CTOs this month who started building AI governance in Q1. All three are now evaluating commercial options." |
| 5 | **MCP is the governance surface** | MCP is not just a protocol for connecting tools. It is where governance happens — at the transport layer, not as a proxy. | "If your governance layer sits in front of MCP as a proxy, every tool call passes through unexamined. Governance must be the transport layer." |

### Posting Cadence (3x per week)

| Day | Type | Pillar rotation | Format |
|-----|------|----------------|--------|
| **Monday** | Thought leadership | Pillars 1-2 (visibility, governance) | Text post, 800-1300 chars |
| **Wednesday** | Technical depth | Pillars 3-5 (binary, build trap, MCP) | Carousel (PDF) or text with code |
| **Friday** | Personal/contrarian | Any pillar, personal angle | Text post, story format |

Rotate pillars across weeks so each pillar gets covered at least twice per month.

### Post Structure (mandatory)

1. **Hook** (line 1, under 150 chars): Contrarian claim, surprising number, or pattern-interrupt. Must earn the "see more" click. Never a question. Never "I'm excited to announce."
2. **Body** (3-5 short paragraphs): One idea per paragraph. Short sentences. Mobile-formatted with line breaks between paragraphs. Specific details — names, numbers, architecture decisions.
3. **Closing**: Strong final statement or specific observation. Never "What do you think?" or "Agree?". If there is a CTA, it is specific: "Clone the template and run the demo scripts."
4. **First comment** (posted immediately after): External link + one sentence of context. This is the only place links appear.

### Anti-Patterns (hard rules)

- NEVER include external links in the post body
- NEVER use hashtags in the hook line
- NEVER end with generic engagement questions ("Thoughts?", "Agree or disagree?")
- NEVER post content that reads as AI-generated (no "delve", "landscape", "game-changer")
- NEVER post the same content to LinkedIn and X — force variation
- NEVER post more than once per day
- NEVER use more than 3 hashtags (prefer 0)
- NEVER fabricate stories, statistics, or case studies

### Voice (Ed's LinkedIn voice)

- First person, direct, confident
- British English (realise, optimise, organisation)
- Personal experience framing: "I built", "I learned", "I talked to"
- Sardonic humour where natural
- Infrastructure-level thinking — systems, standards, architecture
- Genuine excitement about things that work, honest frustration about things that do not
- Specific: names of tools, exact numbers, concrete architecture decisions

---

## Daily Session Structure

When `linkedin-engine` runs (default mode), execute these steps as an interactive conversation with Ed. Each step requires Ed's input before proceeding.

### Step 1: Performance Check-in

Ask Ed to paste yesterday's post metrics (if a post was published yesterday):

```
Yesterday's post: {LI-###}
- Impressions: ___
- Likes: ___
- Comments: ___
- Reposts: ___
- Link clicks (first comment): ___
- Profile views (if available): ___
```

Log the data to `data/linkedin/performance.jsonl`:

```json
{"date":"2026-04-16","post_id":"LI-001","impressions":0,"likes":0,"comments":0,"reposts":0,"link_clicks":0,"profile_views":null,"notes":""}
```

If no post was published yesterday, skip. If Ed does not have metrics yet (too early), note and move on.

### Step 2: Queue Status

Read `data/linkedin/drafts/` and show:

```
Draft queue: {N} posts queued, {M} scheduled, {K} posted
Next scheduled: LI-{###} for {day} — "{first 50 chars of hook}"
Gaps: {list any days in the next 7 without a scheduled post}
```

If the queue has fewer than 3 posts, flag: "Queue is running low. Run `linkedin-engine draft` to batch-generate."

If today is **Monday** and the queue has fewer than 3 posts for this week, automatically enter draft mode and generate posts for Mon/Wed/Fri.

### Step 3: Today's Post Review

If a post is scheduled for today:

1. Show the full draft
2. Ask Ed: "Post as-is, edit, or skip?"
3. If Ed edits, update the draft file
4. If Ed approves: mark as `status: ready` and remind Ed to post manually on LinkedIn
5. After Ed posts: Ed says `posted LI-{###}` and the skill updates `status: posted`, `posted_at: {now}`

If no post is scheduled for today, say so and move on.

### Step 4: Engagement Check

Ask Ed:

```
Any comments on recent posts that need replies?
Any DMs received that need response?
Any connection requests from ICP-matching profiles?
```

If yes: help draft replies. Replies follow the same voice rules — specific, helpful, no self-promotion unless directly asked.

### Step 5: DM Outreach (if active)

Read `data/linkedin/prospects.md`. If there are prospects with `Status: ready`:

1. Show the next prospect: name, title, company, signal
2. Draft a personalised DM (see DM rules below)
3. Ed reviews, edits, approves
4. After Ed sends: Ed says `sent` and the skill updates the prospect row

Maximum 3 DMs per day. If 3 have been sent today, skip.

### Step 6: Pipeline Summary

Show a one-line summary:

```
Posts: {posted}/{scheduled}/{queued} | DMs: {sent}/{total prospects} | Replies: {pending}
This week: {N} posts published, {M} DMs sent, {K} comments replied to
```

### Step 7: Weekly Actions (Monday and Friday only)

**Monday:** Batch-generate 3 posts for the week (Mon/Wed/Fri). Enter draft mode automatically.

**Friday:** Weekly performance review:
- Compare this week's total impressions, likes, comments vs last week
- Identify best-performing post and why
- Score any LinkedIn hypotheses whose windows close this week
- Adjust content pillars if data shows one pillar consistently underperforms
- Update `data/linkedin/strategy.md` with lessons

---

## Draft Generation (`linkedin-engine draft`)

Generate 3-5 posts in a single session. For each post:

1. **Select pillar** — rotate across the 5 pillars, avoiding repeats from the last 3 posts
2. **Select type** — match to the scheduled day (thought leadership Mon, technical Wed, personal Fri)
3. **Research** — search the web for recent news, announcements, or discussions related to the pillar. Ground the post in something current and specific.
4. **Write the draft** — follow post structure rules. Under 1,300 characters for text posts.
5. **Write the first comment** — link + context sentence
6. **Create the hypothesis** — each post gets an H-### from the hypothesis ledger

Save each draft to `data/linkedin/drafts/LI-{###}.md`:

```markdown
---
id: LI-001
status: queued
scheduled_for: 2026-04-17
pillar: 1
type: thought-leadership
hypothesis: H-012
created_at: 2026-04-16
posted_at: null
impressions: null
likes: null
comments: null
reposts: null
link_clicks: null
---

{post body}

---
**First comment:** {link + context}
```

### Draft Quality Rules

- Every post must contain at least one specific detail (a number, a tool name, an architecture decision, a company name, a date)
- No two consecutive posts from the same pillar
- No post should be publishable without Ed reading and approving it — drafts are starting points, not final copy
- If the post references a guide or repo, verify the URL exists before including it
- Read Ed's actual LinkedIn profile and recent posts (if available) to match his voice

---

## DM Outreach

### Prospect Research (`linkedin-engine research`)

Guide Ed through building the prospect list. The skill:

1. **Define search criteria** from marketing-identity ICP2:
   - Title: Head of AI, VP Engineering, Platform Engineering Lead, CTO
   - Company size: 50-500 employees
   - Signal: public post about Claude/AI rollout, job listing mentioning Claude, comment on governance thread, conference talk about AI standardisation

2. **Suggest search queries** for LinkedIn:
   - `"head of AI" "claude" -recruiter`
   - `"VP engineering" "AI governance" OR "AI rollout"`
   - `"platform engineering" "claude code" OR "MCP"`
   - People who commented on Anthropic's official posts
   - People who posted about Microsoft Agent Governance Toolkit

3. **For each prospect Ed finds**, capture in `data/linkedin/prospects.md`:

```markdown
| # | Name | Title | Company | Size | Signal | Status | Contacted | Reply | Notes |
|---|------|-------|---------|------|--------|--------|-----------|-------|-------|
| 1 | | | | | | ready | | | |
```

Status values: `research` → `ready` → `connected` → `messaged` → `replied` → `converted` → `dead`

Target: 20 prospects in the initial list. Refresh monthly.

### DM Rules

- **Maximum 3 DMs per day.** Quality over volume.
- **Engage before messaging.** Before sending a DM, Ed should have liked or commented on at least one of the prospect's posts. The DM should not be the first interaction.
- **Personalise on the signal.** Reference the specific post, job listing, or comment that made them a prospect. Never generic.
- **One message only.** No follow-up sequences. No "just checking in." If they do not reply, they are not interested.
- **Link to the template repo**, not the website. The repo is tangible and evaluable. The website is marketing.
- **Ask one question.** Not a pitch. A question that demonstrates understanding of their specific situation.
- **Under 300 characters.** LinkedIn DMs that are too long do not get read.
- **Connection request first** with a personalised note (under 300 chars). DM only after they accept.

### DM Template (starting point, always personalise)

```
Hi {name}, I saw your {post about X / job listing for Y / comment on Z}.

I built something related — a self-hosted governance layer for Claude Code deployments. Single binary, PostgreSQL, air-gapped.

Would a 10-minute walkthrough of the template repo be useful?

github.com/systempromptio/systemprompt-template
```

Ed must rewrite every DM. This template is a structure, not copy-paste.

### Connection Request Note Template

```
{Name} — your {post/comment} about {specific topic} resonated.
Building AI governance infra in Rust. Would value connecting.
```

Under 300 characters. Always reference something specific.

---

## Performance Tracking

### Daily Metrics (manual, Ed pastes during check-in)

| Metric | Source | Frequency |
|--------|--------|-----------|
| Post impressions | LinkedIn post analytics | Daily |
| Likes | LinkedIn post analytics | Daily |
| Comments | LinkedIn post analytics | Daily |
| Reposts | LinkedIn post analytics | Daily |
| Link clicks (first comment) | LinkedIn post analytics | Daily |
| Profile views | LinkedIn dashboard | Weekly (Monday) |
| Connection requests received | LinkedIn dashboard | Weekly (Monday) |
| DMs sent | Prospect table | Daily |
| DM replies received | Prospect table | Daily |
| Search appearances | LinkedIn dashboard | Weekly (Monday) |

### Performance Log

Append daily to `data/linkedin/performance.jsonl`:

```json
{
  "date": "2026-04-16",
  "post_id": "LI-001",
  "impressions": 0,
  "likes": 0,
  "comments": 0,
  "reposts": 0,
  "link_clicks": 0,
  "profile_views": null,
  "connection_requests": null,
  "search_appearances": null,
  "dms_sent": 0,
  "dm_replies": 0,
  "notes": ""
}
```

### Weekly Review Metrics (Friday)

| Metric | This week | Last week | Delta |
|--------|-----------|-----------|-------|
| Total impressions | | | |
| Total engagement (likes + comments + reposts) | | | |
| Avg engagement rate | | | |
| Profile views | | | |
| Connection requests | | | |
| DMs sent | | | |
| DM reply rate | | | |
| Best post (by impressions) | | | |
| Best post (by comments) | | | |

### Targets (Phase 1: first 30 days)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Posts per week | 3 | Mon/Wed/Fri cadence |
| Avg impressions per post | 500+ | Baseline for a new consistent poster |
| Avg engagement rate | 2%+ | Industry average for B2B thought leadership |
| Profile views per week | 100+ | Signal of growing visibility |
| DMs sent per week | 10-15 | 3/day, 5 days |
| DM reply rate | 20%+ | LinkedIn InMail benchmarks are 10-25% |
| Prospects in pipeline | 20 | Initial research target |

Recalibrate after 30 days against actual data.

---

## Hypothesis Integration

Every LinkedIn post and DM batch gets logged to the hypothesis ledger:

**Feed posts:**
```
hypothesis-ledger log {
  channel: "linkedin",
  action: "Published LI-{###}: '{hook first 50 chars}'",
  hypothesis: "If we post {pillar} content on LinkedIn then linkedin_impressions_7d rises from {baseline} to {target} within 7d",
  metric: "linkedin_impressions_7d",
  baseline: {current},
  window_end: {+7d}
}
```

**DM batches:**
```
hypothesis-ledger log {
  channel: "linkedin",
  action: "Sent {N} personalised DMs to ICP2 prospects",
  hypothesis: "If we DM {N} ICP2 prospects then dm_reply_rate rises above 20% within 14d",
  metric: "linkedin_dm_reply_rate",
  baseline: {current},
  window_end: {+14d}
}
```

---

## First Run Checklist

On the very first run of this skill:

1. Create `data/linkedin/` directory structure
2. Create empty `prospects.md` with table headers
3. Create empty `performance.jsonl`
4. Create `strategy.md` with initial strategy (copy the strategy section from this skill)
5. Read Ed's current LinkedIn profile and recent posts (Ed shares URL)
6. **Batch-generate 5 initial posts** covering all 5 pillars
7. **Start prospect research** — guide Ed through building the first 10 prospects
8. Schedule the first week: Mon/Wed/Fri posts assigned from the queue

---

## Anti-Sludge Rules

- **No vague prose.** "Engagement is growing" is banned. "LI-003 got 847 impressions and 12 comments vs LI-002's 312 impressions and 2 comments" is required.
- **No motivational language.** No "great progress", "keep it up", "building momentum."
- **No emojis** anywhere.
- **No actions without a hypothesis.** If you cannot state the hypothesis, cut the action.
- **Fail loudly.** If Ed has not posted in 5+ days, the first line of the session says so. Do not bury it.
- **The session is for Ed's eyes only.** It is an operator's dashboard, not a social media artifact.
- **Respect Ed's time.** The full daily session should take under 15 minutes. If it is running long, cut to essentials: check-in, today's post, done.
