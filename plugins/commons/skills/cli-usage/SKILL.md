---
name: cli-usage
description: "Complete reference for the systemprompt CLI - 8 domains, 64+ subcommands for managing AI infrastructure, services, agents, cloud deployments, and analytics"
version: "1.0.0"
git_hash: "0000000"
---

# systemprompt CLI Usage

Complete operational reference for the `systemprompt` CLI. Syntax: `systemprompt <domain> <command> [subcommand] [options]`

## Execution Methods

**Direct CLI** (local machine):
```bash
systemprompt <domain> <command> [options]
```

**Via systemprompt MCP server** (remote execution):
The systemprompt admin MCP server exposes CLI commands as tools. When operating remotely, execute commands through the MCP server's CLI tool rather than direct bash. The MCP server handles authentication, profile routing, and session context automatically.

## Global Options

| Option | Description |
|--------|-------------|
| `--profile <NAME>` | Target a specific profile (overrides active session) |
| `--database-url <URL>` | Direct database URL (bypasses profile) |
| `--json` | JSON output format |
| `--yaml` | YAML output format |
| `-v, --verbose` | Increase verbosity |
| `--debug` | Debug logging |
| `-q, --quiet` | Suppress output |
| `--no-color` | Disable colors |
| `--non-interactive` | Non-interactive mode (required for automation) |

Always use `--json` when parsing output programmatically. Use `--non-interactive` in automation to prevent interactive prompts.

## Session and Profile Management

Profiles define connection targets (local or cloud). Sessions authenticate CLI access to a profile.

### Profiles

```bash
# List available profiles
systemprompt cloud profile list

# Show profile configuration
systemprompt cloud profile show [name]
systemprompt cloud profile show --filter agents    # Filter: all|agents|mcp|skills|ai|web|content|env|settings
systemprompt cloud profile show --json

# Create/edit/delete profiles
systemprompt cloud profile create <name>
systemprompt cloud profile edit <name>
systemprompt cloud profile delete <name>
```

### Sessions

```bash
# Show current session, routing info, and all sessions
systemprompt admin session show

# Switch to a different profile
systemprompt admin session switch

# List available profiles for switching
systemprompt admin session list

# Create admin session for CLI access
systemprompt admin session login

# Remove a session
systemprompt admin session logout
```

Session output shows: profile name, user email, session ID, context ID, active/expired status, and routing target (local vs cloud).

### Profile Override

Any command can target a different profile without switching:

```bash
systemprompt core skills list --profile systemprompt-prod
```

---

## Domain: core

Core operations for skills, content, files, contexts, agents, artifacts, plugins, and hooks.

### core skills

Skill management and database sync.

```bash
systemprompt core skills list                              # List configured skills
systemprompt core skills show <skill_id>                   # Show skill details
systemprompt core skills create                             # Create new skill
systemprompt core skills edit <skill_id>                    # Edit skill configuration
systemprompt core skills delete <skill_id>                  # Delete a skill
systemprompt core skills status                             # Show database sync status
systemprompt core skills sync --direction to-db -y          # Sync disk to database
systemprompt core skills sync --direction from-db -y        # Sync database to disk
systemprompt core skills sync --direction to-db --dry-run   # Preview sync changes
```

### core content

Content management with search, analytics, links, and file attachments.

```bash
# List and search
systemprompt core content list [--source <id>] [--category <id>] [--limit 20] [--offset 0]
systemprompt core content show <content_id>
systemprompt core content search "<query>" [--source <id>] [--limit 20]

# Edit and delete
systemprompt core content edit <content_id>
systemprompt core content delete <content_id>
systemprompt core content delete-source <source_id>         # Delete all content from a source

# Analytics
systemprompt core content popular                           # Get popular content
systemprompt core content verify <content_id>               # Verify content is published
systemprompt core content status <source_id>                # Show content health status
```

**Content links** (trackable campaign links):

```bash
systemprompt core content link generate                     # Generate trackable campaign link
systemprompt core content link show <short_code>            # Show link details
systemprompt core content link list [--campaign <name>]     # List links
systemprompt core content link performance <short_code>     # Link performance metrics
systemprompt core content link delete <short_code>          # Delete a link
```

**Content analytics**:

```bash
systemprompt core content analytics clicks <short_code>    # Click history for a link
systemprompt core content analytics campaign <name>        # Campaign-level analytics
systemprompt core content analytics journey <content_id>   # Content navigation graph
```

**Content-file operations**:

```bash
systemprompt core content files link <content_id> <file_id> --role <role>  # Link file to content
systemprompt core content files unlink <content_id> <file_id>              # Unlink file
systemprompt core content files list <content_id>                          # List attached files
systemprompt core content files featured <content_id>                      # Get/set featured image
```

### core files

File management and uploads.

```bash
systemprompt core files list [--type <mime_type>] [--limit 20]  # List files
systemprompt core files show <file_id>                          # Show file details
systemprompt core files upload <path>                           # Upload local file
systemprompt core files delete <file_id>                        # Delete a file
systemprompt core files validate <path>                         # Validate before upload
systemprompt core files config                                  # Show upload config
systemprompt core files search "<pattern>"                      # Search files by path
systemprompt core files stats                                   # File storage statistics
systemprompt core files ai                                      # AI-generated image operations
```

### core contexts

Context management for conversation continuity.

```bash
systemprompt core contexts list                # List all contexts with stats
systemprompt core contexts show <context_id>   # Show context details
systemprompt core contexts create              # Create a new context
systemprompt core contexts edit <context_id>   # Rename a context
systemprompt core contexts delete <context_id> # Delete a context
systemprompt core contexts use <context_id>    # Set session's active context
systemprompt core contexts new                 # Create new context and set active
```

### core agents

Agent entity management and database sync (distinct from `admin agents` which manages runtime operations).

```bash
systemprompt core agents list       # List configured agents
systemprompt core agents show       # Show agent details
systemprompt core agents sync       # Sync agents between disk and database
systemprompt core agents validate   # Validate agent configurations
```

### core artifacts

Artifact inspection and debugging.

```bash
systemprompt core artifacts list                # List artifacts
systemprompt core artifacts show <artifact_id>  # Show artifact details and content
```

### core plugins

Plugin management and marketplace generation.

```bash
systemprompt core plugins list       # List configured plugins
systemprompt core plugins show       # Show plugin details
systemprompt core plugins validate   # Validate plugin configuration
systemprompt core plugins generate   # Generate Claude Code plugin output
```

### core hooks

Hook validation and inspection.

```bash
systemprompt core hooks list       # List hooks across all plugins
systemprompt core hooks validate   # Validate all hook definitions
```

---

## Domain: infra

Infrastructure management for services, database, jobs, and logs.

### infra services

Service lifecycle management for the API server, agents, and MCP servers.

```bash
# Start services
systemprompt infra services start                          # Start all services
systemprompt infra services start --api                    # Start API server only
systemprompt infra services start --agents                 # Start agents only
systemprompt infra services start --mcp                    # Start MCP servers only
systemprompt infra services start agent <name>             # Start specific agent
systemprompt infra services start mcp <name>               # Start specific MCP server
systemprompt infra services start --kill-port-process      # Kill existing port occupant
systemprompt infra services start --skip-migrate           # Skip database migrations

# Stop services
systemprompt infra services stop                           # Stop all services
systemprompt infra services stop --api                     # Stop API server only
systemprompt infra services stop agent <name>              # Stop specific agent
systemprompt infra services stop agent <name> --force      # Force stop (SIGKILL)
systemprompt infra services stop mcp <name>                # Stop specific MCP server

# Restart services
systemprompt infra services restart                        # Restart all
systemprompt infra services restart api                    # Restart API
systemprompt infra services restart agent <name>           # Restart specific agent
systemprompt infra services restart mcp <name>             # Restart specific MCP server
systemprompt infra services restart --failed               # Restart only failed services
systemprompt infra services restart --agents               # Restart all agents
systemprompt infra services restart --mcp                  # Restart all MCP servers

# Status and maintenance
systemprompt infra services status                         # Show detailed service status
systemprompt infra services cleanup                        # Clean up orphaned processes

# Full server (API + agents + MCP)
systemprompt infra services serve                          # Start full server stack
systemprompt infra services serve --foreground             # Run in foreground
systemprompt infra services serve --kill-port-process      # Kill port occupant first
```

### infra db

Database operations and administration.

```bash
# Queries
systemprompt infra db query "<sql>"                        # Execute read-only SQL
systemprompt infra db query "<sql>" --limit 10 --offset 0  # With pagination
systemprompt infra db execute "<sql>"                      # Execute write SQL (INSERT/UPDATE/DELETE)

# Schema inspection
systemprompt infra db tables [--filter <pattern>]          # List tables with row counts
systemprompt infra db describe <table>                     # Describe table schema
systemprompt infra db indexes [--table <name>]             # List indexes
systemprompt infra db count <table>                        # Row count for table
systemprompt infra db size                                 # Database and table sizes

# Administration
systemprompt infra db info                                 # Show database information
systemprompt infra db status                               # Connection status
systemprompt infra db validate                             # Validate schema against expected tables
systemprompt infra db migrate                              # Run database migrations
systemprompt infra db migrations status                    # Show migration status
systemprompt infra db migrations history <ext>             # Migration history
systemprompt infra db assign-admin <user>                  # Assign admin role
```

### infra jobs

Background jobs and scheduling.

```bash
systemprompt infra jobs list                  # List available jobs
systemprompt infra jobs show <job_id>         # Show job details
systemprompt infra jobs run <job_id>          # Run job manually
systemprompt infra jobs history <job_id>      # View execution history
systemprompt infra jobs enable <job_id>       # Enable a job
systemprompt infra jobs disable <job_id>      # Disable a job
systemprompt infra jobs cleanup-sessions      # Clean up inactive sessions
systemprompt infra jobs log-cleanup           # Clean up old log entries
```

### infra logs

Log streaming, tracing, and AI request auditing. This is the primary debugging domain.

```bash
# View and search
systemprompt infra logs view [--tail 20] [--level error] [--since 1h] [--module <name>]
systemprompt infra logs search "<pattern>"
systemprompt infra logs stream                             # Real-time log streaming (tail -f)
systemprompt infra logs summary                            # Log statistics

# Show and export
systemprompt infra logs show <id>                          # Show log entry details
systemprompt infra logs export [--format json] [-o <file>] # Export logs to file

# Cleanup
systemprompt infra logs cleanup [--dry-run]                # Clean up old entries
systemprompt infra logs delete                             # Delete all log entries
```

**Trace debugging**:

```bash
systemprompt infra logs trace list                         # List recent traces
systemprompt infra logs trace show <trace_id>              # Show trace details
```

**AI request inspection**:

```bash
systemprompt infra logs request list                       # List recent AI requests
systemprompt infra logs request show <request_id>          # Show request details
systemprompt infra logs request stats                      # Aggregate AI request statistics
```

**MCP tool execution logs**:

```bash
systemprompt infra logs tools list                         # List MCP tool executions
```

**Full audit** (comprehensive request analysis):

```bash
systemprompt infra logs audit <id>                         # Full audit by request/task/trace ID
systemprompt infra logs audit <id> --full                  # Full content without truncation
systemprompt infra logs audit <id> --json                  # JSON output
```

---

## Domain: admin

Administration for users, agents (runtime operations), configuration, setup, and sessions.

### admin users

User management with roles, sessions, bans, and WebAuthn.

```bash
# CRUD
systemprompt admin users list                              # List users with pagination
systemprompt admin users show <user_id>                    # Show user details
systemprompt admin users search "<query>"                  # Search by name/email
systemprompt admin users create                            # Create new user
systemprompt admin users update <user_id>                  # Update user fields
systemprompt admin users delete <user_id>                  # Delete user
systemprompt admin users count                             # Total user count
systemprompt admin users export                            # Export users to JSON
systemprompt admin users stats                             # User statistics dashboard
systemprompt admin users merge <source> <target>           # Merge users

# Bulk, roles, sessions, bans, WebAuthn
systemprompt admin users bulk                              # Bulk operations
systemprompt admin users role                              # Role management
systemprompt admin users session                           # Session management
systemprompt admin users ban                               # IP ban management
systemprompt admin users webauthn                          # WebAuthn credential management
```

### admin agents

Agent runtime management including A2A protocol messaging, tools inspection, and process control.

```bash
# Configuration
systemprompt admin agents list                             # List configured agents
systemprompt admin agents show <name>                      # Display agent configuration
systemprompt admin agents validate                         # Check configs for errors
systemprompt admin agents create [options]                 # Create new agent
systemprompt admin agents edit <name>                      # Edit agent configuration
systemprompt admin agents delete <name>                    # Delete an agent

# Process management
systemprompt admin agents status <name>                    # Show agent process status
systemprompt admin agents logs <name>                      # View agent logs
systemprompt admin agents run --agent-name <name> --port <port>  # Run agent directly
```

**Agent create options** (key flags):

| Option | Description |
|--------|-------------|
| `--name <NAME>` | Agent name |
| `--display-name <NAME>` | Display name |
| `--port <PORT>` | Port for the agent |
| `--provider <PROVIDER>` | AI provider (anthropic, openai, gemini) |
| `--model <MODEL>` | AI model ID |
| `--system-prompt <TEXT>` | Inline system prompt |
| `--system-prompt-file <PATH>` | Load system prompt from file |
| `--mcp-server <NAME>` | Add MCP server (repeatable) |
| `--skill <ID>` | Add skill reference (repeatable) |
| `--enabled` | Enable after creation |
| `--is-primary` | Mark as primary agent |
| `--default` | Mark as default agent |
| `--streaming true\|false` | Enable streaming |

**A2A Protocol (Agent-to-Agent communication)**:

```bash
# Discovery
systemprompt admin agents registry                         # Get running agents from gateway
systemprompt admin agents registry --running               # Only running agents
systemprompt admin agents registry --verbose               # Include full agent cards

# Messaging
systemprompt admin agents message <name> -m "<text>"       # Send message to agent
systemprompt admin agents message <name> -m "<text>" --blocking --timeout 30  # Wait for response
systemprompt admin agents message <name> -m "<text>" --stream     # Streaming mode
systemprompt admin agents message <name> -m "<text>" --json       # Full task JSON output
systemprompt admin agents message <name> -m "<text>" --context-id <id>  # Conversation continuity
systemprompt admin agents message <name> -m "<text>" --task-id <id>     # Continue existing task

# Task inspection
systemprompt admin agents task <name> --task-id <id>       # Get task details and response
systemprompt admin agents task <name> --task-id <id> --history-length 10  # With history

# Tools
systemprompt admin agents tools <name>                     # List MCP tools available to agent
systemprompt admin agents tools <name> --detailed          # Include full schemas
```

### admin config

Configuration management.

```bash
systemprompt admin config show                             # Configuration overview
systemprompt admin config list                             # List all config files
systemprompt admin config validate                         # Validate config files
systemprompt admin config rate-limits                      # Rate limit configuration
systemprompt admin config server                           # Server configuration
systemprompt admin config runtime                          # Runtime configuration
systemprompt admin config security                         # Security configuration
systemprompt admin config paths                            # Paths configuration
systemprompt admin config provider                         # AI provider configuration
```

### admin setup

```bash
systemprompt admin setup                                   # Interactive setup wizard
```

---

## Domain: cloud

Cloud deployment, sync, authentication, and tenant management.

### cloud auth

```bash
systemprompt cloud auth login     # Login to systemprompt.io cloud
systemprompt cloud auth logout    # Logout
systemprompt cloud auth whoami    # Show current authenticated user
```

### cloud init

```bash
systemprompt cloud init           # Initialize project structure
systemprompt cloud init --force   # Force reinitialize
```

### cloud tenant

```bash
systemprompt cloud tenant list                             # List all tenants
systemprompt cloud tenant create                           # Create new tenant (local or cloud)
systemprompt cloud tenant show <tenant_id>                 # Show tenant details
systemprompt cloud tenant edit <tenant_id>                 # Edit tenant configuration
systemprompt cloud tenant delete <tenant_id>               # Delete tenant
systemprompt cloud tenant rotate-credentials               # Rotate database credentials
systemprompt cloud tenant rotate-sync-token                # Rotate sync token
systemprompt cloud tenant cancel                           # Cancel subscription (IRREVERSIBLE)
```

### cloud deploy

```bash
systemprompt cloud deploy                                  # Deploy to cloud
systemprompt cloud deploy --profile <name>                 # Deploy specific profile
systemprompt cloud deploy --dry-run                        # Preview without deploying
systemprompt cloud deploy --no-sync                        # Skip pre-deploy sync
systemprompt cloud deploy -y                               # Skip confirmation
systemprompt cloud deploy --skip-push                      # Skip git push
```

### cloud status and restart

```bash
systemprompt cloud status                                  # Check cloud deployment status
systemprompt cloud restart [-y]                            # Restart tenant machine
```

### cloud sync

```bash
# Push/pull between local and cloud
systemprompt cloud sync push [--dry-run] [--force]         # Push local to cloud
systemprompt cloud sync pull [--dry-run] [--force]         # Pull cloud to local

# Local sync operations
systemprompt cloud sync local skills                       # Sync skills locally
systemprompt cloud sync local agents --direction to-db -y  # Sync agents to database

# Admin user
systemprompt cloud sync admin-user                         # Sync cloud user as admin to all profiles
```

### cloud secrets

```bash
systemprompt cloud secrets sync                            # Sync secrets.json to cloud
systemprompt cloud secrets set KEY=VALUE [KEY2=VALUE2]      # Set secrets
systemprompt cloud secrets unset KEY [KEY2]                 # Remove secrets
systemprompt cloud secrets cleanup                          # Remove incorrectly synced vars
```

### cloud db

Cloud database operations (mirrors `infra db` but targets cloud database).

```bash
systemprompt cloud db migrate                              # Run migrations on cloud DB
systemprompt cloud db query "<sql>"                        # Read-only SQL on cloud DB
systemprompt cloud db execute "<sql>"                      # Write SQL on cloud DB
systemprompt cloud db validate                             # Validate cloud DB schema
systemprompt cloud db status                               # Cloud DB connection status
systemprompt cloud db info                                 # Cloud DB info
systemprompt cloud db tables                               # List cloud DB tables
systemprompt cloud db describe <table>                     # Describe cloud table schema
systemprompt cloud db count <table>                        # Row count on cloud DB
systemprompt cloud db indexes                              # List cloud DB indexes
systemprompt cloud db size                                 # Cloud DB sizes
systemprompt cloud db backup                               # Backup cloud DB (pg_dump)
systemprompt cloud db restore <file>                       # Restore cloud DB from backup
```

### cloud domain

```bash
systemprompt cloud domain set <domain>    # Set custom domain
systemprompt cloud domain status          # Check domain/TLS status
systemprompt cloud domain remove          # Remove custom domain
```

### cloud dockerfile

```bash
systemprompt cloud dockerfile             # Generate Dockerfile based on extensions
```

---

## Domain: analytics

Analytics and metrics reporting across 9 categories.

```bash
systemprompt analytics overview                            # Dashboard overview of all analytics
```

### analytics conversations

```bash
systemprompt analytics conversations list                  # List conversations
systemprompt analytics conversations trends                # Conversation trends over time
systemprompt analytics conversations summary               # Summary statistics
```

### analytics agents

```bash
systemprompt analytics agents list                         # List agent metrics
systemprompt analytics agents trends                       # Performance trends
systemprompt analytics agents status                       # Agent status summary
```

### analytics tools

```bash
systemprompt analytics tools list                          # List tool usage
systemprompt analytics tools trends                        # Tool usage trends
systemprompt analytics tools by-agent                      # Usage by agent
```

### analytics requests

```bash
systemprompt analytics requests stats                      # Aggregate AI request statistics
systemprompt analytics requests list                       # List individual requests
systemprompt analytics requests trends                     # Request trends over time
systemprompt analytics requests models                     # Model usage breakdown
```

### analytics sessions

```bash
systemprompt analytics sessions list                       # List sessions
systemprompt analytics sessions trends                     # Session trends
systemprompt analytics sessions summary                    # Session summary
```

### analytics content

```bash
systemprompt analytics content popular                     # Most popular content
systemprompt analytics content trending                    # Trending content
systemprompt analytics content performance                 # Content performance metrics
```

### analytics traffic

```bash
systemprompt analytics traffic overview                    # Traffic overview
systemprompt analytics traffic by-endpoint                 # By endpoint
systemprompt analytics traffic geo                         # Geographic distribution
```

### analytics costs

```bash
systemprompt analytics costs overview                      # Cost overview
systemprompt analytics costs by-model                      # Costs by AI model
systemprompt analytics costs trends                        # Cost trends over time
```

---

## Domain: web

Web service configuration management.

```bash
# Content types
systemprompt web content-types list                        # List content types
systemprompt web content-types create                      # Create content type
systemprompt web content-types edit                        # Edit content type
systemprompt web content-types delete                      # Delete content type

# Templates
systemprompt web templates list                            # List templates
systemprompt web templates show                            # Show template details
systemprompt web templates create                          # Create template
systemprompt web templates edit                            # Edit template
systemprompt web templates delete                          # Delete template

# Assets
systemprompt web assets list [--type <mime>]               # List assets
systemprompt web assets show <asset_id>                    # Show asset details

# Sitemap
systemprompt web sitemap list                              # List sitemap entries
systemprompt web sitemap generate                          # Generate sitemap
systemprompt web sitemap validate                          # Validate sitemap

# Validation
systemprompt web validate                                  # Validate web configuration
```

---

## Domain: plugins

Plugins, extensions, and MCP server management.

### Extension management

```bash
systemprompt plugins list                                  # List discovered extensions
systemprompt plugins show <extension>                      # Show extension details
systemprompt plugins run <command> [args]                   # Run CLI extension command
systemprompt plugins validate                              # Validate extension dependencies
systemprompt plugins config                                # Show extension configuration
systemprompt plugins capabilities                          # List capabilities across extensions
```

### plugins mcp

MCP server management and tool execution.

```bash
# Server management
systemprompt plugins mcp list                              # List MCP server configs
systemprompt plugins mcp status                            # Show running MCP status
systemprompt plugins mcp validate <server>                 # Validate MCP connection
systemprompt plugins mcp logs <server>                     # View MCP server logs
systemprompt plugins mcp list-packages                     # List package names for build

# Tool operations
systemprompt plugins mcp tools <server>                    # List tools from MCP server
systemprompt plugins mcp call <server> <tool>              # Execute tool on MCP server
systemprompt plugins mcp call <server> <tool> -a '{"key":"value"}'  # With JSON args
systemprompt plugins mcp call <server> <tool> --timeout 60 # Custom timeout (default: 30s)
```

---

## Domain: build

Build workspace and MCP extensions.

```bash
systemprompt build core    # Build Rust workspace (systemprompt-core)
systemprompt build mcp     # Build MCP extensions
```

---

## Common Workflows

### Initial Setup

```bash
systemprompt cloud auth login                              # 1. Authenticate
systemprompt cloud init                                    # 2. Initialize project
systemprompt cloud profile create local                    # 3. Create profile
systemprompt admin session login                           # 4. Create CLI session
systemprompt infra db migrate                              # 5. Run migrations
systemprompt infra services serve                          # 6. Start all services
```

### Deploy to Cloud

```bash
systemprompt cloud sync push --dry-run                     # 1. Preview changes
systemprompt cloud sync push                               # 2. Push to cloud
systemprompt cloud deploy --profile <name> -y              # 3. Deploy
systemprompt cloud status                                  # 4. Verify deployment
```

### Debugging an Issue

```bash
systemprompt infra logs view --level error --since 1h      # 1. Check recent errors
systemprompt infra logs search "<error pattern>"           # 2. Search for pattern
systemprompt infra logs trace list                         # 3. Find relevant trace
systemprompt infra logs trace show <trace_id>              # 4. Inspect trace
systemprompt infra logs audit <request_id> --full          # 5. Full audit of request
systemprompt infra logs request stats                      # 6. Check request stats
```

### Agent Management

```bash
systemprompt admin agents create --name my_agent --port 9100 --provider anthropic --model claude-sonnet-4-20250514 --enabled  # 1. Create
systemprompt admin agents validate                         # 2. Validate
systemprompt core agents sync                              # 3. Sync to database
systemprompt infra services start agent my_agent           # 4. Start
systemprompt admin agents status my_agent                  # 5. Check status
systemprompt admin agents message my_agent -m "hello" --blocking  # 6. Test
systemprompt admin agents tools my_agent                   # 7. Verify tools
systemprompt admin agents logs my_agent                    # 8. Check logs
```

### Database Operations

```bash
systemprompt infra db status                               # 1. Check connection
systemprompt infra db tables                               # 2. List tables
systemprompt infra db describe <table>                     # 3. Inspect schema
systemprompt infra db query "SELECT * FROM <table> LIMIT 5"  # 4. Query data
systemprompt infra db size                                 # 5. Check sizes
```

### MCP Server Management

```bash
systemprompt plugins mcp list                              # 1. List configured servers
systemprompt plugins mcp status                            # 2. Check running status
systemprompt infra services start mcp <name>               # 3. Start server
systemprompt plugins mcp validate <name>                   # 4. Validate connection
systemprompt plugins mcp tools <name>                      # 5. List available tools
systemprompt plugins mcp call <name> <tool> -a '{}'        # 6. Execute tool
systemprompt plugins mcp logs <name>                       # 7. Check logs
```

### Content Management

```bash
systemprompt core content list --source <id>               # 1. List content
systemprompt core content search "search terms"            # 2. Search
systemprompt core content show <content_id>                # 3. Inspect
systemprompt core files upload <path>                      # 4. Upload file
systemprompt core content files link <cid> <fid> --role hero  # 5. Attach file
systemprompt core content link generate                    # 6. Create campaign link
systemprompt core content analytics campaign <name>        # 7. Check analytics
```

### Skill Sync

```bash
systemprompt core skills list                              # 1. List current skills
systemprompt core skills sync --direction to-db --dry-run  # 2. Preview changes
systemprompt core skills sync --direction to-db -y         # 3. Sync to database
systemprompt core skills status                            # 4. Verify sync status
```

### Profile Switching

```bash
systemprompt admin session show                            # 1. See current session
systemprompt admin session switch                          # 2. Switch profile
systemprompt admin session show                            # 3. Verify switch
# Or use --profile flag for one-off commands:
systemprompt core skills list --profile other-profile
```

## Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Session expired | `admin session show` shows `is_expired: true` | `admin session login` |
| Wrong profile | `admin session show` shows unexpected routing | `admin session switch` or `--profile <name>` |
| Service not running | `infra services status` shows stopped | `infra services start agent/mcp <name>` |
| Port conflict | Start fails with port error | `infra services start --kill-port-process` |
| Orphaned processes | Services show stale PIDs | `infra services cleanup` |
| Database connection | Commands fail with DB errors | `infra db status` then check `cloud profile show --filter env` |
| Migration needed | Schema mismatch errors | `infra db migrate` |
| Sync conflicts | Push/pull fails | `cloud sync push --dry-run` to preview, then `--force` |
| Agent unresponsive | Message times out | `admin agents status <name>`, then `admin agents logs <name>` |
| MCP tool fails | `plugins mcp call` errors | `plugins mcp validate <server>`, then `plugins mcp logs <server>` |
| Skills not loading | Agent missing skill | `core skills sync --direction to-db -y`, verify in `admin agents show <name>` |
| Cloud deploy fails | Deploy errors | `cloud status`, `cloud sync pull --dry-run`, check `cloud secrets sync` |

## Quick Reference

| Domain | Commands | Purpose |
|--------|----------|---------|
| `core skills` | list, show, create, edit, delete, status, sync | Skill CRUD and sync |
| `core content` | list, show, search, edit, delete, delete-source, popular, verify, status, link, analytics, files | Content management |
| `core files` | list, show, upload, delete, validate, config, search, stats, ai | File management |
| `core contexts` | list, show, create, edit, delete, use, new | Context management |
| `core agents` | list, show, sync, validate | Agent entity sync |
| `core artifacts` | list, show | Artifact inspection |
| `core plugins` | list, show, validate, generate | Plugin management |
| `core hooks` | list, validate | Hook inspection |
| `infra services` | start, stop, restart, status, cleanup, serve | Service lifecycle |
| `infra db` | query, execute, tables, describe, info, migrate, migrations, assign-admin, status, validate, count, indexes, size | Database admin |
| `infra jobs` | list, show, run, history, enable, disable, cleanup-sessions, log-cleanup | Job scheduling |
| `infra logs` | view, search, stream, export, cleanup, delete, summary, show, trace, request, tools, audit | Log/trace/audit |
| `admin users` | list, show, search, create, update, delete, count, export, stats, merge, bulk, role, session, ban, webauthn | User management |
| `admin agents` | list, show, validate, create, edit, delete, status, logs, registry, message, task, tools, run | Agent operations + A2A |
| `admin config` | show, list, validate, rate-limits, server, runtime, security, paths, provider | Configuration |
| `admin session` | show, switch, list, login, logout | Session management |
| `cloud auth` | login, logout, whoami | Authentication |
| `cloud tenant` | list, create, show, edit, delete, rotate-credentials, rotate-sync-token, cancel | Tenant management |
| `cloud profile` | list, create, show, edit, delete | Profile management |
| `cloud deploy` | (flags: --profile, --dry-run, --no-sync, -y) | Cloud deployment |
| `cloud sync` | push, pull, local, admin-user | Local-cloud sync |
| `cloud secrets` | sync, set, unset, cleanup | Secret management |
| `cloud db` | migrate, query, execute, validate, status, info, tables, describe, count, indexes, size, backup, restore | Cloud DB operations |
| `cloud domain` | set, status, remove | Custom domain management |
| `analytics` | overview, conversations, agents, tools, requests, sessions, content, traffic, costs | Metrics and reporting |
| `web` | content-types, templates, assets, sitemap, validate | Web configuration |
| `plugins` | list, show, run, validate, config, capabilities | Extension management |
| `plugins mcp` | list, status, validate, logs, list-packages, tools, call | MCP server management |
| `build` | core, mcp | Build workspace |
