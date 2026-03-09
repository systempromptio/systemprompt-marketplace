---
name: content-publishing-guide
description: "Entry point for content-publishing — routes to the right sub-skill for your task"
metadata:
  version: "1.0.6"
  git_hash: "bc2a4a3"
---

# Content Publishing Guide

Entry point for the content-publishing plugin. Use this to find the right skill for your content task.

## Foundation Skills (Load First)

| Skill | Purpose |
|-------|---------|
| `identity` | Source of truth for what systemprompt is, ICP, go-to-market, and messaging hierarchy. **Load before all other skills.** |
| `brand-voice` | Tone, style guide, and messaging pillars. Load after `identity`. |

## Content Creation Skills

| Task | Skill | When to Use |
|------|-------|-------------|
| Write a blog post | `blog-writing` | Long-form posts with Edward's voice (3500-5000 words) |
| Generate a featured image | `blog-image-generation` | Create blog images via Gemini API (text-to-image and editing) |
| Write a guide | `guide-writer` | SEO-focused technical guides targeting CTO audience |
| Draft marketing content | `content-drafting` | LinkedIn, Reddit, blog, email, and documentation content |
| Write or review documentation | `documentation-copywriter` | Docs structure, terminology, and quality standards |
| Write or review website copy | `website-copywriter` | Analyse and rewrite pages for enterprise credibility |
| Monitor Reddit for reply opportunities | `reddit-monitor` | Daily subreddit scanning, filtering, and reply drafting |
| Review SEO and content performance | `seo-monitor` | Daily analytics review with actionable recommendations |
| Follow up on Reddit engagement | `reddit-reply` | Check replies to our comments and draft follow-ups |
| Distribute guides to platforms | `content-distribution` | Daily platform-adapted syndication with backlinks and SEO scoring |

## Quality and Publishing Skills

| Task | Skill | When to Use |
|------|-------|-------------|
| Audit a guide for quality | `guide-revision` | Deterministic checklist for published guide quality |
| Review before publishing | `brand-review` | Pre-publish quality gate against identity, voice, and brand rules |
| Publish to production | `content-publish` | End-to-end CLI workflow: create, sync, publish, verify |

## Common Workflows

### Publish a New Blog Post

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `blog-writing` to generate the blog post markdown
3. Load `blog-image-generation` to create a featured image via Gemini API
4. Load `brand-review` to check content before publishing
5. Load `content-publish` to sync and publish to production

### Draft Marketing Content

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `content-drafting` to write for the target channel
3. Load `brand-review` to verify compliance before posting

### Review and Update Documentation

1. Load `identity` for terminology and positioning context
2. Load `documentation-copywriter` to audit existing docs
3. Make corrections following the quality checklist
4. Load `content-publish` to sync and publish changes

### Monitor Reddit and Draft Replies

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `reddit-monitor` to scan subreddits and draft replies
3. Review the generated report and adjust drafts as needed
4. Post approved replies manually

### Follow Up on Reddit Engagement

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `reddit-reply` to check replies to our previous comments
3. Review the follow-up drafts in `reports/reddit/{date}/reddit-reply.md`
4. Post approved follow-ups manually

### Daily SEO Review

1. Load `identity` for positioning and keyword strategy context
2. Load `seo-monitor` to pull analytics and generate performance report
3. Review the report in `reports/seo/{date}/seo-monitor.md`
4. Action the prioritised recommendations

### Revise an Existing Guide

1. Load `identity` for positioning and keyword strategy context
2. Load `guide-revision` to audit the guide against the checklist
3. Review the report in `reports/guide-revision/{date}/guide-revision-{slug}.md`
4. Fix failing checks in priority order (claims, links, structure)
5. Re-run `guide-revision` to verify fixes

### Distribute Content to External Platforms

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `content-distribution` to generate platform-adapted versions
3. Review generated drafts in `reports/seo/blog/YYYY-MM-DD/`
4. Post approved content to each platform manually

### Rewrite Website Copy

1. Load `identity` and `brand-voice` for positioning and tone
2. Load `website-copywriter` to analyse the current page
3. Apply the rewrite following enterprise credibility standards
4. Load `brand-review` to verify before deploying
5. Load `content-publish` to deploy changes
