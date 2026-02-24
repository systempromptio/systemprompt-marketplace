---
name: scheduler-management
description: "Configure and manage scheduled jobs in systemprompt.io - cron expressions, job monitoring, manual execution, and failure handling"
---

# Scheduler Management

Job scheduling and automation. Config: `services/scheduler/config.yaml`

## Configure Jobs

Edit `services/scheduler/config.yaml`:

```yaml
scheduler:
  enabled: true
  timezone: "UTC"
  jobs:
    - name: publish_pipeline
      schedule: "0 */6 * * *"
      enabled: true
      description: "Publish content changes"
      timeout_seconds: 300
    - name: cleanup_sessions
      schedule: "0 0 * * *"
      enabled: true
      description: "Clean up expired sessions"
      timeout_seconds: 60
    - name: cleanup_anonymous_users
      schedule: "0 2 * * *"
      enabled: true
      description: "Remove anonymous users older than 30 days"
      timeout_seconds: 120
    - name: database_cleanup
      schedule: "0 3 * * 0"
      enabled: true
      description: "Database maintenance"
      timeout_seconds: 600
    - name: analytics_aggregate
      schedule: "0 */1 * * *"
      enabled: true
      description: "Aggregate analytics data"
      timeout_seconds: 120
```

## Cron Format

```
minute (0-59) | hour (0-23) | day of month (1-31) | month (1-12) | day of week (0-6, Sunday=0)
```

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `0 */6 * * *` | Every 6 hours |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |
| `*/5 * * * *` | Every 5 minutes |
| `*/15 * * * *` | Every 15 minutes |
| `0 */4 * * *` | Every 4 hours |
| `0 3 * * *` | Daily at 3 AM |

## Monitor Jobs

```bash
systemprompt infra jobs list
systemprompt infra jobs status <job_name>
systemprompt infra jobs history <job_name>
systemprompt infra logs --context scheduler --limit 50
```

## Run Manually

```bash
systemprompt infra jobs run <job_name>
systemprompt infra jobs run <job_name> --verbose
```

## Create Custom Job

Add to `services/scheduler/config.yaml`:

```yaml
jobs:
  - name: custom_sync
    schedule: "0 */2 * * *"
    enabled: true
    description: "Custom sync operation"
    timeout_seconds: 180
    config:
      source: "external_api"
      batch_size: 100
```

Then verify: `systemprompt infra jobs list`

## Enable/Disable Jobs

Set `enabled: true` or `enabled: false` in the job config, then verify with `systemprompt infra jobs list`.

## Built-in Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| `publish_pipeline` | `0 */6 * * *` | Publish content changes |
| `cleanup_sessions` | `0 0 * * *` | Clean up expired sessions |
| `cleanup_anonymous_users` | `0 2 * * *` | Remove anonymous users older than 30 days |
| `database_cleanup` | `0 3 * * 0` | Weekly database maintenance |
| `analytics_aggregate` | `0 */1 * * *` | Aggregate analytics data |

## Job Configuration Reference

```yaml
jobs:
  - name: job_name
    schedule: "0 * * * *"
    enabled: true
    description: "Description"
    timeout_seconds: 300
    config:
      key: value
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier |
| `schedule` | Yes | Cron expression |
| `enabled` | Yes | Active state |
| `description` | No | What job does |
| `timeout_seconds` | No | Max execution time |
| `config` | No | Job-specific settings |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Job not running | `systemprompt infra jobs list`, check `enabled: true` |
| Job fails | `systemprompt infra logs --context scheduler --level error` |
| Job times out | Increase `timeout_seconds` in config |
| Job history | `systemprompt infra jobs history <job_name>` |

## Quick Reference

| Task | Command |
|------|---------|
| List jobs | `systemprompt infra jobs list` |
| Job status | `systemprompt infra jobs status <name>` |
| Run job | `systemprompt infra jobs run <name>` |
| Job history | `systemprompt infra jobs history <name>` |
| Scheduler logs | `systemprompt infra logs --context scheduler` |
| Error logs | `systemprompt infra logs --context scheduler --level error` |
