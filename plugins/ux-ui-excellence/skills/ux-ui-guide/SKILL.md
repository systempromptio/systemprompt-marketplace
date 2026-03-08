---
name: ux-ui-guide
description: "Entry point for ux-ui-excellence — routes to the right sub-skill for your task"
version: "1.0.0"
git_hash: "0000000"
---

# UX & UI Excellence

World-class UX and UI design standards for systemprompt.io. This plugin provides visual design quality, modern CSS techniques, interaction patterns, and component recipes that complement `frontend-coding-standards` (architecture, BEM naming, Web Components, accessibility).

**Always load `frontend-coding-standards` alongside any skill from this plugin.**

---

## Skills

### visual-design-system
**Load when:** defining colors, typography, spacing, elevation, dark mode, or branded corner tokens.
**Covers:** Three-tier token architecture (primitive/semantic/component), OKLCH color system with `color-mix()`, fluid typography with `clamp()`, spacing rhythm, shadow hierarchy, surface levels, branded asymmetric corners (`--sp-corners-*`), dark mode via `light-dark()`.

### modern-css-patterns
**Load when:** using or reviewing modern CSS features, modernizing legacy CSS, or building responsive components.
**Covers:** Container queries, `:has()`, subgrid, `@scope`, anchor positioning, scroll-driven animations, View Transitions API, `@starting-style`, `text-wrap: balance/pretty`, cascade layers (`@layer`), CSS nesting.

### ux-interaction-patterns
**Load when:** designing interactions, reviewing animation quality, implementing loading states, or optimizing perceived performance.
**Covers:** UX laws as code (Doherty Threshold, Fitts's Law, Hick's Law, Jakob's Law, Peak-End Rule, Miller's Law), animation timing standards, micro-interaction recipes (button, form, card, toggle, loading), skeleton UIs, optimistic UI, loading state hierarchy, performance UX, reduced motion alternatives.

### component-patterns
**Load when:** building or reviewing specific UI components, dashboards, or page layouts.
**Covers:** Cards (standard, metric, bento, horizontal), tables (data, responsive, expandable), forms (input groups, validation, multi-step, error summary), navigation (top bar, sidebar, breadcrumbs, tabs, pagination), dashboard layouts (F/Z-pattern, KPI rows, data density), data visualization (sparklines, progress, status, trends), empty states, feedback (toasts, alerts, dialogs).

---

## Task Router

| I want to... | Load these skills |
|--------------|-------------------|
| Build a new component | `component-patterns` + `visual-design-system` |
| Build a dashboard | `component-patterns` + `visual-design-system` |
| Review visual design quality | `visual-design-system` |
| Define or extend design tokens | `visual-design-system` |
| Implement dark mode | `visual-design-system` |
| Modernize existing CSS | `modern-css-patterns` |
| Add scroll animations or transitions | `modern-css-patterns` + `ux-interaction-patterns` |
| Build responsive components | `modern-css-patterns` |
| Review animation and interaction UX | `ux-interaction-patterns` |
| Add loading states or skeletons | `ux-interaction-patterns` |
| Optimize perceived performance | `ux-interaction-patterns` |
| Full page build or review | All four skills |

---

## Skill Dependencies

```
frontend-coding-standards (external, always required)
        |
        v
visual-design-system (foundational tokens, colors, type)
        |
        +---> modern-css-patterns (CSS techniques, independent)
        |
        +---> ux-interaction-patterns (animation, UX laws)
        |
        v
component-patterns (combines all three into component recipes)
```

**For any task:** always load `frontend-coding-standards` first. Then load the specific skill(s) from the task router above.
