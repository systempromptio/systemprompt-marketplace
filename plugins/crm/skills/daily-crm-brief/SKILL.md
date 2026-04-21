---
name: daily-crm-brief
description: "The morning CRM briefing. Orchestrates pipeline-tracker + hypothesis-ledger into a single actionable brief: pipeline snapshot, hot leads, overdue follow-ups, email drafts to review, and all effective copy-paste-ready actions for Ed (minimum 3, no cap) — each tagged with a new [C-###] hypothesis. Load crm-identity first."
metadata:
  version: "0.3.1"
  git_hash: "9b8a605"
---

# Daily CRM Brief

> **Implements:** `commons:daily-brief-pattern` — 8-step orchestration sequence, unlimited hypothesis- and data-driven actions (minimum 3, no cap), no action without hypothesis, score maturing before generating new. This skill configures the pattern for the CRM domain (C-### hypotheses, pipeline metric whitelist, 15-minute target).

The only CRM skill Ed reads every morning. Everything else in this plugin feeds it. Target: Ed reads and acts in 15 minutes.

## Dependencies (load in order)

1. `crm-identity` — pipeline stages, scoring rubric, email rules, hypothesis format
2. `commons:brand-voice` — every draft passes through this
3. `crm-hypothesis-ledger` — in-flight hypotheses and next `C-###` allocation
4. `pipeline-tracker` — pipeline data (this skill triggers a fresh run unless one already exists for today)
5. `crm-strategy-master.md` — current objectives, active hypotheses, strategy context

## CRITICAL: Profile must be `systemprompt-prod`

Before doing anything, verify `systemprompt admin session list` shows `systemprompt-prod` as the active profile. This skill calls `systemprompt analytics` directly in places. If the active profile is `local`, switch before proceeding:

```bash
systemprompt admin session switch systemprompt-prod
```

Every brief written by this skill must carry a `Profile: systemprompt-prod` line at the top.

## Run Sequence

### 1. Check Today's Pipeline-Tracker Report

Path: `/var/www/html/systemprompt-web/reports/crm/daily/{today}/pipeline-tracker.md`

If missing, invoke `pipeline-tracker` via the Skill tool. If it fails, degrade gracefully: write the brief with what CRM state is available, put the failure in the Headline and System Health, and generate whichever actions don't depend on fresh pipeline data (e.g., follow-ups based on existing leads.json). Do not halt. Do not ask the user — the master-brief orchestrator depends on this skill returning.

### 2. Read CRM State

**leads.json WARNING:** This file exceeds 256KB and cannot be read with the Read tool. Always use Python/Bash to query it:

```bash
# Count by stage
python3 -c "
import json
data = json.load(open('/var/www/html/systemprompt-web/reports/crm/data/leads.json'))
from collections import Counter
counts = Counter(l.get('stage','?') for l in data['leads'])
print(dict(counts))
"

# Find top leads by score
python3 -c "
import json
data = json.load(open('/var/www/html/systemprompt-web/reports/crm/data/leads.json'))
top = sorted([l for l in data['leads'] if l.get('stage') not in ('converted','lost','opted_out')], key=lambda x: x.get('score',0) or 0, reverse=True)[:10]
for l in top: print(l.get('id'), l.get('name'), l.get('score'), l.get('stage'), l.get('email'))
"
```

Read all of these (using the correct method per file size):
- `leads.json` — **use Python** (file > 256KB, Read tool will fail)
- `/var/www/html/systemprompt-web/reports/crm/data/deals.json` — Read tool OK
- `/var/www/html/systemprompt-web/reports/crm/data/pipeline-history.jsonl` — Read tool OK
- `/var/www/html/systemprompt-web/reports/crm/data/interactions.jsonl` — Read tool OK (tail last 20 if large)
- `/var/www/html/systemprompt-web/reports/crm/data/email-log.jsonl` — Read tool OK
- `/var/www/html/systemprompt-web/reports/crm/data/hypothesis-ledger.md` — Read tool OK

### 3. Read Strategy Context

Read `/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md` for current phase, objectives, and active hypotheses.

Also read `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` for top-of-funnel context.

### 4. Score Maturing Hypotheses

For each hypothesis in the ledger where `window_end <= today` and status is `SEEDED` or `IN-FLIGHT`:
1. Read the current value of the `metric` from the latest `pipeline-history.jsonl` entry
2. Compare to baseline + target from the hypothesis
3. Score as `PASS`, `FAIL`, or `INCONCLUSIVE`
4. Call `crm-hypothesis-ledger score {id} {result} {status} {note}`

### 5. Identify Hot Leads

From `data/leads.json`, identify:
- **Highest score leads** — top 5 by score, not in terminal stages
- **Recent activity** — leads with interactions in last 48h
- **Overdue follow-ups** — leads in `contacted` stage with no interaction in 3+ days
- **Stale deals** — deals with no activity in 7+ days
- **New leads** — added in last 24h

### 6. Check Email Queue

From `data/email-log.jsonl`, identify:
- Drafts awaiting review (status `draft_created`)
- Emails sent in last 24h (status `sent`)
- Failed sends (status `failed`)

### 7. Generate Actions

No arbitrary maximum — emit every action that is hypothesis- and data-driven. Minimum 3 when leads/deals have any signal (overdue follow-ups, hot leads, stale deals, new leads); otherwise at least 1 maintenance or sourcing action. Priority order:

1. **Overdue follow-ups:** Leads awaiting response for 3+ days. Draft a follow-up email using `email-composer` or the appropriate template.
2. **Hot lead engagement:** Highest-score leads not yet contacted. Draft initial outreach.
3. **Stale deal re-engagement:** Deals with no activity in 7+ days. Suggest a re-engagement touch.
4. **New lead triage:** New leads from today's pipeline-tracker that need enrichment or initial outreach.
5. **Pipeline progression:** Leads ready to move to next stage (e.g., demo to be scheduled, proposal to be sent).

### How emails actually get sent (non-negotiable)

**Resend API key is send-only.** It can POST to `/emails` but cannot GET delivery stats, list sent emails, or check bounce rates. Do NOT generate a "check Resend delivery stats" hypothesis or action — it cannot be executed or scored with this key. If delivery health is needed, Ed checks the Resend dashboard manually at resend.com.

**Two send paths:**

**A. Single email (via email-composer):** For individual targeted emails (enterprise follow-ups, direct outreach). Goes through `crm:email-composer`, which:
1. Loads the Resend API key from `/var/www/html/systemprompt-web/.systemprompt/profiles/systemprompt-prod/secrets.json` (`resend_api_key`)
2. Presents the draft to Ed for explicit approval (Ed replies `send` / `edit: ...` / `skip`)
3. On `send`, POSTs to `https://api.resend.com/emails`
4. Logs the Resend `id` into `email-log.jsonl` AND appends an interaction to `interactions.jsonl`

**B. Batch send (20 emails via orchestrator script):** For cold-email batches from pre-generated draft directories. Use this Python + curl orchestrator (Python urllib is blocked by Cloudflare 1010 — must shell out to curl):

```python
import os, re, subprocess, json, time

RESEND_API_KEY = # read from secrets.json
draft_dir = "/var/www/html/systemprompt-web/reports/crm/drafts/batch-{DATE}/"
files = sorted([f for f in os.listdir(draft_dir) if f.endswith('.md') and f != 'README.md'])

for i, fname in enumerate(files, 1):
    with open(os.path.join(draft_dir, fname)) as f:
        content = f.read()
    
    to_email = re.search(r'\*\*To:\*\* (.+)', content).group(1).strip()
    lead_id  = re.search(r'\*\*Lead:\*\* (L-\d+)', content).group(1).strip()
    subject  = re.search(r'\*\*Subject:\*\* (.+)', content).group(1).strip()
    
    # Body: everything after the Subject line
    subj_pos = content.find(f'**Subject:** {subject}')
    body = content[content.find('\n', subj_pos) + 1:].strip()
    
    payload = json.dumps({
        "from": "systemprompt.io <hello@systemprompt.io>",
        "to": [to_email],
        "subject": subject,
        "text": body
    })
    
    result = subprocess.run(
        ["curl", "-s", "-w", "\nHTTP:%{http_code}",
         "-X", "POST", "https://api.resend.com/emails",
         "-H", f"Authorization: Bearer {RESEND_API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    # Parse and log result...
    time.sleep(2)  # 2s between sends
```

After batch sends: append all 20 entries to `email-log.jsonl` + `interactions.jsonl`, update each lead's `stage` to `contacted` in leads.json, append a pipeline-history.jsonl snapshot, and add a `C-###-EXEC` row to the hypothesis ledger.

When this brief generates a batch-send action, the action body **must** include the full orchestrator script. Never invite Ed to send directly from Gmail. The Resend log is the only system of record for outbound; Gmail sends are invisible to the ledger.

**Drop rules:**
- Never two emails to the same lead on the same day
- Never draft an email to a lead who was emailed in the last 3 days (unless they replied)
- If pipeline is empty (0 active leads), focus actions entirely on sourcing: reference marketing-strategy brief for top-of-funnel actions
- If Ed marked an action as "skip" yesterday, do not re-suggest it today

### 8. Log New Hypotheses

For each action generated, call `crm-hypothesis-ledger log` to register it with a `C-###` ID. Each action must have a falsifiable hypothesis.

### 9. Write the Brief

Write to `/var/www/html/systemprompt-web/reports/crm/daily/{today}/daily-brief.md`:

```markdown
# CRM Daily Brief — {today}

**Profile:** systemprompt-prod
**Run at:** {timestamp}

## Yesterday's Scorecard

| Action | Hypothesis | Done? | Result |
|---|---|---|---|
| {action from yesterday's brief} | C-### | Yes/No | {outcome if known} |

## Pipeline Snapshot

| Stage | Count | Delta (1d) | Delta (7d) |
|---|---:|---:|---:|
| Prospect | {n} | {+/-} | {+/-} |
| Contacted | {n} | {+/-} | {+/-} |
| Demo Scheduled | {n} | {+/-} | {+/-} |
| Evaluating | {n} | {+/-} | {+/-} |
| Negotiating | {n} | {+/-} | {+/-} |
| Converted | {n} | {+/-} | {+/-} |
| Lost | {n} | {+/-} | {+/-} |

**Pipeline value:** ${n} ({+/-$n} vs 7d ago)
**Active deals:** {n}
**New leads (1d/7d):** {n}/{n}

## Hot Leads

| Lead | Score | Stage | Last Activity | Action Needed |
|---|---:|---|---|---|
| {name/company} | {score} | {stage} | {date} | {one-line action} |

## Stale Alerts

{List of overdue follow-ups and stale deals, if any}

## Email Queue

- Drafts pending review: {n}
- Sent (24h): {n}
- Failed: {n}

## Hypotheses Maturing Today

{Table of hypotheses being scored, with results}

## Today's Actions ({n})

### Action 1: {Channel} — {One-line summary}

**Hypothesis:** [C-###] If we {action} for {lead/segment},
  then {metric} will {direction} by {target} within {window} days.
  Reason: {insight}.

**Metric to watch:** `{metric_name}` (baseline: {n})
**Check back on:** {YYYY-MM-DD}
**Lead:** {name} ({L-### ID})

**Draft (copy-paste ready):**

> {the actual email / message / action text}

**After executing:** reply `done C-###` and I'll log it.

### Action 2: ...
(repeat for each action)
```

### 10. Update Strategy Master

Append a changelog entry to `/var/www/html/systemprompt-web/reports/crm/crm-strategy-master.md`:

```markdown
- **{today} ~{time}Z** `daily-crm-brief` — {one-line summary of pipeline state and actions generated}
```

Update the pipeline snapshot table in Section 1 if numbers changed significantly.

## Integration with Marketing Brief

This brief is complementary to `commons:daily-marketing-brief`. The marketing brief handles top-of-funnel (awareness, impressions, cloners). This brief handles mid-funnel (leads through conversion). Ed should read both each morning.

If the pipeline is empty, reference the marketing brief for sourcing actions rather than generating CRM-specific actions about leads that don't exist yet.

## Empty Pipeline Handling

When `data/leads.json` has zero active leads:

1. Do not generate follow-up or outreach actions (there's nobody to contact)
2. Instead, generate 2-3 sourcing actions:
   - "Review today's marketing brief for new cloners to investigate"
   - "Check GitHub feedback issues for untracked leads"
   - "Enter KnowBe4 and Walmart as leads with available context" (if not yet done)
3. Focus the brief on setup tasks: enriching known interested parties, testing email templates, establishing baseline metrics
