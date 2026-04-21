---
name: linkedin-engine
description: "Daily interactive LinkedIn session: feed posts, DM outreach, prospect research, engagement tracking, and performance review. Human-in-the-loop. Designed for daily /loop."
metadata:
  version: "1.4.0"
  git_hash: "b6c8fff"
---

## HARD RULE — Evidence-or-silence (added 2026-04-20)

**No draft ships without verified evidence.** Every numeric claim, URL, date, quote, and narrative beat in a post or DM must be traced to one of the following before the draft is written:

- File path + line number in this repo (e.g. `extensions/web/src/foo.rs:42`)
- A curl-verified API response saved as JSONL under `reports/marketing/data/evidence/YYYY-MM-DD-{slug}.jsonl`
- A git commit SHA (verify with `git log -1 <sha>`)
- A direct quote Ed has supplied in-conversation (record the conversation turn reference)

A draft that cannot cite evidence for each factual element **must not be written**. The correct output is to say "nothing to post this week" and exit.

### Banned hook classes

The following hook patterns are forbidden. They invite fabrication and were the exact failure mode of the 2026-04-20 crates.io-traction draft:

- **Vanity-traction hooks.** crates.io download counts, GitHub star counts, npm download counts, repo clone counts, or any "look how popular X is" framing for products <90 days old OR with <5 external reverse-dependencies. These numbers are mirror / CI / bot noise until there is downstream production usage. Posting them as if they were adoption is dishonest and readers who know Rust will see through it.
- **Invented emotion.** Narrative hooks that dress up otherwise-thin data with manufactured affect ("I forgot about it and was shocked to see…", "I almost cried when…"). If the emotion is not real, the post is fiction.
- **Fabricated specifics.** Named usernames, URLs, handles, or companies that have not been curl-verified. The 2026-04-20 draft invented `crates.io/users/edjturner` (404) — never again.

### Pre-flight check (the only path to a draft)

Before writing a single line of any LinkedIn draft, the skill must answer these four questions in writing inside the draft file's frontmatter:

```yaml
pre_flight:
  event: "What specifically happened in the last 7 days that Ed earned the right to say?"
  evidence:
    - claim: "..."
      source: "extensions/web/src/.../file.rs:NNN | evidence/YYYY-MM-DD-slug.jsonl | commit abc1234"
  urls_verified: ["https://..."]   # every URL in the post body and first comment, each curl'd and 200-checked
  banned_hook_check: "none-of-the-above"   # or the draft is killed
```

Missing or hand-waved `pre_flight` block → no draft. This is non-negotiable.

# LinkedIn Engine

Daily interactive LinkedIn session for Ed. This is not an automation skill. It is a structured conversation that runs every day, covering content, outreach, engagement, and measurement. Ed executes every action manually. The skill provides drafts, tracks performance, manages the pipeline, and holds Ed accountable to the strategy.

Designed for daily execution via `/loop 1d social-media:linkedin-engine`.

## Dependencies (load in order)

1. `social-media:social-identity` — platform voice, engagement rules, banned patterns
2. `commons:marketing-identity` — ICP, hook, channel rules
3. `commons:brand-voice` — LinkedIn-specific voice, algorithm context, post structure
4. `commons:identity` — product positioning for content pillars

Also read on first run:
- `/var/www/html/systemprompt-web/reports/marketing/drafts/enterprise-value-prop.md` — enterprise positioning and proof points
- `/var/www/html/systemprompt-web/reports/marketing/marketing-strategy-master.md` — current phase, weekly theme, channel priorities

## Data Locations

All LinkedIn data lives under `/var/www/html/systemprompt-web/reports/marketing/data/linkedin/`:

```
data/linkedin/
  drafts/           LI-001.md, LI-002.md, ...  (draft queue)
  prospects.md      Prospect tracking table
  performance.jsonl Daily performance log (append-only)
  strategy.md       Living LinkedIn strategy doc (updated weekly)
```

Create this directory structure on first run if it does not exist.

## Run Modes

```
linkedin-engine                  # Full daily interactive session (default)
linkedin-engine draft            # Batch-generate a week of posts
linkedin-engine review           # Review and approve today's post
linkedin-engine track            # Performance check-in only
linkedin-engine dm               # DM outreach session only
linkedin-engine research         # Prospect research session
linkedin-engine weekly           # Full weekly review and planning
```

---

## LinkedIn Strategy (Researched, April 2026)

### Algorithm Reality

LinkedIn's 2026 "Depth Score" algorithm fundamentally changed content distribution:

- **Dwell time is king.** The algorithm measures how long users engage with content, not just whether they clicked. Long-form text that earns reading time outperforms short hot takes.
- **Personal profiles get 5-7x the organic reach of company pages.** Ed's personal profile is the primary distribution surface, not a company page.
- **External links reduce reach by ~60%.** Never put links in the post body. Links go in the first comment.
- **Comments are worth ~8x likes.** Content that provokes thoughtful comments gets exponentially more distribution.
- **AI-pattern content gets ~47% less reach.** Posts that read as AI-generated are actively suppressed. Every draft must be rewritten in Ed's voice before posting.
- **Carousels (PDF uploads) get 6.6% average engagement** — highest of any format. Use for frameworks, comparisons, and technical breakdowns.
- **First 60-90 minutes of engagement are critical.** Ed must be available to respond to comments immediately after posting.
- **3-5 hashtags maximum.** More than 5 correlates with 68% reduced reach. Prefer 0-3.
- **Zero-click content wins.** Provide the full value natively in the feed. Do not tease with "read more at my blog."

### Content Pillars (5)

Derived from the enterprise value prop and ICP pain points:

| # | Pillar | Angle | Example hook |
|---|--------|-------|-------------|
| 1 | **The visibility gap** | Your SOC has a blind spot. AI agents make tool calls, access APIs, process sensitive data — and none of it appears in your SIEM. | "Your security team monitors every API call in production. Except the ones made by AI agents." |
| 2 | **Governance is infrastructure** | AI governance is not a checklist or a policy doc. It is a runtime system that evaluates every tool call before execution. | "A governance policy that is not enforced at the tool-call level is a PDF, not a control." |
| 3 | **Own the binary** | Self-hosted, air-gapped, source-available. No data leaves your network. No vendor has access. | "We hand over a compiled binary and walk away. Your infrastructure. Your data. Your audit trail." |
| 4 | **The build trap** | You could build AI governance in-house. By the time you ship v1, the landscape has moved. | "I have talked to three CTOs this month who started building AI governance in Q1. All three are now evaluating commercial options." |
| 5 | **MCP is the governance surface** | MCP is not just a protocol for connecting tools. It is where governance happens — at the transport layer, not as a proxy. | "If your governance layer sits in front of MCP as a proxy, every tool call passes through unexamined. Governance must be the transport layer." |

### Posting Cadence (target, not quota)

| Day | Type | Pillar rotation | Format |
|-----|------|----------------|--------|
| **Monday** | Thought leadership | Pillars 1-2 (visibility, governance) | Text post, 800-1300 chars |
| **Wednesday** | Technical depth | Pillars 3-5 (binary, build trap, MCP) | Carousel (PDF) or text with code |
| **Friday** | Personal/contrarian | Any pillar, personal angle | Text post, story format |

Rotate pillars across weeks so each pillar gets covered at least twice per month.

**This cadence is a ceiling, not a floor.** The skill's default output when nothing real has happened is **skip the slot**. Zero posts this week is preferable to one fabricated post. A LinkedIn feed of silence is recoverable; a feed of invented traction is not. A skipped slot is the correct output of the "no evidence, no post" rule above, not a ledger failure.

### Post Structure (mandatory)

1. **Hook** (line 1, under 150 chars): Contrarian claim, surprising number, or pattern-interrupt. Must earn the "see more" click. Never a question. Never "I'm excited to announce."
2. **Body** (3-5 short paragraphs): One idea per paragraph. Short sentences. Mobile-formatted with line breaks between paragraphs. Specific details (names, numbers, architecture decisions).
3. **Closing**: Strong final statement or specific observation. Never "What do you think?" or "Agree?". If there is a CTA, it is specific: "Clone the template and run the demo scripts."
4. **First comment** (posted immediately after): External link + one sentence of context. This is the only place links appear.

### Quality Gate (mandatory — benchmark against the PDF-governance post)

Every LinkedIn draft must clear every item below before it ships. Reference post: `reports/linkedin/drafts/2026-04-20-pdf-governance.md` (body lines 12-22). If a new draft is weaker than that one on any axis, rewrite it or kill it.

**Hook quality**
- [ ] Line 1 stands alone as a quotable sentence. Read it aloud: does it work with zero context, the way a book title or a conference talk title works?
- [ ] Contains a precise noun pairing that names the thing being argued against (e.g. "PDF, not a control" pairs PDF with control and forces the reader to pick a side).
- [ ] Under 150 chars. Not a question. No hedging words (might, could, perhaps, potentially, arguably).

**Argument structure**
- [ ] Defines the enemy precisely in paragraph 2 (e.g. "Most of what gets sold right now as X is Y"). Generic enemies ("the industry", "many companies") fail this gate.
- [ ] Makes the core technical distinction in paragraph 3 using the most specific vocabulary available (transport vs gateway, object vs afterthought, same object vs stitched reconstruction).
- [ ] Includes at least one concession-then-pivot beat ("Proxies aren't bad. They're useful. But..."). Straw-man posts fail this gate.
- [ ] Contains one concrete failure-mode image that a reader could picture in their own stack (e.g. "a reconstruction stitched from three log files and a Slack thread"). Pure abstraction fails.
- [ ] Ends with a diagnostic the reader runs against themselves ("If your SOC can't tell you, right now..."). Ends the reader inside the argument, not outside it.

**Rhythm**
- [ ] Paragraph lengths vary. At least one two-sentence paragraph exists among the longer ones ("Proxies aren't bad. They're useful.").
- [ ] Sentence lengths vary inside paragraphs. No stretch of four sentences of similar clause structure.
- [ ] Read the whole post aloud in under 45 seconds. If it takes longer, cut.

**Specificity**
- [ ] At least two pieces of concrete vocabulary that only somebody who has built in this space would reach for (e.g. "tool invocation", "redacting its arguments", "transport layer", "audit record"). Generic governance vocabulary ("oversight", "accountability", "responsibility") fails.
- [ ] Zero abstract nouns used as the subject of a sentence ("Governance is", "Control requires") unless the sentence then immediately defines them with a concrete claim.

**Voice**
- [ ] Zero em dashes in body or first comment.
- [ ] Zero banned AI-tell words (see Anti-Patterns list).
- [ ] No hedging. No "I think", "I believe", "in my opinion". The post asserts; comments are where it gets defended.
- [ ] No generic engagement bait as closer. No "Thoughts?", "Agree?", "Anyone else finding...?"

**Length and format**
- [ ] 800-1300 chars for a text post. Under the ceiling to respect the mobile read; over the floor to earn the "see more" click.
- [ ] Link lives in first comment, never in the body.
- [ ] No emojis. No hashtags in line 1. Zero to three hashtags overall, prefer zero.

A draft that fails any checkbox goes back to rewrite. A draft that fails three or more checkboxes is killed, not patched.

### Anti-Patterns (hard rules)

- NEVER include external links in the post body
- NEVER use hashtags in the hook line
- NEVER end with generic engagement questions ("Thoughts?", "Agree or disagree?", "Anyone else finding…?")
- NEVER use em dashes (—) in the post body or first comment. Rewrite as two sentences, a comma, a semicolon, or parentheses. Em dashes in LinkedIn text are the single clearest AI tell
- NEVER post content that reads as AI-generated. Banned words and phrases (non-exhaustive, expand as new tells surface): "delve", "delving", "landscape", "game-changer", "game-changing", "leverage" (verb), "robust", "seamlessly", "seamless", "unleash", "unlock" (in marketing sense), "empower", "harness", "transformative", "cutting-edge", "bleeding-edge", "paradigm shift", "in the realm of", "navigate the complexities", "journey" (as metaphor for work), "it's not just X, it's Y" sentence structure, "at its core", "at the end of the day", "deep dive", "ever-evolving", "testament to", "elevate", "tapestry", "in today's fast-paced world", triads of three parallel adjectives or nouns used for rhythm rather than meaning
- NEVER post the same content to LinkedIn and X — force variation
- NEVER post more than once per day
- NEVER use more than 3 hashtags (prefer 0)
- NEVER fabricate stories, statistics, or case studies
- NEVER post a vanity-traction hook (see HARD RULE block above) — download counts, star counts, clone counts on a product <90 days old are mirror/bot noise
- NEVER include a URL that has not been curl-verified 200 in the current session. crates.io user pages are not a valid CTA; they are a profile listing, not a landing page
- NEVER invent a username, handle, or account name. If it is not in Ed's profile, in a git commit, or in a verified API response, it does not exist

### Voice (Ed's LinkedIn voice)

- First person, direct, confident
- British English (realise, optimise, organisation)
- Personal experience framing: "I built", "I learned", "I talked to"
- Sardonic humour where natural
- Infrastructure-level thinking (systems, standards, architecture)
- Genuine excitement about things that work, honest frustration about things that do not
- Specific: names of tools, exact numbers, concrete architecture decisions

---

## Daily Session Structure

When `linkedin-engine` runs (default mode), execute these steps as an interactive conversation with Ed. Each step requires Ed's input before proceeding.

### Step 1: Performance Check-in

Ask Ed to paste yesterday's post metrics (if a post was published yesterday):

```
Yesterday's post: {LI-###}
- Impressions: ___
- Likes: ___
- Comments: ___
- Reposts: ___
- Link clicks (first comment): ___
- Profile views (if available): ___
```

Log the data to `data/linkedin/performance.jsonl`:

```json
{"date":"2026-04-16","post_id":"LI-001","impressions":0,"likes":0,"comments":0,"reposts":0,"link_clicks":0,"profile_views":null,"notes":""}
```

If no post was published yesterday, skip. If Ed does not have metrics yet (too early), note and move on.

### Step 2: Queue Status

Read `data/linkedin/drafts/` and show:

```
Draft queue: {N} posts queued, {M} scheduled, {K} posted
Next scheduled: LI-{###} for {day} — "{first 50 chars of hook}"
Gaps: {list any days in the next 7 without a scheduled post}
```

If the queue has fewer than 3 posts, flag: "Queue is running low. Run `linkedin-engine draft` to batch-generate."

If today is **Monday** and the queue has fewer than 3 posts for this week, automatically enter draft mode and generate posts for Mon/Wed/Fri.

### Step 3: Today's Post Review

If a post is scheduled for today:

1. Show the full draft
2. Ask Ed: "Post as-is, edit, or skip?"
3. If Ed edits, update the draft file
4. If Ed approves: mark as `status: ready` and remind Ed to post manually on LinkedIn
5. After Ed posts: Ed says `posted LI-{###}` and the skill updates `status: posted`, `posted_at: {now}`

If no post is scheduled for today, say so and move on.

### Step 4: Engagement Check

Ask Ed:

```
Any comments on recent posts that need replies?
Any DMs received that need response?
Any connection requests from ICP-matching profiles?
```

If yes: help draft replies. Replies follow the same voice rules — specific, helpful, no self-promotion unless directly asked.

### Step 5: DM Outreach (if active)

Read `data/linkedin/prospects.md`. If there are prospects with `Status: ready`:

1. Show the next prospect: name, title, company, signal
2. Draft a personalised DM (see DM rules below)
3. Ed reviews, edits, approves
4. After Ed sends: Ed says `sent` and the skill updates the prospect row

Maximum 3 DMs per day. If 3 have been sent today, skip.

### Step 6: Pipeline Summary

Show a one-line summary:

```
Posts: {posted}/{scheduled}/{queued} | DMs: {sent}/{total prospects} | Replies: {pending}
This week: {N} posts published, {M} DMs sent, {K} comments replied to
```

### Step 7: Weekly Actions (Monday and Friday only)

**Monday — Posting-licence audit (not batch-generate).** Do not enter draft mode by default. Instead, ask Ed (or self-audit if Ed is not present):

> Did anything real happen in the last 7 days that Ed has earned the right to say publicly? Candidates:
> — A shipped feature with before/after code (cite the commit SHA)
> — A customer or prospect conversation that revealed a defensible pattern (cite the thread)
> — A hard-won integration lesson (cite the code and the problem it solved)
> — A contrarian technical opinion Ed can defend under pushback (cite the architecture it rests on)
> — A response to current industry news (cite the article with a URL verified this session)

If the answer is none-of-the-above, **the correct output is "no LinkedIn posts this week"**. Do not enter draft mode. Reinvest the time into outbound DMs or into shipping something that unlocks next week's post. Log the skip as a ledger entry (channel=linkedin, action="skipped — no verified event", status=SKIPPED-HONEST) so the silence is auditable.

If the answer is one-or-more, enter draft mode and produce one draft per verified event — never more. Do not manufacture pillar coverage to hit a weekly quota.

**Friday:** Weekly performance review:
- Compare this week's total impressions, likes, comments vs last week
- Identify best-performing post and why
- Score any LinkedIn hypotheses whose windows close this week
- Adjust content pillars if data shows one pillar consistently underperforms
- Update `data/linkedin/strategy.md` with lessons

---

## Draft Generation (`linkedin-engine draft`)

Generate **one draft per verified event**. Do not generate drafts to cover unused pillars. For each draft:

1. **Start from the event, not the pillar.** The verified event (commit, conversation, incident, news item) is the only reason to post. Pick the pillar that the event already fits; do not pick a pillar and then hunt for an event.
2. **Fill the pre-flight block** (see HARD RULE at top). Every factual element must have a source line. If the block cannot be filled honestly, stop — there is no draft.
3. **Select type** — thought leadership (opinion + argument), technical (code + architecture), or personal (lesson + specifics).
4. **Write the draft** — follow post structure rules. Under 1,300 characters for text posts.
5. **Write the first comment** — link + one-sentence context. The link must appear in `pre_flight.urls_verified` and have been curl-checked this session.
6. **Create the hypothesis** — each post gets an H-### from the hypothesis ledger, with the measured metric and window explicitly tied to the event (not to "impressions in general").

Save each draft to `data/linkedin/drafts/LI-{###}.md`:

```markdown
---
id: LI-001
status: queued
scheduled_for: 2026-04-17
pillar: 1
type: thought-leadership
hypothesis: H-012
created_at: 2026-04-16
posted_at: null
impressions: null
likes: null
comments: null
reposts: null
link_clicks: null
pre_flight:
  event: "What specifically happened or was observed that Ed earned the right to say this?"
  evidence:
    - claim: "..."
      source: "file:line | evidence/YYYY-MM-DD-slug.jsonl | commit SHA | conversation turn"
  urls_verified: []
  banned_hook_check: "none-of-the-above"
why_this_post_now:
  - "What signal (conversation, observation, shipped feature, news item) triggered this specific post?"
  - "Why this pillar, today, given what was posted in the last 7 days?"
  - "What audience response is expected (ICP1/ICP2, engagement, pipeline signal)?"
---

{post body}

---
**First comment:** {link + one sentence of context}

---
**Pre-submit checklist (Ed completes before posting):**
- [ ] Read last 3 posts on Ed's profile — this does not repeat a recent angle
- [ ] Zero em dashes in body and first comment
- [ ] Zero banned AI-tell words (delve, landscape, game-changer, leverage as verb, robust, seamlessly, etc.)
- [ ] Every numeric claim sourced to pre_flight.evidence above
- [ ] No product name or URL in post body
- [ ] First comment ready to paste immediately after posting
- [ ] Ed is available for 60-90 minutes after posting to respond to comments
- [ ] Mention count: {0 / contextual / direct} (must match funnel tier — 70% = 0, 20% = contextual, 10% = direct)
```

### Draft Quality Rules

- Every post must contain at least one specific detail (a number, a tool name, an architecture decision, a company name, a date)
- No two consecutive posts from the same pillar
- No post should be publishable without Ed reading and approving it — drafts are starting points, not final copy
- If the post references a guide or repo, verify the URL exists before including it
- Read Ed's actual LinkedIn profile and recent posts (if available) to match his voice

### Mention Audit

Count product mentions before shipping. Apply the 70/20/10 funnel rule:

| Funnel tier | % of posts | Product mentions in body | First-comment link |
|-------------|-----------|--------------------------|-------------------|
| Top of funnel | 70% | 0 — no product name, no URL, no "we built" | Optional, one sentence of context |
| Middle of funnel | 20% | 1 — systemprompt named as context, not pitched | Permitted |
| Bottom of funnel | 10% | 1 inline + template/repo CTA | Required |

If the draft exceeds its tier budget, rewrite or reclassify. A top-of-funnel post that sneaks in a product mention at the end is a middle-of-funnel post — label it correctly and recalibrate the weekly mix.

---

## DM Outreach

### Prospect Research (`linkedin-engine research`)

Guide Ed through building the prospect list. The skill:

1. **Define search criteria** from marketing-identity ICP2:
   - Title: Head of AI, VP Engineering, Platform Engineering Lead, CTO
   - Company size: 50-500 employees
   - Signal: public post about Claude/AI rollout, job listing mentioning Claude, comment on governance thread, conference talk about AI standardisation

2. **Suggest search queries** for LinkedIn:
   - `"head of AI" "claude" -recruiter`
   - `"VP engineering" "AI governance" OR "AI rollout"`
   - `"platform engineering" "claude code" OR "MCP"`
   - People who commented on Anthropic's official posts
   - People who posted about Microsoft Agent Governance Toolkit

3. **For each prospect Ed finds**, capture in `data/linkedin/prospects.md`:

```markdown
| # | Name | Title | Company | Size | Signal | Status | Contacted | Reply | Notes |
|---|------|-------|---------|------|--------|--------|-----------|-------|-------|
| 1 | | | | | | ready | | | |
```

Status values: `research` → `ready` → `connected` → `messaged` → `replied` → `converted` → `dead`

Target: 20 prospects in the initial list. Refresh monthly.

### DM Rules

- **Maximum 3 DMs per day.** Quality over volume.
- **Engage before messaging.** Before sending a DM, Ed should have liked or commented on at least one of the prospect's posts. The DM should not be the first interaction.
- **Personalise on the signal.** Reference the specific post, job listing, or comment that made them a prospect. Never generic.
- **One message only.** No follow-up sequences. No "just checking in." If they do not reply, they are not interested.
- **Link to the template repo**, not the website. The repo is tangible and evaluable. The website is marketing.
- **Ask one question.** Not a pitch. A question that demonstrates understanding of their specific situation.
- **Under 300 characters.** LinkedIn DMs that are too long do not get read.
- **Connection request first** with a personalised note (under 300 chars). DM only after they accept.

### DM Template (starting point, always personalise)

```
Hi {name}, I saw your {post about X / job listing for Y / comment on Z}.

I built something related — a self-hosted governance layer for Claude Code deployments. Single binary, PostgreSQL, air-gapped.

Would a 10-minute walkthrough of the template repo be useful?

github.com/systempromptio/systemprompt-template
```

Ed must rewrite every DM. This template is a structure, not copy-paste.

### Connection Request Note Template

```
{Name} — your {post/comment} about {specific topic} resonated.
Building AI governance infra in Rust. Would value connecting.
```

Under 300 characters. Always reference something specific.

---

## Performance Tracking

### Daily Metrics (manual, Ed pastes during check-in)

| Metric | Source | Frequency |
|--------|--------|-----------|
| Post impressions | LinkedIn post analytics | Daily |
| Likes | LinkedIn post analytics | Daily |
| Comments | LinkedIn post analytics | Daily |
| Reposts | LinkedIn post analytics | Daily |
| Link clicks (first comment) | LinkedIn post analytics | Daily |
| Profile views | LinkedIn dashboard | Weekly (Monday) |
| Connection requests received | LinkedIn dashboard | Weekly (Monday) |
| DMs sent | Prospect table | Daily |
| DM replies received | Prospect table | Daily |
| Search appearances | LinkedIn dashboard | Weekly (Monday) |

### Performance Log

Append daily to `data/linkedin/performance.jsonl`:

```json
{
  "date": "2026-04-16",
  "post_id": "LI-001",
  "impressions": 0,
  "likes": 0,
  "comments": 0,
  "reposts": 0,
  "link_clicks": 0,
  "profile_views": null,
  "connection_requests": null,
  "search_appearances": null,
  "dms_sent": 0,
  "dm_replies": 0,
  "notes": ""
}
```

### Weekly Review Metrics (Friday)

| Metric | This week | Last week | Delta |
|--------|-----------|-----------|-------|
| Total impressions | | | |
| Total engagement (likes + comments + reposts) | | | |
| Avg engagement rate | | | |
| Profile views | | | |
| Connection requests | | | |
| DMs sent | | | |
| DM reply rate | | | |
| Best post (by impressions) | | | |
| Best post (by comments) | | | |

### Targets (Phase 1: first 30 days)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Posts per week | 3 | Mon/Wed/Fri cadence |
| Avg impressions per post | 500+ | Baseline for a new consistent poster |
| Avg engagement rate | 2%+ | Industry average for B2B thought leadership |
| Profile views per week | 100+ | Signal of growing visibility |
| DMs sent per week | 10-15 | 3/day, 5 days |
| DM reply rate | 20%+ | LinkedIn InMail benchmarks are 10-25% |
| Prospects in pipeline | 20 | Initial research target |

Recalibrate after 30 days against actual data.

---

## Hypothesis Integration

Every LinkedIn post and DM batch gets logged to the hypothesis ledger:

**Feed posts:**
```
hypothesis-ledger log {
  channel: "linkedin",
  action: "Published LI-{###}: '{hook first 50 chars}'",
  hypothesis: "If we post {pillar} content on LinkedIn then linkedin_impressions_7d rises from {baseline} to {target} within 7d",
  metric: "linkedin_impressions_7d",
  baseline: {current},
  window_end: {+7d}
}
```

**DM batches:**
```
hypothesis-ledger log {
  channel: "linkedin",
  action: "Sent {N} personalised DMs to ICP2 prospects",
  hypothesis: "If we DM {N} ICP2 prospects then dm_reply_rate rises above 20% within 14d",
  metric: "linkedin_dm_reply_rate",
  baseline: {current},
  window_end: {+14d}
}
```

---

## First Run Checklist

On the very first run of this skill:

1. Create `data/linkedin/` directory structure
2. Create empty `prospects.md` with table headers
3. Create empty `performance.jsonl`
4. Create `strategy.md` with initial strategy (copy the strategy section from this skill)
5. Read Ed's current LinkedIn profile and recent posts (Ed shares URL)
6. **Identify up to 5 real events or opinions from Ed's last 30 days** — from git history, from conversations, from shipped features. If fewer than 5 exist, generate fewer drafts. Manufacturing pillar-coverage to hit a round number is banned.
7. **Start prospect research** — guide Ed through building the first 10 prospects
8. Schedule the first week only from the drafts that passed the pre-flight check. Empty slots are acceptable.

---

## Anti-Sludge Rules

- **No vague prose.** "Engagement is growing" is banned. "LI-003 got 847 impressions and 12 comments vs LI-002's 312 impressions and 2 comments" is required.
- **No motivational language.** No "great progress", "keep it up", "building momentum."
- **No emojis** anywhere.
- **No actions without a hypothesis.** If you cannot state the hypothesis, cut the action.
- **Fail loudly.** If Ed has not posted in 5+ days, the first line of the session says so. Do not bury it.
- **The session is for Ed's eyes only.** It is an operator's dashboard, not a social media artifact.
- **Respect Ed's time.** The full daily session should take under 15 minutes. If it is running long, cut to essentials: check-in, today's post, done.
