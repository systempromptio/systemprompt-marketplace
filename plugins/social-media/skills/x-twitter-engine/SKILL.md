---
name: x-twitter-engine
description: "Daily X/Twitter session: reply-first engagement with anchor accounts, news-reactive posts, and earned original threads. 4-week reply-first test with anchor-engagement pass criteria. Human-in-the-loop. Designed for daily /loop."
metadata:
  version: "2.0.0"
  git_hash: "acc9662"
---

## HARD RULE — Evidence-or-silence

**No original tweet or thread ships without verified evidence.** Every numeric claim, URL, date, quote, and narrative beat must be traced to one of the following before the draft is written:

- File path + line number in this repo (e.g. `extensions/web/src/foo.rs:42`)
- A curl-verified API response saved as JSONL under `reports/marketing/data/evidence/YYYY-MM-DD-{slug}.jsonl`
- A git commit SHA (verify with `git log -1 <sha>`)
- A direct quote Ed has supplied in-conversation

A draft that cannot cite evidence for each factual element **must not be written**. The correct output is "nothing to post today — reply-only day" and move on. Replies under other people's tweets follow a lighter bar (a specific technical observation or a counter-example), but the same ban on fabricated specifics applies.

### Banned hook classes

Same list as `linkedin-engine`, applied to original posts:

- **Vanity-traction hooks.** crates.io downloads, GitHub stars, npm downloads, repo clones for products <90 days old OR with <5 external reverse-dependencies. Mirror/bot/CI noise, not adoption.
- **Invented emotion.** Manufactured affect ("I almost cried when…", "I was shocked to see…"). If the emotion is not real, it is fiction.
- **Fabricated specifics.** Named usernames, URLs, handles, or companies that have not been curl-verified.

### Pre-flight check (required for every original post or thread)

Before drafting, fill the frontmatter block. Replies do not require this block; original posts do.

```yaml
pre_flight:
  event: "What specifically happened in the last 7 days that Ed earned the right to say?"
  evidence:
    - claim: "..."
      source: "extensions/web/src/.../file.rs:NNN | evidence/YYYY-MM-DD-slug.jsonl | commit abc1234"
  urls_verified: ["https://..."]   # every URL in the tweet + reply chain
  banned_hook_check: "none-of-the-above"
```

---

# X/Twitter Engine

Daily interactive X/Twitter session for Ed. Ed executes every action manually. The skill drafts replies, suggests engagement targets, tracks performance, and enforces the 4-week reply-first test.

Designed for daily execution via `/loop 1d social-media:x-twitter-engine`.

## Dependencies (load in order)

1. `social-media:social-identity` — platform voice, engagement rules, banned patterns
2. `commons:identity` — product positioning for content pillars
3. `/var/www/html/systemprompt-web/reports/sales-marketing-strategy.md` — current channel priorities and test protocol
4. `commons:marketing-identity` — ICP, template hook, hypothesis format

## Data Locations

All X data lives under `/var/www/html/systemprompt-web/reports/social/x/` (mirrors `reports/social/reddit/` layout):

```
reports/social/x/
  drafts/           YYYY-MM-DD-{slug}.md   (original-post drafts and posted threads)
  replies.jsonl     Reply log (one line per reply sent, append-only)
  performance.jsonl Daily performance log (append-only)
  anchor-accounts.md 20-row anchor-account table
  test-scorecard.md 4-week test tracking document
```

Create this directory structure on first run if it does not exist.

## Run Modes

```
x-twitter-engine              # Full daily session (default)
x-twitter-engine reply        # Reply-session only (default operating mode on most days)
x-twitter-engine draft        # Draft an earned original post (only with a verified event)
x-twitter-engine react        # News-reactive mode (Anthropic/OpenAI/MCP release just dropped)
x-twitter-engine track        # Performance check-in only
x-twitter-engine weekly       # Weekly review
x-twitter-engine scorecard    # Show 4-week test progress
```

---

## Strategy

### Why the old strategy failed

Ed has posted on X for ~1 year with zero traction. Original outbound threads from a cold ~0-follower account in the AI/LLM niche reach nobody — X algorithmically suppresses link-bearing tweets from low-distribution accounts, and senior staff-dev readers scroll past anything that looks like a summary. The v1.0 plan of "5 threads/week backlinking guides" was structurally unable to move the needle.

### What actually produces traction for a cold technical account in 2026

Observed growth patterns for accounts <1k followers targeting senior staff devs:

1. **Reply game under anchor-account threads.** Early, technically substantive replies on posts by accounts the target audience already reads. This is the dominant distribution lever.
2. **News-reactive posts within ~30 minutes** of Anthropic/OpenAI/MCP releases. A single tweet under the official announcement routinely earns 10k+ impressions for small accounts.
3. **Receipts posted as artifacts.** Benchmarks, reproducible scripts, short screen GIFs from shipped merges in `systemprompt-template` / `systemprompt-marketplace`. Senior staff devs reward concrete, not conceptual.
4. **Links in the first reply, never the main tweet.** X suppresses link posts.

### The 4-week reply-first test

Replaces the v1.0 "5 threads/week" test. Runs for 28 days from the first reply logged.

**Weekly targets:**
| Metric | Target |
|--------|--------|
| Substantive replies to anchor-list accounts | 21 (3/day) |
| Earned original posts | 1 (must pass pre-flight) |
| Quote-tweets with a specific take | 3 |
| ICP follows | 5 |
| News-reactive posts | as many as trigger (no cap) |

**Pass criteria (need at least ONE after 4 weeks):**
- ≥3 replies from anchor-list accounts over 4 weeks (reply, like, follow, or quote)
- ≥1 quote-tweet by an account with >5k followers
- Follower delta ≥100 with ICP ratio >40% (audited by hand against the 20 newest follows)

**Fail criteria (ALL must be true):**
- 0 anchor-account engagements over 4 weeks
- 0 quote-tweets by >5k-follower accounts
- Follower delta <25

→ Deactivate this skill. Reallocate time to Reddit and LinkedIn outbound permanently.

**Why these criteria:** Link clicks and attributed leads lag by quarters on X. Anchor-engagement and follower composition are leading indicators that tell us within 4 weeks whether the distribution strategy is working, without waiting for late-funnel signal.

### Content pillars (unchanged, adapted for X)

| # | Pillar | Angle |
|---|--------|-------|
| 1 | Visibility gap | Short observations about ungoverned AI in production stacks |
| 2 | Governance as infrastructure | Transport-layer enforcement specifics, not wiki-page policy |
| 3 | Own the binary | Self-hosted, source-available, no SaaS |
| 4 | Build trap | Why building governance in-house fails |
| 5 | MCP governance | Transport vs proxy architecture |

### Voice (Ed on X)

- Shorter and more technical than LinkedIn
- No hashtags, no emojis, no "thread incoming", no "1/n" numbering
- British English
- Sardonic where natural; never manufactured
- Each tweet stands alone while building a narrative
- Assume the reader is a senior staff dev who has heard every AI pitch this year

### Anti-patterns (hard rules)

- NEVER put links in the main tweet or hook tweet — links go in the first reply only
- NEVER use hashtags or emojis
- NEVER number tweets ("1/5") or announce "thread incoming"
- NEVER cross-post identical content from LinkedIn
- NEVER follow more than 10 accounts/day (spam flags)
- NEVER reply with "+1", "great take", "this", "so true" — every reply adds a specific observation
- NEVER post a vanity-traction hook (see HARD RULE)
- NEVER include a URL that has not been curl-verified 200 this session
- NEVER invent a username or handle
- NEVER draft content that reads as AI-generated (see social-identity banned words)

---

## Anchor Accounts

The anchor-account table is the single most important artifact in this skill. It lists 20 accounts whose replies senior staff devs read. Every reply day starts by checking these accounts' recent posts.

Maintained in `reports/social/x/anchor-accounts.md` as a table:

| # | Handle | Why they matter | Last interaction | Follows back? |
|---|--------|----------------|------------------|---------------|
| 1 | | | | |
| ... | | | | |
| 20 | | | | |

**Seed list (edit on first run based on current landscape):**
- AI infra / agent builders: @simonw, @swyx, @hwchase17, @jxnlco, @transitive_bs
- Anthropic-adjacent: @alexalbert__, @AnthropicAI, @_catwu, relevant Claude team accounts
- Staff eng voices: @mitchellh, @dhh, @eatonphil, @b0rk, @kelseyhightower
- Governance / enterprise AI commentary: @emollick, @willdepue, @ylecun (critique target only)
- MCP / protocol: active contributors on the MCP spec repo

Refresh monthly. Drop accounts that post nothing engageable for 2 weeks. Add accounts whose posts Ed finds himself wanting to reply to.

---

## Daily Session Structure

When `x-twitter-engine` runs (default mode), execute these steps interactively.

### Step 1: News-reactive check (do this first, before anything else)

Scan the last 2 hours of: @AnthropicAI, @OpenAIDevs, @GoogleDeepMind, and the MCP spec repo.

If any of them posted a release, model update, or spec change in the last 2 hours:
- **Immediately enter `react` mode.** Draft one tweet within 30 minutes of the release. This is the highest-leverage moment of the week.
- Format: one tweet (no thread), ≤250 chars, a contrarian or clarifying take (not a summary — X will be flooded with summaries within 10 minutes).
- Link (to systemprompt-template or a relevant guide) goes in the first reply only, not the main tweet.

If no release in the last 2 hours: continue to Step 2.

### Step 2: Performance check-in

Ask Ed to paste metrics from any original post from the last 3 days:

```
Post: {YYYY-MM-DD-slug}
- Impressions: ___
- Engagements: ___
- Link clicks (from first reply): ___
- Profile visits: ___
- Follower delta since post: ___
```

Append to `performance.jsonl`:

```json
{"date":"2026-04-22","post_slug":"2026-04-21-hook","impressions":0,"engagements":0,"link_clicks":0,"profile_visits":null,"quotes":0,"replies":0,"follower_delta":0,"notes":""}
```

### Step 3: Test scorecard

Read `test-scorecard.md`. Show:

```
Reply-first test: Day {N} of 28
Anchor-account engagements: {N}/3 target
>5k-follower quote-tweets: {N}/1 target
Follower delta: {N} (ICP ratio: ~{pct}%)
Replies sent this week: {N}/21 target
On track: {Yes/No/At risk}
```

At Day 14 halfway mark: if anchor engagements = 0 and replies sent ≥40, flag "reply content is the problem, not the strategy — pause and review 3 replies with Ed before continuing."

### Step 4: Reply session (the main event — 3 replies/day target)

Walk the anchor-account table. For each account with a post from the last 24 hours:

1. Show the post.
2. Decide: is there a genuine technical observation to add? (specific counter-example, a file:line from the template, a benchmark number, a contrarian but defensible take).
3. If yes: draft a reply (1–3 sentences, no hashtags, no emojis, no em dashes).
4. If no: skip. Silence > noise.

Target 3 substantive replies per day. If fewer than 3 anchor accounts posted anything engageable, scan conversations under the most-engaged tweet of each anchor account (replies-under-replies also count).

Log each sent reply to `replies.jsonl`:

```json
{"date":"2026-04-22","anchor_handle":"@simonw","parent_tweet_url":"https://x.com/...","reply_text":"...","reply_url":"https://x.com/...","note":""}
```

### Step 5: Earned original post (only if pre-flight passes)

If there is a verified event from the last 7 days (a merge, a benchmark run, a customer conversation Ed can cite, a shipped fix) that Ed has earned the right to post about:

1. Fill the `pre_flight` block in frontmatter.
2. Draft the hook tweet (≤250 chars, no link).
3. Draft 3–5 body tweets (each ≤280 chars, each stands alone).
4. Draft the closing tweet.
5. Draft the link reply (systemprompt-template URL or guide URL + one sentence of context). Link goes in a reply to the closing tweet, not in any main tweet.
6. Save to `reports/social/x/drafts/YYYY-MM-DD-{slug}.md`.
7. Ask Ed: post as-is, edit, or skip?

If no verified event exists: skip Step 5. "No earned post today" is the correct outcome most days.

### Step 6: Quote-tweet opportunities

Scan anchor accounts for 2–3 quote-tweet candidates. For each, draft ≤200 chars of specific commentary (not "this" or "agreed"). Ed reviews and posts.

### Step 7: ICP follows

Suggest 3–5 ICP-matching accounts to follow. Source them from:
- Recent repliers on Anthropic/OpenAI official tweets
- Posters tagged on MCP spec discussions
- Profiles engaging with the anchor-account table

Budget: max 10 follows/day to avoid spam flags.

### Step 8: Pipeline summary

```
Test day: {N}/28 | Replies today: {N}/3 | Anchor engagements: {N}/3 | Follower delta: {N}
```

---

## Reply Quality Rules

Every reply must pass these before sending:

- [ ] Adds a specific technical observation — file:line, a number, a counter-example, or a named architecture choice
- [ ] 1–3 sentences, ≤280 chars
- [ ] No hashtags, no emojis, no em dashes
- [ ] No banned AI-tell words (delve, landscape, leverage, seamless, unlock, empower, robust, etc.)
- [ ] Does not mention systemprompt unless the parent thread is literally asking about the product (≤1 in 20 replies mention it)
- [ ] Would read as credible to a senior staff dev who has never heard of Ed

A reply that fails any box goes back to rewrite. A reply that would be fine on its merits but has no specific observation gets cut — silence is always valid.

---

## News-Reactive Mode (`x-twitter-engine react`)

Triggered when an anchor feed posts a release in the last 2 hours.

Format rules for reactive tweets:

- **One tweet, not a thread.** Threads take too long to draft and the first-hour distribution window closes before you finish tweet 3.
- **≤250 chars.** A contrarian or clarifying observation, not a summary.
- **Cite one specific detail** from the release (a named feature, a number, an API shape).
- **Link in the first reply**, not the main tweet, and only if the link is directly relevant.

After posting, scan the announcement's reply thread and leave 1–2 more substantive replies under the official post (these routinely out-reach Ed's own tweet because they ride the announcement's distribution).

Log the reactive tweet to `performance.jsonl` with a `"reactive": true` flag so the weekly review can distinguish reactive from earned posts.

---

## Earned Thread Format (`x-twitter-engine draft`)

Only enter this mode when Step 5 of the daily session identifies a verified event. Target: 1 earned thread per week. Zero is acceptable; manufactured threads are banned.

File structure `reports/social/x/drafts/YYYY-MM-DD-{slug}.md`:

```markdown
---
id: 2026-04-22-hook-slug
status: queued | posted | killed
pillar: 2
hypothesis: H-XXX
created_at: 2026-04-22
posted_at: null
pre_flight:
  event: "..."
  evidence:
    - claim: "..."
      source: "..."
  urls_verified: []
  banned_hook_check: "none-of-the-above"
impressions: null
engagements: null
link_clicks: null
follower_delta: null
---

**Tweet 1 (hook, ≤250 chars, no link):**
{hook}

**Tweet 2:**
{body}

**Tweet 3:**
{body}

**Tweet 4:**
{body}

**Tweet 5 (closing):**
{closing statement}

**Reply to tweet 5 (link reply):**
{url + one sentence of context}

---
**Pre-submit checklist (Ed completes before posting):**
- [ ] Every numeric claim sourced to pre_flight.evidence
- [ ] No link in any main tweet (link lives in the reply to tweet 5 only)
- [ ] Hook tweet under 250 chars
- [ ] Every body tweet under 280 chars and comprehensible alone
- [ ] Zero em dashes, zero banned AI-tell words
- [ ] Ed is available for 60–90 minutes after posting to reply to replies
```

### Thread quality rules

- At least one specific detail (number, tool name, architecture choice) in the hook OR tweet 2
- No two consecutive earned threads on the same pillar
- Read each tweet on its own — would a scroller stop?
- If the hook is a generic statement, cut it

---

## Performance Tracking

### Test scorecard (`test-scorecard.md`)

Created on first run:

```markdown
# X Reply-First Test Scorecard

**Test start:** {YYYY-MM-DD} (first reply logged)
**Test end:** {YYYY-MM-DD} (+28d)
**Status:** IN PROGRESS

## Pass Criteria (need at least ONE)

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| Anchor-account engagements (reply, like, follow, quote) | ≥3 | 0 | Not met |
| Quote-tweets by >5k-follower accounts | ≥1 | 0 | Not met |
| Follower delta (ICP ratio >40%) | ≥100 | 0 | Not met |

## Weekly Progress

### Week 1 ({date range})
| Metric | Target | Actual |
|--------|--------|--------|
| Replies sent | 21 | |
| Earned original posts | 1 | |
| Quote-tweets with take | 3 | |
| ICP follows | 5 | |
| Reactive posts | — | |
| Anchor engagements received | — | |
| Follower delta | — | |

(Repeat for weeks 2–4)

## Decision

**Verdict:** {PENDING / PASS / FAIL}
**Date:** {YYYY-MM-DD}
**Rationale:** {one sentence}
**Action:** {Continue / Deactivate / Modify}
```

### Weekly review (`x-twitter-engine weekly`)

Run Fridays. Compare this week vs last:

| Metric | This week | Last week | Delta |
|--------|-----------|-----------|-------|
| Replies sent | | | |
| Earned posts | | | |
| Reactive posts | | | |
| Total impressions (all tweets) | | | |
| Anchor engagements received | | | |
| Follower delta | | | |
| ICP-ratio of new followers | | | |

Update `test-scorecard.md` with the week's data.

---

## Hypothesis Integration

**Earned original posts and reactive posts** are logged to the hypothesis ledger with a real metric and window. Replies are logged in bulk weekly, not per-reply.

Earned post:

```
hypothesis-ledger log {
  channel: "x",
  action: "Posted earned thread: '{hook first 50 chars}'",
  hypothesis: "If we post pillar-{N} evidence-backed thread on X then anchor_engagements_7d rises from {baseline} by ≥1 within 7d",
  metric: "anchor_engagements_7d",
  baseline: {current},
  window_end: {+7d}
}
```

Weekly reply batch:

```
hypothesis-ledger log {
  channel: "x",
  action: "Sent {N} anchor-account replies for week of {YYYY-MM-DD}",
  hypothesis: "If we send {N} substantive anchor-account replies then anchor_engagements_28d rises by ≥1 within the test window",
  metric: "anchor_engagements_28d",
  baseline: {current},
  window_end: {test end date}
}
```

---

## First Run Checklist

On the very first run:

1. Create `reports/social/x/` directory structure
2. Create empty `replies.jsonl` and `performance.jsonl`
3. Create `anchor-accounts.md` — populate 20 rows from the seed list above, adjusted for the current landscape
4. Create `test-scorecard.md` with test start = today, test end = today+28d
5. Confirm Ed has an X account and can post manually
6. **Do not generate any original threads on day 1.** The first week is reply-only — 3 replies/day for 7 days, then consider the first earned post.
7. Log the test start to the hypothesis ledger as a meta-hypothesis.

---

## Anti-Sludge Rules

- **No vague prose.** "Engagement is growing" is banned. "3 anchor replies this week, 0 anchor engagements received" is required.
- **No motivational language.** No "great start", "building momentum."
- **No emojis anywhere.**
- **No actions without a hypothesis.**
- **Fail loudly.** If 0 replies sent in 3+ days during the test, the first line of the session says so.
- **The test is the test.** If the 28-day decision is FAIL, deactivate. No extensions.
- **Silence > noise.** On days with no anchor-account posts worth replying to, 0 replies is the correct output. Do not manufacture engagement.
