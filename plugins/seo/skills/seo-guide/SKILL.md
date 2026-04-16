---
name: seo-guide
description: "Entry point for SEO — routes to monitoring, keyword tracking, hypothesis testing, and strategy"
metadata:
  version: "1.2.0"
  git_hash: "dc0c940"
---

# SEO Guide

Search engine optimisation skills for systemprompt.io. Data-driven SEO using Google Search Console, DataForSEO, and hypothesis-tested actions.

## Dependencies

Load `commons:identity` before using any SEO skill.

## Patterns Implemented

This plugin implements three `commons` patterns:
- `commons:hypothesis-ledger-pattern` → `seo-hypothesis-ledger` (S-### prefix, 14-day window)
- `commons:strategy-master-pattern` → `seo-strategy-master` (pillar health, organic sessions north star)
- `commons:daily-brief-pattern` → `daily-seo-brief` (8-step orchestration, daily performance review)

## Skills

| Task | Skill | Frequency |
|------|-------|-----------|
| Daily SEO performance review | `daily-seo-brief` | Daily /loop |
| Keyword data pulls and cross-referencing | `seo-keyword-tracker` | Monthly full + daily cross-ref |
| Track SEO actions as hypotheses (S-###) | `seo-hypothesis-ledger` | On every SEO action |
| Maintain the living SEO strategy doc | `seo-strategy-master` | On phase changes or reviews |
| AI agent answer-engine optimisation | `ai-agent-discovery` | Weekly AEO audit |

## Data Flow

```
DataForSEO → seo-keyword-tracker → keyword-targets.json
                                          ↓
GSC API → daily-seo-brief → daily report → seo-hypothesis-ledger (score maturing)
                    ↓                         ↓
              seo-strategy-master ← hypothesis results (winning/dead)
```

## Report Directory

All SEO reports live at: `/var/www/html/systemprompt-web/reports/seo/`
