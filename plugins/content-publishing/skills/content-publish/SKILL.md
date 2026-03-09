---
name: content-publish
description: "End-to-end content publishing workflow for systemprompt.io. Create blog posts, generate images, sync to database, run the publish pipeline, and verify production deployment via CLI."
version: "1.0.0"
git_hash: "76ef91c"
---

# Content Publishing Workflow

End-to-end workflow for publishing content to systemprompt.io production. All operations use the systemprompt CLI from the web project directory.

## Working Directory

All commands run from: `/var/www/html/systemprompt-web`

## Prerequisites

- `systemprompt` CLI binary built and available
- Database running (local or cloud)
- `GEMINI_API_KEY` set for image generation

## Full Publishing Pipeline

### Step 1: Create the Blog Post

Create the content directory and markdown file:

```bash
SLUG="your-article-slug"
mkdir -p /var/www/html/systemprompt-web/services/content/guides/$SLUG
```

Write the blog post to `/var/www/html/systemprompt-web/services/content/guides/$SLUG/index.md` with this frontmatter:

```yaml
---
title: "Title (max 8 words, no colons or em-dashes)"
description: "Single-line description"
author: "Edward Burton"
slug: "your-article-slug"
keywords: "keyword1, keyword2, keyword3"
kind: "guide"
category: "blog"
public: true
tags: ["tag1", "tag2"]
published_at: "2026-03-09"
updated_at: "2026-03-09"
image: "/files/images/blog/your-article-slug.png"
after_reading_this:
  - "Learning outcome 1"
  - "Learning outcome 2"
  - "Learning outcome 3"
---
```

Use the `blog-writing` skill to generate the content body.

### Step 2: Generate the Featured Image

Use the `blog-image-generation` skill to generate an image via Gemini API.

The image must be saved to:
```
/var/www/html/systemprompt-web/storage/files/images/blog/$SLUG.png
```

And referenced in frontmatter as:
```yaml
image: "/files/images/blog/$SLUG.png"
```

### Step 3: Sync Content to Database

```bash
cd /var/www/html/systemprompt-web
systemprompt cloud sync local content --direction to-db -y
```

This ingests all markdown files from `services/content/` into the database.

### Step 4: Run the Publish Pipeline

```bash
cd /var/www/html/systemprompt-web
systemprompt infra jobs run publish_pipeline
```

The pipeline runs these steps automatically:
1. Content ingestion (markdown to database)
2. Asset copy (CSS/JS to dist)
3. Content prerender (markdown to HTML)
4. Page prerender (index pages, archives)
5. Sitemap generation
6. RSS feed generation
7. llms.txt generation
8. robots.txt generation

Or trigger via just:
```bash
cd /var/www/html/systemprompt-web
just publish
```

### Step 5: Verify Publication

```bash
# Check content exists in database
systemprompt core content show $SLUG --source guides

# List all guides
systemprompt core content list --source guides

# Check generated HTML exists
ls /var/www/html/systemprompt-web/web/dist/guides/$SLUG/index.html
```

### Step 6: Deploy to Production (if needed)

If deploying to cloud:
```bash
cd /var/www/html/systemprompt-web
just deploy
```

Or without rebuilding:
```bash
systemprompt cloud deploy --profile production --skip-build
```

## Quick Reference

| Task | Command |
|------|---------|
| Sync content to DB | `systemprompt cloud sync local content --direction to-db -y` |
| Run publish pipeline | `systemprompt infra jobs run publish_pipeline` |
| Show content | `systemprompt core content show {slug} --source guides` |
| List content | `systemprompt core content list --source guides` |
| Search content | `systemprompt core content search "query"` |
| Verify content | `systemprompt core content verify {slug} --source guides` |
| Upload file | `systemprompt core files upload ./image.png` |
| Deploy | `just deploy` |
| Build + publish | `just build-all` |

## Content Sources

| Source | Path | URL |
|--------|------|-----|
| Guides | `services/content/guides/` | `/guides/{slug}` |
| Documentation | `services/content/documentation/` | `/documentation/{slug}` |
| Platform | `services/content/platform/` | `/platform/{slug}` |
| Legal | `services/content/legal/` | `/legal/{slug}` |

## Updating Existing Content

To update an existing page:

1. Edit the markdown file at the appropriate path
2. Update the `updated_at` field in frontmatter
3. Run Steps 3-5 (sync, publish, verify)

## Troubleshooting

### Content not appearing after publish
```bash
# Check ingestion
systemprompt infra logs --context content --level error --limit 20

# Re-run ingestion only
systemprompt core content publish --step ingest
```

### Image not showing
- Verify image exists at `storage/files/images/blog/{slug}.png`
- Check frontmatter `image` field matches the path
- Run asset copy: `systemprompt core content publish --step assets`

### Database sync errors
```bash
# Check database connectivity
systemprompt admin config show --section database

# Reset and re-sync
systemprompt cloud sync local content --direction to-db -y --force
```
