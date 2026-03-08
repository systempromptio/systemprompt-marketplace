---
name: agent-dev-guide
description: "Entry point for agent-development — routes to the right sub-skill for your task"
version: "1.0.0"
git_hash: "0000000"
---

# Agent Development

Create, configure, and manage AI agents with skills, MCP tools, A2A protocol, and multi-agent architecture on systemprompt.io.

---

## Skills

### agent-management
**Load when:** creating a new agent, configuring agent settings, monitoring agent health, or troubleshooting agent issues.
**Covers:** Agent lifecycle (create, configure, monitor, troubleshoot), A2A protocol, OAuth security, skill assignments, multi-agent mesh architecture, port configuration, endpoint setup. Config: `services/agents/*.yaml`.

### skills-development
**Load when:** creating, assigning, or managing agent skills.
**Covers:** Skill creation (`services/skills/<id>/config.yaml`), capability definitions, tagging and discovery, version management, multi-agent skill sharing, skill assignment to agents.

### mcp-operations
**Load when:** connecting agents to MCP servers, configuring tool access, or debugging MCP connectivity.
**Covers:** MCP server configuration (`services/mcp/*.yaml`), tool discovery, OAuth authentication, lifecycle management (start/stop/restart), debugging connection issues, binary and package setup.

### ai-configuration
**Load when:** setting up AI providers, configuring model selection, or troubleshooting AI responses.
**Covers:** Provider setup (Anthropic, OpenAI, Gemini), fallback strategies, smart routing, model selection, token limits, `services/ai/config.yaml` structure, provider-specific configuration.

---

## Task Router

| I want to... | Load these skills |
|--------------|-------------------|
| Create a new agent | `agent-management` |
| Add skills to an agent | `skills-development` + `agent-management` |
| Create a new skill | `skills-development` |
| Connect an agent to MCP servers | `mcp-operations` |
| Set up AI providers | `ai-configuration` |
| Configure model routing/fallback | `ai-configuration` |
| Debug agent issues | `agent-management` + `mcp-operations` |
| Full agent setup from scratch | All four skills |

---

## Skill Dependencies

```
agent-management (core — agent lifecycle)
        |
        +---> skills-development (add capabilities)
        |
        +---> mcp-operations (connect tools)
        |
        +---> ai-configuration (set up AI providers)
```

Skills are largely independent — load what you need for the task at hand. For a full agent setup from scratch, load `agent-management` first, then the others as you reach each configuration step.
