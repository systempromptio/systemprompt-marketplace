---
name: reddit-audience-finder
description: "Quarterly skill that qualifies WHICH subreddits systemprompt.io should engage in. Fetches subscriber counts, moderation rules, and recent activity from Reddit's public JSON for each candidate, scores them against the ICP across five dimensions, and writes a tiered subreddit list to reports/social/reddit/audience/. Both reddit-monitor and reddit-post-composer read its output. Load social-identity first."
metadata:
  version: "1.0.0"
  git_hash: "pending"
---

# Reddit Audience Finder

Standalone skill that answers one question: **which subreddits should we be in?**

Not a daily skill. Run quarterly, or when the ICP shifts, or when a new AI-governance subreddit appears. The output is consumed by `reddit-monitor` (for opportunity scanning) and `reddit-post-composer` (for post drafting). Keeping audience discovery separate from daily monitoring means we don't rebuild the list every morning — we rebuild it when it matters.

## Dependencies

Load `social-media:social-identity` first. Social-identity defines the ICP (CTOs, VP Eng, Platform Eng, Head of AI at 50–500 person orgs standardising on Claude Code and facing governance pressure).

## Reddit data access

Reddit's public JSON works from `curl` with a browser User-Agent. `WebFetch` may be blocked; use `bash` with `curl`.

```bash
UA="Mozilla/5.0 (compatible; systempromptbot/1.0)"
curl -s -A "$UA" "https://www.reddit.com/r/$SUB/about.json"
curl -s -A "$UA" "https://www.reddit.com/r/$SUB/about/rules.json"
curl -s -A "$UA" "https://www.reddit.com/r/$SUB/hot.json?limit=25"
```

Parallelise with `&` + `wait`. Add a 0.3–0.5s sleep between batches to stay polite.

## Part 1: Candidate pool

Start with these 20 candidates, grouped by bucket. Expand when new governance-relevant subs appear.

### Bucket 1: Governance and decision-makers

`r/cto`, `r/compliance`, `r/ITManagers`, `r/sysadmin`, `r/cybersecurity`, `r/msp`

### Bucket 2: Senior practitioners

`r/ExperiencedDevs`, `r/devops`, `r/mlops`, `r/selfhosted`

### Bucket 3: Claude / MCP / AI ecosystem

`r/ClaudeAI`, `r/Anthropic`, `r/mcp`, `r/AI_Agents`, `r/LLMDevs`, `r/LocalLLaMA`, `r/PromptEngineering`, `r/RAG`, `r/AIOps`, `r/OpenAI`

Drop candidates after scoring if they fall below the Tier-C threshold. Do not prune the candidate list in advance — let the scoring decide.

## Part 2: Data collection

For each candidate, pull and cache:

1. `about.json` — subscribers, title, public_description
2. `about/rules.json` — the full moderation rule set
3. `hot.json?limit=25` — last 25 hot threads, each with `title`, `score`, `num_comments`, `selftext[:500]`

Save the raw JSON to `reports/social/reddit/audience/raw/YYYY-MM-DD/{sub}_{type}.json` so future runs can diff subscriber deltas and activity trends.

## Part 3: Scoring rubric (0–100)

Five dimensions, 20 points each. Compute each score deterministically from the cached data so results are reproducible.

### Dimension 1: Size (20 pts)

From `.data.subscribers`:

| Subscribers | Points |
|---|---|
| ≥ 500k | 20 |
| 100k–500k | 15 |
| 30k–100k | 10 |
| 10k–30k | 6 |
| < 10k | 3 |

Size alone never justifies inclusion. r/AIOps has 715 members (score 3); it stays only if other dimensions push it above threshold.

### Dimension 2: ICP density (20 pts)

Count the fraction of the 25 hot posts whose title contains any ICP-signal keyword:

`CTO, platform engineer, VP eng, head of AI, rollout, standardi[sz]e, team, enterprise, compliance, governance, audit, policy, procurement, 50 devs, 100 engineers, org, budget, vendor, self-host, air-gap`

| Fraction | Points |
|---|---|
| ≥ 40% | 20 |
| 20–40% | 14 |
| 10–20% | 8 |
| 5–10% | 4 |
| < 5% | 0 |

### Dimension 3: Governance relevance (20 pts)

Count the fraction of hot posts whose title or selftext contains:

`govern, polic(y\|ies), shadow AI, audit, complian, EU AI, NIST, ISO 42001, SOC ?2, endpoint, DLP, injection, permissions, secrets, access control, standardi[sz]`

Same scoring bands as Dimension 2.

### Dimension 4: Engagement health (20 pts)

Median `num_comments` across the 25 hot posts:

| Median comments | Points |
|---|---|
| ≥ 50 | 20 |
| 20–50 | 14 |
| 10–20 | 10 |
| 5–10 | 5 |
| < 5 | 2 |

A sub with huge subs but no conversation is a billboard, not a room.

### Dimension 5: Mention tolerance (20 pts, inverted scale 1–5 → points)

Parse `rules.json`. Classify strictness:

| Signal in rules | Tolerance | Points |
|---|---|---|
| "No self-promotion" + "No commercial" + "permaban" language | 1 | 4 |
| "Limit self-promotion", "1/10 rule", "disclose purpose" | 2 | 8 |
| "Self-promo allowed with disclosure" / "links in comments" | 3 | 12 |
| Moderate (standard spam rules, no explicit promo ban) | 4 | 16 |
| Permissive / vendor-friendly | 5 | 20 |

Tolerance is not the same as "we get to pitch more." It tells `reddit-post-composer` how subtle the draft must be. Low tolerance means zero product mentions in body, link in first comment only (if permitted), or megathread-only submission.

### Tier thresholds

Sum the five dimensions:

| Total | Tier | Meaning |
|---|---|---|
| 80–100 | **A** | Engage daily. Full reply strategy. Post-composer eligible (subject to mention-tolerance constraints). |
| 60–79 | **B** | Engage daily (reply-only). Rarely post fresh submissions. |
| 40–59 | **C** | Monday weekly sweep only. No posts. |
| < 40 | **Drop** | Do not engage. |

Tie-break on ICP density: at equal totals the sub with more CTO/Platform Eng signals wins.

## Part 4: Bucket coverage rule

Before finalising tiers, verify the final list has at least:

- **1 Tier-A or Tier-B sub in Governance / decision-makers** (r/cto, r/compliance, r/ITManagers, etc.)
- **1 Tier-A or Tier-B sub in Senior practitioners**
- **1 Tier-A or Tier-B sub in Claude / MCP ecosystem**

If a bucket has zero Tier-A/B subs, promote the highest-scored sub in that bucket to Tier C at minimum and note the gap in the report — it's a signal to find more candidates in that space.

## Part 5: Output

Write two files.

### 1. `reports/social/reddit/audience/subreddits.json`

Machine-readable, consumed by `reddit-monitor` and `reddit-post-composer`:

```json
{
  "generated": "YYYY-MM-DD",
  "generator": "reddit-audience-finder v{version}",
  "candidates_evaluated": 20,
  "subs": [
    {
      "name": "ClaudeAI",
      "tier": "A",
      "score": 82,
      "subscribers": 770846,
      "bucket": "claude_mcp_ecosystem",
      "tone": "casual, fellow-user, evidence-valued",
      "mention_tolerance": 3,
      "key_rules": [
        "Competitor posts must contain sufficient homework",
        "Showcase posts must educate",
        "Use relevant post flair"
      ],
      "dimensions": {
        "size": 15,
        "icp_density": 14,
        "governance_relevance": 14,
        "engagement": 20,
        "mention_tolerance_pts": 12
      },
      "reasoning": "Direct product-fit sub. High engagement. Competitor-post homework rule means any draft must include our own evaluation."
    }
  ]
}
```

### 2. `reports/social/reddit/audience/subreddits.md`

Human-readable tier list with reasoning. Structure:

```markdown
# Reddit Audience — Qualified Subreddits

**Generated:** YYYY-MM-DD
**Generator:** reddit-audience-finder v{version}
**Candidates evaluated:** 20
**Tier A:** {N} | **Tier B:** {N} | **Tier C:** {N} | **Dropped:** {N}

## Tier A — engage daily, post-composer eligible

| Sub | Subs | Score | Bucket | Why |
|---|---|---|---|---|
| r/ClaudeAI | 770k | 82 | Claude/MCP | Direct product fit, high engagement |
| ... |

## Tier B — engage daily, replies only

| Sub | Subs | Score | Bucket | Why |
|---|---|---|---|---|
| ... |

## Tier C — Monday weekly sweep only

| ... |

## Dropped

| Sub | Score | Why dropped |
|---|---|---|
| ... |

## Bucket coverage

- Governance / decision-makers: Tier A = {N}, Tier B = {N}
- Senior practitioners: Tier A = {N}, Tier B = {N}
- Claude / MCP ecosystem: Tier A = {N}, Tier B = {N}

Gaps flagged: {any bucket with zero Tier A/B}

## Changelog since last run

- Added: {new subs}
- Removed: {subs that fell below threshold}
- Promoted: {Tier changes up}
- Demoted: {Tier changes down}

## Posting-rule highlights (for reddit-post-composer)

For each Tier A and B sub, list the 1–3 rules most likely to affect a draft:
- r/mcp — "No AI-generated slop" (enforced), "No astroturfing" (ban), "Showcase tag required for own-work"
- r/LLMDevs — "1/10 self-promo ratio", "Disclose purpose", "Provide sources"
- r/selfhosted — "New projects (<3 months) go to megathread only"
- ...
```

## Quality checklist

- [ ] All subscriber counts come from live `about.json`, not memory
- [ ] Every sub in output has a dimensions breakdown, not just a total
- [ ] Moderation rules captured verbatim from `rules.json`, not paraphrased
- [ ] Bucket coverage rule verified
- [ ] Changelog diff computed against previous `subreddits.json` if one exists
- [ ] Raw JSON cached under `reports/social/reddit/audience/raw/YYYY-MM-DD/` for reproducibility
