---
name: github-monitor
description: "Daily GitHub developer marketing scanner. Finds 6 types of contribution opportunities: discussion replies, directory submissions, code PRs, bug fixes, cookbook contributions, and issue comments. Covers 30+ repos across the Claude/MCP ecosystem. Designed for daily /loop. Load identity first."
metadata:
  version: "2.0.0"
  git_hash: "000000"
---

# GitHub Monitor

Daily scan of the Claude Code / MCP / Agent SDK ecosystem on GitHub to find actionable contribution opportunities. Produces a report with 6 categories of actions, each with copy-pasteable drafts ready for manual execution. Designed for `/loop 1d`.

## Dependencies

**Load `identity` before this skill.** Identity defines positioning, ICP, and keyword strategy context.

## Source of Truth

**Read the SEO Content Strategy Master Plan before running:**

```
/var/www/html/systemprompt-web/services/content/guides/seo-content-strategy-master/index.md
```

Focus on the **External Authority and Backlink Strategy** section.

## Overview

This skill scans for **6 categories** of contribution opportunity:

1. **Discussion Replies** -- GitHub Discussions where developers are having conversations
2. **Directory & Registry Submissions** -- curated lists, registries, and directories for backlinks
3. **Code PRs** -- CLAUDE.md contributions to popular repos
4. **Bug Fix PRs** -- fix bugs in official Anthropic/MCP repos for maximum authority
5. **Cookbook Contributions** -- Jupyter notebooks to anthropics/anthropic-cookbook
6. **Issue Comments** -- only when a guide genuinely answers an unanswered question

Each item in the report must include: URL, what to do, copy-pasteable draft content, and effort estimate.

---

## Step 1: Read Context

Read the previous report and the SEO strategy's External Authority section:

```bash
ls -t reports/github/*/github-monitor.md 2>/dev/null | head -1
```

Check what was already actioned, what submissions are pending, and weekly comment budgets.

---

## Step 2: Scan Discussions

GitHub Discussions are where developers share experiences and debate approaches. These are higher value than issue comments because they are indexed by Google and carry the repo's domain authority.

### Repos with Discussions Enabled

| Repo | Stars | Discussion Focus |
|------|------:|-----------------|
| anthropics/claude-code-action | 6k+ | Q&A on CI/CD, permissions, workflow config |
| modelcontextprotocol/modelcontextprotocol | 7.5k+ | Protocol design, security, OAuth, governance |
| modelcontextprotocol/registry | 6.5k+ | Enterprise MCP, quality standards, skills format |
| PrefectHQ/fastmcp | 23k+ | MCP framework Q&A, deployment, Docker patterns |
| affaan-m/everything-claude-code | 75k+ | Community Q&A on hooks, workflows, CLAUDE.md |
| github/github-mcp-server | 28k+ | GitHub's MCP server usage and config |

### How to Scan

```bash
gh api graphql -f query='{
  repository(owner:"{owner}",name:"{repo}") {
    discussions(first:20, orderBy:{field:CREATED_AT, direction:DESC}) {
      nodes {
        number title url
        comments { totalCount }
        createdAt
        category { name }
        answerChosenAt
      }
    }
  }
}'
```

For each unanswered discussion (answerChosenAt is null, low comment count):
- Read the full body and comments
- Determine if we can add genuine technical value
- Draft a substantive reply (the reply must stand on its own without any link)
- Only include a guide link if genuinely relevant

**Priority:** Unanswered Q&A discussions in claude-code-action and fastmcp (practical problems). Ideas/Security discussions in the MCP spec repo (thought leadership).

---

## Step 3: Scan Directory & Registry Submission Targets

Check which directories are actively accepting submissions and prepare entries.

### Tier 1: Official Registries

| Registry | Stars | Submission Process |
|----------|------:|-------------------|
| modelcontextprotocol/registry | 6.5k | `mcp-publisher` CLI tool, npm package |
| docker/mcp-registry | 453 | PR with `servers/{name}/server.yaml` |
| Anthropic plugins directory | -- | Form at https://clau.de/plugin-directory-submission |

### Tier 2: High-Traffic Lists (10K+ stars)

| Repo | Stars | Format | Activity |
|------|------:|--------|----------|
| punkpeye/awesome-mcp-servers | 83k | PR to README, one-line alphabetical | Merging daily |
| ComposioHQ/awesome-claude-skills | 44k | PR with folder + SKILL.md | Slow/selective |
| hesreallyhim/awesome-claude-code | 28k | Web UI issue form ONLY | Batched merges |
| e2b-dev/awesome-ai-agents | 26k | PR or Google Form | Inactive (skip) |
| davila7/claude-code-templates | 23k | PR with JSON component file | Merging daily |
| VoltAgent/awesome-claude-code-subagents | 14k | PR to README | Check activity |

### Tier 3: Active Community Lists (1K-10K stars)

| Repo | Stars | Format | Activity |
|------|------:|--------|----------|
| travisvn/awesome-claude-skills | 8.8k | PR with SKILL.md | Near-100% rejection |
| BehiSecc/awesome-claude-skills | 7.5k | PR to README | Check activity |
| Jeffallan/claude-skills | 6.7k | PR with structured SKILL.md + CI | Active weekly |
| punkpeye/awesome-mcp-clients | 6.3k | PR to README | Check activity |
| appcypher/awesome-mcp-servers | 5.2k | PR to README | Check activity |
| mahseema/awesome-ai-tools | 4.6k | PR to README | Slow |
| davepoon/buildwithclaude | 2.6k | PR with skill/plugin files | Very active daily |
| rohitg00/awesome-devops-mcp-servers | 961 | PR to README | Active |

### How to Check Activity

```bash
gh pr list -R {repo} --state merged --limit 5 --json title,mergedAt
gh pr list -R {repo} --state open --limit 5 --json title,createdAt
```

Only recommend submissions to repos that merged PRs in the last 14 days.

For each viable target, prepare a ready-to-submit entry in the exact format required by that repo.

---

## Step 4: Scan Code PR Opportunities

### CLAUDE.md Contributions

Popular repos that lack a CLAUDE.md file. Contributing one helps the project and demonstrates the format's value.

**Candidate repos (verify they still lack CLAUDE.md):**

| Repo | Stars | Check |
|------|------:|-------|
| continuedev/continue | 32k | `gh api repos/continuedev/continue/contents/CLAUDE.md` |
| microsoft/playwright-mcp | 29k | `gh api repos/microsoft/playwright-mcp/contents/CLAUDE.md` |
| github/github-mcp-server | 28k | `gh api repos/github/github-mcp-server/contents/CLAUDE.md` |
| chatboxai/chatbox | 39k | `gh api repos/chatboxai/chatbox/contents/CLAUDE.md` |
| awslabs/mcp | 8.5k | `gh api repos/awslabs/mcp/contents/CLAUDE.md` |
| idosal/git-mcp | 7.8k | `gh api repos/idosal/git-mcp/contents/CLAUDE.md` |
| firecrawl/firecrawl-mcp-server | 5.8k | `gh api repos/firecrawl/firecrawl-mcp-server/contents/CLAUDE.md` |

For each repo that lacks a CLAUDE.md:
1. Read the repo's README, CONTRIBUTING.md, and codebase structure
2. Write a genuinely useful CLAUDE.md tailored to that specific project
3. The CLAUDE.md should help contributors using Claude Code, not be a template copy-paste
4. PR title: "Add CLAUDE.md for contributor onboarding"
5. PR body references the CLAUDE.md format documentation

### Bug Fix PRs

Check for labeled bugs in official repos:

```bash
gh search issues "label:bug" --repo anthropics/claude-code-action --state open --sort created --limit 10 --json number,title,url,createdAt,commentsCount
gh search issues "label:bug" --repo modelcontextprotocol/servers --state open --sort created --limit 10 --json number,title,url,createdAt,commentsCount
gh search issues "label:\"good first issue\"" --repo modelcontextprotocol/servers --state open --limit 10 --json number,title,url
```

For each fixable bug:
- Read the issue body and reproduction steps
- Assess whether we can fix it (language, complexity, domain knowledge)
- Note the estimated effort (quick regex fix vs substantial refactor)

---

## Step 5: Check Cookbook & Registry Status

```bash
# Cookbook
gh pr list -R anthropics/anthropic-cookbook --state merged --limit 5 --json title,mergedAt
gh pr list -R anthropics/anthropic-cookbook --state open --limit 5 --json title,createdAt

# MCP Registry
gh pr list -R docker/mcp-registry --state merged --limit 5 --json title,mergedAt
```

Note gaps in cookbook content (zero MCP notebooks, zero production deployment content) and prepare notebook proposals.

---

## Step 6: Scan Issues (Selective)

Only scan for issues where a guide genuinely, specifically answers the question. Do not draft comments where the link is the only value.

Use the same search queries as before but apply a much stricter filter:
- The issue must be unanswered (0 comments) or have a partial answer we can meaningfully extend
- Our guide must cover the SPECIFIC problem described, not just the general topic area
- The comment must be valuable even without any link
- Skip if another commenter already gave a complete answer

Max 2-3 issue comment drafts per report (not 5).

---

## Step 7: Generate Report

Save to `reports/github/YYYY-MM-DD/github-monitor.md`.

Also save copy-pasteable responses to `reports/github/YYYY-MM-DD/responses.md` with no extra formatting (directly pasteable into GitHub).

### Report Structure

```markdown
# GitHub Monitor Report

**Date:** {YYYY-MM-DD}
**Period:** Last 7 days

## Executive Summary

{3-5 bullet points of the most actionable items across all categories}

---

## 1. Discussion Replies

For each discussion opportunity:

### {Discussion Title}
- **Repo:** {repo} | **Discussion:** #{N} | **Comments:** {N} | **Unanswered:** Yes/No
- **URL:** {discussion URL}
- **Topic:** {what's being discussed}
- **Value we add:** {specific technical insight, not just a link}
- **Effort:** 15 min
- **Draft in responses.md:** Yes

---

## 2. Directory & Registry Submissions

For each submission target:

### {Repo Name} ({stars} stars)
- **URL:** {repo URL}
- **Format:** {PR to README / issue form / CLI tool / file structure}
- **What to submit:** {specific entry in exact format}
- **Activity:** {last merge date, active/slow/inactive}
- **Effort:** {30 min / 1 hour / 2 hours}
- **Ready-to-submit entry in responses.md:** Yes

---

## 3. Code PR Opportunities

### CLAUDE.md Contributions

| Repo | Stars | Has CLAUDE.md | Action | Effort |
|------|------:|:------------:|--------|--------|
| {repo} | {N} | No | Draft CLAUDE.md PR | 2-4 hours |

### Bug Fixes

| Repo | Issue | Title | Label | Effort |
|------|-------|-------|-------|--------|
| {repo} | #{N} | {title} | bug/good-first-issue | {estimate} |

---

## 4. Issue Comments (selective)

Only issues where our guide is genuinely the best answer.

### {Issue Title}
- **Repo:** {repo} | **Issue:** #{N} | **Comments:** {N}
- **URL:** {issue URL}
- **Draft in responses.md:** Yes

---

## 5. Cookbook & Registry Status

- **anthropic-cookbook:** {gap analysis, pending contributions}
- **MCP Registry:** {submission status}
- **Docker MCP Registry:** {submission status}

---

## 6. Weekly Tracking

| Date | Category | Repo | Action | Result |
|------|----------|------|--------|--------|
| {date} | {discussion/directory/PR/issue} | {repo} | {what was done} | {outcome} |

---

## Anti-Spam Compliance

| Repo | Comments This Week | Budget (max 2) | Status |
|------|-------------------|----------------|--------|
```

## Anti-Spam Rules

1. Max 2 comments per repo per week (issues + discussions combined)
2. Never comment on closed issues or answered discussions
3. Never bulk-comment (more than 3 across all repos in one day)
4. Always provide standalone value before linking
5. Only link when genuinely relevant
6. No generic praise, no em dashes, no AI cliches, no fabricated stories
7. Content must not read as AI-generated

## Quality Checklist

- [ ] Report has at least 3 actionable items per category
- [ ] Every draft is copy-pasteable directly into GitHub
- [ ] Discussion replies provide genuine technical value without requiring a link
- [ ] Directory submissions use the exact format required by each repo
- [ ] Code PR opportunities are verified (repo still lacks CLAUDE.md, bug still open)
- [ ] Issue comments are genuinely the best answer, not tangential
- [ ] Responses file has no extra markdown formatting that breaks on GitHub
- [ ] Previous report checked for already-actioned items
