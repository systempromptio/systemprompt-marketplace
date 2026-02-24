---
name: agent-management
description: "Create, configure, monitor, and troubleshoot AI agents with A2A protocol, OAuth security, skill assignments, and multi-agent mesh architecture"
---

# Agent Management

Agent lifecycle management. Config: `services/agents/*.yaml`

## Create Agent

Step 1: Create `services/agents/<name>.yaml`:

```yaml
agents:
  my-assistant:
    name: "my-assistant"
    port: 9001
    endpoint: "http://localhost:8080/api/v1/agents/my-assistant"
    enabled: true
    is_primary: false
    default: false
    card:
      protocolVersion: "0.3.0"
      name: "My Assistant"
      displayName: "My Assistant"
      description: "A specialized AI assistant"
      version: "1.0.0"
      preferredTransport: "JSONRPC"
      provider:
        organization: "Your Organization"
        url: "https://yourproject.com"
      iconUrl: "https://ui-avatars.com/api/?name=MA&background=6366f1&color=fff&bold=true&size=256"
      capabilities:
        streaming: true
        pushNotifications: false
        stateTransitionHistory: false
      defaultInputModes:
        - "text/plain"
      defaultOutputModes:
        - "text/plain"
        - "application/json"
      securitySchemes:
        oauth2:
          type: oauth2
          flows:
            authorizationCode:
              authorizationUrl: "http://localhost:8080/api/v1/core/oauth/authorize"
              tokenUrl: "http://localhost:8080/api/v1/core/oauth/token"
              scopes:
                anonymous: "Public access"
                user: "Authenticated user access"
                admin: "Administrative access"
      security:
        - oauth2: ["anonymous"]
      skills:
        - id: "general_assistance"
          name: "General Assistance"
          description: "Help with questions and general tasks"
          tags: ["assistance", "general"]
          examples:
            - "Help me understand this"
      supportsAuthenticatedExtendedCard: false
    metadata:
      systemPrompt: |
        You are My Assistant, a helpful AI agent.
```

Step 2: Validate and sync

```bash
systemprompt admin agents validate
systemprompt cloud sync local agents --direction to-db -y
```

Step 3: Verify and test

```bash
systemprompt admin agents list
systemprompt admin agents show my-assistant
systemprompt admin agents message my-assistant -m "Hello" --blocking
```

## Add Skills to Agent

Step 1: Create skill at `services/skills/<id>/config.yaml`

Step 2: Reference in agent `services/agents/<name>.yaml`:

```yaml
skills:
  - id: "code_review"
    name: "Code Review"
    description: "Review code for quality and best practices"
    tags: ["code", "review"]
    examples:
      - "Review this code for bugs"
```

Step 3: Sync both

```bash
systemprompt core skills sync --direction to-db -y
systemprompt cloud sync local agents --direction to-db -y
```

## Configure OAuth

Public agent (no auth):

```yaml
security:
  - oauth2: ["anonymous"]
```

Authenticated agent:

```yaml
security:
  - oauth2: ["user"]
```

Admin-only agent:

```yaml
security:
  - oauth2: ["admin"]
```

## Configure A2A Protocol

```yaml
capabilities:
  streaming: true
  pushNotifications: false
  stateTransitionHistory: false
```

A2A messaging:

```bash
# Blocking (wait for response)
systemprompt admin agents message <agent> -m "<message>" --blocking

# With timeout
systemprompt admin agents message <agent> -m "<message>" --blocking --timeout 300

# With shared context
systemprompt admin agents message <agent> -m "<message>" --context-id <id> --blocking
```

## Update System Prompt

Edit `services/agents/<name>.yaml` directly:

```yaml
metadata:
  systemPrompt: |
    You are My Assistant, an AI agent specialized in code review.
    Use pipe (|) for multiline. Maintain consistent indentation.
```

Then sync:

```bash
systemprompt cloud sync local agents --direction to-db -y
```

## Multi-Agent Mesh Architecture

The mesh is a coordinated system of specialised agents communicating via A2A protocol:

- **Hub agent** - Central nervous system, Discord notifications, memory management
- **Orchestrator** - Workflow coordinator, routes to worker agents
- **Worker agents** - Specialised content creators with specific skills

Port allocation:
- 9000-9019: Core agents
- 9020-9029: Hub and orchestrators
- 9030-9039: Orchestrators
- 9040-9099: Specialised workers

Workflow pattern:

```
1. User -> Orchestrator (request)
2. Orchestrator -> Hub (notify start)
3. Orchestrator -> Worker Agent (delegate with context)
4. Worker Agent -> MCP tools (execute)
5. Orchestrator -> Hub (notify complete)
6. Hub -> Discord + Memory (record)
```

## Monitor Agent

```bash
systemprompt admin agents status
systemprompt admin agents logs my-assistant
systemprompt admin agents logs my-assistant --follow
systemprompt admin agents registry
systemprompt admin agents tools my-assistant
```

## Troubleshooting

### Agent Not Responding

Symptoms: 502 Bad Gateway, connection refused, timeout

```bash
systemprompt admin agents list
systemprompt admin agents status
systemprompt admin agents logs my-assistant --limit 100
lsof -i :9001  # Check port conflicts
```

Solutions:
- Not in list: `systemprompt admin agents validate` then sync
- Disabled: Set `enabled: true` in agent YAML
- Port in use: Kill conflicting process

### OAuth Authentication Failures

Symptoms: 401 Unauthorized, 403 Forbidden

```bash
systemprompt admin agents show my-assistant
systemprompt admin session status
systemprompt admin config show --section oauth
```

Solutions:
- Public access: Set `security: [oauth2: ["anonymous"]]`
- Session expired: `systemprompt admin session logout` then `login`
- Scope mismatch: Check user role matches required scope

### Skill Not Recognized

```bash
systemprompt core skills list
systemprompt core skills show <skill_id>
systemprompt core skills sync --direction to-db --dry-run
```

Solutions:
- Sync skills: `systemprompt core skills sync --direction to-db -y`
- ID mismatch: Ensure agent `skills.id` matches skill `skill.id` exactly
- Disabled: Set `enabled: true` in skill config

### Task Stuck

States: pending -> submitted -> working -> completed

```bash
systemprompt admin agents task <task_id>
systemprompt admin agents registry
```

- Stuck at pending: `systemprompt infra services restart agents`
- Stuck at working: Check AI provider and MCP status
- Rate limited: Switch provider in `services/ai/config.yaml`

### Tool Execution Failures

```bash
systemprompt admin agents tools my-assistant
systemprompt plugins mcp status
systemprompt plugins mcp logs <server_name>
```

- MCP not running: `systemprompt plugins mcp start <server_name>`
- Tool not listed: `systemprompt plugins mcp refresh`
- Auth error: `systemprompt cloud secrets set MCP_API_KEY "new-key"`

### System Prompt Not Applied

```bash
systemprompt admin agents show my-assistant
systemprompt cloud sync local agents --direction to-db --dry-run
systemprompt admin agents validate
```

- Not synced: `systemprompt cloud sync local agents --direction to-db -y`
- YAML formatting: Use pipe `|` for multiline prompts

## Quick Reference

| Task | Command |
|------|---------|
| List | `admin agents list` |
| Show | `admin agents show <name>` |
| Validate | `admin agents validate` |
| Status | `admin agents status` |
| Logs | `admin agents logs <name>` |
| Message | `admin agents message <name> -m "text" --blocking` |
| Task | `admin agents task <id>` |
| Tools | `admin agents tools <name>` |
| Registry | `admin agents registry` |
| Edit | `admin agents edit <name>` |
| Sync | `cloud sync local agents --direction to-db -y` |
