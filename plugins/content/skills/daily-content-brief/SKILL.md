---
name: daily-content-brief
description: "Daily content briefing. Orchestrates daily-seo-brief data + content-hypothesis-ledger into a single actionable brief: publishing pipeline, guide performance, and all effective actions for Ed (minimum 3, no cap) — each tagged with a new [CT-###] hypothesis. Load identity first."
metadata:
  version: "1.2.0"
  git_hash: "d32d335"
---

# Daily Content Brief

> **Implements:** `commons:daily-brief-pattern` — 8-step orchestration sequence, unlimited hypothesis- and data-driven actions (minimum 3, no cap), no action without hypothesis, score maturing before generating new. This skill configures the pattern for the content domain (CT-### hypotheses, content metric whitelist, 15-minute target).

The daily content operator's dashboard. Shows publishing pipeline status, guide performance from SEO data, GitHub engagement opportunities, and every hypothesis- and data-driven content task (minimum 3, no cap). Target: Ed reads in 15 minutes.

## Dependencies (load in order)

1. `commons:identity` — positioning, ICP, product context
2. `commons:brand-voice` — every draft passes through this
3. `content:content-hypothesis-ledger` — in-flight hypotheses and next `CT-###` allocation
4. `content:content-strategy-master` — current phase, priorities, publishing pipeline

Also read:
- Today's daily-seo-brief report: `reports/seo/daily/{today}/daily-seo-brief.md` — primary data source for guide performance
- Guide inventory: `/var/www/html/systemprompt-web/services/content/guides/*/index.md` frontmatter
- Per-guide reports: `reports/content/guides/*/guide-report.md` (from guide-optimiser)

## CRITICAL: Profile must be `systemprompt-prod`

Before this skill does anything, verify `systemprompt admin session list` shows `systemprompt-prod` as the active profile. The content brief reads daily-seo-brief data which itself requires the production profile. If the active profile is `local`, switch before proceeding:

```bash
systemprompt admin session switch systemprompt-prod
```

## CRITICAL: Data Dependency on SEO Monitor

This brief is deliberately parasitic on daily-seo-brief data. It does NOT pull analytics or GSC data directly. This avoids duplicate API calls and ensures metric consistency across domains.

- If today's daily-seo-brief report exists: use it as the primary data source.
- If missing: invoke `seo:daily-seo-brief` via the Skill tool. Do not ask Ed before invoking. Wait for completion and continue.
- If invocation fails: generate pipeline and github actions only (no performance-based actions). Emit a warning in Instrumentation Notes and continue. Do not halt. Do not ask the user.

## Run Sequence

### Step 1: Verify Data Context

Confirm `systemprompt-prod` profile is active.

### Step 2: Check Today's Data Reports

1. Check daily-seo-brief report at `reports/seo/daily/{today}/daily-seo-brief.md`. If missing, trigger `seo:daily-seo-brief`.

### Step 3: Read Strategy Document

Load `content-strategy-master` for current phase, publishing targets, guide health, and pipeline priorities.

### Step 4: Read Hypotheses

Query the content hypothesis ledger:
- `in-flight`: all active content hypotheses
- `maturing {today}`: hypotheses whose window_end <= today

### Step 5: Score Maturing Hypotheses

For each CT-### with `window_end <= today`:
1. Pull the current value of `metric` from daily-seo-brief data (guide-level or aggregate).
2. Compare to baseline + target.
3. Call `content-hypothesis-ledger score {id} {result} {PASS|FAIL|INCONCLUSIVE} {note}`.
4. Emit the result in the brief.

### Step 6: Generate Actions

No arbitrary maximum — emit every action that is hypothesis- and data-driven. Minimum 3 when the domain has in-flight hypotheses, underperforming guides, or fresh SEO signal; otherwise at least 1 maintenance action. Selection priority:

1. **Dues**: actions from previous day's brief confirmed but not yet scored.
2. **Underperformer fixes**: guides flagged by daily-seo-brief as underperforming (high impressions / low CTR, position drops, poor engagement). These are the highest-leverage content actions.
3. **Pipeline progression**: guides in draft or review that should be moved forward.
4. **Content gaps**: keywords or topics identified in SEO strategy but not yet covered by a guide.
5. **Distribution**: high-performing guides that haven't been syndicated to social platforms.

Floor rule: if `guides_published_total` has not increased in 30+ days, at least one action must be a new guide or a guide pushed to publish.

### Step 7: Log Actions

Each generated action is logged to the content hypothesis ledger via `log`. Each gets a new `CT-###` ID and a full draft written to `data/actions/CT-###.md`.

### Step 8: Write the Brief

Write to `reports/content/daily/{today}/daily-content-brief.md` and print to Ed.

## Action Types and Draft Format

Every action in the brief looks exactly like this:

```markdown
### Action {N}: {Channel} — {One-line summary}

**Hypothesis:** [CT-###] If we {action} on {guide/target},
  then {metric} will {direction} by {amount} within {window} days.
  Reason: {insight from data}.

**Metric to watch:** `{metric_name}` (current baseline: {N})
**Check back on:** {YYYY-MM-DD}
**Guide:** {slug or "new: {proposed title}"}

**What to do:**
{Specific actionable instruction — not a vague suggestion. For optimisations: exact title/meta changes. For new guides: topic + target keyword + outline. For GitHub: exact repo + issue/PR link. For distribution: exact platform + draft.}

**After completing:** reply `done CT-###` and I'll log it.
```

## Brief Report Structure

```markdown
# Content Brief -- {YYYY-MM-DD}

**Profile:** systemprompt-prod
**Phase:** {from content-strategy-master}
**Guides published:** {N} total | {N} indexed | {N} published last 30d
**Active content hypotheses:** {N}

---

## 1. Publishing Pipeline

| Status | Count | Guides |
|--------|------:|--------|
| Draft | {N} | {slug list} |
| In Review | {N} | {slug list} |
| Published (last 7d) | {N} | {slug list} |
| Scheduled | {N} | {slug list} |

## 2. Guide Performance (from SEO Monitor)

### Top 5 by Sessions (7d)

| Guide | Sessions (7d) | Delta vs prev 7d | GSC Clicks | GSC Position | Engagement |
|-------|-------------:|:-----------------:|----------:|:------------:|:----------:|

### Needing Attention

| Guide | Problem | Metric | Suggested Action |
|-------|---------|--------|-----------------|

## 3. Hypotheses Maturing Today

| ID | Action | Metric | Baseline | Result | Verdict | Lesson |
|----|--------|--------|----------|--------|---------|--------|

If zero: "No content hypotheses maturing today. In-flight: {N} ({list IDs and window_end dates})."

## 4. Today's Actions ({N} — all effective, no cap)

{Action 1}
{Action 2}
{Action 3}
... (continue for every hypothesis- and data-driven action)

## 5. What I Noticed

Up to 3 bullets of observation from the data. No speculation. Examples:
- "guide-optimiser raised claude-code-system-prompt from 62 to 78 points — sessions up 23% in 10 days."
- "3 guides have zero GSC impressions after 21 days — likely indexing issue."
- "Distribution push of claude-code-hooks-guide to Dev.to drove 120 referral sessions this week."

## 6. Instrumentation Notes

Anything the brief could not measure (daily-seo-brief stale, GSC unavailable, etc.) — listed so Ed knows the blind spots.
```

**Length discipline**: under 600 words of prose, excluding tables and action drafts.

## Run Modes

```
daily-content-brief              # Normal run, writes report, logs hypotheses
daily-content-brief dry          # Generate the brief, don't log to ledger
daily-content-brief confirm CT-### {url}   # After Ed completes, record the result
```

## After Ed Completes — Confirmation Flow

When Ed says `done CT-###` or `done CT-### {url}`:

1. Update `data/actions/CT-###.md` with completion timestamp and URL/result.
2. Leave the ledger row `IN-FLIGHT` — it only transitions on `window_end`.
3. Print "Confirmed. Checking back on {window_end}."

## Anti-Sludge Rules

- **No vague prose.** "Content is performing well" is banned. "guide_claude-code-system-prompt_sessions_7d rose from 340 to 412, a 21% lift" is required.
- **No motivational language.** No "great progress," "keep publishing." Ed is a professional.
- **No emojis** anywhere in the brief.
- **No actions without a hypothesis.** If you can't state the hypothesis, cut the action.
- **No arbitrary cap on actions.** Minimum 3 when data supports them, no maximum. Every action must cite a measurable hypothesis AND a data signal.
- **Fail loudly, not silently.** If daily-seo-brief is stale or unavailable, say so at the top and limit actions to pipeline/github only.
- **Name specific guides.** Every performance observation must name the guide slug and the exact numbers.
