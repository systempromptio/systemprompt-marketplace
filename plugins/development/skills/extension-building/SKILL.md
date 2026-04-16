---
name: extension-building
description: "Build library extensions for systemprompt.io with Rust - architecture, traits, schemas, API routes, jobs, and code review"
---

# Extension Building

Build library extensions for systemprompt.io. Reference implementation: `extensions/web/`.

## Core Principle

**If it's Rust code, it's an extension. If it's YAML/Markdown, it's a service.**

| Category | Format | Location |
|----------|--------|----------|
| Extensions | `.rs` | `/extensions/` |
| Services | YAML/Markdown | `/services/` |

The `core/` directory is a git submodule. **Never modify it.**

## Project Structure

```
systemprompt-template/
├── core/                     # READ-ONLY submodule
├── extensions/               # ALL Rust code
│   ├── web/                 # Reference implementation
│   ├── cli/                 # CLI extensions
│   └── mcp/                 # MCP servers
├── services/                 # YAML/Markdown only
│   ├── agents/              # Agent definitions
│   ├── config/              # Configuration
│   ├── content/             # Markdown content
│   ├── skills/              # Skills
│   └── web/                 # Theme config
├── profiles/                 # Environment configs
└── src/main.rs              # Server entry
```

## Layer Model

```
┌─────────────────────────────────────────────┐
│              src/main.rs                     │
│  Loads config, connects DB, mounts routers   │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│              extensions/                     │
│  Schemas, Models, Repos, Services, API, Jobs │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│              services/ (config)              │
│  Agent YAML, AI config, schedules, content   │
└──────────────────────┬──────────────────────┘
                       │ imports
┌──────────────────────▼──────────────────────┐
│              core/ (read-only)               │
│  Traits, Models, IDs, DB, Logging, Security  │
└─────────────────────────────────────────────┘
```

## Extension Internal Layers

```
┌─────────────────────────────┐
│     API (handlers)          │  HTTP requests
└─────────────┬───────────────┘
              │ calls
┌─────────────▼───────────────┐
│     Services                │  Business logic
└─────────────┬───────────────┘
              │ calls
┌─────────────▼───────────────┐
│     Repository              │  SQL queries
└─────────────┬───────────────┘
              │ uses
┌─────────────▼───────────────┐
│     Models                  │  Domain types
└─────────────────────────────┘
```

**Rules:**
- API -> Services -> Repository (never skip)
- No SQL in services
- No business logic in repositories
- Jobs use services, not direct repository access

## Creating an Extension

### Directory Structure

```
extensions/my-extension/
├── Cargo.toml
├── schema/
│   └── 001_tables.sql
└── src/
    ├── lib.rs
    ├── extension.rs
    ├── error.rs
    ├── models/
    ├── repository/
    ├── services/
    ├── api/
    └── jobs/
```

### Cargo.toml

```toml
[package]
name = "my-extension"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["rlib"]

[dependencies]
systemprompt = { workspace = true }
axum = { workspace = true }
tokio = { workspace = true }
sqlx = { workspace = true }
serde = { workspace = true }
serde_json = { workspace = true }
async-trait = { workspace = true }
anyhow = { workspace = true }
thiserror = { workspace = true }
tracing = { workspace = true }
```

### src/lib.rs

```rust
mod error;
mod extension;
mod models;
mod repository;
mod services;
mod api;
mod jobs;

pub use error::MyExtensionError;
pub use extension::MyExtension;

pub const PREFIX: &str = "my-extension";
```

### src/extension.rs

```rust
use std::sync::Arc;
use systemprompt::extension::prelude::*;

use crate::api;
use crate::jobs::CleanupJob;

#[derive(Debug, Default)]
pub struct MyExtension;

impl Extension for MyExtension {
    fn metadata(&self) -> ExtensionMetadata {
        ExtensionMetadata {
            id: "my-extension",
            name: "My Extension",
            version: env!("CARGO_PKG_VERSION"),
        }
    }

    fn priority(&self) -> u32 {
        50
    }

    fn dependencies(&self) -> Vec<&'static str> {
        vec!["users"]
    }

    fn schemas(&self) -> Vec<SchemaDefinition> {
        vec![
            SchemaDefinition::inline("my_tables", include_str!("../schema/001_tables.sql")),
        ]
    }

    fn migration_weight(&self) -> u32 {
        50
    }

    fn router(&self, ctx: &dyn ExtensionContext) -> Option<ExtensionRouter> {
        let db = ctx.database();
        let pool = db.as_any().downcast_ref::<Database>()?.pool()?;
        Some(ExtensionRouter::new(api::router(pool), "/api/v1/my-extension"))
    }

    fn jobs(&self) -> Vec<Arc<dyn Job>> {
        vec![Arc::new(CleanupJob)]
    }
}

register_extension!(MyExtension);
```

### src/error.rs

```rust
use axum::http::StatusCode;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyExtensionError {
    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Validation error: {0}")]
    Validation(String),
}

impl MyExtensionError {
    pub fn code(&self) -> &'static str {
        match self {
            Self::NotFound(_) => "NOT_FOUND",
            Self::Database(_) => "DATABASE_ERROR",
            Self::Validation(_) => "VALIDATION_ERROR",
        }
    }

    pub fn status(&self) -> StatusCode {
        match self {
            Self::NotFound(_) => StatusCode::NOT_FOUND,
            Self::Database(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Self::Validation(_) => StatusCode::BAD_REQUEST,
        }
    }
}

impl axum::response::IntoResponse for MyExtensionError {
    fn into_response(self) -> axum::response::Response {
        // JSON: API boundary -- constructing fixed-shape error response
        let body = serde_json::json!({
            "error": {
                "code": self.code(),
                "message": self.to_string(),
            }
        });
        (self.status(), axum::Json(body)).into_response()
    }
}
```

## Database Schema

### SQL Patterns

```sql
CREATE TABLE IF NOT EXISTS my_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_my_items_name ON my_items(name);
CREATE INDEX IF NOT EXISTS idx_my_items_created ON my_items(created_at DESC);
```

### Register Schema

```rust
fn schemas(&self) -> Vec<SchemaDefinition> {
    vec![
        SchemaDefinition::inline("my_items", include_str!("../schema/001_tables.sql")),
    ]
}

fn migration_weight(&self) -> u32 {
    50
}
```

### Migrations

```rust
fn migrations(&self) -> Vec<Migration> {
    vec![
        Migration::new(1, "add_status",
            "ALTER TABLE my_items ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active'"),
    ]
}
```

### Extending Core Tables

Use companion tables, not ALTER:

```sql
CREATE TABLE IF NOT EXISTS content_metadata (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL UNIQUE,
    custom_field JSONB DEFAULT '{}',
    CONSTRAINT fk_content
        FOREIGN KEY (content_id) REFERENCES markdown_content(id) ON DELETE CASCADE
);
```

## API Routes

### Router

```rust
use axum::{Router, routing::{get, post, put, delete}};
use std::sync::Arc;
use sqlx::PgPool;

mod handlers;

#[derive(Clone)]
pub struct AppState {
    pub pool: Arc<PgPool>,
}

pub fn router(pool: Arc<PgPool>) -> Router {
    let state = AppState { pool };
    Router::new()
        .route("/items", get(handlers::list).post(handlers::create))
        .route("/items/:id", get(handlers::get).put(handlers::update).delete(handlers::delete))
        .with_state(state)
}
```

### Handlers

```rust
use axum::{extract::{Path, State, Json}, http::StatusCode};
use uuid::Uuid;

pub async fn list(
    State(state): State<AppState>,
) -> Result<Json<Vec<Item>>, MyExtensionError> {
    let items = sqlx::query_as!(Item, "SELECT * FROM my_items ORDER BY created_at DESC")
        .fetch_all(state.pool.as_ref())
        .await?;
    Ok(Json(items))
}

pub async fn get(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<Item>, MyExtensionError> {
    let item = sqlx::query_as!(Item, "SELECT * FROM my_items WHERE id = $1", id)
        .fetch_optional(state.pool.as_ref())
        .await?
        .ok_or_else(|| MyExtensionError::NotFound(id.to_string()))?;
    Ok(Json(item))
}

pub async fn create(
    State(state): State<AppState>,
    Json(input): Json<CreateInput>,
) -> Result<(StatusCode, Json<Item>), MyExtensionError> {
    let item = sqlx::query_as!(
        Item,
        "INSERT INTO my_items (name, description) VALUES ($1, $2) RETURNING *",
        input.name,
        input.description
    )
    .fetch_one(state.pool.as_ref())
    .await?;
    Ok((StatusCode::CREATED, Json(item)))
}
```

## Background Jobs

### Job Implementation

```rust
use systemprompt_provider_contracts::{Job, JobContext, JobResult};

#[derive(Debug, Clone, Copy, Default)]
pub struct CleanupJob;

#[async_trait::async_trait]
impl Job for CleanupJob {
    fn name(&self) -> &'static str {
        "my-extension-cleanup"
    }

    fn description(&self) -> &'static str {
        "Clean up expired items"
    }

    fn schedule(&self) -> &'static str {
        "0 0 * * * *"
    }

    async fn execute(&self, ctx: &JobContext) -> anyhow::Result<JobResult> {
        let pool = ctx.db_pool::<Arc<PgPool>>()
            .ok_or_else(|| anyhow::anyhow!("Database not available"))?;

        let deleted = sqlx::query!(
            "DELETE FROM my_items WHERE created_at < NOW() - INTERVAL '30 days'"
        )
        .execute(&*pool)
        .await?
        .rows_affected();

        tracing::info!(deleted = deleted, "Cleanup completed");

        Ok(JobResult::success()
            .with_stats(deleted, 0)
            .with_message(format!("Deleted {} items", deleted)))
    }
}

systemprompt::traits::submit_job!(&CleanupJob);
```

### Cron Schedule (6-field)

| Schedule | Meaning |
|----------|---------|
| `0 0 * * * *` | Every hour |
| `0 */15 * * * *` | Every 15 minutes |
| `0 0 0 * * *` | Daily at midnight |
| `0 30 2 * * *` | Daily at 2:30 AM |
| `""` | Manual only |

### Register Job

```rust
fn jobs(&self) -> Vec<Arc<dyn Job>> {
    vec![Arc::new(CleanupJob)]
}
```

## Workspace Registration

### Add to root Cargo.toml

```toml
[workspace]
members = [
    "extensions/my-extension",
]

[dependencies]
my-extension = { path = "extensions/my-extension" }
```

### Link in src/lib.rs

```rust
pub use my_extension as my_ext;

pub fn __force_extension_link() {
    let _ = core::hint::black_box(&my_ext::PREFIX);
}
```

## Rust Standards

### Idiomatic Patterns

```rust
let name = request.name.as_deref().map(str::trim);
let value = opt.unwrap_or_else(|| compute_default());
let result = input.ok_or_else(|| Error::Missing)?;

let valid_items: Vec<_> = items
    .iter()
    .filter(|item| item.is_active())
    .map(|item| item.to_dto())
    .collect();
```

### Forbidden Constructs

| Construct | Resolution |
|-----------|------------|
| `unsafe` | Remove - forbidden |
| `unwrap()` | Use `?`, `ok_or_else()`, or `expect()` with message |
| `panic!()` / `todo!()` | Return `Result` or implement |
| Inline comments (`//`) | Delete - code documents itself |
| Doc comments (`///`) | Delete - no rustdoc |
| Tests in source files | Move to separate test crate |
| `serde_json::Value` | Define typed structs with `#[derive(Deserialize)]`. Allowed only at protocol/trait boundaries with justification comment |

### Mandatory Patterns

- **Typed identifiers**: Use `ContentId`, `UserId`, etc. from `systemprompt_identifiers`
- **Logging**: All via `tracing`. No `println!` in library code
- **Repository pattern**: Services never execute queries directly. All SQL in repositories using SQLX macros
- **SQLX macros only**: `query!()`, `query_as!()`, `query_scalar!()` - compile-time verified
- **Error handling**: Domain-specific errors with `thiserror`
- **DateTime**: `DateTime<Utc>` in Rust, `TIMESTAMPTZ` in PostgreSQL
- **Builder pattern**: Required for types with 3+ fields

### Naming Conventions

| Prefix | Returns |
|--------|---------|
| `get_` | `Result<T>` - fails if missing |
| `find_` | `Result<Option<T>>` - may not exist |
| `list_` | `Result<Vec<T>>` |
| `create_` | `Result<T>` or `Result<Id>` |
| `update_` | `Result<T>` or `Result<()>` |
| `delete_` | `Result<()>` |

### Code Limits

| Metric | Limit |
|--------|-------|
| Source file length | 300 lines |
| Cognitive complexity | 15 |
| Function length | 75 lines |
| Parameters | 5 |

### Derive Ordering

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
```

## Database Access Patterns

### MCP Server Handlers

```rust
let pg_pool = db_pool.pool().ok_or_else(|| {
    McpError::internal_error("Database pool not available", None)
})?;
let repo = ContentRepository::new(pg_pool);
```

### Job Handlers

```rust
let db_pool = ctx.db_pool::<DbPool>()
    .ok_or_else(|| anyhow::anyhow!("Database not available"))?;
let repo = ContentRepository::new(db_pool.pool().unwrap());
```

### Page Data Providers

```rust
// JSON: required by PageDataProvider trait contract
let Some(db) = ctx.db_pool::<Arc<Database>>() else {
    return Ok(json!({ "data": "" }));
};
let Some(pool) = db.pool() else {
    return Ok(json!({ "data": "" }));
};
```

## Dependency Rules

### Extensions CAN Import

```toml
systemprompt-models = { git = "..." }
systemprompt-identifiers = { git = "..." }
systemprompt-traits = { git = "..." }
systemprompt-core-database = { git = "..." }
systemprompt-blog-extension = { path = "../blog" }
```

### Extensions CANNOT Import

```toml
systemprompt-core-api = { git = "..." }        # FORBIDDEN
systemprompt-core-scheduler = { git = "..." }  # FORBIDDEN
```

## The systemprompt Umbrella Crate

Use a single dependency instead of multiple internal crates:

```toml
[dependencies]
systemprompt = { version = "0.1", features = ["api"] }
```

| Feature | Use Case |
|---------|----------|
| `core` | Minimal extensions, CLI tools |
| `database` | Extensions with database tables |
| `mcp` | MCP servers with proc macros |
| `api` | Full HTTP API extensions |
| `full` | Complete applications |

## Extension Checklist

- [ ] `Cargo.toml` with `crate-type = ["rlib"]` and workspace dependencies
- [ ] `src/lib.rs` exports public API and `PREFIX` constant
- [ ] `src/extension.rs` implements `Extension` trait
- [ ] `register_extension!` macro called
- [ ] `src/error.rs` implements error types with `thiserror`
- [ ] Schema files use `IF NOT EXISTS` patterns
- [ ] Linked in template `src/lib.rs` via `__force_extension_link()`
- [ ] Added to workspace members in root `Cargo.toml`
- [ ] `cargo clippy -p {crate} -- -D warnings` passes
- [ ] `cargo fmt -p {crate} -- --check` passes

## Review Process

Review extensions as world-class idiomatic Rust. Generate `status.md` with:

1. Verify required files exist
2. Verify directory structure
3. Read all `.rs` files
4. Execute checklist items
5. Record violations as `file:line` + type
6. Verdict: COMPLIANT if zero violations

## Quick Reference

| Task | Command |
|------|---------|
| Build | `cargo build -p systemprompt-{name}-extension` |
| Test | `cargo test -p systemprompt-{name}-extension` |
| Lint | `cargo clippy -p systemprompt-{name}-extension -- -D warnings` |
| Format | `cargo fmt --all` |
| Clean build | `cargo clean && cargo build` |
| Verify | `cargo run -- extensions list` |
| Run migrations | `systemprompt infra db migrate` |
| Run job | `systemprompt infra jobs run <name>` |

## Reference Implementations

| Concept | Location |
|---------|----------|
| Extension trait | `extensions/web/src/extension.rs` |
| ExtensionError | `extensions/web/src/error.rs` |
| Repository | `extensions/web/src/repository/` |
| Service | `extensions/web/src/services/` |
| API | `extensions/web/src/api/` |
| Jobs | `extensions/web/src/jobs/` |
