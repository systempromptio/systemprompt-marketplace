---
name: lead-enrichment
description: "Enrich a lead's profile with GitHub data, website analytics, interaction history, and ICP fit scoring. Updates the lead record in leads.json. Use when a new lead enters the pipeline or when preparing for outreach."
metadata:
  version: "0.1.0"
---

# Lead Enrichment

Takes a lead identifier (email, GitHub username, or L-### ID) and enriches their profile with all available data. Updates the lead record in `data/leads.json` with enriched metadata and a recalculated score.

## Dependencies

Load `crm-identity` first (for scoring rubric and ICP definitions).

## When to Use

- When a new lead is added to `data/leads.json` (triggered by `pipeline-tracker`)
- When preparing for outreach to a specific lead (triggered by `daily-crm-brief`)
- When Ed asks to "look up" or "research" a lead
- When a lead's stage changes and we need updated context

## Data Sources

### 1. GitHub Profile (if `github_username` is set)

```bash
gh api users/{github_username}
```

Extract:
- `name` — full name
- `company` — employer
- `bio` — role/interests
- `location` — geography
- `public_repos` — activity level
- `followers` — influence level
- `created_at` — account age

Also check their recent activity:
```bash
gh api users/{github_username}/events --jq '.[0:10]'
```

Look for: systemprompt-related activity, MCP/Claude repos starred, AI-related repos.

### 2. GitHub Repo Interactions

Check if they have issues, PRs, or discussions on systemprompt repos:

```bash
gh api search/issues --jq '.items[] | {title, html_url, state, created_at}' -f q="repo:systempromptio/systemprompt-template author:{github_username}"
gh api search/issues --jq '.items[] | {title, html_url, state, created_at}' -f q="repo:systempromptio/systemprompt-core author:{github_username}"
```

### 3. Website Analytics (if we can match)

```bash
# Check if their referrer or session matches (requires systemprompt-prod profile)
systemprompt analytics sessions list --limit 20 --since 30d
```

Look for sessions matching their known identifiers (email domain, company domain, geographic location).

### 4. Interaction History

Read `/var/www/html/systemprompt-web/reports/crm/data/interactions.jsonl` and filter for this lead's `lead_id`. Summarise:
- Total interactions
- Last interaction date
- Interaction types (email, github, call, etc.)
- Direction balance (inbound vs outbound)

### 5. Marketing Funnel Data

Read `/var/www/html/systemprompt-web/reports/marketing/data/funnel-history.jsonl` for aggregate context. This doesn't identify individual leads, but provides the baseline metrics for scoring.

### 6. Email History (if email is known)

Read `/var/www/html/systemprompt-web/reports/crm/data/email-log.jsonl` and filter for this lead's email address. Summarise:
- Emails sent (dates, subjects, templates used)
- Any replies noted in `interactions.jsonl`
- Last email date and direction

## Enrichment Process

1. **Identify the lead** — look up in `data/leads.json` by email, github_username, or L-### ID
2. **Pull GitHub data** — if github_username is set, fetch profile and activity
3. **Check for interactions** — search interactions.jsonl, GitHub issues, email-log.jsonl
4. **Score against ICP2** — use the rubric from `crm-identity`:
   - Company size 50-500? (+20 if yes)
   - Using Claude Code? (+20 if evidence found)
   - Technical decision-maker? (+10 if title matches)
   - In target geography? (+5 if US/UK/EU)
5. **Recalculate total score** — sum all signals from scoring rubric
6. **Update leads.json** — write enriched fields, updated score, score_breakdown, and `updated_at`
7. **Report** — print a summary of what was found and the new score

## Output Format

Print a summary like:

```markdown
## Lead Enrichment: {name} ({github_username})

**Score:** {old_score} → {new_score} ({delta})
**Stage:** {stage}
**Company:** {company} ({employee_estimate} employees)
**Role:** {role/title from bio}
**ICP Fit:** {High/Medium/Low} — {reason}

### New Information Found
- {bullet list of new data points}

### Interaction Summary
- Total interactions: {N}
- Last contact: {date} ({type})
- Direction: {N} inbound / {M} outbound

### Recommended Next Action
{One specific action based on their stage and score}
```

## Rules

- Never fabricate data — if a field can't be determined, leave it null
- Always attribute the data source (e.g. "company from GitHub profile")
- If LinkedIn research is needed (company size, role), suggest the search URL for Ed to check manually — do not scrape LinkedIn
- Update `updated_at` timestamp on every enrichment
- Log the enrichment as an interaction of type `enrichment` in `data/interactions.jsonl`
