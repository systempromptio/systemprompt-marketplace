# systemprompt-marketplace

Development plugin marketplace for [systemprompt.io](https://systemprompt.io) codebases. Install plugins to get AI-powered skills, agents, and tools for building with systemprompt.io.

## Installation

Add the marketplace to Claude Code:

```bash
/plugin marketplace add systemprompt-io/systemprompt-marketplace
```

Then install individual plugins:

```bash
/plugin install rust-development@systemprompt-marketplace
/plugin install web-development@systemprompt-marketplace
/plugin install content-writing@systemprompt-marketplace
```

## Plugins

| Plugin | Skills | Agents | Category | Description |
|--------|--------|--------|----------|-------------|
| **rust-development** | 4 | 0 | development | Build Rust extensions, CLI binaries, and MCP servers |
| **web-development** | 1 | 0 | development | Build web features, pages, templates, and assets |
| **content-writing** | 12 | 0 | content | Blog posts, technical docs, narrative writing |
| **marketplace-management** | 6 | 2 | platform | Socratic skill/agent/workflow creation |
| **operations** | 6 | 1 | operations | Cloud, monitoring, scheduling, Discord |
| **agent-development** | 4 | 1 | development | AI agents, MCP tools, A2A protocol |
| **frontend-development** | 1 | 0 | development | Front-end JS, CSS, HTML coding standards |
| **general** | 1 | 0 | general | General assistance utilities |

**Total: 8 plugins, 35 skills, 4 agents**

## Plugin Details

### rust-development

Skills for building Rust extensions, CLI binaries, and MCP servers with idiomatic patterns.

- `extension-building` - Library extensions with architecture, traits, schemas, API routes, jobs
- `cli-extension-building` - Standalone CLI extension binaries
- `rust-coding-standards` - Rust coding standards and quality patterns
- `mcp-building` - MCP servers with tools and AI integration

### web-development

Skills for building web features with pages, templates, and content management.

- `web-building` - Pages, templates, content ingestion, prerendering, assets

### content-writing

Skills for creating and managing all content types.

- `content-writing` - General writing and editing
- `content-creation` - Content creation workflows
- `technical-writing` - Technical documentation
- `technical-content-writing` - Technical blog content
- `narrative-writing` - Narrative-driven content
- `blog-writing` - Long-form blog posts
- `blog-image-generation` - Featured image generation
- `guide-writing` - Guides and tutorials
- `announcement-writing` - Announcements
- `edwards-voice` - Brand voice guidelines
- `research-blog` - Research-driven blog content
- `update-content` - Read and edit existing content

### marketplace-management

Socratic interview-driven skill and agent creation, with MCP server integration.

- `marketplace-onboarding` - Guided discovery interview
- `skill-creator` - Skill creation through interview
- `agent-creator` - Agent creation through interview
- `mcp-configurator` - MCP server configuration
- `workflow-designer` - Multi-agent workflow design
- `plugin-packager` - Package plugins for distribution
- Agents: `marketplace_consultant`, `marketplace_editor`

### operations

Infrastructure, monitoring, and system management.

- `cloud-operations` - DNS, SSL, multi-tenant routing, deployment
- `scheduler-management` - Job scheduling
- `analytics-monitoring` - Usage metrics and analytics
- `system-configuration` - System configuration
- `discord-integration` - Discord bot setup
- `cli-reference` - CLI command reference
- Agent: `systemprompt_hub`

### agent-development

Agent lifecycle management with AI configuration.

- `agent-management` - Create, configure, monitor agents
- `ai-configuration` - Configure AI providers
- `skills-development` - Create and manage skills
- `mcp-operations` - MCP server operations
- Agent: `welcome`

### frontend-development

Front-end coding standards for static site generation with modular vanilla JS.

- `frontend-coding-standards` - JavaScript, CSS, and HTML standards with Web Components

### general

- `general-assistance` - General help and questions

## Syncing from systemprompt-web

To update plugins from the monorepo source:

```bash
python3 scripts/convert.py --source ../systemprompt-web
```

Requires Python 3 with PyYAML: `pip install pyyaml`

## License

Copyright systemprompt.io. All rights reserved.
