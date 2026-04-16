---
name: x-twitter-engine
description: "Daily X/Twitter session: thread creation, engagement, prospect following, and performance tracking. 4-week test protocol with clear pass/fail criteria. Human-in-the-loop. Designed for daily /loop."
metadata:
  version: "1.0.0"
  git_hash: "0000000"
---

# X/Twitter Engine

Daily interactive X/Twitter session for Ed. Structured conversation covering thread creation, engagement, and measurement. Ed executes every action manually. The skill provides drafts, tracks performance, and manages the 4-week test protocol.

This skill exists to properly test X/Twitter as a channel. It has a built-in 4-week test protocol with clear pass/fail criteria. If the test fails, this skill is deactivated and time is reallocated.

Designed for daily execution via `/loop 1d social-media:x-twitter-engine`.

## Dependencies (load in order)

1. `social-media:social-identity` — platform voice, engagement rules, banned patterns
2. `commons:identity` — product positioning for content pillars
3. `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — current channel priorities and test protocol

Also read on first run:
- `marketing:marketing-identity` — ICP, template hook, hypothesis format
- `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — current phase, weekly theme

## Data Locations

All X/Twitter data lives under `/var/www/html/systemprompt-web/reports/x-twitter/`:

```
x-twitter/
  threads/          XT-001.md, XT-002.md, ...  (thread drafts and posted threads)
  performance.jsonl Daily performance log (append-only)
  test-scorecard.md 4-week test tracking document
```

Create this directory structure on first run if it does not exist.

## Run Modes

```
x-twitter-engine              # Full daily session (default)
x-twitter-engine draft        # Batch-generate threads
x-twitter-engine engage       # Engagement session only (replies, quote-tweets)
x-twitter-engine track        # Performance check-in only
x-twitter-engine weekly       # Weekly review
x-twitter-engine scorecard    # Show 4-week test progress
```

---

## X/Twitter Strategy

### The Test Protocol

X/Twitter is an unproven channel for systemprompt.io. This skill runs a 4-week structured test to determine whether X deserves ongoing investment.

**Test start date:** Set on first run. Recorded in `test-scorecard.md`.

**Weekly targets during test:**
| Metric | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| Threads posted | 5 | 5 | 5 | 5 |
| Engagement replies | 50 | 50 | 50 | 50 |
| ICP accounts followed | 25 | 25 | 10 | 10 |
| Quote-tweets | 5 | 5 | 5 | 5 |

**Pass criteria (after 4 weeks, at least ONE):**
- >50 link clicks to systemprompt.io from X
- >5 meaningful conversations with ICP-matching accounts (VP Eng, Head of AI, CTO at 50-500 person companies)
- >1 lead attributable to X (clone + feedback traceable to X referral)

**Fail criteria (ALL of these):**
- <50 link clicks
- <5 meaningful ICP conversations
- 0 attributable leads

→ Deactivate this skill. Reallocate time to LinkedIn outbound and SEO.

### Content Format

**Threads (primary format):**
1. **Hook tweet** (under 250 chars): Contrarian observation, surprising number, or pattern-interrupt about AI governance. Must earn the "show more" expansion.
2. **Body tweets** (3-5 tweets): One idea per tweet. Short sentences. Specific details. Each tweet must be comprehensible on its own while building a narrative.
3. **Closing tweet**: Strong final statement. Link to template repo or guide in a reply to this tweet, not in the tweet itself.

**Quote-tweets:**
- Add perspective to Anthropic, MCP, or AI governance news
- Never just "This is great" or "Interesting"
- Add a specific, non-obvious observation
- Under 200 chars of added commentary

**Replies:**
- Engage with AI governance, Claude, and MCP conversations
- Provide concrete value (specific technical insight, useful perspective)
- 1-3 sentences max
- Only mention systemprompt if directly relevant (30% cap applies)

### Content Pillars (adapted for X)

| # | Pillar | X-specific angle | Example hook tweet |
|---|--------|-----------------|-------------------|
| 1 | Visibility gap | One-line observations about ungoverned AI | "Every API call in your stack has monitoring. Except the ones your AI agents make." |
| 2 | Governance as infrastructure | Technical specifics about runtime enforcement | "A governance policy that lives in a wiki page is a wish. A governance policy that evaluates every tool call in real time is infrastructure." |
| 3 | Own the binary | Anti-SaaS, anti-vendor-lock-in | "50MB compiled binary. PostgreSQL. Air-gapped. Every AI interaction logged to your database, on your servers. No SaaS." |
| 4 | Build trap | Why building governance in-house fails | "Three CTOs I talked to this month started building AI governance in Q1. All three are now evaluating commercial options." |
| 5 | MCP governance | Transport-layer governance specifics | "MCP is the new attack surface. If your governance layer sits in front of it as a proxy, tool calls pass through unexamined." |

### Voice (Ed on X)

- Shorter and more direct than LinkedIn
- More technical, less narrative
- Thread format allows depth but each tweet must stand alone
- British English maintained
- Sardonic humour concentrated into fewer words
- No hashtags ever
- No emojis
- No "thread incoming" or "1/n" numbering

### Anti-Patterns

- NEVER use hashtags
- NEVER use emojis
- NEVER post "thread incoming" or number tweets
- NEVER include links in tweets (links go in replies only)
- NEVER cross-post identical content from LinkedIn
- NEVER fabricate stories or statistics
- NEVER engage with trolls or hostile accounts
- NEVER post more than 1 thread per day
- NEVER follow more than 10 accounts per day (avoid spam flags)
- NEVER use AI cliches (see social-identity banned words list)

---

## Daily Session Structure

When `x-twitter-engine` runs (default mode), execute these steps interactively.

### Step 1: Performance Check-in

Ask Ed to paste yesterday's thread metrics (if a thread was posted):

```
Yesterday's thread: XT-{###}
- Impressions (first tweet): ___
- Engagements: ___
- Link clicks (reply link): ___
- Profile visits: ___
- Retweets/quotes: ___
```

Log to `x-twitter/performance.jsonl`:

```json
{"date":"2026-04-16","thread_id":"XT-001","impressions":0,"engagements":0,"link_clicks":0,"profile_visits":null,"retweets":0,"quotes":0,"replies":0,"follows_gained":null,"notes":""}
```

If no thread was posted yesterday, skip.

### Step 2: Test Scorecard Check

Read `test-scorecard.md`. Show:

```
4-Week Test: Day {N} of 28
Link clicks total: {N}/50 target
ICP conversations: {N}/5 target
Attributable leads: {N}/1 target
Threads posted this week: {N}/5 target
On track: {Yes/No/At risk}
```

If any pass criterion is already met, flag it. If all fail criteria are trending towards failure at the halfway mark (Day 14), recommend early termination to Ed.

### Step 3: Today's Thread

If a thread is scheduled for today:

1. Show the full draft (hook + body tweets + closing + link reply)
2. Ask Ed: "Post as-is, edit, or skip?"
3. If Ed approves, remind to post manually on X
4. After posting: Ed says `posted XT-{###}` and the skill updates status

If no thread is queued, draft one now (enter draft mode for a single thread).

### Step 4: Engagement Session

Guide Ed through today's engagement targets:

1. **Quote-tweet opportunities:** Search for recent tweets from Anthropic, MCP community, AI governance voices. Suggest 2-3 quote-tweet targets with drafted commentary.

2. **Reply targets:** Search for conversations about AI governance, Claude standardisation, MCP security. Suggest 3-5 reply targets with drafted responses.

3. **Follow targets:** Suggest 3-5 ICP-matching accounts to follow based on:
   - Title: Head of AI, VP Engineering, CTO at 50-500 person companies
   - Recent activity: Posted about Claude, AI governance, MCP
   - Mutual connections or ecosystem adjacency

### Step 5: Pipeline Summary

```
Test day: {N}/28 | Threads: {posted}/{queued} | Link clicks: {total}/50
Engagement today: {quote-tweets}/{replies}/{follows}
```

---

## Thread Generation (`x-twitter-engine draft`)

Generate 3-5 threads in a single session. For each thread:

1. **Select pillar** — rotate across 5 pillars, avoid repeats from last 2 threads
2. **Research** — search for recent news, announcements, or conversations related to the pillar
3. **Write the thread** — follow format rules. Hook under 250 chars. 3-5 body tweets. Each under 280 chars.
4. **Write the link reply** — template repo link or guide link + one sentence of context
5. **Create the hypothesis** — each thread gets an H-### from the hypothesis ledger

Save each to `x-twitter/threads/XT-{###}.md`:

```markdown
---
id: XT-001
status: queued
scheduled_for: 2026-04-17
pillar: 1
hypothesis: H-015
created_at: 2026-04-16
posted_at: null
impressions: null
engagements: null
link_clicks: null
---

**Tweet 1 (hook):**
{hook tweet text}

**Tweet 2:**
{body tweet}

**Tweet 3:**
{body tweet}

**Tweet 4:**
{body tweet}

**Tweet 5 (closing):**
{closing tweet}

---
**Link reply:** {link + context}
```

### Quality Rules

- Every thread must contain at least one specific detail (a number, a tool name, an architecture decision)
- No two consecutive threads from the same pillar
- Each tweet must be under 280 characters
- The hook tweet must be under 250 characters
- Read the thread as a timeline scroller. Would each tweet stop you?
- No tweet should be a generic statement. Specifics or cut it.

---

## Performance Tracking

### Test Scorecard (`test-scorecard.md`)

Created on first run:

```markdown
# X/Twitter 4-Week Test Scorecard

**Test start:** {YYYY-MM-DD}
**Test end:** {YYYY-MM-DD}
**Status:** IN PROGRESS

## Pass Criteria (need at least ONE)

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| Link clicks to systemprompt.io | >50 | 0 | Not met |
| Meaningful ICP conversations | >5 | 0 | Not met |
| Attributable leads | >1 | 0 | Not met |

## Weekly Progress

### Week 1 ({date range})
| Metric | Target | Actual |
|--------|--------|--------|
| Threads posted | 5 | |
| Engagement replies | 50 | |
| ICP accounts followed | 25 | |
| Quote-tweets | 5 | |
| Link clicks | — | |
| ICP conversations | — | |

(Repeat for weeks 2-4)

## Decision

**Verdict:** {PENDING / PASS / FAIL}
**Date:** {YYYY-MM-DD}
**Rationale:** {one sentence}
**Action:** {Continue / Deactivate / Modify}
```

### Weekly Review (`x-twitter-engine weekly`)

Run on Fridays. Compare this week vs last:

| Metric | This week | Last week | Delta |
|--------|-----------|-----------|-------|
| Threads posted | | | |
| Total impressions | | | |
| Total link clicks | | | |
| Engagement replies sent | | | |
| Accounts followed | | | |
| ICP conversations | | | |
| Profile visits | | | |

Update test-scorecard.md with the week's data.

---

## Hypothesis Integration

Every thread gets logged to the hypothesis ledger:

```
hypothesis-ledger log {
  channel: "x-twitter",
  action: "Published XT-{###}: '{hook first 50 chars}'",
  hypothesis: "If we post {pillar} thread on X then x_link_clicks_7d rises from {baseline} to {target} within 7d",
  metric: "x_link_clicks_7d",
  baseline: {current},
  window_end: {+7d}
}
```

---

## First Run Checklist

On the very first run:

1. Create `x-twitter/` directory structure
2. Create empty `performance.jsonl`
3. Create `test-scorecard.md` with test start date = today
4. Confirm Ed has an X account and can post threads
5. **Generate 5 initial threads** covering all 5 pillars
6. Set the posting schedule: daily Mon-Fri
7. **Start engagement:** guide Ed through following 10 ICP accounts and making 5 replies
8. Log the test start in the hypothesis ledger as a meta-hypothesis

---

## Anti-Sludge Rules

- **No vague prose.** "Engagement is growing" banned. "XT-003 got 1,200 impressions and 8 link clicks vs XT-002's 340 impressions and 0 link clicks" required.
- **No motivational language.** No "great progress", "keep it up."
- **No emojis.**
- **No actions without a hypothesis.**
- **Fail loudly.** If Ed has not posted in 3+ days during the test, the first line says so.
- **The test is the test.** Do not extend, modify, or rationalise failure. If the numbers do not meet pass criteria after 4 weeks, the answer is FAIL.
