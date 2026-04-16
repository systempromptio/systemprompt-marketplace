---
name: marketing-guide
description: "Entry point for marketing — routes to outreach, social monitoring, lead gen, and strategy"
metadata:
  version: "1.0.0"
  git_hash: "pending"
---

# Marketing Guide

Lead generation, distribution, and outreach skills for systemprompt.io. Hypothesis-driven marketing across GitHub, Reddit, LinkedIn, and AI agents.

## Dependencies

Load `commons:identity` and `commons:brand-voice` before using marketing skills. Load `marketing-identity` for lead-gen specific positioning.

## Skills

### Strategy and Measurement

| Task | Skill | Frequency |
|------|-------|-----------|
| Morning actionable brief | `daily-marketing-brief` | Daily /loop |
| Track marketing actions (H-###) | `hypothesis-ledger` | On every action |
| Daily funnel measurement | `lead-tracker` | Daily (14d GitHub retention) |
| Living marketing strategy doc | `marketing-strategy-master` | On reviews |
| Lead-gen positioning and ICP | `marketing-identity` | Load first |

### Outreach and Monitoring

| Task | Skill | Frequency |
|------|-------|-----------|
| LinkedIn feed, DMs, engagement | `linkedin-engine` | Daily /loop |
| GitHub contribution opportunities | `github-monitor` | Daily /loop |
| Reddit/social engagement scanner | `reddit-monitor` | Daily /loop |
| Follow-up on Reddit posts | `reddit-reply` | Daily /loop |
| AI agent answer-engine visibility | `ai-agent-discovery` | Weekly |

## Report Directory

All marketing reports live at: `/var/www/html/systemprompt-web/reports/marketing/`
