---
name: analytics-monitoring
description: "Monitor usage metrics, AI costs, traffic analytics, bot detection, session tracking, and content performance reporting"
---

# Analytics Monitoring

Analytics and monitoring workflows. Config: `services/config/analytics.yaml`

## Dashboard Overview

```bash
systemprompt analytics overview
systemprompt analytics overview --since 24h
systemprompt analytics summary
systemprompt analytics summary --period day
systemprompt analytics summary --period week
systemprompt analytics summary --period month
```

## AI Provider Usage

```bash
systemprompt analytics ai --period day
systemprompt analytics ai --provider anthropic --period week
systemprompt analytics ai --detail model --period day
```

## Traffic Analytics

```bash
systemprompt analytics traffic sources
systemprompt analytics traffic geo --limit 10
systemprompt analytics traffic devices
systemprompt analytics traffic bots
```

## Session Analytics

```bash
systemprompt analytics sessions stats
systemprompt analytics sessions trends
systemprompt analytics sessions live --limit 20
systemprompt analytics sessions --active
```

## Content Performance

```bash
systemprompt analytics content stats
systemprompt analytics content top --limit 10
systemprompt analytics content trends
systemprompt analytics content --source blog --period week
```

## Cost Analytics

```bash
systemprompt analytics costs summary
systemprompt analytics costs summary --days 30
systemprompt analytics costs trends --group-by day
systemprompt analytics costs breakdown --by model
systemprompt analytics costs breakdown --by agent
```

## Agent Analytics

```bash
systemprompt analytics agents stats
systemprompt analytics agents trends --days 7
systemprompt analytics agents show <name>
```

## Tool Usage

```bash
systemprompt analytics tools stats
systemprompt analytics tools trends
systemprompt analytics tools show <tool-name>
```

## AI Request Analytics

```bash
systemprompt analytics requests stats
systemprompt analytics requests list --limit 50 --model claude
systemprompt analytics requests trends
systemprompt analytics requests models
```

## Bot Detection

Three-tier detection system:

1. **User-Agent Detection** - Known bots: Googlebot, Bingbot, ChatGPT-User, Claude-Web
2. **Scanner Detection** - Malicious patterns: `.env`, `.php`, `/wp-admin` probes
3. **Behavioral Detection** - 7-signal system: request velocity, page coverage, timing patterns

```bash
systemprompt analytics bots --period day
systemprompt analytics bots --suspicious
systemprompt admin users banned
systemprompt admin users unban 192.168.1.100
```

## Export Data

```bash
systemprompt analytics export --format json --period week > analytics.json
systemprompt analytics export --format csv --period week > analytics.csv
systemprompt analytics overview --export file.csv
```

## Configuration

`services/config/analytics.yaml`:

```yaml
analytics:
  enabled: true
  retention_days: 90
  tracking:
    sessions: true
    requests: true
    ai_usage: true
    content: true
    bots: true
  bot_detection:
    enabled: true
    block_threshold: 10
    monitoring_window: 3600
  aggregation:
    interval: 3600
```

## Alerts

```yaml
analytics:
  alerts:
    daily_cost_limit: 50.00
    hourly_request_limit: 1000
```

```bash
systemprompt analytics alerts --period week
```

## Common Flags

| Flag | Description |
|------|-------------|
| `--since` | Time range: `1h`, `24h`, `7d`, `30d` |
| `--until` | End time for range |
| `--period` | Period: `hour`, `day`, `week`, `month` |
| `--export` | Export to CSV file |
| `--json` | Output as JSON |
| `--group-by` | Group by: `hour`, `day`, `week` |

## Session Tracking

Every visitor session captures: referrer source, landing page, UTM parameters (source, medium, campaign), geographic data, device type, browser, and OS.

Reading pattern classification:

| Pattern | Criteria |
|---------|----------|
| `bounce` | <10s on page AND <25% scroll |
| `skimmer` | Default fallback |
| `scanner` | >30% scroll AND <20s |
| `reader` | >50% scroll AND >15s |
| `engaged` | >75% scroll AND >30s |

## Troubleshooting

- **Events not recording** - Check browser console for JS errors, verify API endpoint accessible
- **Bot traffic in reports** - Run `analytics traffic bots`, check bot flags
- **Missing UTM data** - Verify URL parameters are properly formatted
- **Inflated visitor counts** - Check for undetected bots in user-agent patterns
- **No data showing** - Check date range with `--since` flag
- **Permission denied** - Check profile with `admin session show`

## Database Views

| View | Purpose |
|------|---------|
| `v_top_referrer_sources` | Sessions by referrer |
| `v_utm_campaign_performance` | UTM parameter analysis |
| `v_traffic_source_quality` | Quality scoring by source |
| `v_bot_traffic_summary` | Bot activity by date |
| `v_clean_human_traffic` | Filtered human-only data |

## Quick Reference

| Task | Command |
|------|---------|
| Overview | `analytics overview` |
| Traffic sources | `analytics traffic sources` |
| Bot traffic | `analytics traffic bots` |
| Session stats | `analytics sessions stats` |
| Top content | `analytics content top` |
| Cost summary | `analytics costs summary` |
| Agent stats | `analytics agents stats` |
| Tool usage | `analytics tools stats` |
| Export data | `analytics overview --export file.csv` |
| AI usage | `analytics ai --period day` |
