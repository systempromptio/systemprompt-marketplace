---
name: commons-guide
description: "Entry point for commons — routes to shared infrastructure skills for identity, brand, patterns, and CLI"
metadata:
  version: "1.1.0"
  git_hash: "dc0c940"
---

# Commons Guide

Shared infrastructure skills used across all domains. Load these before domain-specific skills.

## Master Entry Point

| Task | Skill | Load when |
|------|-------|-----------|
| **Morning master brief** | `daily-master-brief` | **Daily: single entry point across all domains. Answers 9 KPIs: strategy effectiveness, pipeline growth, what's working/not, today's priorities, system health** |

## Skills

| Task | Skill | Load when |
|------|-------|-----------|
| Understand product identity, ICP, positioning | `identity` | Before any content, marketing, or CRM skill |
| Apply brand voice, style, terminology | `brand-voice` | Before drafting any content |
| Pre-publish quality gate | `brand-review` | Before publishing any content |
| systemprompt CLI reference | `cli-usage` | When running CLI commands |
| Build a hypothesis ledger | `hypothesis-ledger-pattern` | When setting up action tracking for a new domain |
| Build a strategy master doc | `strategy-master-pattern` | When setting up a living strategy document |
| Build a daily brief | `daily-brief-pattern` | When building an orchestrated daily briefing |
| Marketing lead-gen positioning | `marketing-identity` | Before any marketing, social-media, or CRM skill |
| Marketing strategy document | `marketing-strategy-master` | To read/update the living marketing strategy |
| Marketing hypothesis ledger (H-###) | `marketing-hypothesis-ledger` | To log/score marketing actions |
| Morning marketing brief | `daily-marketing-brief` | Daily orchestration: funnel deltas + 3-5 actions |

## Dependency Model

```
commons (no external dependencies)
  |
  +-- content (loads: identity, brand-voice, brand-review)
  +-- seo (loads: identity, brand-voice, hypothesis-ledger-pattern, strategy-master-pattern)
  +-- social-media (loads: identity, marketing-identity)
  +-- crm (loads: identity, marketing-identity, brand-voice, hypothesis-ledger-pattern, daily-brief-pattern)
  +-- development (loads: identity for product context)
```
