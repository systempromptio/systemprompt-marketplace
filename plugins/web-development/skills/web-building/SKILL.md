---
name: web-building
description: "Build web features for systemprompt.io - pages, templates, content ingestion, prerendering, assets, and extension traits"
---

# Web Building

Build web features for systemprompt.io. Reference implementation: `extensions/web/`.

## Page Architecture

Two patterns for generating web pages:

### Content Collections (Markdown)

For blog posts, documentation, articles -- many items with similar structure.

| Aspect | Description |
|--------|-------------|
| Data source | Markdown files with YAML frontmatter |
| Storage | Database (for search, analytics) |
| Template vars | `{{TITLE}}`, `{{DESCRIPTION}}`, `{{CONTENT}}` |

### Configured Pages (YAML)

For homepage, feature pages, landing pages -- singleton pages with custom structure.

| Aspect | Description |
|--------|-------------|
| Data source | `services/web/config.yaml` |
| Template vars | `{{site.homepage.*}}`, `{{feature.*}}` |

**Rule of thumb**: Collections -> Content. Singletons -> Configured.

## Rendering Pipeline

```
Database Query
     |
ContentDataProvider::enrich_content()    # Add computed fields
     |
PageDataProvider::provide_page_data()    # Supply template variables
     |
ComponentRenderer::render()              # Generate HTML fragments
     |
TemplateDataExtender::extend()           # Final modifications
     |
Template rendering                       # Handlebars output
```

## Extension Traits

| Trait | Purpose | Register Via |
|-------|---------|-------------|
| `PagePrerenderer` | Generate entire pages at build time | `page_prerenderers()` |
| `PageDataProvider` | Inject data into existing page types | `page_data_providers()` |
| `ComponentRenderer` | Render HTML fragments for templates | `component_renderers()` |
| `ContentDataProvider` | Enrich content items with extra data | `content_data_providers()` |
| `FrontmatterProcessor` | Parse custom frontmatter fields | `frontmatter_processors()` |
| `TemplateDataExtender` | Final template data modifications | `template_data_extenders()` |

## PagePrerenderer

Generate static HTML pages at build time.

```rust
use std::path::PathBuf;
use anyhow::Result;
use async_trait::async_trait;
use systemprompt::template_provider::{PagePrepareContext, PagePrerenderer, PageRenderSpec};

pub struct BlogListPrerenderer;

#[async_trait]
impl PagePrerenderer for BlogListPrerenderer {
    fn page_type(&self) -> &'static str {
        "blog-list-prerenderer"
    }

    fn priority(&self) -> u32 {
        100
    }

    async fn prepare(&self, ctx: &PagePrepareContext<'_>) -> Result<Option<PageRenderSpec>> {
        let db = ctx.db_pool::<Arc<Database>>().ok_or_else(|| {
            anyhow::anyhow!("No database in context")
        })?;
        let pool = db.pool().ok_or_else(|| anyhow::anyhow!("Pool not initialized"))?;

        let posts = sqlx::query!(
            r#"
            SELECT slug, title, description, image, category, published_at
            FROM markdown_content
            WHERE source_id = 'blog' AND public = true
            ORDER BY published_at DESC
            "#
        )
        .fetch_all(&*pool)
        .await?;

        let cards_html = render_blog_cards(&posts);
        let template_data = json!({
            "POSTS": cards_html,
            "site": ctx.web_config,
        });

        Ok(Some(PageRenderSpec::new(
            "blog-list",
            template_data,
            PathBuf::from("blog/index.html"),
        )))
    }
}
```

Register: `Extension::page_prerenderers()` returns `Vec<Arc<dyn PagePrerenderer>>`.

## PageDataProvider

Supply template variables for pages.

```rust
use systemprompt::extension::prelude::{PageContext, PageDataProvider};

pub struct ContentPageDataProvider;

#[async_trait]
impl PageDataProvider for ContentPageDataProvider {
    fn provider_id(&self) -> &'static str {
        "content-page-data"
    }

    fn applies_to_pages(&self) -> Vec<String> {
        vec![]  // Empty = all pages
    }

    async fn provide_page_data(&self, ctx: &PageContext<'_>) -> Result<Value> {
        let item = ctx.content_item()
            .ok_or_else(|| anyhow::anyhow!("No content item"))?;

        let title = item.get("title").and_then(|v| v.as_str()).unwrap_or("");
        let description = item.get("description").and_then(|v| v.as_str()).unwrap_or("");

        Ok(json!({
            "TITLE": title,
            "DESCRIPTION": description,
        }))
    }
}
```

Register: `Extension::page_data_providers()` returns `Vec<Arc<dyn PageDataProvider>>`.

## ComponentRenderer

Generate reusable HTML fragments for templates.

```rust
use systemprompt::template_provider::{ComponentContext, ComponentRenderer, RenderedComponent};

pub struct ContentCardsRenderer;

#[async_trait]
impl ComponentRenderer for ContentCardsRenderer {
    fn component_id(&self) -> &str {
        "content-cards"
    }

    fn variable_name(&self) -> &str {
        "POSTS"
    }

    fn applies_to(&self) -> Vec<String> {
        vec!["blog-list".to_string()]
    }

    async fn render(&self, ctx: &ComponentContext<'_>) -> Result<RenderedComponent> {
        let items = ctx.all_items.unwrap_or(&[]);
        let html = items
            .iter()
            .filter(|item| {
                item.get("slug").and_then(|v| v.as_str()).is_some_and(|s| !s.is_empty())
            })
            .map(|item| self.render_card(item))
            .collect::<Vec<_>>()
            .join("\n");
        Ok(RenderedComponent::new("POSTS", html))
    }
}
```

Use triple braces in templates for unescaped HTML: `{{{POSTS}}}`.

Register: `Extension::component_renderers()` returns `Vec<Arc<dyn ComponentRenderer>>`.

## ContentDataProvider

Enrich content items with additional data during the early pipeline.

```rust
use systemprompt::extension::prelude::{ContentDataContext, ContentDataProvider};

pub struct DocsContentDataProvider;

#[async_trait]
impl ContentDataProvider for DocsContentDataProvider {
    fn provider_id(&self) -> &'static str {
        "docs-content-enricher"
    }

    fn applies_to_sources(&self) -> Vec<String> {
        vec!["documentation".to_string()]
    }

    async fn enrich_content(
        &self,
        ctx: &ContentDataContext<'_>,
        item: &mut serde_json::Value,
    ) -> Result<()> {
        let kind = item.get("kind").and_then(|v| v.as_str()).unwrap_or("");
        if kind == "docs-index" {
            let children = self.fetch_children(ctx).await?;
            if let Some(obj) = item.as_object_mut() {
                obj.insert("children".to_string(), json!(children));
            }
        }
        Ok(())
    }
}
```

Register: `Extension::content_data_providers()` returns `Vec<Arc<dyn ContentDataProvider>>`.

## FrontmatterProcessor

Hook into content ingestion to parse custom frontmatter fields.

```rust
use systemprompt_provider_contracts::{FrontmatterContext, FrontmatterProcessor};

pub struct MyFrontmatterProcessor;

#[async_trait]
impl FrontmatterProcessor for MyFrontmatterProcessor {
    fn processor_id(&self) -> &'static str {
        "my-frontmatter"
    }

    fn applies_to_sources(&self) -> Vec<String> {
        vec!["docs".to_string()]
    }

    fn priority(&self) -> u32 {
        100
    }

    async fn process_frontmatter(&self, ctx: &FrontmatterContext<'_>) -> Result<()> {
        if let Some(my_field) = ctx.raw_frontmatter().get("my_custom_field") {
            let db = ctx.db_pool::<DbPool>()
                .ok_or_else(|| anyhow::anyhow!("DB not available"))?;
            sqlx::query!(
                "INSERT INTO my_metadata (content_id, custom_field)
                 VALUES ($1, $2)
                 ON CONFLICT (content_id) DO UPDATE SET custom_field = $2",
                ctx.content_id(),
                my_field.as_str()
            )
            .execute(db.as_ref())
            .await?;
        }
        Ok(())
    }
}
```

Register: `Extension::frontmatter_processors()` returns `Vec<Arc<dyn FrontmatterProcessor>>`.

## TemplateDataExtender

Final template data modifications before HTML rendering.

```rust
use systemprompt::template_provider::{ExtenderContext, TemplateDataExtender};

pub struct ReadingTimeExtender;

#[async_trait]
impl TemplateDataExtender for ReadingTimeExtender {
    fn extender_id(&self) -> &str {
        "reading-time"
    }

    fn applies_to(&self) -> Vec<String> {
        vec!["blog".to_string()]
    }

    async fn extend(&self, ctx: &ExtenderContext<'_>, data: &mut Value) -> Result<()> {
        let word_count = ctx.content_html.split_whitespace().count();
        let reading_time = (word_count / 200).max(1);
        if let Some(obj) = data.as_object_mut() {
            obj.insert("READING_TIME_LABEL".to_string(),
                json!(format!("{} min read", reading_time)));
        }
        Ok(())
    }
}
```

Register: `Extension::template_data_extenders()` returns `Vec<Arc<dyn TemplateDataExtender>>`.

## Templates

### Location

```
services/web/templates/
├── templates.yaml      # Template-to-content-type mapping
├── homepage.html
├── blog-post.html
├── blog-list.html
├── docs-page.html
└── docs-list.html
```

### templates.yaml

```yaml
templates:
  homepage:
    content_types:
      - homepage
  blog-post:
    content_types:
      - blog
      - article
  legal-post:
    content_types:
      - legal
```

### Handlebars Syntax

| Syntax | Purpose |
|--------|---------|
| `{{VAR}}` | Escaped output |
| `{{{VAR}}}` | Raw HTML output |
| `{{#if VAR}}...{{/if}}` | Conditional |
| `{{#each items}}...{{/each}}` | Loop |

### Template Variables

| Variable | Source |
|----------|--------|
| `TITLE` | frontmatter `title` |
| `DESCRIPTION` | frontmatter `description` |
| `CONTENT` | Markdown -> HTML |
| `TOC_HTML` | Table of contents |
| `ORG_NAME` | `branding.name` |
| `DISPLAY_SITENAME` | `branding.display_sitename` |

## Content Ingestion

### Data Flow

```
Markdown File (frontmatter + body)
    -> parse_markdown()
    -> ContentMetadata (struct)
    -> CreateContentParams (builder)
    -> ContentRepository::create()
    -> markdown_content (PostgreSQL)
    -> ContentDataProvider::enrich_content()
    -> Enriched JSON (for templates)
```

### Frontmatter Template

```yaml
---
title: "Article Title"
description: "Brief description for SEO"
author: "Author Name"
slug: "url-friendly-slug"
keywords: "comma, separated, keywords"
kind: "article"
image: "/files/images/blog/featured.webp"
public: true
published_at: "2025-12-11"
updated_at: "2026-01-13"
---
```

### Content Types (kind)

| Kind | Use For |
|------|---------|
| `article` | Blog posts, news |
| `paper` | Research, whitepapers |
| `guide` | How-to guides |
| `tutorial` | Learning materials |
| `reference` | API docs, CLI reference |
| `docs` | Generic documentation |

Source of truth: `extensions/web/src/models/content.rs` (`ContentKind` enum).

### Adding New Content Kinds

Update three places:
1. `extensions/web/src/models/content.rs` - Add variant to `ContentKind` enum
2. Same file - Add to `as_str()` and `FromStr` impl
3. `services/content/config.yaml` - Add to `allowed_content_types` for source

## CSS and Assets

### CSS File Location (CRITICAL)

**All CSS files go in `storage/files/css/`**

```
storage/files/css/           <- PUT CSS FILES HERE
extensions/web/src/extension.rs  <- REGISTER in required_assets()
web/dist/css/               <- OUTPUT (generated, never edit)
```

### Adding CSS

1. Create file in `storage/files/css/my-page.css`
2. Register in `extension.rs`:
   ```rust
   fn required_assets(&self, paths: &SystemPaths) -> Vec<AssetDefinition> {
       let storage_css = paths.storage_files().join("css");
       vec![
           AssetDefinition::css(storage_css.join("my-page.css"), "css/my-page.css"),
       ]
   }
   ```
3. Build: `just build && systemprompt infra jobs run publish_pipeline`
4. Reference: `<link rel="stylesheet" href="/css/my-page.css">`

### URL Routing

| URL Path | Served From |
|----------|-------------|
| `/css/*` | `web/dist/css/` |
| `/js/*` | `web/dist/js/` |
| `/fonts/*` | `web/dist/fonts/` |
| `/files/*` | `storage/files/` |

## Theme Configuration

`services/web/config.yaml`:

```yaml
branding:
  copyright: "2024 Company"
  twitter_handle: "@handle"
  display_sitename: true
  favicon: "/favicon.ico"
  logo:
    primary:
      svg: "/logo.svg"

colors:
  light:
    primary:
      hsl: "hsl(0, 0%, 35%)"
    text:
      primary: "#111111"

typography:
  sizes:
    md: "15px"
  weights:
    regular: 400
    bold: 700
```

## Adding a New Content Type

1. Define `kind` in frontmatter
2. Add to content source in `services/content/config.yaml`
3. Map to template in `templates.yaml`
4. Create template file in `services/web/templates/`

## Building List Pages

List pages use content type `{source}-list` (e.g., `blog-list`, `documentation-list`).

Required coordination:
- `PageDataProvider` supplies `TITLE`, `DESCRIPTION`
- `ComponentRenderer` supplies `POSTS` (rendered HTML cards)
- Template uses `{{{POSTS}}}` for unescaped HTML

## Web Content Editing Workflow

| Content Type | Location | Job to Publish |
|--------------|----------|----------------|
| Homepage template | `services/web/templates/homepage.html` | `page_prerender` |
| Blog templates | `services/web/templates/blog-*.html` | `content_prerender` |
| Blog/docs content | `services/content/blog/*.md` | `content_prerender` |
| CSS/JS | `storage/files/css/`, `storage/files/js/` | `copy_extension_assets` |
| Theme/branding | `services/web/config.yaml` | `page_prerender` |

## Quick Reference

| Task | Command |
|------|---------|
| Full publish | `systemprompt infra jobs run publish_pipeline` |
| Prerender pages | `systemprompt infra jobs run page_prerender` |
| Prerender content | `systemprompt infra jobs run content_prerender` |
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Ingest content | `systemprompt infra jobs run blog_content_ingestion` |
| List content | `systemprompt core content list --source <source>` |
| Search content | `systemprompt core content search "<query>"` |
| Upload image | `systemprompt core files upload <path>` |
| Build | `just build` |

## Reference Implementations

| Concept | Location |
|---------|----------|
| Extension trait | `extensions/web/src/extension.rs` |
| Content models | `extensions/web/src/models/content.rs` |
| Ingestion service | `extensions/web/src/services/ingestion.rs` |
| Content repository | `extensions/web/src/repository/content.rs` |
| Jobs | `extensions/web/src/jobs/` |
| Templates | `services/web/templates/` |
| Theme config | `services/web/config.yaml` |
