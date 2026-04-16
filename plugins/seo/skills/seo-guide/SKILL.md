---
name: seo-guide
description: "Entry point for SEO — routes to monitoring, keyword tracking, hypothesis testing, and strategy"
metadata:
  version: "1.0.0"
  git_hash: "5079c7a"
---

# SEO Guide

Search engine optimisation skills for systemprompt.io. Data-driven SEO using Google Search Console, DataForSEO, and hypothesis-tested actions.

## Dependencies

Load `commons:identity` before using any SEO skill.

## Skills

| Task | Skill | Frequency |
|------|-------|-----------|
| Daily SEO performance review | `seo-monitor` | Daily /loop |
| Keyword data pulls and cross-referencing | `seo-keyword-tracker` | Monthly full + daily cross-ref |
| Track SEO actions as hypotheses (S-###) | `seo-hypothesis-ledger` | On every SEO action |
| Maintain the living SEO strategy doc | `seo-strategy-master` | On phase changes or reviews |

## Data Flow

```
DataForSEO → seo-keyword-tracker → keyword-targets.json
                                          ↓
GSC API → seo-monitor → daily report → seo-hypothesis-ledger (score maturing)
                    ↓                         ↓
              seo-strategy-master ← hypothesis results (winning/dead)
```

## Report Directory

All SEO reports live at: `/var/www/html/systemprompt-web/reports/seo/`
