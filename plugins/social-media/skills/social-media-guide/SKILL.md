---
name: social-media-guide
description: "Entry point for social-media — routes to LinkedIn, Reddit, X/Twitter, and the daily social brief"
metadata:
  version: "1.0.0"
  git_hash: "3a55706"
---

# Social Media Guide

Social media engagement skills for systemprompt.io. Consolidated LinkedIn, Reddit, and X/Twitter under one plugin with shared identity, cross-platform coordination, and unified metrics.

## Dependencies

Load `social-media:social-identity` before using any social-media skill. It loads `commons:identity` and `commons:marketing-identity` upstream.

## Skills

### Foundation

| Task | Skill | When |
|------|-------|------|
| Platform voice, engagement rules, metrics | `social-identity` | Load first |
| Morning social dashboard | `daily-social-brief` | Daily /loop |

### LinkedIn

| Task | Skill | Frequency |
|------|-------|-----------|
| Posts, DMs, prospect research, performance | `linkedin-engine` | 3x/week (Mon/Wed/Fri) |

### Reddit

| Task | Skill | Frequency |
|------|-------|-----------|
| Scan subreddits, draft replies | `reddit-monitor` | Daily /loop |
| Follow up on posted replies | `reddit-reply` | Daily /loop |

### X / Twitter

| Task | Skill | Frequency |
|------|-------|-----------|
| Threads, engagement, 4-week test | `x-twitter-engine` | Daily (during test) |

## Daily Workflow

1. Run `daily-social-brief` as part of the morning brief sequence (after marketing and CRM briefs)
2. Execute today's social actions per the weekly schedule in `sales-marketing-strategy.md`
3. End of day: log completed actions and paste metrics

## Report Directories

| Platform | Path |
|----------|------|
| Social briefs | `reports/social/daily/{YYYY-MM-DD}/` |
| LinkedIn | `reports/linkedin/` |
| Reddit | `reports/social/reddit/daily/{YYYY-MM-DD}/` |
| X/Twitter | `reports/x-twitter/` |

## Strategy Reference

Channel priorities and weekly schedule are governed by:
`/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` §4.3 and §5
