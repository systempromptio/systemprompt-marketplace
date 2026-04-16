---
name: email-composer
description: "Draft and send CRM emails via the Resend API. Loads templates from reports/crm/templates/, personalises with lead context, presents draft for MANDATORY human approval, then sends via curl. Every email requires Ed's explicit approval before sending — no exceptions."
metadata:
  version: "0.2.0"
---

# Email Composer

Drafts and sends emails to CRM leads via the **Resend API**. Every email is personalised based on the lead's profile, stage, and interaction history.

## CRITICAL: Every Email Requires Human Approval

**No email is ever sent automatically.** The workflow is always:

1. Skill composes a draft
2. Draft is presented to Ed in full
3. Ed reviews and replies `send`, `edit: {instructions}`, or `skip`
4. Only on explicit `send` does the skill call the Resend API

This is non-negotiable. There is no batch-send, no auto-send, no scheduled send. Every single email goes through Ed's eyes first.

## Dependencies

Load in order:
1. `crm-identity` — email rules, pipeline stages, forbidden patterns
2. `content-publishing:brand-voice` — tone and style enforcement

## Email Infrastructure

### Provider: Resend

Emails are sent via the [Resend](https://resend.com) API using a simple `curl` call from the local machine.

### Credentials Location

The Resend API key and SMTP config are stored in the **production profile secrets**:

```
/var/www/html/systemprompt-web/.systemprompt/profiles/systemprompt-prod/secrets.json
```

Relevant keys:

| Key | Value | Purpose |
|---|---|---|
| `resend_api_key` | `re_Cc87TvR...` | API authentication |
| `smtp_from` | `systemprompt.io <hello@systemprompt.io>` | Sender address |
| `smtp_host` | `smtp.resend.com` | SMTP relay (used by the Rust binary, not this skill) |
| `smtp_port` | `587` | SMTP port (used by the Rust binary, not this skill) |
| `smtp_username` | `resend` | SMTP username (used by the Rust binary, not this skill) |

**This skill uses the Resend HTTP API directly (not SMTP).** The SMTP path is used by the Rust email extension for transactional system emails (verification, magic links). CRM outreach uses the API.

### Reading the API Key

```bash
# Extract the API key from the prod profile secrets
RESEND_API_KEY=$(python3 -c "import json; d=json.load(open('/var/www/html/systemprompt-web/.systemprompt/profiles/systemprompt-prod/secrets.json')); print(d['resend_api_key'])")
```

### Sending an Email via Resend API

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H "Authorization: Bearer ${RESEND_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "systemprompt.io <hello@systemprompt.io>",
    "to": ["recipient@example.com"],
    "subject": "Email subject here",
    "text": "Plain text body here"
  }'
```

The response includes an `id` field — log this as the `resend_email_id` in `email-log.jsonl`.

**Optional HTML body:** Add `"html": "<p>HTML body</p>"` to send rich email. For CRM outreach, plain text is preferred (more personal, less likely to be flagged as marketing).

## Email Templates

Templates are stored in `/var/www/html/systemprompt-web/reports/crm/templates/`:

| Template | Use When |
|---|---|
| `outreach-initial.md` | First contact after clone + feedback |
| `outreach-followup.md` | 3+ days since initial outreach, no reply |
| `demo-booked.md` | Demo or call confirmed |
| `nurture-value.md` | Lead not ready for call, share value content |
| `onboarding-welcome.md` | Lead converted to customer |

Read the appropriate template, then personalise it based on the lead's data.

## Composing an Email

### Input

The skill expects one of:
- A lead identifier (L-### ID, email, or GitHub username) + template name
- A lead identifier + free-form context for a custom email

### Process

1. **Load the lead** — read `/var/www/html/systemprompt-web/reports/crm/data/leads.json` and find the lead
2. **Load interaction history** — read `data/interactions.jsonl` filtered for this lead
3. **Load email history** — read `data/email-log.jsonl` filtered for this lead
4. **Check email rules** (from `crm-identity`):
   - Has this lead been emailed in the last 3 days? If yes, reject unless it's a reply to their message
   - Has this template been used for this lead before? If yes, use a different template or compose custom
   - Is the lead in a terminal stage (converted/lost)? If converted, only onboarding templates. If lost, reject.
5. **Load template** — read the specified template from `reports/crm/templates/`
6. **Personalise** — replace all variables:
   - `{name}` — from lead record
   - `{company}` — from lead record
   - `{feedback_summary}` — from most recent feedback interaction
   - `{specific_pain_point}` — inferred from their feedback/issues
   - `{guide_url}` / `{guide_title}` — select a relevant guide based on their interests
   - `{last_interaction}` — date and type of last contact
   - Any other template-specific variables
7. **Apply brand voice** — ensure the email follows `content-publishing:brand-voice` guidelines
8. **Present draft to Ed for approval** — see format below

### Draft Review Format (MANDATORY — always show this)

```markdown
## Email Draft

**To:** {email}
**From:** systemprompt.io <hello@systemprompt.io>
**Subject:** {subject}
**Template:** {template_name} (or "custom")
**Lead:** {name} (L-###, score: {score}, stage: {stage})
**Last contact:** {date} ({type})

---

{full email body — exactly what will be sent}

---

**Reply with one of:**
- `send` — approve and send this email now via Resend API
- `edit: {your instructions}` — revise the draft
- `skip` — discard, do not send
```

**STOP HERE AND WAIT.** Do not proceed until Ed replies. Do not assume approval. Do not send without the word `send`.

## Sending (after explicit approval only)

When Ed replies `send`:

### Step 1: Read the API key

```bash
RESEND_API_KEY=$(python3 -c "import json; d=json.load(open('/var/www/html/systemprompt-web/.systemprompt/profiles/systemprompt-prod/secrets.json')); print(d['resend_api_key'])")
```

### Step 2: Send via Resend API

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H "Authorization: Bearer ${RESEND_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "systemprompt.io <hello@systemprompt.io>",
    "to": ["{lead_email}"],
    "subject": "{subject}",
    "text": "{plain_text_body}"
  }'
```

### Step 3: Log to email-log.jsonl

Append to `/var/www/html/systemprompt-web/reports/crm/data/email-log.jsonl`:

```json
{
  "timestamp": "{ISO timestamp}",
  "lead_id": "{L-###}",
  "to": "{email}",
  "from": "hello@systemprompt.io",
  "subject": "{subject}",
  "template": "{template_name}",
  "status": "sent",
  "resend_email_id": "{id from Resend API response}",
  "approved_by": "ed",
  "logged_by": "email-composer"
}
```

### Step 4: Log interaction

Append to `/var/www/html/systemprompt-web/reports/crm/data/interactions.jsonl`:

```json
{
  "timestamp": "{ISO timestamp}",
  "lead_id": "{L-###}",
  "deal_id": "{D-### if applicable}",
  "type": "email_sent",
  "direction": "outbound",
  "subject": "{subject}",
  "summary": "{one-line summary of email content}",
  "channel": "resend",
  "logged_by": "email-composer"
}
```

### Step 5: Confirm

```
Email sent to {name} ({email}).
Subject: {subject}
Resend ID: {resend_email_id}
Logged as interaction for {L-###}.
```

## Batch Drafting

When `daily-crm-brief` generates multiple email actions:

1. Process each lead sequentially
2. Present **each draft individually** for review
3. Ed must approve/edit/skip **each one separately**
4. Never batch-approve — every email gets its own `send` confirmation
5. Log all approved sends after each individual approval

## Rules (from crm-identity)

1. **EVERY email requires Ed's explicit `send` approval** — no exceptions, no automation
2. **Max frequency:** 1 email per lead per 3 days (unless replying to their message)
3. **Follow-up limit:** Max 1 follow-up after initial outreach
4. **Nurture frequency:** Max 1 email per 2 weeks
5. **Tone:** Technical peer, not salesperson
6. **Mandatory CTA:** Exactly one clear next step per email
7. **Never say:** "just checking in", "bumping this", "demo" (say "walkthrough")
8. **Never mention pricing** except in negotiating stage
9. **Never send same template twice** to same lead
10. **Never CC multiple leads**
11. **Always log** every email to both `email-log.jsonl` and `interactions.jsonl`

## Error Handling

- If the Resend API returns an error, show the full error to Ed and do not retry automatically
- If the API key is missing from `secrets.json`, stop and tell Ed to configure it
- If the lead has no email address, suggest Ed find it via GitHub profile or LinkedIn and update `leads.json` first
- If the lead is in the exclusion list, refuse to compose (they are not a real lead)
- If the template references variables that can't be filled, flag them with `[FILL: description]` for Ed to complete manually
