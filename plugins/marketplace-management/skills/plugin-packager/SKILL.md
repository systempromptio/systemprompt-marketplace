---
name: plugin-packager
description: "Socratic interview to package skills, agents, and MCP servers into a distributable plugin"
---

# Plugin Packager

Guide the user through packaging their skills, agents, and MCP servers into a plugin — a distributable bundle that others can install and use.

## What is a Plugin?

A plugin is a container that bundles:
- **Skills** — reusable capabilities
- **Agents** — AI assistants with specific roles
- **MCP Servers** — tool integrations
- **Metadata** — name, description, category, keywords, dependencies

Plugins are the unit of distribution in the marketplace. Users install a plugin and get everything it contains.

## Interview Flow

### Step 1: Identity

**Ask:** "What is the name of your plugin? And in one sentence, what does it do?"

- Listen for: a clear, concise name and purpose
- Follow-up: "Who is this plugin for? What type of user or business benefits from it?"
- This derives: id, name, description

### Step 2: Skills

**Ask:** "Which skills should this plugin include?"

List the user's available skills using `list_skills` MCP tool or `core skills list` CLI.

- Present the list and let them pick
- Follow-up: "Any skills missing that we should create first?"
- If yes: pause and use `skill_creator` workflow, then return
- This derives: skills.include list

### Step 3: Agents

**Ask:** "Which agents should this plugin include?"

List available agents using `admin agents list` CLI.

- Present the list and let them pick
- Follow-up: "Any agents missing?"
- If yes: pause and use `agent_creator` workflow, then return
- Note: agents auto-include their skills, so skills from Step 2 may already be covered
- This derives: agents.include list

### Step 4: MCP Servers

**Ask:** "Which MCP servers does this plugin depend on? These are the tool integrations that agents use."

List available servers using `plugins mcp list` CLI.

- Present the list and let them pick
- Follow-up: "Any MCP connections missing?"
- If yes: pause and use `mcp_configurator` workflow, then return
- This derives: mcp_servers list

### Step 5: Category

**Ask:** "What category best describes this plugin?
- **platform** — system management, infrastructure
- **business** — business operations, workflows
- **content** — writing, media, publishing
- **development** — code, testing, CI/CD
- **integration** — external service connections
- **analytics** — data, reporting, monitoring
- **communication** — messaging, notifications"

- This derives: category field

### Step 6: Dependencies

**Ask:** "Does this plugin depend on any other plugins? For example, does it require the base systemprompt plugin to be installed first?"

- Most plugins have no dependencies
- If yes: note the plugin IDs
- This derives: depends list

### Step 7: Access Control

**Ask:** "Who should be able to install and use this plugin?
- **Everyone** (no restrictions)
- **Specific roles** (e.g., only admins, only content team)"

- This derives: roles list (empty = everyone)

## Synthesis

Present the complete plugin configuration:

> "Here is the plugin package:
>
> **Name:** {name}
> **Description:** {description}
> **Category:** {category}
>
> **Contains:**
> - Skills: {list}
> - Agents: {list}
> - MCP Servers: {list}
>
> **Dependencies:** {list or none}
> **Access:** {everyone or specific roles}
>
> Ready to create?"

Wait for confirmation.

## Plugin Config Template

```yaml
plugin:
  id: {plugin_id}
  name: "{Plugin Name}"
  description: "{One-sentence description}"
  version: "1.0.0"
  enabled: true
  skills:
    source: explicit
    include:
      - {skill_id_1}
      - {skill_id_2}
  agents:
    source: explicit
    include:
      - {agent_id_1}
      - {agent_id_2}
  mcp_servers:
    - {mcp_server_1}
    - {mcp_server_2}
  scripts: []
  keywords: [{keyword1}, {keyword2}, {keyword3}]
  category: {category}
  author:
    name: "{author_name}"
  roles: [{role1}]
  depends: [{dependency1}]
```

## Creation

After confirmation:

1. Create the plugin directory: `services/plugins/{plugin_id}/`
2. Write `services/plugins/{plugin_id}/config.yaml`
3. Sync: `core plugins sync --direction to-db -y`
4. Verify: `core plugins show {plugin_id}`

## Naming Conventions

- **plugin_id:** lowercase, no spaces, hyphens or underscores allowed
  - Good: `content_suite`, `sales_toolkit`, `dev_tools`
  - Bad: `My Plugin`, `content-suite`, `ContentSuite`
- **name:** Human-readable, title case
- **description:** One sentence, starts with a noun or verb phrase
- **keywords:** 5-10 lowercase terms for search/discovery

## Version Guidelines

- Start at `1.0.0` for initial release
- Increment minor version for new skills/agents added
- Increment major version for breaking changes (removed skills, renamed agents)

## Quality Checks

Before finalising, verify:
- [ ] All included skills exist and are enabled
- [ ] All included agents exist and are enabled
- [ ] All MCP servers are configured and accessible
- [ ] Description accurately reflects what the plugin contains
- [ ] Keywords are relevant for marketplace search
- [ ] Category is appropriate
- [ ] Dependencies (if any) are available in the marketplace
