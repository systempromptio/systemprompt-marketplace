---
name: mcp-operations
description: "Configure, manage, and troubleshoot MCP servers including tool discovery, OAuth authentication, lifecycle management, and debugging"
---

# MCP Operations

MCP server setup and management. Config: `services/mcp/*.yaml`

## Configure Server

Step 1: Create `services/mcp/<name>.yaml`:

```yaml
mcp_servers:
  my-server:
    binary: "node"
    args: ["dist/index.js"]
    package: "my-mcp-server"
    port: 5011
    endpoint: "http://localhost:8080/api/v1/mcp/my-server/mcp"
    enabled: true
    display_in_web: true
    description: "My custom MCP server"
    env:
      API_KEY: ${MY_SERVER_API_KEY}
      DEBUG: "false"
    oauth:
      required: true
      scopes: ["user"]
      audience: "mcp"
      client_id: null
    working_dir: "/path/to/server"
```

Step 2: Set secrets and start

```bash
systemprompt cloud secrets set MY_SERVER_API_KEY "your-api-key"
systemprompt cloud sync local mcp --direction to-db -y
systemprompt plugins mcp start my-server
systemprompt plugins mcp status
```

Step 3: Verify tools

```bash
systemprompt plugins mcp tools my-server
```

## Configure OAuth

Public (no auth):

```yaml
oauth:
  required: false
```

Authenticated:

```yaml
oauth:
  required: true
  scopes: ["user"]
  audience: "mcp"
  client_id: null
```

Admin only:

```yaml
oauth:
  required: true
  scopes: ["admin"]
```

## Lifecycle Management

```bash
# Start
systemprompt plugins mcp start my-server
systemprompt plugins mcp start --all

# Stop
systemprompt plugins mcp stop my-server
systemprompt plugins mcp stop --all

# Restart
systemprompt plugins mcp restart my-server
systemprompt plugins mcp restart --all

# Status
systemprompt plugins mcp status
systemprompt plugins mcp status my-server

# Logs
systemprompt plugins mcp logs my-server
systemprompt plugins mcp logs my-server --follow
systemprompt plugins mcp logs my-server --level error
```

## Tool Discovery

```bash
systemprompt plugins mcp refresh
systemprompt plugins mcp tools my-server
```

## AI Integration

In `services/ai/config.yaml`:

```yaml
ai:
  mcp:
    auto_discover: true
    connect_timeout_ms: 5000
    execution_timeout_ms: 30000
    retry_attempts: 3
```

Check agent tools: `systemprompt admin agents tools welcome`

## Configuration Reference

| Field | Description |
|-------|-------------|
| `binary` | Executable to run |
| `args` | Command-line arguments |
| `working_dir` | Working directory |
| `package` | Package identifier |
| `port` | Port to listen on |
| `endpoint` | Full endpoint URL |
| `enabled` | Server is active |
| `display_in_web` | Show in UI |
| `description` | Human-readable description |
| `env` | Environment variables (use ${VAR} for secrets) |
| `oauth.required` | Require auth |
| `oauth.scopes` | Required OAuth scopes |

## Troubleshooting

### Server Not Starting

Symptoms: Status "stopped" or "failed", tools unavailable

```bash
systemprompt plugins mcp status
systemprompt plugins mcp logs my-server --limit 50
systemprompt plugins mcp start my-server
```

Solutions:
- Binary not found: Use full path in `binary` field
- Port in use: `lsof -i :5011`, change port or stop conflicting process
- Config error: Check YAML syntax in `services/mcp/<name>.yaml`

### Tools Not Appearing

```bash
systemprompt plugins mcp tools my-server
systemprompt plugins mcp status
systemprompt admin config show --section ai
```

Solutions:
- Server not running: `systemprompt plugins mcp start my-server`
- Auto-discover disabled: Set `mcp.auto_discover: true` in `services/ai/config.yaml`
- Force refresh: `systemprompt plugins mcp refresh`

### Tool Execution Timeout

```bash
systemprompt admin config show --section ai
systemprompt plugins mcp logs my-server
```

Increase timeout:

```yaml
ai:
  mcp:
    execution_timeout_ms: 60000
    retry_attempts: 3
```

### Authentication Failures

Symptoms: 401/403 errors

```bash
systemprompt plugins mcp show my-server
systemprompt admin session status
```

Solutions:
- Reduce scope: `scopes: ["user"]`
- Disable auth: `oauth.required: false`
- Token expired: `systemprompt admin session logout` then `login`

### Connection Failures

Symptoms: "Connection refused", intermittent connectivity

```bash
systemprompt plugins mcp status
nc -zv localhost 5011
```

Solutions:
- Start server: `systemprompt plugins mcp start my-server`
- Increase connection timeout: `connect_timeout_ms: 10000`

### Environment Variables Not Set

```bash
systemprompt cloud secrets list
systemprompt plugins mcp logs my-server
```

Solution: `systemprompt cloud secrets set MY_SERVER_API_KEY "your-api-key"` then restart.

### Server Crashes

```bash
systemprompt plugins mcp logs my-server --limit 100
```

Check for: out of memory, uncaught exceptions, dependency issues.

## Log Messages

| Message | Meaning |
|---------|---------|
| `MCP server started on port XXXX` | Running |
| `Tool registered: tool_name` | Tool available |
| `Tool execution started` | Tool called |
| `Tool execution completed` | Tool finished |
| `Tool execution failed` | Tool error |
| `Connection refused` | Can't reach server |

## Quick Reference

| Task | Command |
|------|---------|
| List | `plugins mcp list` |
| Show | `plugins mcp show <name>` |
| Start | `plugins mcp start <name>` |
| Stop | `plugins mcp stop <name>` |
| Restart | `plugins mcp restart <name>` |
| Status | `plugins mcp status` |
| Logs | `plugins mcp logs <name>` |
| Tools | `plugins mcp tools <name>` |
| Refresh | `plugins mcp refresh` |
