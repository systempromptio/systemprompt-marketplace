---
name: rust-coding-standards
description: "Rust coding standards, documentation authoring, content workflows, and quality patterns for systemprompt.io development"
---

# Coding Standards

All code and content standards for systemprompt.io. Follow without exception.

## Core Principle

systemprompt.io is a world-class Rust programming brand. Every file must be instantly recognizable as on-brand, world-class idiomatic code.

## Code Locations

| Type | Location | Language |
|------|----------|----------|
| Extensions | `extensions/*/src/` | Rust |
| MCP Servers | `extensions/mcp/*/src/` | Rust |
| Agents | `services/agents/*.yaml` | YAML |
| Skills | `services/skills/**/*.yaml` | YAML |
| Config | `services/config/*.yaml` | YAML |

## Rust Standards

Primary language for all extensions, MCP servers, and core logic.

- Write idiomatic Rust (Steve Klabnik style)
- Use typed identifiers from `systemprompt_identifiers`
- SQLX macros only (`query!`, `query_as!`, `query_scalar!`)
- Repository pattern for all database access
- `thiserror` for domain-specific errors, `anyhow` only at application boundaries
- All logging via `tracing` -- no `println!` in library code
- Builder pattern required for types with 3+ fields or mixed required/optional fields

### Error Handling

```rust
#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("Item not found: {0}")]
    NotFound(String),
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}
```

### Logging

```rust
tracing::info!(user_id = %user.id, "Created user");
tracing::error!(error = %e, "Operation failed");
```

### Forbidden Constructs

| Construct | Resolution |
|-----------|------------|
| `unsafe` | Remove -- forbidden |
| `unwrap()` | Use `?`, `ok_or_else()`, or `expect()` |
| `panic!()` / `todo!()` | Return `Result` or implement |
| Inline comments (`//`) | Delete -- code documents itself |
| Doc comments (`///`) | Delete -- no rustdoc |
| `println!` in libraries | Use `tracing` |
| Raw SQL strings | Use SQLX macros |

### File Limits

| Metric | Limit |
|--------|-------|
| Source file length | 300 lines |
| Cognitive complexity | 15 |
| Function length | 75 lines |
| Parameters | 5 |

### Naming Conventions

| Prefix | Returns |
|--------|---------|
| `get_` | `Result<T>` -- fails if missing |
| `find_` | `Result<Option<T>>` -- may not exist |
| `list_` | `Result<Vec<T>>` |
| `create_` | `Result<T>` or `Result<Id>` |
| `update_` | `Result<T>` or `Result<()>` |
| `delete_` | `Result<()>` |

### Allowed Abbreviations

`id`, `uuid`, `url`, `jwt`, `mcp`, `a2a`, `api`, `http`, `json`, `sql`, `ctx`, `req`, `res`, `msg`, `err`, `cfg`

## Extension Requirements

Every extension requires:

- `Cargo.toml` with systemprompt dependencies
- `src/extension.rs` implementing Extension trait
- `src/error.rs` implementing ExtensionError trait
- Schema files in `schema/` numbered `001_*.sql`

## MCP Server Requirements

Every MCP server requires:

- Tool definitions with JSON schemas
- Error handling with domain-specific errors
- Structured logging via `tracing`

## Documentation Authoring

### Required Frontmatter

```yaml
---
title: "Page Title"
description: "SEO description (150-160 characters)"
slug: "section/page-name"
kind: "guide"
public: true
published_at: "2025-01-27"
after_reading_this:
  - "First learning objective (action verb)"
  - "Second learning objective"
---
```

### Content Types

| Kind | Use For |
|------|---------|
| `docs-index` | Section index pages |
| `guide` | How-to guides, tutorials |
| `reference` | API, CLI, config reference |
| `page` | Static pages (FAQ, glossary) |

### Linking Strategy

Always use absolute paths from docs root:

```markdown
[Installation](/documentation/installation)
[Services](/documentation/services)
```

### Grounding Requirements

Every CLI command or code reference MUST include a grounding link:

| Reference Type | Grounding Link Required |
|----------------|------------------------|
| CLI command | Link to `--help` output |
| Rust crate | Link to crates.io page |
| Code snippet | Link to GitHub source file |
| Configuration | Link to schema or config file |

## Content Workflows

### Create and Publish Blog Post

1. Create markdown file in `services/content/blog/`
2. Include required frontmatter (title, description, author, slug, keywords, kind, image, public, tags, published_at)
3. Run: `systemprompt infra jobs run publish_pipeline`
4. Verify: `systemprompt core content verify <slug> --source blog`

### Add Custom CSS

1. Create file in `storage/files/css/`
2. Register in `extensions/web/src/extension.rs` `required_assets()`
3. Run: `just build && systemprompt infra jobs run copy_extension_assets`
4. Reference in template: `<link rel="stylesheet" href="/css/custom.css">`

### Add Custom JavaScript

1. Create file in `storage/files/js/`
2. Register in `extensions/web/src/extension.rs` `required_assets()`
3. Run: `systemprompt infra jobs run copy_extension_assets`
4. Reference in template: `<script src="/js/custom.js" defer></script>`

## Validation Workflow

Before committing any code:

```bash
cargo clippy --workspace -- -D warnings
cargo fmt --all
cargo test --workspace
just build
```

### Documentation Validation

- `title` under 60 characters
- `description` is 150-160 characters
- `after_reading_this` has 3-5 items with action verbs
- Single H1 (page title only)
- All internal links use absolute paths
- All CLI commands have grounding links

## Quick Reference

| Task | Command |
|------|---------|
| Lint | `cargo clippy --workspace -- -D warnings` |
| Format | `cargo fmt --all` |
| Test | `cargo test --workspace` |
| Build | `just build` |
| Publish content | `systemprompt infra jobs run publish_pipeline` |
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Verify content | `systemprompt core content verify <slug> --source blog` |
