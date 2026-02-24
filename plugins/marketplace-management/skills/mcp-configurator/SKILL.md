---
name: mcp-configurator
description: "Socratic interview to configure and connect a new MCP server with tools, auth, and environment setup"
---

# MCP Configurator

Guide the user through connecting a new MCP server. MCP (Model Context Protocol) servers expose tools that agents can use — search, file management, API access, database queries, and more. You ask questions and configure everything.

## What is an MCP Server?

An MCP server is a program that exposes tools via the Model Context Protocol. Agents connect to MCP servers to gain capabilities like:
- Searching the web
- Reading and writing files
- Calling external APIs
- Managing databases
- Sending messages (email, Slack, Discord)
- Running code

## Interview Flow

### Step 1: What Server?

**Ask:** "What MCP server do you want to connect? Tell me one of the following:
- **The name** of a known MCP server (e.g., 'filesystem', 'github', 'slack')
- **A URL** for a remote MCP endpoint
- **A binary** you have installed locally"

- Listen for: server type (local binary, remote endpoint, npm/pip package)
- Follow-up if unsure: "What capability do you need? I can suggest an MCP server."

### Step 2: Purpose

**Ask:** "What does this server do? What tools does it provide to your agents?"

- Listen for: specific tool names, capabilities, use cases
- Follow-up: "Which agents will use this server?"
- This determines: description field and which agents to update

### Step 3: Authentication

**Ask:** "Does this server require any API keys, tokens, or credentials to work?"

- Listen for: API key names, OAuth flows, token types
- If yes: "What is the environment variable name for each credential? (For example: GITHUB_TOKEN, SLACK_API_KEY)"
- If no: "Good — we will set it up without auth."
- This determines: environment variables and secrets to configure

### Step 4: Access Control

**Ask:** "Who should be able to use this MCP server?
- **All users** (anyone with a user account)
- **Admins only** (restricted to administrators)
- **Specific roles** (only certain team members)"

- This determines: oauth scopes and RBAC configuration

### Step 5: Port and Endpoint

**Ask:** "Should this server run locally (built-in) or connect to a remote endpoint?"

- If local: assign next available port (check existing with `plugins mcp status`)
- If remote: "What is the endpoint URL?"
- This determines: port, endpoint, binary fields

## Synthesis

Present the configuration:

> "Here is the MCP server configuration:
>
> **Name:** {server_id}
> **Type:** {local binary / remote endpoint}
> **Port:** {port} (or N/A for remote)
> **Endpoint:** {endpoint}
> **Auth:** {required/not required}
> **Secrets:** {list of env vars to set}
>
> Does this look right?"

Wait for confirmation.

## MCP Config Template

Generate following the pattern from existing configs:

```yaml
mcp_servers:
  {server_id}:
    binary: "{binary_name}"          # For local servers
    package: "{package_name}"        # Package/crate name
    port: {port}                     # Local port
    endpoint: "{endpoint_url}"       # API endpoint
    enabled: true
    display_in_web: true
    description: "{description}"
    oauth:
      required: {true/false}
      scopes: ["{scope}"]
      audience: "mcp"
      client_id: null
```

For remote-only servers (no local binary):

```yaml
mcp_servers:
  {server_id}:
    endpoint: "{remote_url}"
    enabled: true
    display_in_web: true
    description: "{description}"
    oauth:
      required: {true/false}
      scopes: ["{scope}"]
```

## Creation

After confirmation:

1. Write the config file to `services/mcp/{server_id}.yaml`
2. Set secrets (if any):
   - Using MCP tool: `manage_secrets` with action "set", plugin_id, var_name, var_value, is_secret=true
   - Fallback CLI: `cloud secrets set {KEY} "value"`
3. Sync: `cloud sync local mcp --direction to-db -y`
4. Start: `plugins mcp start {server_id}`
5. Verify: `plugins mcp tools {server_id}`

## Port Allocation

Check existing ports before assigning:

```bash
plugins mcp status
```

Existing allocations:
- 5010: systemprompt
- 5040: content-manager
- 5050: marketplace
- 5060+: available for new servers

## Common Server Patterns

### Node.js MCP Server (npm package)

```yaml
mcp_servers:
  {name}:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-{name}"]
    port: {port}
    endpoint: "http://localhost:{port}/mcp"
    enabled: true
```

### Python MCP Server (pip package)

```yaml
mcp_servers:
  {name}:
    command: "uvx"
    args: ["mcp-server-{name}"]
    port: {port}
    endpoint: "http://localhost:{port}/mcp"
    enabled: true
```

### Rust Binary (local build)

```yaml
mcp_servers:
  {name}:
    binary: "systemprompt-mcp-{name}"
    package: "{name}"
    port: {port}
    endpoint: "http://localhost:8080/api/v1/mcp/{name}/mcp"
    enabled: true
```

### Remote Endpoint (hosted service)

```yaml
mcp_servers:
  {name}:
    endpoint: "https://api.example.com/mcp"
    enabled: true
    description: "Remote {name} MCP server"
```

## Troubleshooting

If the server fails to start:
1. Check logs: `plugins mcp logs {server_id}`
2. Verify binary exists: `which {binary_name}`
3. Test endpoint: `curl {endpoint}/health`
4. Check secrets are set: `cloud secrets list`
5. Verify port is free: `lsof -i :{port}`
