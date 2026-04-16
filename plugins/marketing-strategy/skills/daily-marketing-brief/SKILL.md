---
name: daily-marketing-brief
description: "The morning /loop skill. Orchestrates lead-tracker + hypothesis-ledger + marketing-strategy-master into a single actionable brief: funnel deltas (1d/7d/31d), hypotheses maturing today, and 3–5 copy-paste-ready actions for Ed — each tagged with a new [H-###] hypothesis. Load marketing-identity first."
metadata:
  version: "0.1.0"
---

# Daily Marketing Brief

The only skill Ed reads every morning. Everything else in this plugin feeds it. Target: Ed reads and executes in 20 minutes over one coffee.

## Dependencies (load in order)

1. `marketing-identity` — ICP, hook, hypothesis format, banned words
2. `content-publishing:brand-voice` — every draft passes through this
3. `hypothesis-ledger` — in-flight hypotheses and next `H-###` allocation
4. `lead-tracker` — funnel data (this skill triggers a fresh run, unless one already exists for today)
5. `marketing-strategy-master` — current weekly theme, channel priorities, objectives

## CRITICAL: Profile must be `systemprompt-prod`

Before this skill does anything, verify `systemprompt admin session list` shows `systemprompt-prod` as the active profile. `lead-tracker` enforces this on its own — but this skill also calls `systemprompt analytics` directly in places (for example, to pull a freshness check or a specific content stat), so the rule applies here too. If the active profile is `local`, switch before proceeding:

```bash
systemprompt admin session switch systemprompt-prod
```

The `local` profile reads a frozen dev DB that was last prod-synced at an earlier date; every analytics number will be silently wrong. Never run this skill against `local`. Every brief written by this skill must carry a `Profile: systemprompt-prod` line at the top.

## Run Sequence

1. **Check today's `lead-tracker` report exists.** Path: `/var/www/html/systemprompt-web/reports/marketing/daily/{today}/lead-tracker.md`. If missing, invoke `lead-tracker` to generate it. If it failed, surface failure and stop — we do not run the brief blind.
2. **Read strategy doc.** `marketing-strategy-master read` to get current phase, weekly theme, channel priorities.
3. **Read in-flight and maturing hypotheses.** `hypothesis-ledger in-flight` and `hypothesis-ledger maturing {today}`.
4. **Score any hypothesis whose `window_end` <= today.** For each, pull `metric` value from `lead-tracker`'s JSON tail, compare to baseline + target, call `hypothesis-ledger score {id} {result} {PASS|FAIL|INCONCLUSIVE} {note}`.
5. **Generate 3–5 actions for today** (see next section).
6. **Log each generated action** via `hypothesis-ledger log` — each action gets a new `H-###` and its full draft written to `data/actions/H-###.md`.
7. **Write the brief** to `/var/www/html/systemprompt-web/reports/marketing/daily/{today}/daily-brief.md` and print to Ed.

## How Actions Are Chosen

Maximum 5 actions. Priority order:

1. **Dues**: any action from the previous day's brief that Ed confirmed he'd do but wasn't scored yet (check ledger for `IN-FLIGHT` rows logged yesterday that should have been actioned today).
2. **Theme-aligned**: 2–3 actions aligned to the current weekly theme from `marketing-strategy-master §6`.
3. **Channel-balanced**: weighted by the channel priorities in `marketing-strategy-master §7`. If the top channel is Reddit, it gets the most actions; do not over-sample a single channel unless §7 explicitly says so.
4. **One experiment of the day**: one net-new hypothesis in a channel we haven't tested in ≥7 days. Bias toward learning when data is thin.
5. **Floor**: if `leads_new_7d == 0` for 3+ consecutive days, at least one action must be a direct outreach DM (LinkedIn or email) — not a broadcast post.

Drop rules:

- Never two Reddit posts on the same day in the same subreddit.
- Never a LinkedIn post and an X post with the same body — force variation.
- If the brief would contain zero drafts because `lead-tracker` shows no data, emit only a baseline-gathering action: "Do nothing today, let baseline build."

## Action Draft Format

Every action in the brief looks exactly like this — copy-paste ready:

```markdown
### Action {1–5}: {Channel} — {One-line summary}

**Hypothesis:** [H-###] If we {action} on {channel} targeting {ICP-sub},
  then {metric} will {direction} by {Δ} within {window} days.
  Reason: {insight}.

**Metric to watch:** `{metric_name}` (current baseline: {N})
**Check back on:** {YYYY-MM-DD}
**Target URL to link:** {exactly one URL}

**Draft (copy-paste ready):**

> {the actual post / DM / PR comment / email body}
> {multiple lines ok}

**Post to:** {exact destination — subreddit name, LI feed, PR # + URL, DM recipient + LinkedIn profile URL}
**After posting:** reply `done H-###` and I'll log the URL of your post.
```

No placeholders in the body. No `{name}` except in personalised DMs where it's at the very top for Ed to replace.

## Brief Report Structure

```markdown
# Daily Marketing Brief — {YYYY-MM-DD}

**Phase:** {1|2|3|4 from strategy master}
**Weekly theme:** {from §6}
**Days since last run:** {N}
**Active hypotheses in flight:** {N}
**Leads total:** {N}  **|  Leads this week:** {N}  **|  Qualified convos this week:** {N}

---

## 1. Funnel Snapshot (1d / 7d / 31d)

| Stage | 1d | 7d (Δ% vs prev 7d) | 31d |
|---|---|---|---|
| Web sessions | ... | ... | ... |
| Repo unique views (core+template) | ... | ... | ... |
| **Unique cloners (core+template)** | ... | ... | ... |
| Feedback leads | ... | ... | ... |
| Qualified convos | ... | ... | ... |

**Target pace:** 30d unique-cloners/wk target is {T}. Current 7d is {C}. At this rate we hit {%} of target.

## 2. Hypotheses Maturing Today

For each hypothesis with `window_end <= today`:

- **[H-###]** {hypothesis one-liner}
  - Metric: `{name}`  Baseline: {N}  Result: {N}
  - Status: **{PASS|FAIL|INCONCLUSIVE}**
  - Lesson: {one line}
  - Diff to strategy doc: {§4 Winning Tactic | §5 Dead Hypothesis | no change}

If zero: "No hypotheses maturing today. In flight: {list of IDs and their window_end dates}."

## 3. Today's Actions (3–5)

{Action 1}
{Action 2}
{Action 3}
{Action 4}
{Action 5}

## 4. What I Noticed

Up to 3 bullets of observation from the data. No speculation. Examples:
- "crates.io became a template referrer for the first time — worth an experiment."
- "web_sessions dropped 18% vs prev 7d despite no content change — investigate source split."
- "959-clone spike on core on {date} was automation; ignore for lead counting but note as a distribution surface."

## 5. Instrumentation Notes

Anything `lead-tracker` couldn't measure (GSC unavailable, session expired, LinkedIn needs manual paste-in, etc.) — listed so Ed knows the blind spots of today's brief.
```

**Length discipline**: the brief must be under ~800 words of prose, excluding code/draft blocks. If it's longer, it's not a brief.

## Run Modes

```
daily-marketing-brief              # Normal run, writes report, prints to stdout
daily-marketing-brief dry          # Generate the brief, don't log hypotheses to ledger
daily-marketing-brief confirm H-### {url}   # After Ed posts, record the live URL in data/actions/H-###.md
```

## After Ed Posts — Confirmation Flow

When Ed pastes `done H-### {url}` or says "posted H-###", run:

```
daily-marketing-brief confirm H-### {url}
```

Which:
1. Appends `posted_at: {now}` and `live_url: {url}` to `data/actions/H-###.md`.
2. Leaves the ledger row `IN-FLIGHT` — it only transitions on `window_end`.
3. Prints "Confirmed. Checking back on {window_end}."

## Anti-Sludge Rules

- **No vague prose.** "Traffic is growing" is banned. "template_cloners_7d rose from 47 to 62, a 32% lift" is required.
- **No motivational language.** No "great work," "keep it up," "building momentum." Ed is a professional.
- **No emojis** anywhere in the brief. The brand-voice rules apply.
- **No actions without a hypothesis.** If you can't state the hypothesis, cut the action.
- **No more than 5 actions**, ever. If the ledger has 10 maturing today, score them all but still only generate 5 new ones.
- **Fail loudly, not silently.** If `lead-tracker` is stale or the session is expired, the brief's top line says so and no actions are generated.
- **The brief is for Ed's eyes only.** It is not a social-media-ready artifact. It is an operator's dashboard.
