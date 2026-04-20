---
name: db-sync-prod-to-local
description: "Sync systemprompt-prod Postgres data into a local dev DB for dashboard/analytics preview when libpq can't complete the TLS handshake"
metadata:
  version: "1.0.0"
  git_hash: ""
---

# DB Sync — Production to Local

Copy production `user_sessions` + `engagement_events` (or other tables) into the local dev DB so the admin traffic dashboard renders with real data. The prod DB cannot be dumped with `pg_dump`/`psql` because libpq 17+ sends an ALPN handshake that the prod TLS terminator rejects; this skill uses the pure-Python `pg8000` driver instead.

## When to use

- You've made dashboard or analytics changes that need real volume to verify.
- The CLI sync path (`systemprompt cloud sync pull`) complains *"Sync token not configured"* and rotating the token isn't authorised.
- You hit `SSL error: tlsv1 alert no application protocol` from `pg_dump`, `psql`, `psycopg`, or any libpq-based client.

## Why libpq fails

- `pg_dump` / `psql` / `psycopg` all use libpq under the hood.
- libpq 17+ mandates ALPN (`postgresql`) during the TLS handshake.
- The prod DB sits behind a TLS terminator that advertises **no ALPN**.
- The Rust `sqlx` driver used by `systemprompt infra db query` does not enforce ALPN, which is why the CLI works even though `pg_dump` doesn't.
- Downgrading libpq clients (Postgres 14/16 images) doesn't help — the server alert is absolute, not a libpq version mismatch.

The only path short of rotating the sync token or reconfiguring the TLS terminator is a client that speaks the Postgres wire protocol natively. `pg8000` is pure Python, built on `ssl` stdlib, and works.

## Pre-flight

```bash
# 1. pg8000 installed?
python3 -c "import pg8000.native" 2>&1 | head -1
# Install if missing:
pip3 install --user pg8000

# 2. Both profiles present locally?
ls /var/www/html/systemprompt-web/.systemprompt/profiles/
# -> local  systemprompt-prod

# 3. Docker with postgres:18 available? (needed for local backup — local server is PG 18)
docker image inspect postgres:18 >/dev/null 2>&1 || docker pull postgres:18
```

## Step 1 — Back up local

The script truncates local tables. Always back up first. `pg_dump` 14 / 17 refuses local PG 18, so run through Docker:

```bash
BACKUP=/var/www/html/systemprompt-web/.backups/local-$(date +%Y-%m-%d-%H%M%S).sql.gz
mkdir -p /var/www/html/systemprompt-web/.backups
LOCAL_URL=$(python3 -c "import json; print(json.load(open('/var/www/html/systemprompt-web/.systemprompt/profiles/local/secrets.json'))['database_url'])")
docker run --rm --network=host postgres:18 pg_dump --no-owner --no-acl "$LOCAL_URL" | gzip > "$BACKUP"
ls -lh "$BACKUP"
```

Expected size: ~15 MB. Keep the path — the sync script refuses to run if its BACKUP constant points at a missing file.

## Step 2 — Sync script

Save at `/tmp/sync_prod_to_local.py`. Point `BACKUP` at the file you just created. Adjust `TABLES` if you need more than user_sessions + engagement_events. Always start with `--dry-run` (default).

```python
"""Sync prod -> local for dashboard preview. Prod is read-only."""
import pg8000.native, json, sys, time, os
from urllib.parse import urlparse

BACKUP = '/var/www/html/systemprompt-web/.backups/local-YYYY-MM-DD-HHMMSS.sql.gz'  # set me
TABLES = ['user_sessions', 'engagement_events']
DRY_RUN = '--execute' not in sys.argv

if not os.path.exists(BACKUP):
    sys.exit(f"ABORT: backup file not found at {BACKUP}")

def connect(profile):
    with open(f'/var/www/html/systemprompt-web/.systemprompt/profiles/{profile}/secrets.json') as f:
        url = urlparse(json.load(f)['database_url'])
    return pg8000.native.Connection(
        user=url.username, password=url.password, host=url.hostname,
        port=url.port or 5432, database=url.path.lstrip('/'),
        ssl_context=(url.hostname != 'localhost') or None)

prod = connect('systemprompt-prod')
local = connect('local')

print(f"Mode: {'DRY-RUN' if DRY_RUN else 'EXECUTE'}")
print(f"Backup: {BACKUP} ({os.path.getsize(BACKUP)//1024} KB)")
for tbl in TABLES:
    n_prod = prod.run(f"SELECT COUNT(*) FROM {tbl}")[0][0]
    n_local = local.run(f"SELECT COUNT(*) FROM {tbl}")[0][0]
    print(f"  {tbl}: prod={n_prod}  local={n_local}")

if DRY_RUN:
    print("\nDry-run only. Rerun with --execute.")
    sys.exit(0)

local.run("SET session_replication_role = replica")  # defer FKs

for tbl in TABLES:
    print(f"\n=== {tbl} ===", flush=True)
    local_cols = [r[0] for r in local.run(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_name='{tbl}' AND table_schema='public' ORDER BY ordinal_position")]
    prod_col_set = set(r[0] for r in prod.run(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_name='{tbl}' AND table_schema='public'"))
    shared = [c for c in local_cols if c in prod_col_set]
    extra_local = [c for c in local_cols if c not in prod_col_set]
    if extra_local:
        print(f"  Local-only cols (left NULL): {extra_local}")
    col_list = ', '.join(f'"{c}"' for c in shared)

    local.run(f'TRUNCATE TABLE "{tbl}" CASCADE')
    n_prod = prod.run(f"SELECT COUNT(*) FROM {tbl}")[0][0]
    print(f"  copying {n_prod} rows ...", flush=True)

    offset, total, batch = 0, 0, 2000
    t0 = time.time()
    while offset < n_prod:
        rows = prod.run(f'SELECT {col_list} FROM "{tbl}" ORDER BY 1 OFFSET {offset} LIMIT {batch}')
        if not rows:
            break
        # multi-row INSERT in 500-row chunks
        for i in range(0, len(rows), 500):
            sub = rows[i:i+500]
            values, params = [], {}
            for ri, row in enumerate(sub):
                ph = []
                for ci, val in enumerate(row):
                    k = f'v{ri}_{ci}'
                    params[k] = val
                    ph.append(f':{k}')
                values.append(f"({','.join(ph)})")
            local.run(f'INSERT INTO "{tbl}" ({col_list}) VALUES ' + ','.join(values), **params)
            total += len(sub)
        offset += batch
        print(f"    {total}/{n_prod}", flush=True)
    print(f"  done in {time.time()-t0:.1f}s", flush=True)

local.run("SET session_replication_role = origin")
print("\nSYNC COMPLETE")
for tbl in TABLES:
    print(f"  local.{tbl} now: {local.run(f'SELECT COUNT(*) FROM {tbl}')[0][0]}")
```

## Step 3 — Run dry then execute

```bash
python3 /tmp/sync_prod_to_local.py               # DRY RUN — prints row counts only
python3 /tmp/sync_prod_to_local.py --execute     # real run
```

Expected wall time for ~11 K sessions + 19 K engagement events: ~75 s total.

## Step 4 — Restart server

Session rows changed under the running server; per the workspace rule *never kill the server yourself*. Ask the operator to restart. Then refresh `/admin` → Traffic tab.

## Gotchas

- **FK violations on `user_sessions.user_id`.** The `users` table is not synced. The script deliberately sets `session_replication_role = replica` to defer all FKs during the load. Do **not** leave replica mode on — the final statement resets it to `origin`.
- **Columns that exist on local but not on prod** (e.g. after a new migration like `utm_content`, `utm_term`, `event_data` added ahead of prod) are skipped during the copy. They remain NULL in the synced rows. That's fine for dashboard preview.
- **TRUNCATE CASCADE.** Both tables have dependents (engagement_events references user_sessions). CASCADE is required on the first table to avoid `cannot truncate a table referenced in a foreign key constraint`.
- **session_replication_role** requires superuser or replication role on the target DB. Local dev DB satisfies this; production does not.
- **ORDER BY 1** assumes the first column is the primary key. For `user_sessions` it's `session_id` (text), for `engagement_events` it's `id` (text). Both stable. If you sync a different table, pick a deterministic column.
- **Passwords in logs.** pg8000 does not leak the password in its error messages, but the URL lives on disk in `secrets.json`. Don't paste script output into tickets without stripping.

## Alternatives considered

| Path | Why it didn't work |
|------|---------------------|
| `pg_dump` on host | Host has PG 14/17 client, local server is PG 18 — version-mismatch abort |
| `docker run postgres:18 pg_dump` against prod | libpq 18 enforces ALPN → `tlsv1 alert no application protocol` |
| `postgres:14` / `postgres:16` images against prod | Server TLS terminator rejects all non-ALPN handshakes equally |
| `psycopg` (Python) | Thin wrapper over libpq — same ALPN failure |
| `systemprompt cloud sync pull` | Requires a sync token in the profile; `rotate-sync-token` is destructive on prod |
| `sslnegotiation=direct` / `PGSSLNEGOTIATION=direct` | Still sends ALPN; server still rejects |

`pg8000` works because it implements the Postgres wire protocol in Python and drives TLS via `ssl` stdlib without ALPN.

## Checklist

- [ ] Backup taken and path points at real file in `BACKUP`
- [ ] Dry-run shows plausible row counts
- [ ] `--execute` completes, `SYNC COMPLETE` printed
- [ ] `session_replication_role` reset to `origin`
- [ ] Server restarted, `/admin` Traffic tab renders expected numbers
