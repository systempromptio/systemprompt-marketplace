---
name: content-guide
description: "Entry point for content — routes to guide writing, blog posts, copywriting, and publishing"
metadata:
  version: "2.0.1"
  git_hash: "8e40a90"
---

# Content Guide

Content creation and publishing skills for systemprompt.io. Guides, blog posts, documentation, website copy, and feature pages.

## Dependencies

Load `commons:identity` and `commons:brand-voice` before using content skills.

## Content Creation Skills

| Task | Skill | When to Use |
|------|-------|-------------|
| Write a technical guide | `guide-writer` | Data-driven long-form guides (4,000-11,000 words) |
| Audit and optimise a published guide | `guide-optimiser` | 14-section audit + data-driven rewrite using GSC data, 11-dimension scoring |
| Write a blog post | `blog-writing` | Long-form posts with Edward's voice (3,500-5,000 words) |
| Generate a featured image | `blog-image-generation` | Create blog images via Gemini API |
| Draft marketing content | `content-drafting` | LinkedIn, Reddit, blog, email content |
| Distribute content to platforms | `content-distribution` | Platform-adapted syndication with backlinks |
| Write or review documentation | `documentation-copywriter` | Docs structure, terminology, quality |
| Write or review website copy | `website-copywriter` | Page copy for enterprise credibility |
| Rewrite feature pages | `feature-copywriter` | Technical copy for feature pages |

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

### Optimise an Existing Guide

1. Load `commons:identity` and `commons:brand-voice`
2. Load `guide-optimiser` with the guide slug
3. Review the score delta and query coverage matrix
4. The optimiser commits changes and updates the per-guide report

### Publish a New Blog Post

1. Load `commons:identity` and `commons:brand-voice`
2. Load `blog-writing` to generate the markdown
3. Load `blog-image-generation` for the featured image
4. Load `commons:brand-review` to check before publishing
5. Load `content-publish` to sync and deploy
