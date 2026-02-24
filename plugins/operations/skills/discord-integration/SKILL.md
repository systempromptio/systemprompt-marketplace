---
name: discord-integration
description: "Configure and operate Discord bot integration for systemprompt.io - outbound CLI messaging, inbound Gateway reception, webhook setup, and troubleshooting"
---

# Discord Integration

Bidirectional Discord communication: CLI for outbound messages, Gateway for inbound message reception.

## Architecture

| Mode | Direction | Component | Use Case |
|------|-----------|-----------|----------|
| **CLI** | Outbound | `extensions/cli/discord/` | Send notifications, alerts, status updates |
| **Gateway** | Inbound | `extensions/soul/src/discord/` | Receive messages, trigger agent workflows |

## Prerequisites

- Discord bot created at https://discord.com/developers/applications
- Bot token obtained and configured in `services/config/discord.yaml`
- Bot invited to your Discord server with Send Messages permission
- MESSAGE CONTENT intent enabled (required for Gateway inbound messages)

## Discord Developer Portal Setup

### Create Application

1. Go to https://discord.com/developers/applications
2. Click **New Application** -> name it -> **Create**
3. Go to **Bot** in sidebar -> **Reset Token** -> copy and save token securely

### Configure Bot Settings

- **Public Bot**: OFF (only you can invite)
- **Requires OAuth2 Code Grant**: OFF

### Enable Gateway Intents

In Bot settings under Privileged Gateway Intents:

- **MESSAGE CONTENT INTENT**: ON (required to read message text)
- **SERVER MEMBERS INTENT**: Optional
- **PRESENCE INTENT**: Optional

**CRITICAL**: Without MESSAGE CONTENT INTENT, the gateway cannot read message content.

### Invite Bot to Server

1. Go to **OAuth2** -> **URL Generator**
2. Select scopes: `bot`
3. Select permissions: Read Messages/View Channels, Send Messages, Read Message History
4. Copy generated URL -> open in browser -> select server -> **Authorize**

## Configuration

Config file: `services/config/discord.yaml`

```yaml
bot_token: "YOUR_BOT_TOKEN"
default_channel_id: "1234567890123456789"
default_user_id: "9876543210987654321"
enabled: true
gateway:
  enabled: true
  target_agent: "systemprompt_hub"
  message_prefix: "DISCORD_MESSAGE"
  ignore_channels: []
  ignore_bots: true
```

### Getting Discord IDs

1. User Settings -> Advanced -> **Developer Mode**: ON
2. **Channel ID**: Right-click channel -> Copy Channel ID
3. **User ID**: Right-click username -> Copy User ID

## Outbound: CLI Commands

| Task | Command |
|------|---------|
| Test connection | `systemprompt plugins run discord test` |
| Send to default | `systemprompt plugins run discord send "message"` |
| Send to channel | `systemprompt plugins run discord send -c <channel-id> "message"` |
| Send DM | `systemprompt plugins run discord send -u <user-id> "message"` |
| Show help | `systemprompt plugins run discord --help` |

### Agent Discord Notifications

Agents send Discord messages using:

```yaml
systemprompt plugins run discord send "<message>"
systemprompt plugins run discord send "<message>" --channel <id>
```

## Inbound: Gateway

The Gateway maintains a persistent WebSocket connection to Discord and forwards messages to a target agent.

### Message Format

```
DISCORD_MESSAGE: channel=<id> (<name>) author=<username> content=<message>
```

### Gateway Operation

```bash
systemprompt infra jobs run soul_discord_gateway
systemprompt infra jobs list | grep discord
```

The gateway job has `run_on_startup: true` and schedule `@reboot` -- it starts automatically with the server.

### Path Resolution in Rust

```rust
use systemprompt::cloud::ProjectContext;
use systemprompt::loader::ExtensionLoader;

fn resolve_cli_binary() -> PathBuf {
    let project = ProjectContext::discover();
    ExtensionLoader::get_cli_binary_path(project.root(), "systemprompt")
        .unwrap_or_else(|| PathBuf::from("systemprompt"))
}
```

Always use `ProjectContext` and `ExtensionLoader` for path resolution. Never hardcode paths.

### Target Agent Configuration

```yaml
name: systemprompt_hub
description: Central communications hub
instructions: |
  When you receive a DISCORD_MESSAGE:
  1. Parse the author and content
  2. Process the request appropriately
  3. Respond via Discord if needed:
     systemprompt plugins run discord send "<response>"
```

## Monitoring

```bash
systemprompt infra logs view --limit 50
systemprompt infra logs search "discord"
```

Expected log messages:
- `INFO Starting Discord gateway bot target_agent=systemprompt_hub`
- `INFO Discord gateway connected bot_name=systemprompt guild_count=1`
- `INFO Received Discord message, forwarding to agent`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gateway won't connect | Verify bot token: `systemprompt plugins run discord test` |
| Messages not received | Enable MESSAGE CONTENT INTENT in Developer Portal |
| Permission denied | Build project: `just build`, run from project root |
| Missing access error | Ensure bot is invited to server with Send Messages permission |
| Cannot send DM | User must share a server with bot and have DMs enabled |
| Invalid ID format | Copy ID directly from Discord using Developer Mode (17-20 digits) |
| Rate limited | Wait and retry. Limits: 5 msgs/5s per channel, 10 DM creates/s |
| Agent returns error | Check agent exists: `systemprompt admin agents list` |

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `bot_token` | Required | Discord bot token |
| `default_channel_id` | None | Default channel for CLI |
| `default_user_id` | None | Default user for DMs |
| `enabled` | `true` | Enable Discord integration |
| `gateway.enabled` | `true` | Enable inbound gateway |
| `gateway.target_agent` | `systemprompt_hub` | Agent to receive messages |
| `gateway.message_prefix` | `DISCORD_MESSAGE` | Message format prefix |
| `gateway.ignore_channels` | `[]` | Channel IDs to ignore |
| `gateway.ignore_bots` | `true` | Ignore bot messages |

## Quick Reference

| Task | Command |
|------|---------|
| Test connection | `systemprompt plugins run discord test` |
| Send message | `systemprompt plugins run discord send "msg"` |
| Send to channel | `systemprompt plugins run discord send -c <id> "msg"` |
| Send DM | `systemprompt plugins run discord send -u <id> "msg"` |
| Run gateway | `systemprompt infra jobs run soul_discord_gateway` |
| List jobs | `systemprompt infra jobs list` |
| View logs | `systemprompt infra logs view --limit 50` |
