---
name: marketing-strategy-master
description: "Maintains the living marketing strategy doc at /var/www/html/systemprompt-web/reports/marketing-strategy-master.md. Never rewrites wholesale — writes diffs. Contains objectives, 30/60/90 targets, channel hypotheses in flight, dead hypotheses, winning tactics, and funnel snapshots. Load marketing-identity first."
metadata:
  version: "0.1.0"
---

# Marketing Strategy Master

Owner of the single living strategy doc. Every other marketing-strategy skill **reads** this doc for current priorities; only this skill **writes** to it. Modelled on `content-publishing:seo-monitor`'s use of `seo-content-strategy-master`.

## Dependencies

Load `marketing-identity` first. It defines ICP, hook, and hypothesis format.

## The Strategy Doc

```
/var/www/html/systemprompt-web/reports/marketing-strategy-master.md
```

Structure (enforced on every write):

```markdown
# systemprompt.io — Marketing Strategy Master

**Last updated:** {YYYY-MM-DD by {skill-name}}
**Phase:** {1: Baseline | 2: Test Channels | 3: Double Down | 4: Scale}
**North Star:** Qualified Leads/week (lead = template-ran + feedback)

## 1. Current Funnel Snapshot
(tables updated by lead-tracker; this skill only reads, never overwrites)

## 2. Objectives — 30 / 60 / 90
| Horizon | Template unique cloners/week | Feedback leads | Qualified convos | Sandbox | Ref customers |
|---|---|---|---|---|---|
| 30d | {N} | {N} | {N} | {N} | {N} |
| 60d | {N} | {N} | {N} | {N} | {N} |
| 90d | {N} | {N} | {N} | {N} | {N} |

## 3. Active Hypotheses (in flight)
Table of hypotheses currently being tested — owned by `hypothesis-ledger`, rendered here.

## 4. Winning Tactics (validated)
Tactics where hypothesis tests passed. Short paragraph per tactic: what, why, playbook.

## 5. Dead Hypotheses (and why)
Short table: hypothesis, result, reason for failure, lesson.

## 6. This Week's Theme
One sentence theme, 3–5 message pillars, list of draft hooks.

## 7. Channel Priorities (ranked by leads/Ed-hour)
Ranked list with current weight (% of Ed's outreach hours).

## 8. Instrumentation Gaps
Things we cannot yet measure. Listed so we remember to fix them.

## 9. Changelog
Append-only. One line per diff, newest first: `{YYYY-MM-DD} {skill-name} — {what changed}`
```

## Write Rules

**This skill NEVER rewrites the doc wholesale.** It only applies targeted diffs, and every diff appends a line to §9 Changelog.

Permitted operations:

| Operation | When | Who triggers |
|---|---|---|
| Seed (first run only) | Doc doesn't exist | This skill, one time |
| Update objectives (§2) | Monthly review or explicit Ed instruction | This skill |
| Propose winning tactic (§4) | A hypothesis passed in ledger | `weekly-marketing-review` |
| Retire hypothesis to §5 | A hypothesis failed in ledger | `weekly-marketing-review` |
| Set weekly theme (§6) | Sunday run | `weekly-marketing-review` |
| Reweight channels (§7) | Sunday run, based on ledger ROI | `weekly-marketing-review` |
| Flag instrumentation gap (§8) | Any skill detects a blind spot | Any |

Sections §1 (funnel snapshot) and §3 (active hypotheses) are **rendered** — the actual source is `lead-tracker` output and `hypothesis-ledger`. This skill only re-renders them, never stores derived data.

## Run Modes

```
marketing-strategy-master seed        # First-run: create the doc if missing
marketing-strategy-master read        # Print the doc (default for other skills)
marketing-strategy-master diff {...}  # Apply a targeted diff + changelog entry
marketing-strategy-master render      # Re-render §1 and §3 from lead-tracker + hypothesis-ledger
```

## Seed Data (first run)

Use real baseline captured on 2026-04-15:

- **Template repo (14d):** 81 views, 11 unique viewers, 1,134 clones, **162 unique cloners** (Apr 14 spike of 959/119 flagged as CI bots — treat unique cloners as honest signal). Referrers: github.com, systemprompt.io.
- **Core repo (14d):** 112 views, 8 unique viewers, 128 clones, **47 unique cloners**. Referrers: github.com, crates.io, docs.rs, systemprompt.io.
- **Website (7d):** 165 sessions, 107 unique users, 389s avg duration, 2.28 requests/session. Top pages: `claude-skills-non-technical-teams`, `mcp-vs-cli-tools`, `claude-plugins-vs-mcp-vs-skills`. Traffic sources include GitHub (~30%), ProductHunt, Bing, Slack.
- **Stars:** 1 each (both self-stars).
- **External feedback leads:** 0.

30/60/90 targets (starter — to be recalibrated after Phase 1 baseline week):

| Horizon | Unique cloners/wk (template + core combined) | Feedback leads | Qualified convos | Sandbox | Ref customers |
|---|---|---|---|---|---|
| 30d | 50 (baseline ~30 observed) | 5 | 3 | 1 | 0 |
| 60d | 150 | 15 | 8 | 3 | 1 |
| 90d | 400 | 40 | 20 | 8 | 2 |

## Instrumentation Gaps (known at seed time)

- No GitHub Discussions enabled on either repo → feedback path routes through Issues with `feedback` label, plus `hello@systemprompt.io`. Needs a decision: enable Discussions?
- No GSC service account key at `/var/www/html/systemprompt-marketplace/gsc.json` → GSC data unavailable until Ed provisions one.
- No way to deduplicate "CI bot clones" from "human clones" beyond the unique-cloner count. Large raw-clone spikes get flagged but not removed.
- LinkedIn/X impressions are manual paste-in only (no API access yet).

## Anti-Sludge Rules

- Every diff must reference the hypothesis ID or data source that motivated it.
- Numbers over vibes: "template unique cloners/wk rose from 30 to 72" not "clones growing."
- No sections added without a hypothesis attached.
- If a diff would make the doc contradict itself (e.g., channel ranked #1 in §7 but all its hypotheses in §5), abort and surface the conflict to Ed.
