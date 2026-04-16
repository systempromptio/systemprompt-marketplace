---
name: crm-guide
description: "Entry point for CRM — routes to pipeline tracking, lead management, and outreach"
metadata:
  version: "1.1.0"
  git_hash: "3a55706"
---

# CRM Guide

Pipeline management, lead tracking, and outreach skills for systemprompt.io.

## Dependencies

Load `commons:identity` and `commons:marketing-identity` before using CRM skills. Load `crm-identity` for pipeline definitions and lead scoring.

## Patterns Implemented

This plugin implements three `commons` patterns:
- `commons:hypothesis-ledger-pattern` → `crm-hypothesis-ledger` (C-### prefix, 14-day window)
- `commons:strategy-master-pattern` → `crm-strategy-master` (pipeline health, deal velocity north star)
- `commons:daily-brief-pattern` → `daily-crm-brief` (8-step orchestration, 15-minute target)

## Skills

### Strategy and Measurement

| Task | Skill | Frequency |
|------|-------|-----------|
| Pipeline definitions and lead scoring | `crm-identity` | Load first |
| Morning CRM briefing | `daily-crm-brief` | Daily /loop |
| Track CRM actions (C-###) | `crm-hypothesis-ledger` | On every action |
| Living CRM strategy doc | `crm-strategy-master` | On reviews |
| Daily data collection and pipeline state | `pipeline-tracker` | Daily |

### Lead Operations

| Task | Skill | Frequency |
|------|-------|-----------|
| Enrich leads with GitHub/web data | `lead-enrichment` | On new leads |
| Draft and send emails via Resend API | `email-composer` | On outreach |

## Report Directory

All CRM reports live at: `/var/www/html/systemprompt-web/reports/crm/`
