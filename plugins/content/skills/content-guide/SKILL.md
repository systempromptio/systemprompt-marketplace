---
name: content-guide
description: "Entry point for content — routes to guide, feature, and documentation writer+optimiser pairs, distribution, and publishing"
metadata:
  version: "3.0.0"
  git_hash: "7f3e532"
---

# Content Guide

Content creation, optimisation, and publishing skills for systemprompt.io. Three writer+optimiser pairs (guides, features, documentation), multi-channel distribution, and a full publishing pipeline.

## Dependencies

Load `commons:identity` and `commons:brand-voice` before using content skills.

## Daily Operations

| Task | Skill | When to Use |
|------|-------|-------------|
| Morning content brief | `daily-content-brief` | Daily orchestration: pipeline status, guide performance, 3-5 actions |
| Content hypothesis ledger (CT-###) | `content-hypothesis-ledger` | Log/score content actions as falsifiable hypotheses |
| Content strategy document | `content-strategy-master` | Read/update the living content strategy |

## Writer + Optimiser Pairs

Each content type has a matched writer (create/rewrite) and optimiser (audit/score/fix).

| Content Type | Writer | Optimiser | Content Location |
|-------------|--------|-----------|-----------------|
| Guides | `guide-writer` | `guide-optimiser` | `services/content/guides/{slug}/index.md` |
| Feature pages | `feature-writer` | `feature-optimiser` | `services/web/config/features/*.yaml` |
| Documentation | `documentation-writer` | `documentation-optimiser` | `services/content/documentation/{slug}/index.md` |

## Content Creation Skills

| Task | Skill | When to Use |
|------|-------|-------------|
| Write a technical guide | `guide-writer` | Data-driven long-form guides (4,000-11,000 words) |
| Write a blog post | `guide-writer` (blog mode) | Edward's voice, kind: blog (3,500-5,000 words) |
| Audit and optimise a published guide | `guide-optimiser` | 14-section audit + data-driven rewrite, 11-dimension scoring |
| Write or rewrite a feature page | `feature-writer` | Technical copy, Why-What-How doctrine, claim verification |
| Audit and optimise a feature page | `feature-optimiser` | 10-section audit + deterministic rewrite, 75-point scoring |
| Write or review documentation | `documentation-writer` | Docs structure, terminology, per-doc reports |
| Audit and optimise documentation | `documentation-optimiser` | 10-section audit + deterministic rewrite, 75-point scoring |
| Generate a featured image | `blog-image-generation` | Create blog images via Gemini API |
| Draft and distribute content | `content-distribution` | All channels: Dev.to, Medium, LinkedIn, Reddit, email, landing pages |
| Scan GitHub for contributions | `github-monitor` | Daily /loop, 30+ repos in Claude/MCP ecosystem |

## Publishing

| Task | Skill | When to Use |
|------|-------|-------------|
| Publish to production | `content-publish` | End-to-end CLI workflow: create, sync, publish, verify |
| Pre-publish quality gate | `commons:brand-review` | Check against identity, voice, and brand rules |

## Common Workflows

### Write and Publish a New Guide

1. Load `commons:identity` for positioning and audience
2. Load `guide-writer` — follow research-first workflow (Steps 1-1.9 create the guide report, Steps 2-4 write the guide)
3. Load `guide-optimiser` to audit, fix, score, and commit
4. Load `content-publish` to sync and deploy

### Write a Blog Post

1. Load `commons:identity` for positioning and audience
2. Load `guide-writer` with `kind: blog` — uses blog mode (narrative structure, 3,500-5,000 words)
3. Load `blog-image-generation` for the featured image
4. Load `commons:brand-review` to check before publishing
5. Load `content-publish` to sync and deploy

### Write and Publish a Feature Page

1. Load `commons:identity` and `commons:brand-voice`
2. Load `feature-writer` — research phase, audit, rewrite with Why-What-How doctrine
3. Load `feature-optimiser` to score and verify
4. Load `content-publish` to deploy

### Write and Publish Documentation

1. Load `commons:identity` and `commons:brand-voice`
2. Load `documentation-writer` — research phase, write, quality gate
3. Load `documentation-optimiser` to score and verify
4. Load `content-publish` to deploy

### Optimise an Existing Guide

1. Load `commons:identity` and `commons:brand-voice`
2. Load `guide-optimiser` with the guide slug
3. Review the score delta and query coverage matrix
4. The optimiser commits changes and updates the per-guide report

### Optimise a Feature Page

1. Load `commons:identity` and `commons:brand-voice`
2. Load `feature-optimiser` with the feature slug
3. Review the score delta and claim verification results
4. The optimiser commits changes and updates the per-feature report

### Optimise a Documentation Page

1. Load `commons:identity` and `commons:brand-voice`
2. Load `documentation-optimiser` with the doc slug
3. Review the score delta and link health results
4. The optimiser commits changes and updates the per-doc report
