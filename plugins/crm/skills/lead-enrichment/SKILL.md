---
name: lead-enrichment
description: "World-class lead enrichment using 7 data sources: Gmail threads, GitHub profile, web search, company website, email domain analysis, internal CRM cross-reference, and website analytics. Builds a complete picture of who we're selling to."
metadata:
  version: "1.0.0"
---

# Lead Enrichment

Takes a lead identifier (email, GitHub username, or L-### ID) and enriches their profile using every available data source. Updates the lead record in `data/leads.json` with enriched metadata, recalculated score, and recommended next action.

## Dependencies

Load `crm-identity` first (for scoring rubric and ICP definitions).

## When to Use

- When a new lead is added to `data/leads.json`
- When preparing for outreach to a specific lead
- When Ed asks to "look up" or "research" a lead
- When a lead's stage changes and we need updated context
- Before drafting any email to a lead (always enrich first)

## Enrichment Sequence

Run these 7 steps in order. Each step may inform the next.

### Step 1: Identify & Load Lead

Look up the lead in `/var/www/html/systemprompt-web/reports/crm/data/leads.json` by email, `github_username`, or `L-###` ID. Record the current state before enrichment.

### Step 2: Email Domain Analysis

Extract the domain from the lead's email address. Classify it:

| Domain Type | Examples | Signal |
|-------------|---------|--------|
| **Corporate** | `@knowbe4.com`, `@dynapps.be` | High — identifies company directly |
| **Personal (tech)** | `@gmail.com`, `@proton.me` | Low — no company signal, check GitHub |
| **Academic** | `@academicos.udg.mx` | Medium — research institution |
| **Regional personal** | `@qq.com`, `@icloud.com` | Low — geographic signal only |

If corporate domain, the company domain is the enrichment anchor for Steps 5-6.

### Step 3: Gmail Thread Search

Search for all email history with this lead using Gmail MCP:

```
gmail_search_messages: "from:{email} OR to:{email}"
```

If threads are found, read the most recent 3 threads with `gmail_read_thread`. Extract:

- **Thread count** — total email conversations
- **Last email date** — most recent contact
- **Sentiment** — positive/neutral/negative based on last message tone
- **Key interests** — what did they ask about or respond to?
- **Objections** — any concerns or reasons for hesitation
- **Additional contacts** — anyone CC'd or mentioned (potential related leads)
- **Role/title** — often in email signatures

**Rules:**
- Read-only. Never send, draft, or modify emails in this step.
- Summarise conversation context — do not quote email content verbatim in CRM notes.
- If no threads found, set `email_context.sentiment` to `"no_contact"`.

### Step 4: GitHub Profile (if `github_username` is set)

```bash
gh api users/{github_username}
```

Extract: `name`, `company`, `bio`, `location`, `public_repos`, `followers`, `created_at`

Check recent activity:
```bash
gh api "users/{github_username}/events?per_page=10"
```

Look for:
- systemprompt-related activity (stars, forks, issues)
- MCP/Claude repos starred or forked
- AI/governance-related repos
- Recent commit frequency (active developer vs dormant)

Also check for interactions on systemprompt repos:
```bash
gh api search/issues -f q="repo:systempromptio/systemprompt-template author:{github_username}"
gh api search/issues -f q="repo:systempromptio/systemprompt-core author:{github_username}"
```

### Step 5: Web Research

Run up to 3 targeted web searches per lead. Only search if company is known or inferable.

**Search 1 — Person + Company:**
```
WebSearch: "{full_name} {company_name}"
```
Look for: LinkedIn profile URL, role confirmation, conference talks, blog posts, public GitHub presence.

**Search 2 — Company + AI/Tech:**
```
WebSearch: "{company_name} AI governance" OR "{company_name} Claude Code" OR "{company_name} MCP"
```
Look for: company's AI adoption, existing tools, public statements about AI strategy.

**Search 3 — Company profile (if needed):**
```
WebSearch: "{company_name} company size employees founded"
```
Look for: headcount, funding stage, founding year, industry vertical.

**Rules:**
- Never scrape LinkedIn. If a LinkedIn URL is found in search results, save the URL as `web_research.linkedin_url` for Ed to check manually.
- Attribute every data point to its source.
- If searches return nothing useful, note "no public presence found" and move on.

### Step 6: Company Website

If a corporate email domain was identified in Step 2, fetch the company homepage:

```
WebFetch: "https://{company_domain}"
```

Extract from the page content:
- **Company description** — what they do (one sentence)
- **Industry vertical** — e.g. "cybersecurity training", "food services", "ERP consulting"
- **Size signals** — team page, office locations, customer logos
- **Technology signals** — mentions of AI, Claude, MCP, automation, governance
- **Geographic presence** — headquarters, office locations

If the fetch fails or returns nothing useful, fall back to web search results from Step 5.

### Step 7: Internal Cross-Reference

Read the full `leads.json` and check:

1. **Same-company leads** — find other leads with matching `company` field or email domain. Record their IDs in `related_leads`.
2. **Shared tenants** — if lead has a `tenant_id`, find other leads on the same tenant.
3. **Interaction history** — read `interactions.jsonl` filtered by `lead_id`. Summarise total count, last date, types, direction balance.
4. **Email log** — read `email-log.jsonl` filtered by email. Note templates used, reply status.
5. **Deal association** — check `deals.json` for deals linked to this lead's ID or company.

## Enriched Data Schema

After enrichment, the lead's `enriched_data` field should contain:

```json
{
  "company_size": "100+|31-100|11-30|1-10|unknown",
  "role": "CTO|Senior Engineer|etc",
  "location": "city, country",
  "icp_fit": "high|medium|low|unknown",
  "tenant_id": "uuid or null",
  "tenant_active": true/false/null,
  "company_profile": {
    "domain": "company.com",
    "description": "One-sentence company description",
    "industry": "Industry vertical",
    "headcount_estimate": "~200 employees",
    "tech_signals": ["Claude Code user", "MCP adopter", "AI governance interest"]
  },
  "web_research": {
    "linkedin_url": "https://linkedin.com/in/... (suggested, not scraped)",
    "public_mentions": "Brief summary of public presence",
    "last_researched": "2026-04-16"
  },
  "email_context": {
    "thread_count": 3,
    "last_email_date": "2026-04-02",
    "sentiment": "positive|neutral|negative|no_contact",
    "key_interests": ["governance", "white-label", "MCP security"],
    "objections": ["maturity concerns", "integration requirements"]
  },
  "related_leads": ["L-004", "L-005"],
  "enrichment_sources": ["gmail", "github", "websearch", "webfetch", "internal"],
  "enrichment_confidence": "high|medium|low",
  "last_enriched": "2026-04-16T12:00:00+00:00"
}
```

## Scoring After Enrichment

Recalculate the lead's total score using all enrichment signals plus the rubric from `crm-identity`:

| Signal | Points | Source |
|--------|-------:|--------|
| GitHub clone (template) | 10 | GitHub Traffic API |
| GitHub clone (core) | 5 | GitHub Traffic API |
| Feedback given | 25 | GitHub issue, email, DM |
| Demo requested | 30 | Demo form, direct ask |
| Email reply | 20 | Email log / Gmail threads |
| Website return visit (3+ sessions) | 5 | systemprompt analytics |
| Read 3+ guides | 15 | systemprompt analytics |
| Company fits ICP2 (50-500 emp, using Claude) | 20 | Enrichment Steps 5-6 |
| Star on GitHub repo | 3 | GitHub API |
| Multiple feedback interactions | 10 | Interaction count >= 3 |
| **Active tenant deployed** | 25 | Internal cross-ref |
| **Multiple users from same company** | 10 | Internal cross-ref |
| **Corporate email (vs personal)** | 5 | Email domain analysis |
| **Positive email sentiment** | 10 | Gmail thread analysis |
| **Technical decision-maker role** | 10 | Gmail sig / GitHub bio / web search |

## Output Format

Print a summary after enrichment:

```markdown
## Lead Enrichment: {name} ({email})

**Score:** {old_score} → {new_score} ({+delta})
**Stage:** {stage}
**Company:** {company} — {company_description}
**Role:** {role/title}
**Industry:** {industry_vertical}
**Location:** {location}
**ICP Fit:** {High/Medium/Low} — {one-line reason}

### Data Sources Used
{list of sources that returned data: gmail, github, websearch, webfetch, internal}

### Key Findings
- {bullet list of new or updated data points, each attributed to source}

### Email Context
- Threads: {N} | Last contact: {date} | Sentiment: {sentiment}
- Interests: {comma-separated list}
- Objections: {comma-separated list or "none identified"}

### Related Leads
- {L-### name (company) — relationship}

### Interaction Summary
- Total: {N} | Last: {date} ({type})
- Direction: {N} inbound / {M} outbound

### Recommended Next Action
{One specific, actionable recommendation based on stage, score, sentiment, and recency}
```

## Rules

1. **Never fabricate data** — if a field can't be determined, leave it null
2. **Always attribute the data source** — e.g. "CTO (from Gmail email signature)" or "~200 employees (from company website)"
3. **LinkedIn: suggest URL, never scrape** — save the URL for Ed to verify manually
4. **Gmail: read-only, summarise** — extract insights but do not quote email content verbatim in CRM data
5. **Max 3 web searches per lead** — be targeted, not exhaustive
6. **Update `updated_at`** timestamp on every enrichment
7. **Log enrichment** as an interaction of type `enrichment` in `data/interactions.jsonl`
8. **Rate limit** — max 1 full enrichment per lead per day (re-running same day overwrites, doesn't duplicate)
9. **Batch mode** — when enriching multiple leads, process sequentially and print a summary table at the end
