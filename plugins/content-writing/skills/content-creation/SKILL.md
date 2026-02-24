---
name: content-creation
description: "Manage content sources, categories, publishing workflows, sitemap generation, RSS feeds, and troubleshoot content issues"
---

# Content Creation

Content lifecycle management. Config: `services/content/config.yaml`

## Configure Content Source

Edit `services/content/config.yaml`:

```yaml
content:
  sources:
    - name: blog
      path: services/content/blog
      url_pattern: /blog/{slug}
      template: blog-post
      enabled: true
      categories:
        - name: tutorials
          slug: tutorials
          description: "Step-by-step guides"
        - name: announcements
          slug: announcements
          description: "Product updates"
      sitemap:
        enabled: true
        changefreq: weekly
        priority: 0.8
      rss:
        enabled: true
        title: "Blog RSS Feed"
        description: "Latest posts"
        max_items: 20
    - name: documentation
      path: services/content/documentation
      url_pattern: /documentation/{category}/{slug}
      template: documentation
      enabled: true
      sitemap:
        enabled: true
        changefreq: monthly
        priority: 0.9
```

## Create Content

Create a markdown file with required frontmatter:

```markdown
---
title: "My First Blog Post"
description: "An introduction to systemprompt.io"
slug: "my-first-post"
kind: "blog"
public: true
tags: ["introduction", "tutorial"]
published_at: "2026-02-01"
---

# My First Blog Post

Content goes here.
```

Required frontmatter fields:

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `description` | string | Yes |
| `slug` | string | Yes |
| `kind` | string | Yes |
| `public` | boolean | Yes |
| `published_at` | date | Yes |
| `author` | string | No |
| `tags` | array | No |
| `category` | string | No |

## Publish Content

```bash
# Sync to database
systemprompt cloud sync local content --direction to-db -y

# Run publish pipeline
systemprompt infra jobs run publish_pipeline

# Verify
systemprompt core content list --source blog
systemprompt core content show blog/my-first-post
```

## Configure Categories

```yaml
sources:
  - name: blog
    categories:
      - name: tutorials
        slug: tutorials
        description: "Step-by-step guides"
        order: 1
      - name: announcements
        slug: announcements
        description: "Product updates"
        order: 2
```

Assign content to category via frontmatter:

```yaml
category: tutorials
```

## Configure Sitemap

```yaml
sources:
  - name: blog
    sitemap:
      enabled: true
      changefreq: weekly
      priority: 0.8
```

Changefreq options: `always`, `hourly`, `daily`, `weekly`, `monthly`, `yearly`, `never`

Regenerate: `systemprompt infra jobs run publish_pipeline`

## Configure RSS

```yaml
sources:
  - name: blog
    rss:
      enabled: true
      title: "Blog Feed"
      description: "Latest posts"
      max_items: 20
      language: "en"
```

## Search Content

```bash
systemprompt core content search "getting started"
systemprompt core content search "tutorial" --source blog
```

## Validate Content

```bash
systemprompt core content validate
```

## Troubleshooting

### Content Not Appearing

Symptoms: File exists but not in list, 404 errors

```bash
systemprompt core content list --source blog
systemprompt core content validate
```

Solutions:
- Not synced: `systemprompt cloud sync local content --direction to-db -y` then `systemprompt infra jobs run publish_pipeline`
- Frontmatter invalid: Add all required fields
- Not public: Set `public: true` in frontmatter

### Content Sync Fails

```bash
systemprompt cloud sync local content --direction to-db --dry-run
systemprompt core content validate
```

Solutions:
- YAML error: Ensure titles with colons are quoted
- Invalid slug: Use lowercase-with-dashes only
- Database error: `systemprompt infra db status`

### Search Not Finding Content

```bash
systemprompt core content search "known text"
systemprompt infra jobs status publish_pipeline
```

Solution: Re-index with `systemprompt infra jobs run publish_pipeline`

### Sitemap Not Updating

Ensure `sitemap.enabled: true` in source config. Regenerate with `systemprompt infra jobs run publish_pipeline`.

### RSS Feed Not Generating

Ensure `rss.enabled: true` in source config. Regenerate with `systemprompt infra jobs run publish_pipeline`.

### Template Rendering Errors

```bash
systemprompt infra logs --context web --level error
```

Check template name in config matches available templates.

### Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Missing field | Frontmatter incomplete | Add required field |
| Invalid date | Wrong format | Use "YYYY-MM-DD" |
| Invalid slug | Spaces/special chars | Use lowercase-with-dashes |
| YAML syntax | Formatting issue | Fix indentation |

## Quick Reference

| Task | Command |
|------|---------|
| List | `core content list` |
| Show | `core content show <source>/<slug>` |
| Search | `core content search "query"` |
| Sync | `cloud sync local content --direction to-db -y` |
| Publish | `infra jobs run publish_pipeline` |
| Validate | `core content validate` |
| By category | `core content list --source blog --category tutorials` |
