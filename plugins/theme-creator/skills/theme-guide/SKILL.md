---
name: theme-guide
description: "Entry point for theme-creator — routes to the right sub-skill for your task"
version: "1.0.0"
git_hash: "3bc512f"
---

# Theme Creator

Create, implement, and audit world-class website themes for systemprompt.io with color science, design tokens, and premium CSS patterns.

---

## Skills

### theme-design
**Load when:** designing a new theme, choosing colors, defining typography, or establishing visual principles.
**Covers:** OKLCH color science, palette generation, typography systems (type scales, font stacks, line height), spacing systems, design principles, visual harmony. This is the creative/design skill — start here when building a theme from scratch.

### theme-engineering
**Load when:** implementing a theme in CSS, building token architecture, or adding dark mode.
**Covers:** Three-tier token architecture (primitive/semantic/component), CSS implementation patterns, `--sp-` custom property definitions, dark mode systems, advanced theming techniques. Extends `frontend-coding-standards` conventions.

### theme-audit
**Load when:** reviewing, debugging, or improving an existing theme.
**Covers:** Systematic evaluation checklists, pass/fail criteria for every token layer, contrast checks, consistency audits, dark mode verification, typography validation. No subjective assessments — every check is measurable.

---

## Task Router

| I want to... | Load these skills |
|--------------|-------------------|
| Design a new theme from scratch | `theme-design` then `theme-engineering` |
| Choose a color palette | `theme-design` |
| Implement theme tokens in CSS | `theme-engineering` |
| Add dark mode to a theme | `theme-engineering` + `theme-design` |
| Review/audit an existing theme | `theme-audit` |
| Fix theme issues | `theme-audit` + `theme-engineering` |
| Full theme lifecycle | All three skills in order |

---

## Skill Dependencies

```
theme-design (creative: colors, typography, principles)
        |
        v
theme-engineering (implementation: tokens, CSS, dark mode)
        |
        v
theme-audit (validation: checklists, pass/fail criteria)
```

**Workflow:** Design → Engineer → Audit. For existing themes, start with `theme-audit` to identify issues, then use `theme-engineering` or `theme-design` to fix them.
