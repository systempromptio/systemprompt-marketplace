---
name: cli-reference
description: "Complete CLI command reference for all systemprompt domains including session management, agents, services, database, logs, analytics, cloud, jobs, users, config, files, skills, contexts, plugins, build, deploy, sync, web, content publishing, discord, mesh, and secrets"
---

# CLI Reference

Complete command reference for the systemprompt CLI organized by domain.

## CLI Structure

```
systemprompt <domain> <subcommand> [args]
```

| Domain | Purpose |
|--------|---------|
| `core` | Skills, content, files, contexts, plugins, hooks, artifacts |
| `infra` | Services, database, jobs, logs |
| `admin` | Users, agents, config, setup, session |
| `cloud` | Auth, deploy, sync, secrets, tenant, domain |
| `analytics` | Overview, conversations, agents, tools, requests, sessions, content, traffic, costs |
| `web` | Content-types, templates, assets, sitemap, validate |
| `plugins` | Extensions, MCP servers, capabilities |
| `build` | Build core workspace and MCP extensions |

Use `systemprompt <domain> --help` to explore any domain.

---

## Session Management

Sessions are tenant-keyed. Configuration priority (highest to lowest):

1. `--profile` CLI flag
2. `SYSTEMPROMPT_PROFILE` environment variable
3. Active session from `.systemprompt/sessions/index.json`
4. Default profile

Sessions expire 24 hours after creation.

| Task | Command |
|------|---------|
| Check session | `admin session show` |
| List profiles | `admin session list` |
| Switch profile | `admin session switch <name>` |
| Login | `just login` (terminal) |
| Logout | `just logout` (terminal) |

---

## Agents

Create, configure, and communicate with AI agents via A2A protocol. Agent names must be lowercase alphanumeric with underscores only.

| Task | Command |
|------|---------|
| List agents | `admin agents list` |
| List enabled | `admin agents list --enabled` |
| Show config | `admin agents show <name>` |
| Check status | `admin agents status <name>` |
| View logs | `admin agents logs <name>` |
| Running agents | `admin agents registry` |
| Send message | `admin agents message <name> -m "text" --blocking` |
| Send with timeout | `admin agents message <name> -m "text" --blocking --timeout 120` |
| Stream response | `admin agents message <name> -m "text" --stream` |
| Continue context | `admin agents message <name> -m "text" --context-id <id> --blocking` |
| Get task response | `admin agents task <name> --task-id <id>` |
| List tools | `admin agents tools <name>` |
| Validate all | `admin agents validate` |
| Create agent | `admin agents create --name <name> --port <port>` |
| Create with options | `admin agents create --name <name> --port <port> --mcp-server content-manager --skill research --enabled` |
| Enable agent | `admin agents edit <name> --enable` |
| Disable agent | `admin agents edit <name> --disable` |
| Edit model | `admin agents edit <name> --provider anthropic --model claude-3-5-sonnet-20241022` |
| Add MCP server | `admin agents edit <name> --mcp-server filesystem` |
| Remove MCP server | `admin agents edit <name> --remove-mcp-server filesystem` |
| Add skill | `admin agents edit <name> --skill new_skill` |
| Remove skill | `admin agents edit <name> --remove-skill old_skill` |
| Delete agent | `admin agents delete <name> -y` |
| Delete all | `admin agents delete --all -y` |
| Restart agent | `infra services restart agent <name>` |
| Restart all agents | `infra services restart --agents` |

---

## Services

Three service types: API (HTTP server), Agents (AI processes), MCP (Model Context Protocol servers).

| Task | Command |
|------|---------|
| Start services | `just start` (terminal) |
| Check status | `infra services status` |
| Health check | `infra services status --health` |
| Detailed status | `infra services status --detailed` |
| Stop all | `infra services stop --all` |
| Stop agents | `infra services stop --agents` |
| Stop MCP | `infra services stop --mcp` |
| Stop API | `infra services stop --api` |
| Force stop | `infra services stop --all --force` |
| Restart API | `infra services restart api` |
| Restart agent | `infra services restart agent <name>` |
| Restart MCP | `infra services restart mcp <name>` |
| Restart MCP + rebuild | `infra services restart mcp <name> --build` |
| Restart failed | `infra services restart --failed` |
| Cleanup orphans | `infra services cleanup -y` |
| Dry-run cleanup | `infra services cleanup --dry-run` |

---

## Database

Database queries, schema exploration, and administration.

| Task | Command |
|------|---------|
| Check status | `infra db status` |
| List tables | `infra db tables` |
| Describe table | `infra db describe <table>` |
| List indexes | `infra db indexes` |
| Database info | `infra db info` |
| Database size | `infra db size` |
| Query data | `infra db query "<SQL>"` |
| Row count | `infra db count <table>` |
| Run migrations | `infra db migrate` |
| Validate schema | `infra db validate` |
| Execute DDL | `infra db execute "<SQL>"` |
| Assign admin | `infra db assign-admin user@example.com` |

### Cloud Database

| Task | Command |
|------|---------|
| Cloud DB status | `cloud db status --profile <name>` |
| Cloud query | `cloud db query --profile <name> "<SQL>"` |
| Cloud tables | `cloud db tables --profile <name>` |
| Cloud migrate | `cloud db migrate --profile <name>` |
| Cloud DDL | `cloud db execute --profile <name> "<SQL>"` |

### Schema Modification Patterns

```sql
-- Add column
ALTER TABLE <table> ADD COLUMN IF NOT EXISTS <column> TEXT

-- Modify column
ALTER TABLE <table> ALTER COLUMN <column> TYPE JSONB USING <column>::jsonb

-- Create index
CREATE INDEX IF NOT EXISTS idx_<table>_<column> ON <table>(<column>)

-- Add foreign key
ALTER TABLE <table> ADD CONSTRAINT fk_<name> FOREIGN KEY (<column>) REFERENCES <other_table>(id) ON DELETE CASCADE
```

Always use `IF EXISTS` / `IF NOT EXISTS` to prevent errors on repeated runs.

---

## Logs and Debugging

| Task | Command |
|------|---------|
| Recent logs | `infra logs view --tail 50` |
| Error logs | `infra logs view --level error` |
| Last hour errors | `infra logs view --level error --since 1h` |
| Search logs | `infra logs search "pattern"` |
| Log summary | `infra logs summary --since 1h` |
| Show log entry | `infra logs show <log-id>` |
| View trace | `infra logs trace show <id>` |
| List requests | `infra logs request list` |
| Audit request | `infra logs audit <id> --full` |
| Tool executions | `infra logs tools` |
| MCP server logs | `plugins mcp logs <server>` |
| Agent logs | `admin agents logs <name>` |
| Export logs | `infra logs export --format json --since 24h -o logs.json` |
| Clean old logs | `infra logs cleanup --days 30` |
| Delete all logs | `infra logs delete` |
| Stream live | `infra logs stream` (terminal only) |
| Stream errors | `infra logs stream --level error` (terminal only) |

### Debugging Workflow

1. Find errors: `infra logs view --level error --since 1h`
2. Get request ID from error, then audit: `infra logs audit <request-id> --full`
3. View full trace: `infra logs trace show <trace-id> --all`
4. For MCP issues: `plugins mcp logs <server-name>`

### Log Files (Terminal Only)

```bash
ls -la logs/
tail -100 logs/mcp-content-manager.log
tail -100 logs/agent-blog.log
```

Local log files only contain logs from locally-running services. For remote profiles, use CLI commands which fetch from the remote database.

---

## Analytics

| Task | Command |
|------|---------|
| Overview | `analytics overview` |
| Overview (time range) | `analytics overview --since 24h` |
| Traffic sources | `analytics traffic sources` |
| Geographic | `analytics traffic geo --limit 10` |
| Devices | `analytics traffic devices` |
| Bot traffic | `analytics traffic bots` |
| Session stats | `analytics sessions stats` |
| Session trends | `analytics sessions trends` |
| Live sessions | `analytics sessions live --limit 20` |
| Content stats | `analytics content stats` |
| Top content | `analytics content top --limit 10` |
| Content trends | `analytics content trends` |
| Popular content | `analytics content popular --limit 20` |
| Cost summary | `analytics costs summary` |
| Cost by period | `analytics costs summary --days 30` |
| Cost trends | `analytics costs trends --group-by day` |
| Cost by model | `analytics costs breakdown --by model` |
| Cost by agent | `analytics costs breakdown --by agent` |
| Agent stats | `analytics agents stats` |
| Agent trends | `analytics agents trends --days 7` |
| Agent detail | `analytics agents show <name>` |
| Tool usage | `analytics tools stats` |
| Tool trends | `analytics tools trends` |
| Request stats | `analytics requests stats` |
| Request list | `analytics requests list --limit 50 --model claude` |
| Request models | `analytics requests models` |
| Conversation stats | `analytics conversations stats` |

### Common Flags

| Flag | Description |
|------|-------------|
| `--since` | Time range: `1h`, `24h`, `7d`, `30d`, or ISO datetime |
| `--until` | End time for range |
| `--export` | Export to CSV file |
| `--json` | Output as JSON |
| `--group-by` | Group by: `hour`, `day`, `week` |

---

## Cloud

### Authentication

| Task | Command |
|------|---------|
| Login | `just login` (terminal) |
| Check auth | `cloud auth whoami` |
| Logout | `just logout` (terminal) |

### Tenants

| Task | Command |
|------|---------|
| List tenants | `cloud tenant list` |
| Show tenant | `cloud tenant show` |
| Create tenant | `cloud tenant create --region iad` |
| Create named | `cloud tenant create --name "My Project" --region lhr` |
| Select tenant | `cloud tenant select <id>` |
| Rotate credentials | `cloud tenant rotate-credentials <id> -y` |

### Profiles

| Task | Command |
|------|---------|
| List profiles | `cloud profile list` |
| Show profile | `cloud profile show <name>` |
| Create profile | `cloud profile create <name>` |
| Create with env | `cloud profile create staging --environment staging` |
| Edit profile | `cloud profile edit <name>` |
| Delete profile | `cloud profile delete <name> -y` |

### Secrets

| Task | Command |
|------|---------|
| List secrets | `cloud secrets list` |
| List for profile | `cloud secrets list --profile <name>` |
| Set secret | `cloud secrets set ANTHROPIC_API_KEY sk-ant-xxxxx` |
| Delete secret | `cloud secrets delete OLD_KEY -y` |
| Sync secrets | `cloud secrets sync` |
| Sync for profile | `cloud secrets sync --profile <name>` |
| Set directly | `cloud secrets set KEY=VALUE` |
| Remove secret | `cloud secrets unset KEY` |
| Cleanup system vars | `cloud secrets cleanup` |

### Cloud Operations

| Task | Command |
|------|---------|
| Cloud status | `cloud status` |
| Restart cloud | `cloud restart --yes` |
| Init project | `cloud init` |
| Generate Dockerfile | `cloud dockerfile` |

### Setup Flow

| Phase | Command | Verify |
|-------|---------|--------|
| 1 | `just login` | credentials.json created |
| 2 | `just tenant` | tenants.json created |
| 3 | `just init` | services/ created |
| 4 | `just configure` | profiles/ created |
| 5 | `just db-up` | Container running |
| 6 | `just migrate` | Tables created |
| 7 | `just sync` | Data synced |
| 8 | `just start` | Server running |
| 9 | `just deploy` | Deployed (optional) |

---

## Jobs

| Task | Command |
|------|---------|
| List jobs | `infra jobs list` |
| Show job | `infra jobs show <name>` |
| Run job | `infra jobs run <name>` |
| Job history | `infra jobs history` |
| Job history (filtered) | `infra jobs history --job <name>` |
| Enable job | `infra jobs enable <name>` |
| Disable job | `infra jobs disable <name>` |
| Cleanup sessions | `infra jobs cleanup-sessions --hours 24` |
| Cleanup logs | `infra jobs log-cleanup --days 30` |

---

## Users

| Task | Command |
|------|---------|
| List users | `admin users list` |
| Search users | `admin users search "query"` |
| Show user | `admin users show <id>` |
| Create user | `admin users create --email <email> --name "Name"` |
| Update user | `admin users update <id> --name "New Name"` |
| Delete user | `admin users delete <id>` |
| User count | `admin users count` |
| User stats | `admin users stats` |
| Export users | `admin users export --format json` |
| Assign role | `admin users role assign <id> admin` |
| Promote | `admin users role promote <id>` |
| Demote | `admin users role demote <id>` |
| List sessions | `admin users session list <id>` |
| End session | `admin users session end <session-id>` |
| Cleanup sessions | `admin users session cleanup --hours 24` |
| List bans | `admin users ban list` |
| Add ban | `admin users ban add <ip> --reason "Abuse"` |
| Timed ban | `admin users ban add <ip> --duration 1440 --reason "Spam"` |
| Remove ban | `admin users ban remove <ip>` |
| Check ban | `admin users ban check <ip>` |
| Merge users | `admin users merge <source-id> <target-id>` |
| Bulk delete | `admin users bulk delete --inactive-days 365` |

---

## Configuration

Configuration is loaded from profiles and is read-only at runtime. Bootstrap sequence: ProfileBootstrap -> SecretsBootstrap -> CredentialsBootstrap -> Config -> AppContext.

| Task | Command |
|------|---------|
| Config overview | `admin config show` |
| Server config | `admin config server show` |
| Security config | `admin config security show` |
| Paths config | `admin config paths show` |
| Runtime config | `admin config runtime show` |
| Rate limits | `admin config rate-limits show` |
| List rate limits | `admin config rate-limits list` |
| Active session | `admin session show` |

---

## Files

| Task | Command |
|------|---------|
| List files | `core files list` |
| List by MIME | `core files list --mime image/png` |
| Show file | `core files show <id>` |
| Upload file | `core files upload /path --context <id>` |
| Upload AI image | `core files upload /path --context <id> --ai` |
| Validate file | `core files validate /path/to/file` |
| Search files | `core files search "pattern"` |
| Delete file | `core files delete <id> -y` |
| Storage stats | `core files stats` |
| File config | `core files config` |
| List AI images | `core files ai list` |

---

## Skills

Skills are reusable capabilities stored in YAML files under `services/skills/` and synced to the database.

| Task | Command |
|------|---------|
| List skills | `core skills list` |
| Check sync status | `core skills status` |
| Sync skills | `core skills sync` |
| Preview sync | `core skills sync --dry-run` |
| Create skill | `core skills create <name>` |
| Edit skill | `core skills edit <name>` |
| Delete skill | `core skills delete <name> -y` |

---

## Contexts

Contexts maintain conversation history for agent interactions. Short IDs (first 8 chars) work for most commands.

| Task | Command |
|------|---------|
| List contexts | `core contexts list` |
| Show context | `core contexts show <id>` |
| Create context | `core contexts create --name "x"` |
| Create and activate | `core contexts new --name "x"` |
| Switch context | `core contexts use <id>` |
| Rename context | `core contexts edit <id> --name "x"` |
| Delete context | `core contexts delete <id> -y` |

### Multi-Agent Shared Context

All agents share the active context:

```
core contexts new --name "content-pipeline"
admin agents message researcher -m "Research AI costs" --blocking
admin agents message writer -m "Create post from research" --blocking
```

---

## Plugins and MCP

### Extensions

| Task | Command |
|------|---------|
| List extensions | `plugins list` |
| Show extension | `plugins show <name>` |
| Extension config | `plugins config <id>` |
| Validate extensions | `plugins validate` |

### MCP Servers

| Task | Command |
|------|---------|
| List MCP servers | `plugins mcp list` |
| List packages | `plugins mcp list-packages` |
| MCP status | `plugins mcp status` |
| Validate MCP | `plugins mcp validate <server>` |
| MCP logs | `plugins mcp logs <server>` |
| List tools | `plugins mcp tools` |
| List server tools | `plugins mcp tools --server <name>` |
| Call tool | `plugins mcp call <server> <tool> --args '{...}'` |

### Capabilities

```
plugins capabilities schemas
plugins capabilities jobs
plugins capabilities templates
plugins capabilities tools
plugins capabilities roles
plugins capabilities llm-providers
```

---

## Build

| Task | Command |
|------|---------|
| Build all | `just build` |
| Build core | `build core` |
| Build core release | `build core --release` |
| Build MCP | `build mcp` |
| Build MCP release | `build mcp --release` |
| Build single crate | `cargo build -p <crate-name>` |
| Release single | `cargo build -p <crate-name> --release` |

---

## Deploy

Full deploy is a long-running operation -- use the terminal with `just deploy`.

| Task | Command |
|------|---------|
| Full deploy (interactive) | `just deploy` (terminal) |
| Full deploy (non-interactive) | `cloud deploy --profile <name> --yes` |
| Deploy without sync | `cloud deploy --profile <name> --yes --no-sync` |
| Skip rebuild | `cloud deploy --profile <name> --yes --skip-push` |
| Cloud status | `cloud status` |
| Restart cloud | `cloud restart --yes` |

### Non-Interactive Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--profile <name>` | Yes | Target profile |
| `--yes` | Yes | Confirm operation |
| `--no-sync` | No | Skip syncing runtime files |
| `--skip-push` | No | Skip Docker build/push |

---

## Sync

### File Sync (Cloud)

| Task | Command |
|------|---------|
| Push files | `cloud sync push` |
| Push dry run | `cloud sync push --dry-run --verbose` |
| Pull files | `cloud sync pull` |

### Content Sync (Local)

| Task | Command |
|------|---------|
| Disk to DB (publish) | `infra jobs run publish_pipeline` |
| DB to disk (export) | `infra jobs run content_sync -p direction=to-disk` |
| Export by source | `infra jobs run content_sync -p direction=to-disk -p source=blog` |

Content lives on disk in `services/content/` and is ingested via `publish_pipeline`. CLI `edit` commands only update the database temporarily -- next `publish_pipeline` overwrites DB with disk content.

### Skills Sync

| Task | Command |
|------|---------|
| Skills sync preview | `cloud sync local skills --dry-run` |
| Skills sync execute | `cloud sync local skills` |

---

## Web

| Task | Command |
|------|---------|
| Validate config | `web validate` |
| List content types | `web content-types list` |
| Show content type | `web content-types show <name>` |
| Create content type | `web content-types create <name>` |
| Edit content type | `web content-types edit <name>` |
| Delete content type | `web content-types delete <name> -y` |
| List templates | `web templates list` |
| Show template | `web templates show <name>` |
| Create template | `web templates create <name>` |
| Edit template | `web templates edit <name>` |
| Delete template | `web templates delete <name> -y` |
| List assets | `web assets list` |
| Show sitemap | `web sitemap show` |
| Generate sitemap | `web sitemap generate` |

---

## Content Publishing

### Publishing Pipeline

| Task | Command |
|------|---------|
| Full publish | `core content publish` |
| Ingest only | `core content publish --step ingest` |
| Assets only | `core content publish --step assets` |
| Prerender only | `core content publish --step prerender` |
| Pages only | `core content publish --step pages` |
| Sitemap only | `core content publish --step sitemap` |

Pipeline steps: ingest -> assets -> prerender -> homepage -> sitemap.

### Content Management

| Task | Command |
|------|---------|
| List content | `core content list --source blog` |
| Show content | `core content show <slug> --source <source>` |
| Search content | `core content search "<query>"` |
| Verify content | `core content verify <slug> --source <source>` |
| Content status | `core content status --source <source>` |
| Re-ingest | `core content ingest services/content/blog --source blog --override` |
| Delete content | `core content delete <content-id> --yes` |
| Export to disk | `cloud sync local content --direction to-disk` |
| Import to DB | `cloud sync local content --direction to-db` |

### Content Jobs

```
infra jobs run publish_pipeline
infra jobs run blog_image_optimization
infra jobs run copy_extension_assets
```

---

## Discord CLI Extension

Send messages to Discord channels or users from the command line.

### Prerequisites

- Discord bot token configured in `services/config/discord.yaml`
- Bot invited to server with "Send Messages" permission

### Configuration

```yaml
# services/config/discord.yaml
bot_token: "YOUR_BOT_TOKEN"
default_channel_id: "1234567890123456789"
default_user_id: "9876543210987654321"
enabled: true
```

| Task | Command |
|------|---------|
| Test connection | `plugins run discord test` |
| Send to default | `plugins run discord send "message"` |
| Send to channel | `plugins run discord send -c <channel-id> "message"` |
| Send DM | `plugins run discord send -u <user-id> "message"` |

---

## Agent Mesh

A mesh is a coordinated group of agents working together.

| Task | Command |
|------|---------|
| List mesh agents | `admin agents list --enabled` |
| Check registry | `admin agents registry` |
| Agent status | `admin agents status <name>` |
| Agent logs | `admin agents logs <name> -n 50` |
| Agent config | `admin agents show <name>` |
| Enable agent | `admin agents edit <name> --enable` |
| Disable agent | `admin agents edit <name> --disable` |
| Restart all | `infra services restart --agents` |
| Restart one | `infra services restart agent <name>` |
| Validate all | `admin agents validate` |
| Test message | `admin agents message <name> -m "test" --blocking` |
| List tools | `admin agents tools <name>` |

### Mesh Communication

```
admin agents message <name> -m "text" --blocking --timeout 300
admin agents message <name> -m "text" --context-id "ctx-id" --blocking
```

---

## Secrets Management

Secrets are stored in profile-specific `secrets.json` files. All secrets files are gitignored.

### secrets.json Format

```json
{
  "jwt_secret": "minimum-32-character-secret-key-here",
  "database_url": "postgres://user:pass@host:5432/db",
  "anthropic": "sk-ant-...",
  "openai": "sk-...",
  "gemini": "AIza..."
}
```

| Task | Command |
|------|---------|
| Sync to cloud | `cloud secrets sync` |
| Set secret | `cloud secrets set KEY=VALUE` |
| Set multiple | `cloud secrets set K1=V1 K2=V2` |
| Remove secret | `cloud secrets unset KEY` |
| Cleanup | `cloud secrets cleanup` |
| Sync for profile | `cloud secrets sync --profile NAME` |

### Required Secrets

| Secret | Required For | Format |
|--------|--------------|--------|
| `jwt_secret` | Authentication | Min 32 characters |
| `database_url` | Database | `postgres://user:pass@host:port/db` |
| `anthropic` | Claude AI | `sk-ant-...` |
| `openai` | OpenAI | `sk-...` |
| `gemini` | Google AI | `AIza...` |

Generate JWT secret: `openssl rand -base64 48`
