---
name: ai-configuration
description: "Configure AI providers including Anthropic, OpenAI, and Gemini with fallback strategies, smart routing, model selection, and troubleshooting"
---

# AI Configuration

AI provider setup and management. Config: `services/ai/config.yaml`

## Full Configuration Example

```yaml
ai:
  default_provider: anthropic
  default_max_output_tokens: 8192
  sampling:
    enable_smart_routing: false
    fallback_enabled: true
  providers:
    anthropic:
      enabled: true
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-sonnet-4-20250514
    openai:
      enabled: false
      api_key: ${OPENAI_API_KEY}
      default_model: gpt-4-turbo
      google_search_enabled: true
    gemini:
      enabled: false
      api_key: ${GEMINI_API_KEY}
      endpoint: https://generativelanguage.googleapis.com/v1beta
      default_model: gemini-2.5-flash
      google_search_enabled: true
  mcp:
    auto_discover: true
    connect_timeout_ms: 5000
    execution_timeout_ms: 30000
    retry_attempts: 3
  history:
    retention_days: 30
    log_tool_executions: true
```

## Configure Anthropic

```bash
systemprompt cloud secrets set ANTHROPIC_API_KEY "sk-ant-api03-..."
```

```yaml
ai:
  default_provider: anthropic
  providers:
    anthropic:
      enabled: true
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-sonnet-4-20250514
```

| Model | Use Case | Context |
|-------|----------|---------|
| `claude-opus-4-20250514` | Complex reasoning | 200K |
| `claude-sonnet-4-20250514` | Balanced | 200K |
| `claude-haiku-3-20240307` | Fast, economical | 200K |

## Configure OpenAI

```bash
systemprompt cloud secrets set OPENAI_API_KEY "sk-..."
```

```yaml
ai:
  default_provider: openai
  providers:
    openai:
      enabled: true
      api_key: ${OPENAI_API_KEY}
      default_model: gpt-4-turbo
```

| Model | Use Case | Context |
|-------|----------|---------|
| `gpt-4-turbo` | Latest GPT-4 | 128K |
| `gpt-4o` | Optimized speed | 128K |
| `gpt-4o-mini` | Economical | 128K |

## Configure Gemini

```bash
systemprompt cloud secrets set GEMINI_API_KEY "AIza..."
```

```yaml
ai:
  default_provider: gemini
  providers:
    gemini:
      enabled: true
      api_key: ${GEMINI_API_KEY}
      endpoint: https://generativelanguage.googleapis.com/v1beta
      default_model: gemini-2.5-flash
```

| Model | Use Case | Context |
|-------|----------|---------|
| `gemini-2.5-flash` | Fast multimodal | 1M |
| `gemini-2.5-pro` | Advanced reasoning | 1M |

## Multi-Provider Fallback

Enable all providers with fallback:

```yaml
ai:
  default_provider: anthropic
  sampling:
    fallback_enabled: true
  providers:
    anthropic:
      enabled: true
      api_key: ${ANTHROPIC_API_KEY}
    openai:
      enabled: true
      api_key: ${OPENAI_API_KEY}
    gemini:
      enabled: true
      api_key: ${GEMINI_API_KEY}
```

Fallback order: anthropic -> openai -> gemini

## Smart Routing

```yaml
ai:
  sampling:
    enable_smart_routing: true
    fallback_enabled: true
```

| Request Type | Provider |
|--------------|----------|
| Complex reasoning | Anthropic |
| Fast queries | Gemini |
| Code generation | OpenAI/Anthropic |
| Cost-sensitive | Gemini/GPT-3.5 |

## Provider Capabilities

| Feature | Gemini | OpenAI | Anthropic |
|---------|--------|--------|-----------|
| Text Generation | Yes | Yes | Yes |
| Web Search | Yes (Google Search) | Yes | Not yet |
| Image Generation | Yes (up to 4K) | Yes (1K only) | No |

## Switch Provider

Change `default_provider` in config and validate:

```bash
systemprompt admin config validate
systemprompt admin config show --section ai
systemprompt admin agents message welcome -m "Hello" --blocking
```

## Provider CLI Commands

```bash
systemprompt admin config provider list
systemprompt admin config provider set <PROVIDER>
systemprompt admin config provider enable <PROVIDER>
systemprompt admin config provider disable <PROVIDER>
```

## Token Limits

```yaml
ai:
  default_max_output_tokens: 8192
```

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| Anthropic | claude-opus-4 | 200K | 32K |
| Anthropic | claude-sonnet-4 | 200K | 16K |
| OpenAI | gpt-4-turbo | 128K | 4K |
| Gemini | gemini-2.5-flash | 1M | 8K |

## Configuration Reference

| Field | Description |
|-------|-------------|
| `default_provider` | Primary: anthropic, openai, gemini |
| `default_max_output_tokens` | Max response tokens |
| `sampling.enable_smart_routing` | Auto-select provider |
| `sampling.fallback_enabled` | Try other providers on failure |
| `providers.<name>.enabled` | Enable/disable |
| `providers.<name>.api_key` | API key (use ${VAR}) |
| `providers.<name>.default_model` | Default model |
| `providers.<name>.google_search_enabled` | Enable web search |
| `mcp.auto_discover` | Auto-discover MCP servers |
| `mcp.execution_timeout_ms` | Tool timeout |

## Troubleshooting

### Provider Authentication Failed

Symptoms: "Invalid API key", "Unauthorized"

```bash
systemprompt cloud secrets list
systemprompt admin config show --section ai
systemprompt infra logs --context ai --level error --limit 20
```

Key prefixes: Anthropic `sk-ant-`, OpenAI `sk-`, Gemini `AIza`

Solution: `systemprompt cloud secrets set ANTHROPIC_API_KEY "correct-key"`

### Rate Limiting

Symptoms: 429 errors, "Too many requests"

```bash
systemprompt analytics ai --period hour
```

Solution: Enable fallback with multiple providers enabled.

### Model Not Available

Symptoms: "Model not found", "Invalid model"

Valid models:
- Anthropic: `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-haiku-3-20240307`
- OpenAI: `gpt-4-turbo`, `gpt-4o`, `gpt-4o-mini`
- Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`

### Token Limit Exceeded

Symptoms: "Input too long", responses cut off

Increase output limit:

```yaml
ai:
  default_max_output_tokens: 16384
```

Or use larger context model (e.g., Gemini with 1M context).

### Tool Execution Timeout

```bash
systemprompt plugins mcp status
systemprompt plugins mcp logs <server_name>
```

Increase timeout:

```yaml
ai:
  mcp:
    execution_timeout_ms: 60000
    retry_attempts: 3
```

### Slow Responses

Use faster model or enable smart routing:

```yaml
sampling:
  enable_smart_routing: true
```

## Quick Reference

| Task | Command |
|------|---------|
| Set key | `cloud secrets set <NAME> "value"` |
| List secrets | `cloud secrets list` |
| Show AI config | `admin config show --section ai` |
| Validate | `admin config validate` |
| AI logs | `infra logs --context ai` |
| Analytics | `analytics ai --period day` |
| Test | `admin agents message <name> -m "text" --blocking` |
| Provider list | `admin config provider list` |
| Set provider | `admin config provider set <provider>` |
