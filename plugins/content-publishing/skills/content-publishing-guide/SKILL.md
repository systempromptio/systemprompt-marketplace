---
name: content-publishing-guide
description: "Entry point for content-publishing — routes to the right sub-skill for your task"
version: "1.0.0"
git_hash: "76ef91c"
---

# Content Publishing Guide

Entry point for the content-publishing plugin. Use this to find the right skill for your content task.

## Available Skills

| Task | Skill | When to Use |
|------|-------|-------------|
| Write a blog post | `blog-writing` | Generate long-form blog posts with Edward's voice (3500-5000 words) |
| Generate a featured image | `blog-image-generation` | Create blog images via Gemini API with curl (text-to-image and editing) |
| Write or review documentation | `documentation-copywriter` | Ensure docs follow structure, terminology, and quality standards |
| Write or review website copy | `website-copywriter` | Analyse, critique, and rewrite website pages for enterprise credibility |
| Write a guide | `guide-writer` | Create SEO-focused technical guides targeting CTO audience |
| Publish content to production | `content-publish` | End-to-end publishing workflow: create content, generate image, sync, publish |

## Common Workflows

### Publish a New Blog Post

1. Load `blog-writing` to generate the blog post markdown
2. Load `blog-image-generation` to create a featured image via Gemini API
3. Load `content-publish` to sync and publish to production

### Review and Update Documentation

1. Load `documentation-copywriter` to audit existing docs
2. Make corrections following the quality checklist
3. Load `content-publish` to sync and publish changes

### Rewrite Website Copy

1. Load `website-copywriter` to analyse the current page
2. Apply the rewrite following enterprise credibility standards
3. Load `content-publish` to deploy changes

## Dependencies

Many skills in this plugin reference the systemprompt identity and brand voice. Load `systemprompt-identity` and `systemprompt-brand-voice` from the `system-prompt-marketing-tools` plugin before using copywriting skills.
