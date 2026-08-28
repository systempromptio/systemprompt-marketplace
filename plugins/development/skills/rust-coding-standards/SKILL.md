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
- `thiserror` for domain-specific errors, `anyhow` only at application boundaries (`entry/cli`, `entry/api`). **Library crates MUST NOT expose `anyhow::Error` in their public API.**
- All logging via `tracing` -- no `println!` in library code
- Builder pattern required for types with 3+ fields or mixed required/optional fields
- Native `async fn` in traits (Rust 1.75+) by default. Use `#[async_trait]` only when the trait must be `dyn`-compatible; document the reason on the trait.

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

#### HTTP error propagation (entry layer)

HTTP status mapping lives at the **entry layer only**; `domain/*` must never reference the HTTP
envelope (`ApiError`) — Domain → HTTP inverts the dependency rule. The orphan rule forbids
`impl From<DomainError> for ApiError` in `entry/api`, so map domain → HTTP via an **entry-local
error type** that owns the `From` impls (the `oauth/error/` `OAuthHttpError` and `error/`
`ApiHttpError` pattern), then propagate with bare `?`. Variant → status is decided once, in one
place; `IntoResponse` logs exactly once by status class. Reuse the shared
`From<RepositoryError|ServiceError> for ApiError` for methods that return those.

**Banned:** inline `map_err(|e| ApiError::ctor(format!("…{e}")))` at HTTP call sites — it discards
the typed cause and flattens distinct failure modes into one status (a DB outage becomes a 404).
Also banned: `tracing::*` inside a `map_err` that then propagates (the boundary logs once).
`map_err` stays correct for deliberate variant re-classification (must `match`, not catch-all) and
for adapting a foreign, variant-less error (`http::Error`, `std::io::Error`) at the boundary.

### Logging

The message is a static event label; every runtime value is a structured field. Interpolating
a named value into the message is banned — interpolated messages can't be filtered or aggregated.

```rust
tracing::info!(user_id = %user.id, "Created user");   // required
tracing::error!(error = %e, "Operation failed");      // required
tracing::info!("Created user {}", user.id);           // banned
```

The sole exception is a freeform prepared string carrying no named value (`tracing::debug!("{summary}")`).

### Forbidden Constructs

| Construct | Resolution |
|-----------|------------|
| `unsafe` | Remove -- forbidden |
| `unwrap()` / `expect()` | Use `?` or `ok_or_else()`. `expect()` is permitted **only** in macro-generated `From<String>` impls for validated typed IDs and for compile-time-constant `Regex::new()`; both must be unreachable at runtime. |
| `panic!()` / `todo!()` / `unimplemented!()` | Return `Result` or implement |
| `map_err(\|e\| ApiError::ctor(format!("…{e}")))` at an HTTP call site | Map domain → HTTP via an entry-local error type's `From` impls and propagate with bare `?`; the variant decides the status. Exempt: deliberate variant re-classification (`match`, not catch-all) and foreign variant-less adaptation (`http::Error`, `io::Error`). |
| `dbg!()` / `println!` / `eprintln!` in libraries | Use `tracing`. CLI-display layers (`infra/logging/services/cli`, `database/services/display`) and `build.rs` `cargo:rerun-if-changed=` directives are exempt -- nothing else. |
| Interpolating a named value into a `tracing` message (`tracing::info!("started {}", name)`) | Emit it as a structured field: `tracing::info!(name = %name, "started")`. Identifiers, counts, paths, and errors are fields, not message text. |
| Inline comments (`//`) | Delete unless they encode a non-obvious *why*. WHAT-comments are banned; WHY-comments are required when the code's intent is not derivable from naming. Never narrate "what we just changed" or reference past callers/issues. |
| Doc comments (`///`) | Reserved for **pub traits, top-level types (`struct`/`enum`/`union`/`type`), and `mod` declarations** — and even there only when the doc carries non-obvious value. `///` on functions, methods, consts, statics, struct fields, enum variants, or macros is **banned** (machine-enforced by `scripts/lint-inline-comments.sh`): a non-obvious constraint on such an item becomes a `// Why:` comment or moves into the owning type/trait's `///` or the module's `//!`. See "Rustdoc placement" below. |
| Raw SQL strings (`sqlx::query()`) | Use compile-time-verified `query!` / `query_as!` / `query_scalar!`. Allowlist (and ONLY this allowlist) for dynamic SQL: `crates/infra/database/src/admin/**` and `crates/infra/database/src/services/postgres/{introspection,query_executor,transaction,ext}.rs`. Anything else is a violation. |
| `serde_json::Value` | Define typed structs with `#[derive(Deserialize)]` -- see exceptions below |
| `let _ = <fallible>` | Banned for `Result`/`#[must_use]` exprs. Use `?`, log on error, or `.ok()` with a `tracing::warn!` first. Permitted ONLY for: unused trait-arg suppression in default method bodies, `OnceCell::set()` idempotent init, and writes to a CLI display sink that recursing into `tracing` would itself be the failure mode. Each exemption must be justified inline as a `// Why: ...` comment. |
| `.ok()` discarding `Result` | Add a `tracing::warn!(error = %e, "...")` BEFORE converting to `Option`. Carve-outs: `std::env::var(...).ok()`, HTTP-header `to_str().ok()`, integer `try_from().ok()` -- "missing-is-normal" cases only. |
| `*Manager` type names | Use `*Service` (default), `*Handler` (HTTP/RPC request handlers only), `*Orchestrator` (cross-domain workflows only). |
| Raw `String` / `&str` for entity IDs | Use typed IDs from `systemprompt_identifiers` constructed via `TypedId::new(s)` or `TypedId::try_new(s)?`. `From<String>` / `.into()` are forbidden at call sites (the impls exist for serde/`Into<T>` bounds only). Carve-out: A2A protocol types in `models/a2a/protocol/*` retain `String` to match external JSON-RPC spec. |
| `#[cfg(test)] mod tests` | Banned. Tests live in `crates/tests/unit/<layer>/<crate>/`. |
| Backwards-compat shims, `Option<T>` migration stubs, dual code paths | Land the new code AND delete the old form in the same PR. No deprecation periods inside this repo. |
| Imperative SQL in `<crate>/schema/*.sql` | Schema files are pure declarative target state. Allowed: `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, `CREATE [OR REPLACE] FUNCTION/VIEW/TRIGGER`, `CREATE TYPE`, `CREATE EXTENSION IF NOT EXISTS`, `COMMENT ON`. Rejected: `ALTER`, `DROP`, top-level `DO $$`, `UPDATE`/`INSERT`/`DELETE`, `TRUNCATE`, `GRANT`, `REVOKE`. State transitions go in `<crate>/schema/migrations/NNN_<name>.sql`. Boot-time linter at `infra/database/services/schema_linter` hard-rejects; pre-merge gate: `just lint-schema`. See `instructions/information/migrations.md`. |
| SQL string literals or hand-written `Migration::new(...)` in `extension.rs` | No SQL as a Rust string. Schema DDL lives in `<crate>/schema/<table>.sql`, embedded via `include_str!()`. Migration SQL lives in `<crate>/schema/migrations/NNN_<name>.sql`, discovered by the crate's `build.rs` (`systemprompt_extension::build::emit_migrations()`) and returned by `extension_migrations!()` — version and name come from the filename, never a hand-listed `Vec<Migration>`. Pre-merge gate: `just lint-extensions`. |

### Public-API Hygiene (published crates)

Any crate published to crates.io has a different bar than internal application code. The rules below are MANDATORY for `shared/*`, `infra/*`, `domain/*`, `app/*`, and the `systemprompt` facade.

| Rule | Required state |
|------|----------------|
| Crate / module heads | `//!` on `lib.rs` (purpose, public surface, feature matrix, error model). `//!` on every significant `pub mod` file. **No `///` walls of paraphrase below that.** |
| Public errors | `thiserror`-derived enum in `error.rs`; **never** `anyhow::Error` in a `pub fn` signature |
| Feature flags | Documented in `lib.rs` `//!` matrix; `[package.metadata.docs.rs] all-features = true` set in `Cargo.toml` |
| Examples | At least one runnable example per major feature flag in `examples/` (compiled in CI) — the facade's docs.rs landing page should show real usage, not a wall of one-liners |
| Re-exports | Facade `pub use` lines stay bare — `///` is not a permitted placement on re-exports; the crate/module `//!` heads explain the surface |
| Semver | Breaking changes go through a deliberate major bump, never piggyback on a patch |
| `cargo doc -D warnings` | Must pass — broken intra-doc links are bugs. This is **not** the same as "every item must have a doc"; do NOT enable `#![deny(missing_docs)]` workspace-wide. |

### CHANGELOG authoring

Every published crate has a `CHANGELOG.md`. Entries are written for **downstream consumers** (the people opening the file on crates.io / docs.rs), not for the team that shipped the code. The reference register is the `tokio`, `sqlx`, and `serde` changelogs — terse, neutral, consumer-facing.

**Required structure per release:**

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Breaking
- **Breaking:** `<signature change>`. Migrate by `<one-line action>`.

### Added
- `<one-sentence user-visible addition>`.

### Changed
- `<one-sentence user-visible change>`.

### Fixed
- `<one-sentence user-visible fix>`.

### Removed
- `<one-sentence removal>`. Migrate by `<one-line action>`.
```

- Reverse-chronological order. ISO 8601 dates. One heading per release.
- Group strictly under `### Breaking`, `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Deprecated`. No custom sections.
- One sentence per bullet for the user-visible change. A second sentence is reserved for migration guidance — only include when non-obvious.
- Breaking changes always lead with `**Breaking:**`, name the affected symbol, and end with `Migrate by …`.

**Banned framing** (caught in review, rewritten before tag):

- "Phase 1 / Phase 2 / Phase N" — internal sequencing.
- "wave", "overhaul", "the great X migration" — release-narrative language.
- "we got burned", "the regression that broke 0.9.1", "the prod incident where …" — team-internal anecdotes.
- "previously the scanner did X, now it does Y" — archaeology. State the new behaviour; if archaeology matters, link the commit hash.
- File-line traces inline (`crates/infra/database/src/services/executor.rs:execute_statements_parsed`) — link the symbol, don't dump the path.
- Marketing language: "world-class", "best-in-class", "industry-leading". Emojis.

**Reviewer test.** Read the entry aloud as a downstream maintainer who has never met the team. If any sentence needs team context to parse, rewrite it.

### Rustdoc placement (the rule)

`///` exists to answer questions a reader CANNOT answer from the type, the signature, and the function name. Anything that just restates them is noise.

**Placement is mechanical, not judgment-based.** `///` may appear ONLY on `pub` traits, top-level types (`struct`, `enum`, `union`, `type` aliases), and `mod` declarations. It is banned everywhere else — free functions, methods (obvious or not), associated consts, statics, struct fields, enum variants, and `macro_rules!`. This is enforced by `scripts/lint-inline-comments.sh`. When a function or method carries a genuinely non-obvious constraint, encode it as a `// Why:` inline comment above the item, or lift it into the owning trait/type's `///` block or the module's `//!` head — the contract belongs on the surface a reader lands on, not scattered per-method.

**Within the allowed placements, add `///` only when one of these is true** — and in every case the comment must encode something that **is not present in the code at all**. If the fact can be reconstructed by reading the body, the signature, and the names, it is not an exception, no matter how accurately the prose restates it:

- A hidden constraint or invariant the signature does not encode (e.g. "callers must hold the registry lock before calling").
- An error case that is non-obvious AND not implied by the `Result` type (e.g. "returns `Err(InvalidGrant)` if the code was issued for a different `client_id`" — yes; "errors if the query matches zero or more than one row" for `fetch_one` returning `Result<Row>` — no, the function name says it).
- A security or safety boundary the caller must respect.
- A performance characteristic worth flagging (allocation, blocking, retry behaviour).
- A workaround for a specific bug that a future reader would otherwise undo — naming the **external** cause (the upstream quirk, the prior incident), not paraphrasing what the workaround code does.
- A footgun that has caused a production incident.

**Strip on sight (a non-exhaustive list of the smell):**

- `/// Returns the X.` over `pub fn foo(...) -> X`
- `/// Constructs / Builds / Creates an X.` over `pub fn new() -> X` or `pub fn build() -> X`
- `/// Fetches Y.` / `/// Inserts Y.` / `/// Deletes Y.` over `fn fetch_y` / `fn insert_y` / `fn delete_y`
- `/// Errors if X.` when `X` is implied by the parameter or return type
- One-liners on enum variants whose name is the entire content of the line
- One-liners on struct fields whose name is the entire content of the line
- **Multi-line `///` (or `//`) that narrates the body's own control flow** — a doc that walks the reader through which `match` arm maps where, which branch fires when, or what each step does, when the body below already says exactly that. The length and accuracy of the prose make it *worse*, not better: it is a second, un-compiled copy of the logic that will rot. Delete it; the code is the documentation.

**Worked example — the canonical rejected form.** This is unacceptable:

```rust
/// Translates an upstream failure into the status the *client* should see.
///
/// A malformed request (400/404/422) or rate limit (429) is the caller's to
/// fix, so it passes through; auth, 5xx, timeout, and transport failures are
/// the gateway/provider's problem and collapse to 502/504 without leaking the
/// upstream's credential-level detail.
pub fn map_upstream_error(e: &UpstreamError) -> (StatusCode, String) {
    let mapped = match *status {
        400 | 404 | 422 => StatusCode::from_u16(*status).unwrap_or(StatusCode::BAD_REQUEST),
        429 => StatusCode::TOO_MANY_REQUESTS,
        408 | 504 => StatusCode::GATEWAY_TIMEOUT,
        _ => StatusCode::BAD_GATEWAY,
    };
    // ...
}
```

The correct form is the **same function with no doc at all**: the `match` is the spec, the name says the intent, the prose is noise. Every clause of that six-line doc is already spelled out in the arms beneath it. Self-documenting code means the reader looks *down* at the body, not *up* at a paragraph that will silently drift from it.

**Crate / module heads are different.** Write a real `//!` block at the top of `lib.rs` and at the top of significant `mod.rs` files. That is where docs.rs gets its landing page; that is where the public surface, layering, feature flags, and error model are explained. A reader who lands on a docs.rs page with a one-paragraph crate-level overview and a clean module index will find what they need; a reader landing on a wall of method paraphrases will not.

**Sweeps.** If a future audit prompt orders "add `///` on every pub item", refuse and apply this rule instead. Rustdoc coverage is not a quality metric; signal is.

### Comment Rules (the full picture)

Comments are governed by a single principle: **the code documents itself unless the *why* is non-obvious.** Concretely:

| Crate type | `//` inline | `///` rustdoc | `//!` module |
|------------|-------------|---------------|--------------|
| Production code — **all** crates (`shared/*`, `infra/*`, `domain/*`, `app/*`, facade, `entry/*`) | only when encoding a non-obvious *why* | only on pub traits, top-level types, and `mod` declarations — never on fns/methods/fields/variants (see "Rustdoc placement") | high-quality head on `lib.rs` and every significant `pub mod` file |
| Tests (`crates/tests/**`) | as needed for test scaffolding | banned | optional |
| `build.rs` | as needed | n/a | n/a |

Entry binaries are held to the **same** comment bar as libraries — entry is not special. The only thing unique to published crates is *publishing* hygiene (docs.rs config, semver, feature matrix, examples), not comment style.

A WHY-comment must answer one of: a hidden constraint, a subtle invariant, a workaround for a specific bug, behaviour that would surprise a reader. WHAT-comments ("increments the counter"), narrative comments ("we just refactored this"), and reference-to-history comments ("used by X flow", "added for issue #123") are all banned.

**The default is no comment.** A WHY-comment is the rare exception, not a routine annotation — reach for one only when omitting it would let a competent reader silently break a real invariant. The bar is *genuinely exceptional*: if the "why" is derivable from the code, the types, or a well-named function, write none. Prose that re-explains intent at length, paints a consumer-facing picture ("so the UI can tell X apart from Y rather than crying wolf"), or recounts protocol/format trivia belongs in a `//!` module head if it belongs anywhere — not scattered as inline `//`. When in doubt, delete it. A file dense with why-comments is a signal the bar has slipped, not that the code is unusually subtle.

**Accurate is not sufficient.** Truth is the floor, not the bar. A `///` that is perfectly correct but merely restates the signature, the type, or the body's control flow is *still banned* — the test is whether it carries **non-derivable signal**, not whether it is true. An AI writing this code will be fluent and will produce confident, well-phrased narration for every function; that fluency is exactly the trap. Hold the line: most functions in world-class self-documenting code have **no** `///` and **no** `//`, and that is the target state, not a gap to fill.

### serde_json::Value is a Code Smell

`serde_json::Value` erases type information and pushes validation to runtime. Treat every occurrence as a code smell requiring heavy justification.

**Always prefer typed structs:**

```rust
#[derive(Debug, Clone, Deserialize)]
pub struct ToolInput {
    pub input: String,
    pub tags: Option<Vec<String>>,
}

let args: ToolInput = serde_json::from_value(raw_value)?;
```

**Narrow exceptions (require inline justification comment):**

| Exception | Justification |
|-----------|---------------|
| MCP `Tool` schema fields (`input_schema`, `output_schema`) | Protocol requires `serde_json::Map` -- external spec boundary |
| MCP `CallToolResult::structured_content` | Protocol defines as `Option<serde_json::Value>` |
| `serde_json::json!()` for constructing known-shape responses | Acceptable at API boundaries when shape is fixed and outgoing-only |
| Core trait signatures requiring `Value` | Cannot change without core modification |

**When you encounter `serde_json::Value` in existing code:**

1. If receiving/parsing: refactor to a typed struct with `#[derive(Deserialize)]`
2. If constructing outgoing JSON at an API boundary: acceptable, add `// JSON: protocol boundary` comment
3. If the trait signature requires it: acceptable, add `// JSON: required by trait contract` comment

### File Limits

| Metric | Limit | Notes |
|--------|-------|-------|
| Source file length | 300 lines | Treated as a cohesion proxy. Splits must extract genuinely cohesive sub-modules; do not shuffle code into `<name>_helpers.rs` to silence the rule. |
| Function length | 75 lines | |
| Parameters | 5 | |
| Cognitive complexity | not enforced | `clippy::cognitive_complexity` is `allow` at workspace scope -- explicit project decision. |

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
cargo fmt --all
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace
RUSTDOCFLAGS="-D warnings" cargo doc --no-deps --all-features
just build
just file-size      # 0 prod files >300 lines
just check-bans     # raw sqlx::query, *Manager, raw String IDs
just deny           # license + advisory check
just audit          # cargo-audit
```

The `quality.yml` CI workflow gates the same checks. Any of them red blocks merge.

## Git Hygiene

Repos stay clean. The default state is `main` plus the release tags — nothing else.

**Branches**
- No long-lived feature, `wip/*`, `backup/*`, `wt/*`, `worktree-agent-*`, `visibility-*`, `dd-coverage-*`, or checkpoint branches. Land work on `main` via a short-lived PR branch, then delete the branch (local + remote) on merge.
- Never create extra branches without explicit user approval. "Let me snapshot this on a branch first" is not a default behaviour — ask.
- Never run `git push --tags` (pushes per-crate `cargo-workspaces` tags). Push individual release tags: `git push origin v<X.Y.Z>`.

**Tags**
- Only release tags are kept: `v<X.Y.Z>` for the core repo, `bridge-v<X.Y.Z>` for the bridge binary, `<product>-v<X.Y.Z>` for sibling product releases. No checkpoint, wave, milestone, sweep, or `pre-*` tags.
- Per-crate `<crate>@<version>` tags emitted by `cargo-workspaces` are noise — prune locally before pushing: `git tag -l '*@*' | xargs -r git tag -d`.
- Never create extra tags without explicit user approval.
- Protected-tag rulesets (GitHub Settings → Rules) will block deletion even with admin perms — only enable them on tags you genuinely want to be permanent.

**Commit messages**
- Maintainer style, like `tokio` / `sqlx`: neutral, present tense, consumer-facing. `type(scope): summary` for the subject.
- No `Phase N`, `wave`, `attempt`, `wip`, incident narrative, or process commentary in the body.
- One logical change per commit. Stage with explicit paths (`git add <path>`), not `git add -A`. Never lump unrelated work.
- Never amend a published commit. Never `--no-verify` or skip signing. Never `git stash` — commit + push instead.

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
| Format | `cargo fmt --all` |
| Lint | `cargo clippy --workspace --all-targets --all-features -- -D warnings` |
| Doc | `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps --all-features` |
| Test | `cargo test --manifest-path crates/tests/Cargo.toml --workspace` |
| Build | `just build` |
| File size gate | `just file-size` |
| Bespoke ban gate | `just check-bans` |
| Supply-chain gate | `just deny && just audit` |
| Publish content | `systemprompt infra jobs run publish_pipeline` |
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Verify content | `systemprompt core content verify <slug> --source blog` |
