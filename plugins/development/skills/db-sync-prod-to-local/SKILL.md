---
name: db-sync-prod-to-local
description: "Sync a systemprompt.io project's production Postgres data into the local dev DB. Covers two failure modes: TLS ALPN rejection (libpq 17+) and cloud-profile path mismatch (/app does not exist locally)."
metadata:
  version: "1.1.0"
  git_hash: "ae3252f"
---

# DB Sync — Production to Local

Copy production data into the local dev DB so dashboards and analytics render with real data.

Two failure modes are common — identify yours first, then follow the matching path.

---

## Failure Mode A — `systemprompt cloud sync pull` → `Permission denied (os error 13)`

**Root cause:** The cloud profile has `paths.system: /app`. The sync command downloads files from the API and tries to write to `/app/storage/...`. That path doesn't exist on the local machine.

**Fix — create the expected path:**

```bash
sudo mkdir -p /app/storage
sudo chown $(whoami) /app
```

Then retry:

```bash
systemprompt cloud sync pull --profile <profile-name>
```

If `/app` is undesirable on your machine (it pollutes the root), use the pg8000 direct DB sync instead (see below).

---

## Failure Mode B — `pg_dump` / `psql` → `SSL error: tlsv1 alert no application protocol`

**Root cause:** libpq 17+ mandates ALPN during the TLS handshake. The prod DB TLS terminator advertises no ALPN and rejects the connection. Downgrading libpq doesn't help — the server alert is absolute.

The Rust `sqlx` driver used by `systemprompt infra db query` does not enforce ALPN, which is why the CLI works even when `pg_dump` doesn't.

**Fix:** use `pg8000` (pure-Python, no libpq, no ALPN enforcement).

---

## pg8000 Direct Sync (works for both failure modes)

### Pre-flight

```bash
# pg8000 installed?
python3 -c "import pg8000.native" 2>&1 | head -1
# Install if missing:
pip3 install --user pg8000

# Docker with postgres:18 for local backup (local server is PG 18)
docker image inspect postgres:18 >/dev/null 2>&1 || docker pull postgres:18

# Find your profile secrets
cat /var/www/html/<project>/.systemprompt/profiles/<profile>/secrets.json
# Keys needed: database_url (local), external_database_url (prod)
```

### Step 1 — Back up local DB

Always back up before truncating. `pg_dump` on the host refuses local PG 18 (version mismatch) — run through Docker:

```bash
BACKUP=/var/www/html/<project>/.backups/local-$(date +%Y-%m-%d-%H%M%S).sql.gz
mkdir -p /var/www/html/<project>/.backups
LOCAL_URL=$(python3 -c "import json; print(json.load(open('/var/www/html/<project>/.systemprompt/profiles/local/secrets.json'))['database_url'])")
docker run --rm --network=host postgres:18 pg_dump --no-owner --no-acl "$LOCAL_URL" | gzip > "$BACKUP"
ls -lh "$BACKUP"
```

Expected size: ~15–750 KB depending on project. Keep the path for the BACKUP constant below.

### Step 2 — Dry-run to verify counts

Save as `/tmp/sync_prod_to_local.py`. Fill in `BACKUP`, `PROD_*`, `LOCAL_*`, and `TABLES`.

```python
"""Sync prod -> local. Prod is read-only."""
import pg8000.native, ssl, sys, time, os

BACKUP = '/var/www/html/<project>/.backups/local-YYYY-MM-DD-HHMMSS.sql.gz'

# Tables in dependency order (parents before children)
TABLES = [
    # systemprompt.io platform tables:
    # 'user_sessions', 'engagement_events',
    #
    # marcbo property tables:
    # 'activos', 'inquilinos', 'propietarios', 'acreedores',
    # 'contratos', 'contabilidad', 'depositos', 'incidencias',
    # 'remesas', 'remesas_sepa', 'activo_web', 'contrato_detalles',
    # 'notas', 'seguros', 'indices_referencia', 'recordatorios',
]

DRY_RUN = '--execute' not in sys.argv

if not os.path.exists(BACKUP):
    sys.exit(f"ABORT: backup not found at {BACKUP}")

def connect_prod():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    import json
    from urllib.parse import urlparse
    secrets = json.load(open('/var/www/html/<project>/.systemprompt/profiles/<profile>/secrets.json'))
    url = urlparse(secrets['external_database_url'])
    return pg8000.native.Connection(
        user=url.username, password=url.password,
        host=url.hostname, port=url.port or 5432,
        database=url.path.lstrip('/'),
        ssl_context=ctx
    )

def connect_local():
    import json
    from urllib.parse import urlparse
    secrets = json.load(open('/var/www/html/<project>/.systemprompt/profiles/local/secrets.json'))
    url = urlparse(secrets['database_url'])
    return pg8000.native.Connection(
        user=url.username, password=url.password,
        host=url.hostname or 'localhost', port=url.port or 5432,
        database=url.path.lstrip('/')
    )

prod = connect_prod()
local = connect_local()

print(f"Mode: {'DRY-RUN (pass --execute to sync)' if DRY_RUN else 'EXECUTE'}")
print(f"Backup: {BACKUP} ({os.path.getsize(BACKUP)//1024} KB)\n")

for tbl in TABLES:
    try:
        n_prod = prod.run(f'SELECT COUNT(*) FROM "{tbl}"')[0][0]
        n_local = local.run(f'SELECT COUNT(*) FROM "{tbl}"')[0][0]
        diff = "✓" if n_prod == n_local else f"DIFF prod={n_prod} local={n_local}"
        print(f"  {tbl}: prod={n_prod}  local={n_local}  {diff}")
    except Exception as e:
        print(f"  {tbl}: ERROR - {e}")

if DRY_RUN:
    print("\nDry-run complete. Rerun with --execute to sync.")
    sys.exit(0)

local.run("SET session_replication_role = replica")

for tbl in TABLES:
    print(f"\n=== {tbl} ===", flush=True)
    try:
        local_cols = [r[0] for r in local.run(
            "SELECT column_name FROM information_schema.columns "
            f"WHERE table_name='{tbl}' AND table_schema='public' ORDER BY ordinal_position")]
        prod_col_set = set(r[0] for r in prod.run(
            "SELECT column_name FROM information_schema.columns "
            f"WHERE table_name='{tbl}' AND table_schema='public'"))
        shared = [c for c in local_cols if c in prod_col_set]
        extra_local = [c for c in local_cols if c not in prod_col_set]
        if extra_local:
            print(f"  Local-only cols (left NULL): {extra_local}")
        col_list = ', '.join(f'"{c}"' for c in shared)

        local.run(f'TRUNCATE TABLE "{tbl}" CASCADE')
        n_prod = prod.run(f'SELECT COUNT(*) FROM "{tbl}"')[0][0]
        print(f"  copying {n_prod} rows ...", flush=True)

        offset, total, batch = 0, 0, 2000
        t0 = time.time()
        while offset < n_prod:
            rows = prod.run(f'SELECT {col_list} FROM "{tbl}" ORDER BY created_at OFFSET {offset} LIMIT {batch}')
            if not rows:
                break
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
    except Exception as e:
        print(f"  FAILED: {e}", flush=True)

local.run("SET session_replication_role = origin")
print("\nSYNC COMPLETE")
for tbl in TABLES:
    q = 'SELECT COUNT(*) FROM "' + tbl + '"'
    try:
        print(f"  local.{tbl}: {local.run(q)[0][0]} rows")
    except:
        pass
```

### Step 3 — Run dry then execute

```bash
python3 /tmp/sync_prod_to_local.py            # dry-run — prints counts + diffs
python3 /tmp/sync_prod_to_local.py --execute  # real run
```

If all counts show `✓` in dry-run, the local DB is already in sync — no execute needed.

---

## Gotchas

- **`ORDER BY created_at`** — most tables have this column. If a table doesn't, change to `ORDER BY id` or another stable column to ensure consistent pagination.
- **FK violations** — `session_replication_role = replica` defers all FK checks during load. The final line resets it to `origin`. Do not leave replica mode on.
- **TRUNCATE CASCADE** — required when tables have dependents (e.g. `engagement_events` references `user_sessions`). CASCADE handles the order automatically.
- **Local-only columns** (added in a migration not yet on prod) are skipped during copy and left NULL. Fine for dev/preview.
- **`/app` path fix requires sudo** — if you'd rather not create `/app`, use pg8000 sync instead.
- **Passwords in logs** — pg8000 does not leak passwords in error messages, but `secrets.json` lives on disk. Strip credentials before sharing script output.

---

## Checklist

- [ ] Identified failure mode (Permission denied vs TLS ALPN)
- [ ] Backup taken and path set in `BACKUP`
- [ ] Dry-run shows all `✓` (already in sync) or expected diffs
- [ ] If diffs found: `--execute` runs, `SYNC COMPLETE` printed, `session_replication_role` reset to `origin`
- [ ] For `cloud sync pull` fix: `/app/storage` created, retry succeeded
