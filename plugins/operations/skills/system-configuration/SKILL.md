---
name: system-configuration
description: "Complete configuration reference for systemprompt.io covering bootstrap sequence, profiles, secrets, credentials, server settings, security, paths, runtime, rate limits, and tenant management"
---

# System Configuration

Complete configuration reference for systemprompt.io covering profiles, secrets, server, security, paths, runtime, rate limits, and tenants.

---

## Bootstrap Sequence

systemprompt.io initializes through a 5-stage bootstrap sequence:

```
Stage 1: ProfileBootstrap    -> Load and validate profile YAML
Stage 2: SecretsBootstrap    -> Load sensitive credentials
Stage 3: CredentialsBootstrap -> Load cloud API credentials (optional)
Stage 4: Config              -> Aggregate Profile + Secrets
Stage 5: AppContext           -> Initialize database, extensions, services
```

Each stage checks prerequisites from prior stages. ProfileBootstrap and Config are fatal on failure. CredentialsBootstrap is optional (local-only deployments skip it). SecretsBootstrap behavior is configurable via validation mode.

All bootstrap components use `std::sync::OnceLock` for thread-safe, initialize-once semantics.

### CLI Commands

```
admin config show              # View all configuration
admin config server show       # Server settings
admin config security show     # Security settings
admin config paths show        # Directory paths
admin config runtime show      # Runtime settings
admin config rate-limits show  # Rate limits
```

---

## Profiles

Profiles are environment configurations stored in `.systemprompt/profiles/<name>/profile.yaml`.

### Profile Structure

```yaml
name: local
display_name: "Local Development"
target: local                    # local | cloud

site:
  name: "My Project"
  github_link: "https://github.com/org/repo"

database:
  type: postgres
  external_db_access: true

server:
  host: "0.0.0.0"
  port: 8080
  api_server_url: "http://localhost:8080"
  api_internal_url: "http://localhost:8080"
  api_external_url: "http://localhost:8080"
  use_https: false
  cors_allowed_origins:
    - "http://localhost:8080"
    - "http://localhost:5173"

paths:
  system: "/path/to/project"
  services: "/path/to/project/services"
  bin: "/path/to/project/target/release"
  web_path: "/path/to/project/web"
  storage: "/path/to/project/storage"

security:
  jwt_issuer: "systemprompt-local"
  jwt_access_token_expiration: 2592000
  jwt_refresh_token_expiration: 15552000
  jwt_audiences:
    - web
    - api
    - a2a
    - mcp

rate_limits:
  disabled: true

runtime:
  environment: development
  log_level: verbose
  output_format: text
  no_color: false
  non_interactive: false

cloud:
  credentials_path: "../../credentials.json"
  tenants_path: "../../tenants.json"
  tenant_id: local_19bff27604c

secrets:
  secrets_path: "./secrets.json"
  source: file
  validation: warn

extensions:
  disabled: []
```

### Environment Variable Substitution

Profile YAML supports `${VAR_NAME}` syntax:

```yaml
server:
  host: ${HOST:-0.0.0.0}
  port: ${PORT}
```

### Path Resolution

Relative paths in profiles are resolved relative to the profile directory. Paths starting with `~/` expand to the home directory.

### Validation Chain

Profile validation runs: required fields -> paths -> security settings -> CORS origins -> rate limits.

### CLI Commands

```
cloud profile list
cloud profile show <name>
cloud profile create <name>
cloud profile edit <name>
cloud profile delete <name> -y
```

---

## Server Configuration

ServerConfig defines HTTP server settings: host, port, API URLs, CORS, and HTTPS.

### The 3 API URLs

| URL | Purpose | Example (Production) |
|-----|---------|---------------------|
| `api_server_url` | Primary API endpoint | `https://api.example.com` |
| `api_internal_url` | Internal service-to-service | `http://internal:8080` |
| `api_external_url` | Public/external access | `https://api.example.com` |

### Host Values

| Value | Use Case |
|-------|----------|
| `127.0.0.1` | Local development only |
| `0.0.0.0` | Accept connections from any interface |

### CORS Rules

Each CORS origin must be non-empty and start with `http://` or `https://`. No trailing slashes, no wildcards.

### HTTPS

In cloud deployments, TLS is typically terminated at the proxy. Set `use_https: false` and use HTTPS in `api_external_url`.

### Environment Variables

| Env Variable | Maps To |
|--------------|---------|
| `HOST` | `server.host` |
| `PORT` | `server.port` |
| `API_SERVER_URL` | `server.api_server_url` |
| `API_INTERNAL_URL` | `server.api_internal_url` |
| `API_EXTERNAL_URL` | `server.api_external_url` |
| `USE_HTTPS` | `server.use_https` |
| `CORS_ALLOWED_ORIGINS` | `server.cors_allowed_origins` (comma-separated) |

---

## Security Configuration

SecurityConfig defines JWT token settings: issuer, expiration times, and allowed audiences.

### Settings

| Setting | YAML Name | Range | Default |
|---------|-----------|-------|---------|
| Issuer | `jwt_issuer` | Non-empty | - |
| Access expiration | `jwt_access_token_expiration` | 1 - 31,536,000 sec | 2,592,000 (30 days) |
| Refresh expiration | `jwt_refresh_token_expiration` | > 0 | 15,552,000 (180 days) |
| Audiences | `jwt_audiences` | Non-empty | - |

### JWT Audiences

| Audience | Use Case |
|----------|----------|
| `web` | Browser-based applications |
| `api` | Direct API access |
| `a2a` | Agent-to-agent communication |
| `mcp` | Model Context Protocol |

### Time Conversions

| Duration | Seconds |
|----------|---------|
| 1 hour | 3,600 |
| 1 day | 86,400 |
| 1 week | 604,800 |
| 30 days | 2,592,000 |
| 90 days | 7,776,000 |
| 180 days | 15,552,000 |
| 1 year | 31,536,000 |

### Environment Variables

| Env Variable | Maps To |
|--------------|---------|
| `JWT_ISSUER` | `security.issuer` |
| `JWT_ACCESS_TOKEN_EXPIRATION` | `security.access_token_expiration` |
| `JWT_REFRESH_TOKEN_EXPIRATION` | `security.refresh_token_expiration` |
| `JWT_AUDIENCES` | `security.audiences` (comma-separated) |

---

## Secrets

Secrets contain sensitive credentials: JWT signing keys, database URLs, and API keys.

### secrets.json Format

```json
{
  "jwt_secret": "your-secret-key-minimum-32-characters-long",
  "database_url": "postgres://user:password@localhost:5432/dbname",
  "sync_token": "optional-sync-token",
  "gemini": "AIza...",
  "anthropic": "sk-ant-...",
  "openai": "sk-...",
  "github": "ghp_..."
}
```

### Loading Strategy

1. If Fly.io container (`FLY_APP_NAME` set) or subprocess mode -> load from environment
2. If `source: env` -> try file first, fallback to environment
3. If `source: file` -> load from `secrets_path`

### Profile Configuration

```yaml
secrets:
  secrets_path: "./secrets.json"    # Relative to profile directory
  source: file                       # file | env
  validation: warn                   # strict | warn | skip
```

### Validation

| Field | Rule |
|-------|------|
| `jwt_secret` | Minimum 32 characters |
| `database_url` | Non-empty string |

### Validation Modes

| Mode | Missing File | Invalid Content |
|------|--------------|-----------------|
| `strict` | Error | Error |
| `warn` | Warning + fallback | Warning + continue |
| `skip` | Silent fallback | Silent continue |

### Environment Variable Mapping

| Env Variable | Maps To |
|--------------|---------|
| `JWT_SECRET` | `secrets.jwt_secret` |
| `DATABASE_URL` | `secrets.database_url` |
| `SYNC_TOKEN` | `secrets.sync_token` |
| `GEMINI_API_KEY` | `secrets.gemini` |
| `ANTHROPIC_API_KEY` | `secrets.anthropic` |
| `OPENAI_API_KEY` | `secrets.openai` |
| `GITHUB_TOKEN` | `secrets.github` |

Custom secrets via `SYSTEMPROMPT_CUSTOM_SECRETS=KEY1,KEY2` with corresponding env vars.

### Generate JWT Secret

```bash
openssl rand -base64 48
```

---

## Cloud Credentials

CloudCredentials authenticate CLI and API requests to systemprompt.io Cloud. Optional for local-only deployments.

### credentials.json Format

```json
{
  "api_token": "sp_live_eyJ...",
  "api_url": "https://api.systemprompt.io",
  "authenticated_at": "2026-02-01T10:00:00Z",
  "user_email": "user@example.com"
}
```

Default location: `.systemprompt/credentials.json`

### Token Expiration

Tokens expire 24 hours after `authenticated_at`. Warning issued when token expires within 1 hour.

### Validation Modes

| Mode | Missing File | Invalid Token | API Failure |
|------|--------------|---------------|-------------|
| `strict` | Error | Error | Error |
| `warn` | Warning | Warning | Warning |
| `skip` | Silent | Silent | Silent |

### Fly.io Container

When `FLY_APP_NAME` is set, credentials load from environment:

| Env Variable | Required | Default |
|--------------|----------|---------|
| `SYSTEMPROMPT_API_TOKEN` | Yes | - |
| `SYSTEMPROMPT_USER_EMAIL` | Yes | - |
| `SYSTEMPROMPT_API_URL` | No | `https://api.systemprompt.io` |

### OAuth Login Flow

```bash
just login                        # Terminal-based login
systemprompt cloud auth login     # Direct CLI
```

Opens browser for GitHub/Google OAuth, saves credentials to `.systemprompt/credentials.json`.

---

## Paths Configuration

PathsConfig defines directory locations for system files, services, binaries, and optional storage.

### Required Paths

| Path | Local Validation | Cloud Validation |
|------|-----------------|------------------|
| `system` | Must exist on filesystem | Must start with `/app` |
| `services` | Must exist on filesystem | Must start with `/app` |
| `bin` | Must exist on filesystem | Must start with `/app` |

### Optional Paths

| Path | Default | Description |
|------|---------|-------------|
| `web_path` | `{system}/web` | Web assets output |
| `storage` | None | File storage |
| `geoip_database` | None | MaxMind .mmdb file |

### Derived Paths

| Method | Pattern |
|--------|---------|
| `skills()` | `{services}/skills` |
| `config()` | `{services}/config/config.yaml` |
| `ai_config()` | `{services}/ai/config.yaml` |
| `content_config()` | `{services}/content/config.yaml` |
| `web_config()` | `{services}/web/config.yaml` |
| `web_metadata()` | `{services}/web/metadata.yaml` |

### Configuration Examples

```yaml
# Relative paths (recommended)
paths:
  system: "../../.."
  services: "../../../services"
  bin: "../../../target/release"
  web_path: "../../../web"
  storage: "../../../storage"

# Cloud deployment
paths:
  system: "/app"
  services: "/app/services"
  bin: "/app/bin"
  web_path: "/app/web"
```

### Environment Variables

| Env Variable | Maps To |
|--------------|---------|
| `SYSTEM_PATH` | `paths.system` |
| `SYSTEMPROMPT_SERVICES_PATH` | `paths.services` |
| `BIN_PATH` | `paths.bin` |
| `SYSTEMPROMPT_WEB_PATH` | `paths.web_path` |
| `STORAGE_PATH` | `paths.storage` |
| `GEOIP_DATABASE_PATH` | `paths.geoip_database` |

---

## Runtime Configuration

RuntimeConfig controls environment type, logging, output format, and interactive behavior.

### Settings

| Field | Values | Default |
|-------|--------|---------|
| `environment` | `development`, `test`, `staging`, `production` | `development` |
| `log_level` | `quiet`, `normal`, `verbose`, `debug` | `normal` |
| `output_format` | `text`, `json`, `yaml` | `text` |
| `no_color` | `true`, `false` | `false` |
| `non_interactive` | `true`, `false` | `false` |

### Log Levels

| Level | Tracing Filter | Shows |
|-------|---------------|-------|
| `quiet` | `error` | Only errors |
| `normal` | `info` | Info, warnings, errors |
| `verbose` | `debug` | Debug and above |
| `debug` | `trace` | Everything |

### Recommended Settings by Environment

| Environment | Log Level | Output | Color | Interactive |
|-------------|-----------|--------|-------|-------------|
| Development | `verbose` | `text` | on | on |
| Test | `quiet` | `text` | off | off |
| Staging | `normal` | `json` | off | off |
| Production | `normal` | `json` | off | off |

### Environment Variables

| Env Variable | Maps To |
|--------------|---------|
| `SYSTEMPROMPT_ENV` | `environment` |
| `SYSTEMPROMPT_LOG_LEVEL` | `log_level` |
| `SYSTEMPROMPT_OUTPUT_FORMAT` | `output_format` |
| `NO_COLOR` | `no_color` (any value = true) |
| `CI` | `non_interactive` (any value = true) |

---

## Rate Limits

RateLimitsConfig controls API request throttling with per-endpoint limits and user tier multipliers.

### Default Values

| Endpoint | Default (req/sec) |
|----------|--------------------|
| `oauth_public_per_second` | 10 |
| `oauth_auth_per_second` | 10 |
| `contexts_per_second` | 100 |
| `tasks_per_second` | 50 |
| `artifacts_per_second` | 50 |
| `agent_registry_per_second` | 50 |
| `agents_per_second` | 20 |
| `mcp_registry_per_second` | 50 |
| `mcp_per_second` | 200 |
| `stream_per_second` | 100 |
| `content_per_second` | 50 |
| `burst_multiplier` | 3 |

### Tier Multipliers

| Tier | Default Multiplier |
|------|--------------------|
| `admin` | 10.0x |
| `user` | 1.0x |
| `a2a` | 5.0x |
| `mcp` | 5.0x |
| `service` | 5.0x |
| `anon` | 0.5x |

Effective rate = Base Rate x Tier Multiplier. Burst capacity = Effective Rate x Burst Multiplier.

### Configuration Examples

```yaml
# Development (disabled)
rate_limits:
  disabled: true

# Production (defaults)
rate_limits:
  disabled: false

# High-security production
rate_limits:
  disabled: false
  oauth_public_per_second: 5
  burst_multiplier: 2
  tier_multipliers:
    admin: 10.0
    user: 1.0
    anon: 0.1
```

### Validation

When `disabled: false`, all rate limits and `burst_multiplier` must be > 0.

---

## Tenant Management

Tenants are isolated environments that own databases and configuration.

### Tenant Types

| Aspect | Local Tenant | Cloud Tenant |
|--------|--------------|--------------|
| Database | Docker container | Managed PostgreSQL |
| URL | `database_url` field | `internal_database_url` field |
| Hostname | `localhost:port` | `{id}.systemprompt.io` |
| Sync token | Optional | Required for sync |
| Region | None | `iad`, `lhr`, `syd` |

### tenants.json Format

```json
{
  "tenants": [
    {
      "id": "local_19bff27604c",
      "name": "my-project",
      "tenant_type": "local",
      "database_url": "postgres://systemprompt:localdev@localhost:5432/systemprompt"
    },
    {
      "id": "999bc654-9a64-49bc-98be-db976fc84e76",
      "name": "my-project-prod",
      "tenant_type": "cloud",
      "app_id": "sp-999bc6549a64",
      "hostname": "999bc6549a64.systemprompt.io",
      "region": "iad",
      "sync_token": "sp_sync_abc123..."
    }
  ],
  "synced_at": "2026-02-01T10:00:00Z"
}
```

Storage location: `.systemprompt/tenants.json` (configured in profile as `cloud.tenants_path`).

### Linking Tenants to Profiles

```yaml
cloud:
  tenant_id: local_19bff27604c
  tenants_path: "../../tenants.json"
```

### CLI Commands

| Task | Command |
|------|---------|
| List tenants | `cloud tenant list` |
| Show tenant | `cloud tenant show <id>` |
| Create local | `cloud tenant create --type local` |
| Create cloud | `cloud tenant create --region iad` |
| Select tenant | `cloud tenant select <id>` |
| Rotate credentials | `cloud tenant rotate-credentials <id> -y` |
| Rotate sync token | `cloud tenant rotate-sync-token <id> -y` |

---

## The .systemprompt Directory

```
project-root/
 .systemprompt/                      # Project-level (gitignored)
    credentials.json                # Auth token + user info
    tenants.json                    # Tenant cache
    Dockerfile                      # Application image
    profiles/                       # Environment-specific configs
        local/
            profile.yaml
            secrets.json
            docker/
                docker-compose.yaml
        production/
            profile.yaml
            secrets.json
```

### Security

1. Never commit secrets -- `.systemprompt/` is gitignored
2. File permissions -- secrets files created with `0o600`
3. Environment isolation -- each profile has its own secrets
4. JWT secret length -- minimum 32 characters enforced

---

## Troubleshooting

**"Profile not initialized"** -- Check `SYSTEMPROMPT_PROFILE` environment variable. Verify profile file exists at specified path.

**"Secrets not initialized"** -- Ensure ProfileBootstrap completed first. Check `secrets.json` path in profile. Verify JWT secret is at least 32 characters.

**"Credentials expired"** -- Re-authenticate with `just login`. Token expires 24 hours after login.

**"Config validation failed"** -- Check all required YAML files exist. Verify database type is "postgres". Check path permissions.

**"Port already in use"** -- Check with `lsof -i :8080`. Change port or stop conflicting process.

**"CORS error in browser"** -- Add frontend origin to `cors_allowed_origins`. No trailing slashes, no wildcards. Protocol must match (http vs https).

**"Rate limit exceeded" (HTTP 429)** -- Wait and retry with exponential backoff. Check user tier. Increase limits for specific endpoints.

**"Tenants not synced"** -- Run `cloud tenant list` to sync. Verify credentials are valid.

**"JWT Secret Too Short"** -- Generate a longer secret: `openssl rand -base64 48`.
