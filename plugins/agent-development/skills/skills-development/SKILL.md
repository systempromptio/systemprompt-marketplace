---
name: skills-development
description: "Create, configure, assign, and manage agent skills as reusable capabilities with tagging, discovery, and multi-agent sharing"
---

# Skills Development

Skill creation and management. Config: `services/skills/<id>/config.yaml`

## Create Skill

Step 1: Create `services/skills/<id>/config.yaml`:

```yaml
skill:
  id: code_review
  name: "Code Review"
  description: "Review code for quality, bugs, security issues, and best practices"
  version: "1.0.0"
  enabled: true
  tags:
    - code
    - review
    - quality
    - development
    - security
  examples:
    - "Review this code for bugs"
    - "Check this function for security issues"
    - "What improvements can be made to this code?"
  metadata:
    category: "development"
    difficulty: "intermediate"
```

Step 2: Sync to database

```bash
systemprompt core skills sync --direction to-db -y
```

Step 3: Verify

```bash
systemprompt core skills list
systemprompt core skills show code_review
```

## Assign to Agent

Reference in `services/agents/<agent>.yaml`:

```yaml
agents:
  developer-assistant:
    card:
      skills:
        - id: "code_review"
          name: "Code Review"
          description: "Review code for quality and best practices"
          tags: ["code", "review"]
          examples:
            - "Review this code for bugs"
```

Sync both:

```bash
systemprompt core skills sync --direction to-db -y
systemprompt cloud sync local agents --direction to-db -y
```

Verify: `systemprompt admin agents show developer-assistant`

## Update Skill

Edit config or use CLI:

```bash
systemprompt core skills edit code_review
```

Then sync:

```bash
systemprompt core skills sync --direction to-db -y
systemprompt core skills show code_review
```

## Configuration Reference

```yaml
skill:
  id: skill_id           # Unique identifier (required)
  name: "Skill Name"     # Display name (required)
  description: "..."     # What skill does (required)
  version: "1.0.0"       # Semantic version (required)
  enabled: true           # Active state (required)
  tags:                   # Categorization (optional)
    - tag1
    - tag2
  examples:               # Usage examples (optional)
    - "Example input 1"
  metadata:               # Additional data (optional)
    category: "category"
    difficulty: "beginner|intermediate|advanced"
```

## Best Practices

**Naming:**
- Use lowercase with underscores: `code_review`
- Be descriptive but concise

**Descriptions:**
- Start with verb: "Review...", "Help with..."
- Under 100 characters

**Tags:**
- Use lowercase
- Include category and action tags
- Limit to 5-7 per skill

**Examples:**
- Include 3-5 diverse examples
- Show different ways to invoke
- Cover common use cases

## Skills Architecture

Skills are loaded into agent context at startup. Agent YAML references skills by ID:

```yaml
skills:
  - edwards_voice
  - technical_content_writing
  - research_blog
```

Skills provide:
- Voice and tone guidelines
- Content structure templates
- Formatting rules
- Anti-patterns to avoid

## Troubleshooting

### Skill Not Found

```bash
systemprompt core skills list
systemprompt core skills show <skill_id>
systemprompt core skills sync --direction to-db --dry-run
```

Solutions:
- Sync: `systemprompt core skills sync --direction to-db -y`
- ID mismatch: Ensure agent `skills.id` matches skill `skill.id` exactly
- Disabled: Set `enabled: true` in skill config

### Sync Fails

```bash
systemprompt core skills validate
```

Solutions:
- Check YAML syntax
- Verify required fields (id, name, description, version, enabled)
- Fix indentation issues

### Skill Not Used by Agent

```bash
systemprompt admin agents show <agent-name>
```

Solutions:
- Add skill ID to agent config `skills` section
- Sync both skills and agents
- Verify agent system prompt references the skill

## Quick Reference

| Task | Command |
|------|---------|
| List | `core skills list` |
| Show | `core skills show <id>` |
| Edit | `core skills edit <id>` |
| Sync | `core skills sync --direction to-db -y` |
| Validate | `core skills validate` |
