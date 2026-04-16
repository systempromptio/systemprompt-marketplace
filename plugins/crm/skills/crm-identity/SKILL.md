---
name: crm-identity
description: "CRM identity and definitions for systemprompt.io. Defines pipeline stages, lead scoring rubric, email rules, and integration with marketing. Load FIRST before any other crm skill."
metadata:
  version: "0.1.0"
---

# CRM Identity

Single source of truth for **pipeline definitions, lead scoring, and engagement rules**. Every skill in the `crm` plugin loads this first. This skill complements `commons:marketing-identity` (distribution and lead-gen) with the mid-funnel pipeline management layer.

## Upstream Sources of Truth (read before any CRM work)

Load these once per session in order:

1. `commons:marketing-identity` — ICP, template hook, hypothesis format
2. `commons:identity` — brand positioning, voice, banned words
3. `commons:brand-voice` — tone and style for all written communication
4. `/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md` — current CRM strategy state (read-only here)
5. `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — marketing funnel context (read-only)

If any file is missing, stop and tell Ed.

## The Lead Definition (inherited from marketing)

A **lead** = someone who clones `systempromptio/systemprompt-template`, runs it, and gives feedback (any channel: GitHub issue labelled `feedback`, email to `hello@systemprompt.io`, DM reply, form submission).

Activation requires **all three**: clone + run + feedback. Clones alone are not leads — they are prospects. Feedback without a run is not a lead.

## Pipeline Stages

| Stage | Definition | Entry Criteria | Exit Criteria |
|---|---|---|---|
| `prospect` | Identified but not yet contacted | GitHub clone detected, or manual entry | First outreach sent |
| `contacted` | First outreach sent, awaiting response | Email/DM sent | Reply received or 14d timeout |
| `demo_scheduled` | Demo or call booked | Calendar link confirmed | Demo completed |
| `evaluating` | Actively evaluating — trial/sandbox running | Demo done + sandbox access provided | Decision communicated |
| `negotiating` | Terms/pricing discussion | Verbal interest in purchase | Contract signed or deal lost |
| `converted` | Customer — handover complete | Contract/payment confirmed | N/A (terminal) |
| `lost` | Did not convert | Explicit rejection or 30d+ no response after evaluating | N/A (terminal) |

**Stage progression rules:**
- Stages are sequential — never skip a stage (except `prospect` → `contacted` can happen same day)
- Lost leads can be re-activated to `contacted` if they re-engage
- Every stage change must create an interaction record in `data/interactions.jsonl`
- Every stage change must update `stage_changed_at` in `data/leads.json`

## Lead Scoring Rubric

Scores are additive. A lead's total score = sum of all matching signals.

| Signal | Points | Source | Notes |
|---|---:|---|---|
| GitHub clone (template) | 10 | GitHub Traffic API | Base signal — everyone starts here |
| GitHub clone (core) | 5 | GitHub Traffic API | Lower intent than template |
| Feedback given | 25 | GitHub issue with `feedback` label, email, DM | The activation event |
| Demo requested | 30 | Demo form, direct ask | Highest-intent inbound signal |
| Email reply | 20 | Email log / Ed reports manually | Active engagement |
| Website return visit (3+ sessions) | 5 | systemprompt analytics | Passive but shows ongoing interest |
| Read 3+ guides | 15 | systemprompt analytics | Research behaviour |
| Company fits ICP2 (50-500 emp, using Claude) | 20 | Manual enrichment / LinkedIn | Best-fit signal |
| Star on GitHub repo | 3 | GitHub API | Weak signal but non-zero |
| Multiple feedback interactions | 10 | Interaction count ≥ 3 | Repeated engagement |

**Score thresholds:**
- 0-15: Low priority (passive prospect)
- 16-40: Medium priority (active prospect, worth outreach)
- 41-70: High priority (engaged lead, prioritise follow-up)
- 71+: Hot lead (high fit + high engagement, daily attention)

## Lead Source Categories

| Source | Description | How Detected |
|---|---|---|
| `github_clone` | Cloned systemprompt-template or systemprompt-core | GitHub Traffic API |
| `demo_request` | Submitted demo request form | Website form / email |
| `website` | Visited website, read guides, engaged with content | systemprompt analytics |
| `inbound_email` | Sent email to hello@systemprompt.io | Ed reports manually |
| `referral` | Referred by another person or company | Manual entry |
| `outreach` | Ed initiated contact (cold or warm) | Manual entry |
| `conference` | Met at conference or event | Manual entry |

## Email Rules

1. **Max frequency:** 1 email per lead per 3 days (unless they reply — then respond immediately)
2. **Follow-up limit:** Max 1 follow-up after initial outreach. If no reply, move to nurture sequence.
3. **Nurture frequency:** Max 1 email per 2 weeks per lead
4. **Tone:** Technical peer, not salesperson. Reference their specific use case. Use `commons:brand-voice`.
5. **Mandatory CTA:** Every email must have exactly one clear next step
6. **Forbidden patterns:**
   - Never say "just checking in" or "bumping this"
   - Never use "demo" — say "walkthrough" or "quick call"
   - Never mention pricing in outreach (only in negotiating stage)
   - Never send the same template to the same lead twice
   - Never CC multiple leads in one email
7. **Template location:** `/var/www/html/systemprompt-web/reports/crm/templates/`
8. **Logging:** Every email (sent or drafted) must be logged to `data/email-log.jsonl` AND create an interaction in `data/interactions.jsonl`

## Hypothesis Format (mandatory for every CRM action)

Uses `C-###` IDs (distinct from `H-###` marketing and `S-###` SEO):

```
[C-###] If we {verb + specific action} for {lead/segment},
        then {metric} will {direction} by {target} within {window} days.
        Reason: {insight or prior evidence}.
```

Example:

```
[C-001] If we send a personalised walkthrough email to the 3 leads who gave
        feedback this week, then leads_qualified_7d will increase from 0 to >= 1
        within 14 days.
        Reason: feedback givers have highest intent — direct engagement should convert.
```

## State Files

All CRM state lives in `/var/www/html/systemprompt-web/reports/crm/`:

| File | Purpose | Update Pattern |
|---|---|---|
| `data/leads.json` | Canonical lead database | Updated in-place by `pipeline-tracker` |
| `data/deals.json` | Active deals and pipeline | Updated in-place by `pipeline-tracker` |
| `data/pipeline-history.jsonl` | Daily pipeline snapshots | Append-only, one line per run |
| `data/interactions.jsonl` | All lead interactions | Append-only event log |
| `data/email-log.jsonl` | Emails sent/drafted | Append-only |
| `data/hypothesis-ledger.md` | CRM hypothesis log | Append-only table |
| `data/actions/C-###.md` | Hypothesis detail files | Write-once |
| `crm-strategy-master.md` | Living strategy doc | Append-only changelog |
| `templates/*.md` | Email templates | Edited as needed |
| `YYYY-MM-DD/*.md` | Daily reports | Generated fresh each day |

## Exclusions

These GitHub users are excluded from lead counts (self-activity and automation):

- `Ejb503` (Ed — the owner)
- `dependabot[bot]`
- `github-actions[bot]`

If a cloner matches an exclusion, they are marked `is_excluded: true` in `leads.json` and not counted in pipeline metrics.
