---
name: reddit-reply
description: "Daily follow-up on Reddit engagement. Reads recent reddit-monitor reports, checks each URL for replies to our comments, and drafts follow-up responses. Designed for daily /loop. Load identity and brand-voice first."
metadata:
  version: "1.0.1"
  git_hash: "PENDING"
---

# Reddit Reply

Daily follow-up skill that monitors replies to our previous Reddit comments. Reads the reddit-monitor reports from today and yesterday, visits each post URL, checks for replies to our comments, and drafts follow-up responses. Designed for `/loop 1d`.

## Dependencies

**Load `identity` and `brand-voice` before this skill.** Identity defines what we say and to whom. Brand voice defines how we sound. This skill handles ongoing conversation, not initial outreach.

## Overview

1. Read recent reddit-monitor reports
2. Visit each post URL and fetch the comment thread
3. Identify replies to our comments
4. Draft follow-up responses
5. Generate and save a reply report

## Step 1: Read Recent Reports

Read the reddit-monitor reports from the `reports/` directory:

```
reports/reddit/YYYY-MM-DD/reddit-monitor.md
```

Check for today's report and yesterday's report. If neither exists, check the last 3 days. Extract all post URLs from the `## Reply Targets` section (lines matching `- **URL:**`).

Also read any previous reddit-reply reports from the last 7 days to avoid re-drafting responses to threads already handled:

```
reports/reddit/YYYY-MM-DD/reddit-reply.md
```

Build a list of:
- All post URLs from recent reddit-monitor reports
- All thread URLs already handled in previous reddit-reply reports (to skip)

## Step 2: Fetch Comment Threads

For each post URL from the reports, fetch the comment thread using Reddit's public JSON API:

```
https://www.reddit.com{permalink}.json
```

This returns an array with two elements: the post data and the comment tree. Parse the comment tree to find:

1. **Our comments**: Look for comments by the account that posted the reply (the username will be consistent across replies). If the username is not known, look for comments that closely match the draft reply text from the reddit-monitor report.
2. **Replies to our comments**: For each of our comments, check if there are child comments (replies) in the `replies` field.

Add a 2-second delay between requests to respect Reddit rate limits.

## Step 3: Identify Actionable Replies

For each reply to our comment, assess whether it needs a follow-up:

**Reply warrants a response:**
- The replier asks a follow-up question
- The replier shares their own experience or asks for clarification
- The replier disagrees or challenges something we said (opportunity to engage respectfully)
- The replier mentions a specific use case or problem we can help with
- The replier thanks us and adds context that opens a natural follow-up

**Reply does NOT warrant a response:**
- Simple "thanks" with no follow-up context
- The replier is clearly trolling or being hostile
- The conversation has moved on (reply is older than 3 days)
- Another commenter has already adequately addressed the reply
- Our response would just be restating what we already said

## Step 4: Draft Follow-Up Responses

For each actionable reply, draft a follow-up. These are second or third messages in a thread, so they should feel like a natural conversation, not a fresh pitch.

### Conversation Rules

- **Be brief.** Follow-ups should be shorter than initial replies. 1-4 sentences is typical.
- **Be direct.** Address exactly what they said or asked. No preamble.
- **Be helpful.** If they asked a question, answer it. If they shared an experience, acknowledge it specifically.
- **Be human.** This is a conversation, not a content piece. Match their energy and tone.
- **Know when to stop.** Not every thread needs to go 5 rounds deep. If you have said what is useful, let the conversation end naturally.

### Anti-Sludge Rules (same as reddit-monitor, MANDATORY)

- NO em dashes. Use commas, periods, or parentheses.
- NO generic praise: "Great point!", "That's a really good observation!"
- NO sludge: "Absolutely!", "Totally agree!", "100% this!"
- NO fabricated personal stories
- NO AI cliches
- NO hashtags
- NO forced product mentions. If systemprompt was not mentioned in the original reply, do not introduce it in the follow-up unless they specifically asked about the kind of problem it solves.
- Content must NOT read as AI-generated

### systemprompt Mention Rules

- If our original reply mentioned systemprompt and the replier asks a follow-up question about it, answer naturally and specifically.
- If our original reply did NOT mention systemprompt, do not introduce it in the follow-up.
- Never pitch in a follow-up. If they want to know more, give them a direct answer. If they do not ask, do not volunteer.

## Step 5: Generate and Save Report

Save the report to:

```
reports/reddit/YYYY-MM-DD/reddit-reply.md
```

### Report Structure

```markdown
# Reddit Reply Report

**Date:** {YYYY-MM-DD}
**Reports scanned:** reports/reddit/{date1}/reddit-monitor.md, reports/reddit/{date2}/reddit-monitor.md
**Posts checked:** {N}
**Posts with our comments found:** {N}
**Replies to our comments:** {N}
**Follow-ups drafted:** {N}

---

## Threads Needing Follow-Up

### 1. "{Post Title}"
- **Subreddit:** r/{subreddit}
- **Post URL:** {url}
- **Our original comment:** (summary or first line)
- **Reply from u/{username}:**

> {Their reply text}

- **Assessment:** {Why this warrants a follow-up}

**Draft follow-up:**

> {The drafted follow-up text}

---

(repeat for each thread)

## Threads Checked, No Action Needed

| Post | Subreddit | Reason |
|------|-----------|--------|
| {title} | r/{sub} | No replies yet |
| {title} | r/{sub} | Reply was a simple thanks |
| {title} | r/{sub} | Already handled in previous report |
| {title} | r/{sub} | Thread older than 3 days |

## Engagement Summary

| Metric | Count |
|--------|-------|
| Posts checked | {N} |
| Our comments found | {N} |
| Replies received | {N} |
| Follow-ups needed | {N} |
| Threads with no activity | {N} |
| Previously handled | {N} |

## Observations

- {Patterns in how people respond to our comments}
- {Topics generating the most engagement}
- {Any feedback about systemprompt.io worth noting}
```

## Quality Checklist

Before saving the report, verify:

- [ ] No em dashes in any drafted follow-up
- [ ] No generic praise or sludge openings
- [ ] No fabricated personal stories
- [ ] No AI cliches
- [ ] Follow-ups are shorter than initial replies (conversational, not content pieces)
- [ ] systemprompt only mentioned where the replier specifically asked about it
- [ ] Each follow-up directly addresses what the replier said
- [ ] "No action needed" threads have a clear reason documented
- [ ] Report saved to the correct path with today's date
