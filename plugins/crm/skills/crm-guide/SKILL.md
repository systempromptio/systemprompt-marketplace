---
name: crm-guide
description: "Entry point for CRM — routes to pipeline tracking, lead management, and outreach"
metadata:
  version: "1.0.0"
  git_hash: "5079c7a"
---

# CRM Guide

Pipeline management, lead tracking, and outreach skills for systemprompt.io.

## Dependencies

Load `commons:identity` and `marketing:marketing-identity` before using CRM skills. Load `crm-identity` for pipeline definitions and lead scoring.

## Skills

| Task | Skill | Frequency |
|------|-------|-----------|
| Pipeline definitions and lead scoring | `crm-identity` | Load first |
| Morning CRM briefing | `daily-crm-brief` | Daily /loop |
| Track CRM actions (C-###) | `crm-hypothesis-ledger` | On every action |
| Daily data collection and pipeline state | `pipeline-tracker` | Daily |
| Enrich leads with GitHub/web data | `lead-enrichment` | On new leads |
| Draft and send emails via Resend API | `email-composer` | On outreach |

## Report Directory

All CRM reports live at: `/var/www/html/systemprompt-web/reports/crm/`
