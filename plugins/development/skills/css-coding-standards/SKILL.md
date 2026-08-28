---
name: css-coding-standards
description: "CSS coding standards for systemprompt.io — one --sp- token system in OKLCH with color-mix derivation, BEM naming, one component per file, CSS-first behaviour, forbidden constructs, comment rules, and file limits. Canonical source of truth for all CSS. Load before writing or reviewing any stylesheet."
version: "1.0.0"
git_hash: "3c29369"
---

# CSS Coding Standards

All CSS standards for systemprompt.io. Follow without exception.

This skill is **canonical for CSS**. `frontend-coding-standards` owns HTML and
the asset-registration workflow; `javascript-coding-standards` owns JS. The
design skills build *on top* of this one and never redefine what it owns:
`visual-design-system` (colour science, typography scale, elevation),
`component-patterns` (component recipes), `modern-css-patterns` (container
queries, `:has()`, subgrid, view transitions), `ux-interaction-patterns`
(motion and interaction). Where any of them appears to restate a rule below,
this skill wins.

## Core Principle

One token system, one component per file, and no value that is not a token.
CSS implements every visual change; JavaScript only toggles a class or an
attribute. A stylesheet is read top to bottom by a human — it is not a bundle,
not a cascade puzzle, and never a place where specificity is fought with
`!important`.

## Code Locations

| Context | Path | Token namespace |
|---------|------|-----------------|
| App shell | `bin/bridge/web/css/` (systemprompt-core) | `--sp-` |
| Static site | `storage/files/css/` (systemprompt-web) | `--sp-` |
| Sandboxed widget | `crates/domain/mcp/.../ui_renderer/templates/assets/css/` | `--sp-` |

**There is exactly one token namespace: `--sp-`.** A second namespace is a
defect, not a design choice — it means the same colour is defined twice, drifts
independently, and a white-label rebrand only moves half the product.

Structure inside any of them:

```
css/
├── tokens.css        # custom properties ONLY — no selectors that paint
├── reset.css         # reset and base element styles
├── typography.css    # font stacks, sizes, line heights
├── layout/           # page-level structure
└── <component>.css   # one file per component, named for its block
```

Register every stylesheet through the app's asset registration (see
`frontend-coding-standards`). Reference with `<link rel="stylesheet">` — never
`@import`.

---

## Design Tokens

Every design value is a custom property, `--sp-` prefixed, defined once in
`tokens.css`. Components consume tokens; they never define them and never
carry a fallback.

### Colour — OKLCH with a single literal accent

Colour is authored in **OKLCH**, and the brand accent is the *only* literal in
the accent family. Every other accent value is derived with `color-mix()` on
`var(--sp-accent)`, so a white-label theme injected as a later `:root` block
moves the entire family by setting one property — and keeps doing so under
`[data-theme]` and `[data-contrast]`.

```css
:root {
  --sp-accent:       oklch(0.72 0.17 52);
  --sp-accent-hover: color-mix(in oklch, var(--sp-accent) 93%, black);
  --sp-accent-soft:  color-mix(in oklch, var(--sp-accent) 12%, transparent);
  --sp-accent-ring:  color-mix(in oklch, var(--sp-accent) 40%, transparent);
}
```

`bin/bridge/web/css/tokens.css` is the reference implementation.

### Required token families

`--sp-accent-*`, `--sp-bg` / `--sp-bg-elev-N`, `--sp-line*`, `--sp-text` /
`--sp-muted*`, semantic status (`--sp-ok`, `--sp-warn`, `--sp-err`,
`--sp-danger`, `--sp-info`), `--sp-focus*`, `--sp-font-*`, `--sp-text-*`,
`--sp-space-*`, `--sp-radius-*` / `--sp-corners-*`, `--sp-shadow-*`,
`--sp-ease-*` / `--sp-dur-*`, `--sp-z-*`.

### Token usage rules

| Rule | Rationale |
|------|-----------|
| Every custom property starts with `--sp-` | One namespace; greppable; collision-proof |
| No literal colour outside `tokens.css` | A hex or bare `oklch()` in a component is an un-themeable value |
| No literal spacing, radius, z-index, duration, or easing | Use the token family |
| No `var(--sp-x, fallback)` in component CSS | Tokens are defined centrally and always exist; a fallback hides a missing token |
| A token is defined once and never redefined downstream | Theme axes (`[data-theme]`, `@media (prefers-color-scheme)`) are the only place a token is reassigned, and only in `tokens.css` |
| Contrast-critical tokens carry their measured ratio as a comment | A future edit that breaks WCAG must be visibly breaking a stated constraint |

## Naming Convention

BEM with the `sp-` prefix.

| Type | Pattern | Example |
|------|---------|---------|
| Block | `.sp-{block}` | `.sp-agent-row` |
| Element | `.sp-{block}__{element}` | `.sp-agent-row__action` |
| Modifier | `.sp-{block}--{modifier}` | `.sp-agents-status--loading` |
| State | `.is-{state}` | `.is-active`, `.is-open` |
| Utility | `.sp-u-{utility}` | `.sp-u-sr-only` |

The file is named for its block: `.sp-agent-row` lives in `agent-row.css`. A
class bound by JavaScript is a bug — JS binds to `[data-*]`, CSS binds to
classes.

## CSS-First Patterns

JavaScript toggles a class or an attribute. CSS does everything visual.

| Need | CSS implementation | JS role |
|------|--------------------|---------|
| Show/hide | `[hidden] { display: none }` | Toggle the `hidden` attribute |
| Animation | `transition` on a class change | Add/remove the trigger class |
| Responsive | `@media` / `@container` | None |
| Theme | `:root` / `[data-theme]` custom properties | Toggle the attribute |
| Scroll effects | `scroll-snap`, `position: sticky` | None |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` | None |
| Expand/collapse | `<details>`, or `[aria-expanded]` selectors | Toggle the ARIA attribute |

If a visual change can be expressed in CSS, expressing it in JS is a violation.

## Responsive and Required Queries

Mobile-first: base styles are the small case; complexity is added at
`min-width` breakpoints in `rem`. Prefer `@container` over `@media` when the
component's size, not the viewport's, is what matters.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

That block is required, lives in `reset.css`, and is the **only** sanctioned
use of `!important` in the codebase.

## Forbidden Constructs

| Construct | Resolution |
|-----------|------------|
| `!important` | Restructure the selector. Sole allowlist: the `prefers-reduced-motion` reset in `reset.css` |
| A second token namespace (`--mcpui-`, `--app-`, …) | Migrate every consumer to `--sp-` and delete the duplicate token file |
| Unprefixed custom properties (`--bg-base`) | `--sp-` prefix, always |
| Literal hex / `rgb()` / bare `oklch()` outside `tokens.css` | Use a `--sp-color` token |
| Magic numbers — hardcoded `px` spacing, radius, z-index | Use the token family |
| `px` for font size | `rem`, or a `--sp-text-*` token |
| `var()` fallback in component CSS | Define the token centrally |
| Inline `<style>` block in a template or HTML page | A registered `.css` file |
| Inline `style=""` attribute | A class, or a custom property set on the element |
| A `* { margin: 0; padding: 0 }` reset duplicated per page | One shared `reset.css` |
| `@import` | `<link>` |
| `float` for layout | Flexbox or Grid |
| ID selectors for styling | Class selectors |
| Selector nesting deeper than 3, or a 4-part descendant chain | BEM makes it flat — add an element class |
| Styling a `[data-*]` JS hook | Data attributes are JS hooks; add a class. Exception: genuine state attributes (`[hidden]`, `[aria-expanded]`, `[data-theme]`) |
| Vendor prefixes | Standard properties. Allowlist (no standard alternative): `-webkit-line-clamp`, `-webkit-box`, `-webkit-box-orient`, `::-webkit-scrollbar` family, `::-webkit-details-marker` |
| CSS file over 200 lines | Split by component or concern |
| Monolithic bundle files (`admin-bundle.css`) | Split into component files; fix the source, never the output |
| Alias declarations (`--old: var(--sp-new)`) | Replace `--old` at every consumer, delete the alias |
| Any file named `*-compat`, `*-legacy`, `*-shim`, `variables-compat.css` | Migrate the consumers and delete it |
| A focus style removed without replacement (`outline: none`) | Every focusable element keeps a visible indicator meeting 3:1 |

### Exceptions

| Context | Allowed | Why |
|---------|---------|-----|
| `@media (prefers-reduced-motion: reduce)` in `reset.css` | `!important` on duration/iteration/scroll-behavior | Must beat every animation regardless of specificity |
| `-webkit-line-clamp` pattern | `-webkit-box`, `-webkit-box-orient` | No standard `line-clamp` yet |
| Scrollbar and `<details>` marker styling | `::-webkit-scrollbar*`, `::-webkit-details-marker` | Only mechanism available |
| `@media print` | Literal colours, `!important` for visibility | Custom properties do not resolve reliably in print engines |
| Generated or vendored output | Line-limit and comment rules | Fix the source, not the artefact |

## Comment Rules

The Rust rule, applied to CSS. **WHAT-comments are banned; a non-obvious WHY is
permitted and rare.**

| Comment | Verdict |
|---|---|
| `/* Card styles */` above `.sp-card` | Delete |
| `/* Set the background */` | Delete |
| `/* Only --sp-accent is a literal. Everything else is a color-mix on it, so a white-label theme moves the whole family by setting one property. */` | Keep — the invariant the file exists to protect |
| `/* A focus indicator must reach 3:1 (WCAG 1.4.11). --sp-accent-soft measures 1.17:1 and --sp-accent-ring 2.01:1, so neither can be the ring. */` | Keep — an external constraint with measured evidence |
| A section divider banner (`/* --- Layout --- */`) | Delete — if a file needs sections, it needs splitting |

`bin/bridge/web/css/tokens.css` is the reference for comment quality.

## File Limits

| Unit | Limit |
|------|-------|
| CSS file | 200 lines |
| Selector nesting | 3 |
| Selector chain | 3 parts |

Over the limit, split by component. A component file that has grown past 200
lines is usually two components that share a name.

## Accessibility Requirements

- Text meets WCAG AA (4.5:1 body, 3:1 large); non-text UI meets 3:1.
- Focus indicators meet 3:1 against their own background — a translucent tint
  usually does not, so measure before choosing it.
- Colour is never the only carrier of state; pair it with a glyph, label, or
  shape.
- `prefers-reduced-motion` and `prefers-color-scheme` are both honoured.
- Nothing is hidden from assistive tech by `display: none` that should be
  `.sp-u-sr-only`.

## Review Checklist

- [ ] Every value a `--sp-` token? Any literal colour outside `tokens.css`?
- [ ] One token namespace across the whole surface?
- [ ] BEM, `sp-` prefixed, file named for the block?
- [ ] Could any JS-driven visual change be pure CSS?
- [ ] `!important` anywhere outside the reduced-motion reset?
- [ ] File under 200 lines, nesting under 4?
- [ ] Focus visible everywhere, contrast measured on contrast-critical tokens?
- [ ] Reduced-motion block present?
- [ ] Every comment a *why*?
