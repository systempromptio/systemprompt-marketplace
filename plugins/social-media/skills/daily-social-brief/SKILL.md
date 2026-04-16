---
name: daily-social-brief
description: "Morning social media orchestrator. Reads LinkedIn, Reddit, and X metrics, identifies engagement opportunities, generates 3-5 social actions for the day. Cross-references hypothesis ledger. Load social-identity first."
metadata:
  version: "1.1.0"
  git_hash: "3a55706"
---

# Daily Social Brief

> **Implements:** `commons:daily-brief-pattern` — 8-step orchestration sequence, max 5 actions, no action without hypothesis, score maturing before generating new. This skill configures the pattern for the social media domain (shares marketing H-### hypotheses, cross-platform metrics, 5-minute target).

Morning social media dashboard for Ed. Reads metrics and engagement signals from LinkedIn, Reddit, and X/Twitter. Identifies today's social opportunities. Generates 3-5 actionable items. Designed to be read in 5 minutes as part of the morning brief sequence.

Designed for daily execution via `/loop 1d social-media:daily-social-brief`.

## Dependencies (load in order)

1. `social-media:social-identity` — platform voice, engagement rules, metrics definitions
2. `commons:marketing-hypothesis-ledger` — in-flight social hypotheses and next H-### allocation
3. `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — current domain weights, weekly schedule, channel priorities

Also reads (if they exist for today):
- `reports/social/daily/{today}/action-list.md` — from reddit-monitor (if already run)
- `reports/linkedin/` — latest performance data
- `reports/x-twitter/` — latest performance data and test scorecard

## Run Sequence

1. **Check what day it is.** Determine which social platforms are active today per the weekly schedule in the strategy doc.
2. **Read latest metrics from each active platform.**
3. **Read in-flight social hypotheses** from the hypothesis ledger (filter by channel: linkedin, reddit, x-twitter).
4. **Score any social hypotheses** whose windows close today.
5. **Read today's reddit-monitor action list** if it exists (reddit-monitor may run separately).
6. **Generate 3-5 social actions** for today.
7. **Write the brief** to `reports/social/daily/{today}/daily-social-brief.md`.

## How Actions Are Chosen

Maximum 5 social actions per day. Priority order:

1. **Engagement follow-ups:** Replies to comments on yesterday's posts, DM responses, thread replies that need follow-up.
2. **Scheduled content:** Today's LinkedIn post, X thread, or Reddit engagement per the weekly schedule.
3. **High-signal opportunities:** Trending conversations, breaking AI governance news, viral threads where Ed can add genuine value.
4. **Cross-platform reinforcement:** If a topic performed well on one platform, adapt it for another (with 24h separation).
5. **Prospect engagement:** LinkedIn connection requests, X follows of ICP accounts.

**Drop rules:**
- Never recommend the same content on two platforms on the same day
- Never recommend engagement on a platform not scheduled for today (exception: urgent replies to direct questions)
- If reddit-monitor already generated an action list, integrate it rather than duplicating

## Brief Report Structure

```markdown
# Daily Social Brief — {YYYY-MM-DD}

**Platforms active today:** {LinkedIn, Reddit, X — per weekly schedule}
**Social hypotheses in flight:** {N}
**Actions generated:** {N}

---

## 1. Yesterday's Social Performance

### LinkedIn
- Last post: LI-{###} ({date}) — {impressions} impressions, {comments} comments, {link clicks} link clicks
- Pending replies: {N}
- DMs awaiting response: {N}

### Reddit
- Replies to our comments: {N new since last check}
- Active threads: {N}

### X/Twitter
- Last thread: XT-{###} ({date}) — {impressions} impressions, {link clicks} link clicks
- Test scorecard: Day {N}/28, {link clicks total}/50 clicks target
- Pending quote-tweet opportunities: {N}

## 2. Hypotheses Maturing Today

For each social hypothesis with `window_end <= today`:
- **[H-###]** {hypothesis one-liner}
  - Result: {PASS|FAIL|INCONCLUSIVE}
  - Lesson: {one line}

If none: "No social hypotheses maturing today."

## 3. Today's Social Actions (3-5)

### Action 1: {Platform} — {Summary}

**What:** {Specific action}
**Why:** {Engagement opportunity or scheduled content}
**Draft:** {Copy-paste ready content, if applicable}
**Hypothesis:** [H-###] {if creating a new hypothesis}
**Time estimate:** {5/10/15 min}

(Repeat for each action)

## 4. Cross-Platform Notes

- {Any topic trending across multiple platforms}
- {Content adaptation opportunities}
- {Platform-specific observations}
```

## Platform-Specific Metric Sources

### LinkedIn

Read from `reports/linkedin/`:
- `performance.jsonl` — latest entry for yesterday's metrics
- `drafts/` — queue status (queued, scheduled, posted counts)
- `prospects.md` — DM pipeline status

If `performance.jsonl` does not exist or has no entries, note: "LinkedIn metrics not yet tracked. Run `linkedin-engine track` to initialise."

### Reddit

Read from `reports/reddit/daily/`:
- Latest `reddit-monitor.md` — action list and drafted replies
- Latest `reddit-reply.md` — follow-up status

If no recent reports, note: "Reddit not scanned today. Run `reddit-monitor` to scan."

### X/Twitter

Read from `reports/x-twitter/`:
- `performance.jsonl` — latest entry for yesterday's metrics
- `test-scorecard.md` — 4-week test progress
- `threads/` — queue status

If `test-scorecard.md` does not exist, note: "X/Twitter test not started. Run `x-twitter-engine` to initialise."

## Integration with Other Briefs

This brief is designed to be read AFTER `daily-marketing-brief` and `daily-crm-brief`. It adds the social media layer. The marketing brief may generate social media actions (especially LinkedIn DMs for outbound); this brief coordinates those with the broader social calendar to avoid conflicts.

If the marketing brief has already generated a LinkedIn action for today, do not duplicate it. Reference it: "Marketing brief already assigned: [H-###] LinkedIn DM to {prospect}."

## Anti-Sludge Rules

- **Under 400 words of prose** (excluding action drafts). This is a 5-minute read.
- **No vague prose.** Numbers or nothing.
- **No motivational language.**
- **No emojis.**
- **Fail loudly.** If no social metrics are available from any platform, the first line says so.
- **Respect the schedule.** If today is not a LinkedIn day per the strategy doc, do not generate LinkedIn actions (exception: urgent reply to a hot prospect).
