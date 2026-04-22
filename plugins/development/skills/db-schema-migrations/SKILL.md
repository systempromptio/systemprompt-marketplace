---
name: db-schema-migrations
description: "Add or change DB columns in the marketplace extension: update the base schema SQL, write an idempotent migration, register it in schemas.rs, regenerate the sqlx offline cache, and verify local + prod DB match."
metadata:
  version: "1.0.0"
  git_hash: "f2f79e50"
---

# DB Schema Migrations

How to safely add or change columns in the marketplace extension, keep the sqlx offline cache in sync, and verify local and prod match.

---

## Principles

- **Base schema = current DB state.** `006_usage_aggregations.sql` (and every other base schema file) must reflect the final column definitions. Never leave a base file showing the old type after a migration.
- **Migrations are idempotent.** Every migration uses `IF NOT EXISTS`, `IF EXISTS`, or a `DO $$ BEGIN … END $$` guard so it is safe to run on every startup.
- **Migrations run on startup.** They are registered in `schemas.rs` and called by `SchemaDefinition::inline`. A fresh install runs all of them in sequence; an existing install skips what's already done.
- **sqlx cache = offline truth.** `cargo sqlx prepare` regenerates `.sqlx/` from the live DB. Without this step the offline build sees stale types.

---

## Workflow

### 1 — Update the base schema SQL

Edit the relevant file in `extensions/marketplace/schema/` to reflect the final column definition.

Example — changing `INT` to `BIGINT`:

```sql
-- Before
subagent_spawns INT DEFAULT 0,

-- After
subagent_spawns BIGINT DEFAULT 0,
```

### 2 — Write the idempotent migration

Create `extensions/marketplace/schema/NNN_description.sql` (next number after the current highest).

Pattern for a column type change:

```sql
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name  = 'my_table'
          AND column_name = 'my_column'
          AND data_type   = 'integer'      -- the OLD type
    ) THEN
        ALTER TABLE my_table ALTER COLUMN my_column TYPE BIGINT;
    END IF;
END $$;
```

Pattern for adding a column:

```sql
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS my_column BIGINT NOT NULL DEFAULT 0;
```

### 3 — Register in schemas.rs

Add the constant and the `SchemaDefinition::inline` entry:

```rust
// in schemas.rs
pub const SCHEMA_MY_MIGRATION: &str =
    include_str!("../schema/NNN_description.sql");

// in schema_definitions()
SchemaDefinition::inline("my_migration", SCHEMA_MY_MIGRATION),
```

### 4 — Fix Rust code types

If a column type changed (e.g. `INT` → `BIGINT`), find every query that binds or reads that column and update the Rust type:

| Postgres type | sqlx cache type | Rust type |
|---------------|-----------------|-----------|
| `INTEGER`     | `Int4`          | `i32`     |
| `BIGINT`      | `Int8`          | `i64`     |

**Special case — `SUM` aggregate type promotion:**

Postgres promotes `SUM` return types:
- `SUM(INT4)` → `INT8` (i64)
- `SUM(INT8)` → `NUMERIC` (Decimal)

If you upgrade a column from `INT` to `BIGINT`, any `SUM(that_column)` query must add a `::BIGINT` cast, otherwise sqlx expects `Decimal`:

```rust
// Wrong after INT -> BIGINT upgrade
sqlx::query_scalar!("SELECT SUM(my_col) FROM t WHERE …", …)

// Correct
sqlx::query_scalar!(
    r#"SELECT COALESCE(SUM(my_col), 0)::BIGINT AS "val!" FROM t WHERE …"#,
    …
)
```

### 5 — Regenerate the sqlx offline cache

Run `cargo sqlx prepare` from the marketplace extension directory with `DATABASE_URL` pointed at the local DB. This regenerates all `.sqlx/*.json` files and runs `cargo check` to verify types match.

```bash
cd extensions/marketplace
DATABASE_URL="$(python3 -c "
import json
print(json.load(open('../../.systemprompt/profiles/local/secrets.json'))['database_url'])
")" cargo sqlx prepare
```

If `cargo check` fails during prepare, fix the type mismatches in Rust code first, then rerun.

After success:

```
query data written to .sqlx in the current directory; please check this into version control
```

Commit the updated `.sqlx/` files alongside the schema and Rust changes.

### 6 — Verify local and prod DB match

Check that the column type is correct in both DBs:

```bash
# Local
psql "$(python3 -c "import json; print(json.load(open('.systemprompt/profiles/local/secrets.json'))['database_url'])")" \
  -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'my_table' AND column_name = 'my_column'"

# Prod (via postgres superuser — libpq TLS ALPN works on this endpoint)
psql "postgres://postgres:<pw>@db.systemprompt.io:5432/site_<id>" \
  -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'my_table' AND column_name = 'my_column'"
```

If prod is behind (old type), the migration will run automatically on the next server startup. For urgent fixes, run it manually:

```bash
psql "postgres://postgres:<pw>@db.systemprompt.io:5432/site_<id>" -f extensions/marketplace/schema/NNN_description.sql
```

### 7 — Build and verify

```bash
just build
```

Must finish with `Finished` and no errors.

---

## Checklist

- [ ] Base schema file updated to final column definition
- [ ] Idempotent migration file created with correct guard
- [ ] `schemas.rs` constant and `SchemaDefinition::inline` added
- [ ] Rust code types updated (`i32` / `i64` / `Decimal` as appropriate)
- [ ] `SUM` aggregates rechecked if column changed from INT to BIGINT
- [ ] `cargo sqlx prepare` ran cleanly against local DB
- [ ] `.sqlx/` files committed
- [ ] Local and prod DB column types verified to match
- [ ] `just build` succeeds

---

## Prod DB connection

libpq 17+ rejects the prod DB TLS endpoint with `SSL error: no application protocol`. Use the postgres superuser URL (non-tenant) which does work:

```
postgres://postgres:<pw>@db.systemprompt.io:5432/site_<tenant_id>
```

Credentials are in `.systemprompt/profiles/systemprompt-prod/secrets.json`.

For bulk data operations (not schema), use pg8000 — see the `db-sync-prod-to-local` skill.
