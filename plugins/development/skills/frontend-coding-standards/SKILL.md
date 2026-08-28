---
name: frontend-coding-standards
description: "Front-end entry point for systemprompt.io — HTML standards, progressive enhancement doctrine, asset registration, and performance requirements. Routes to javascript-coding-standards and css-coding-standards, which are canonical for their languages."
version: "2.0.0"
git_hash: "0d054c8"
---

# Front-End Coding Standards

HTML standards and the front-end delivery workflow for systemprompt.io. Follow
without exception.

## Where the rules live

This skill no longer carries JavaScript or CSS rules. Each language has one
canonical source of truth, so a review can cite a rule instead of arguing with a
second copy of it.

| Subject | Skill |
|---------|-------|
| JavaScript — modules, rendering architectures, state, forbidden constructs | `javascript-coding-standards` |
| CSS — tokens, BEM, forbidden constructs, file limits | `css-coding-standards` |
| **HTML, progressive enhancement, asset registration, performance** | **this skill** |
| Colour science, typography scale, elevation | `visual-design-system` |
| Component recipes (cards, tables, forms, dashboards) | `component-patterns` |
| Container queries, `:has()`, subgrid, view transitions | `modern-css-patterns` |
| Micro-interactions, skeleton UI, motion choreography | `ux-interaction-patterns` |
| PDF factsheets and print one-pagers | `factsheet-design` |

## Core Principle

systemprompt.io uses progressive enhancement with static HTML/CSS and minimal
vanilla JavaScript. Every front-end file must be modular, framework-free, and
enhance -- never replace -- server-rendered content. CSS-only solutions are
always preferred over JavaScript. No frameworks, no build tools, no
transpilation.

## Language Separation Principle

**JavaScript files contain only JavaScript. CSS belongs in `.css` files or
`CSSStyleSheet` objects. HTML belongs in templates, in `<template>` elements, or
in the one sanctioned render-to-string architecture.**

Embedding one language inside another (CSS strings in JS, inline styles, HTML
assembled by ad-hoc concatenation) creates code no linter, formatter, or
language server can analyse. The two sanctioned rendering architectures and the
escaping contract that makes the second one safe are defined in
`javascript-coding-standards`.

## Code Locations

| Type | Location | Purpose |
|------|----------|---------|
| Components | `storage/files/js/components/` | Web Components and UI modules |
| Services | `storage/files/js/services/` | API calls and data fetching |
| Utils | `storage/files/js/utils/` | Pure helper functions |
| Pages | `storage/files/js/pages/` | Page-specific initialization |
| Stylesheets | `storage/files/css/` | All CSS files |
| Templates | `services/web/templates/` | Handlebars HTML templates |

Register all JS and CSS files in `extensions/web/src/extension.rs` `required_assets()`. Reference JS with `<script src="/js/filename.js" type="module" defer></script>`. Reference CSS with `<link rel="stylesheet" href="/css/filename.css">`.

---

## HTML Standards

### Required Structure

Every page template must use semantic HTML:

```html
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{DESCRIPTION}}">
  <title>{{TITLE}}</title>
  <link rel="stylesheet" href="/css/main.css">
</head>
<body>
  <a href="#main" class="sp-skip-link">Skip to content</a>
  <header role="banner">{{> header}}</header>
  <main id="main" role="main">{{> content}}</main>
  <footer role="contentinfo">{{> footer}}</footer>
  <script src="/js/pages/page.js" type="module" defer></script>
</body>
</html>
```

### Semantic Elements

| Use | Element | Never |
|-----|---------|-------|
| Page header | `<header>` | `<div class="header">` |
| Navigation | `<nav>` | `<div class="nav">` |
| Main content | `<main>` | `<div class="main">` |
| Content block | `<article>` or `<section>` | Unsemantic `<div>` wrapper |
| Sidebar | `<aside>` | `<div class="sidebar">` |
| Page footer | `<footer>` | `<div class="footer">` |
| Clickable action | `<button>` | `<div onclick>` or `<a href="#">` |
| Navigation link | `<a href="...">` | `<span onclick>` |

### Required Attributes

| Element | Required Attributes |
|---------|--------------------|
| `<html>` | `lang` |
| `<img>` | `alt`, `loading="lazy"`, `width`, `height` |
| `<a>` (external) | `rel="noopener noreferrer"` |
| `<button>` | `type` attribute |
| `<input>` | `<label>` association via `for`/`id` |
| `<svg>` (decorative) | `aria-hidden="true"` |
| `<svg>` (informative) | `role="img"`, `aria-label` |

### Heading Hierarchy

Single `<h1>` per page (the page title). Headings must not skip levels -- `<h1>` then `<h2>` then `<h3>`.

### Forbidden HTML

| Construct | Resolution |
|-----------|------------|
| `<div>` soup (nested divs without semantics) | Use semantic elements |
| Inline `style=""` attributes | Use CSS classes |
| Inline event handlers (`onclick=`) | Use `addEventListener()` |
| `<br>` for spacing | Use CSS margin/padding |
| `<table>` for layout | Use CSS Grid or Flexbox |
| `<font>`, `<center>`, `<marquee>` | Use CSS |
| Missing `alt` on `<img>` | Always provide `alt` text |
| `<div>` or `<span>` as buttons | Use `<button>` |
| HTML comments (`<!-- -->`) | Delete -- HTML documents itself. No comments in templates or compiled output |

### Template Syntax

Handlebars templates use `{{VAR}}` for escaped output and `{{{VAR}}}` for raw HTML. Template variables are provided by `PageDataProvider` and `ComponentRenderer` traits.

---

## Performance Requirements

| Requirement | Implementation |
|-------------|---------------|
| Non-blocking scripts | `type="module" defer` on all `<script>` tags |
| No render-blocking JS | Never place synchronous `<script>` in `<head>`. Exception: a single inline FOUC-prevention script that applies a stored theme class to `<html>` before first paint (must be under 5 lines, no network requests) |
| Lazy loading modules | Dynamic `import()` for non-critical features |
| Event delegation | Single listener on parent container |
| DOM batch reads/writes | Group reads before writes, use `requestAnimationFrame` |
| Animation performance | CSS transitions preferred, `requestAnimationFrame` for JS |
| Scroll behavior | `IntersectionObserver` -- never `scroll` event listeners |
| Image loading | `loading="lazy"` attribute on all below-fold images |
| No bundler | Native ES modules loaded directly by browser |
| Minimal JS footprint | Pages must function without JavaScript enabled |

## Accessibility Requirements

| Requirement | Implementation |
|-------------|---------------|
| Keyboard navigation | All interactive elements reachable via Tab, operable via Enter/Space |
| Focus management | Call `element.focus()` after dynamic content insertion |
| Focus visibility | Never remove `:focus-visible` outlines |
| Screen readers | `aria-label`, `aria-live="polite"`, `role` on custom elements |
| Reduced motion | Check `prefers-reduced-motion` before JS animation |
| Color contrast | WCAG AA minimum (4.5:1 for text, 3:1 for large text) |
| Skip links | `<a href="#main" class="sp-skip-link">` as first body child |
| Heading hierarchy | Single `<h1>`, no skipped levels |
| Form labels | Every input has an associated `<label>` |

Screen reader announcements for dynamic content:

```javascript
export function announceToScreenReader(message) {
  const region = document.querySelector('[data-live-region]');
  if (region) {
    region.textContent = '';
    requestAnimationFrame(() => { region.textContent = message; });
  }
}
```

Pair with HTML: `<div data-live-region aria-live="polite" class="sp-u-sr-only"></div>`

---

## Asset Registration Workflow

### Adding JavaScript

1. Create file in `storage/files/js/`
2. Register in `extensions/web/src/extension.rs` `required_assets()`
3. Run: `just build && systemprompt infra jobs run copy_extension_assets`
4. Reference in template: `<script src="/js/filename.js" type="module" defer></script>`

### Adding CSS

1. Create file in `storage/files/css/`
2. Register in `extensions/web/src/extension.rs` `required_assets()`
3. Run: `just build && systemprompt infra jobs run copy_extension_assets`
4. Reference in template: `<link rel="stylesheet" href="/css/filename.css">`

### Registration Example

```rust
fn required_assets(&self, paths: &SystemPaths) -> Vec<AssetDefinition> {
    let storage = paths.storage_files();
    vec![
        AssetDefinition::css(storage.join("css/main.css"), "css/main.css"),
        AssetDefinition::css(storage.join("css/components/card.css"), "css/components/card.css"),
        AssetDefinition::js(storage.join("js/components/sp-copy-button.js"), "js/components/sp-copy-button.js"),
        AssetDefinition::js(storage.join("js/pages/blog.js"), "js/pages/blog.js"),
    ]
}
```

## Validation Checklist — HTML

```bash
grep -rn '<!--' services/web/templates/ --include='*.hbs' && echo "FAIL: HTML comment in template"
grep -rn 'style="' services/web/templates/ --include='*.hbs' && echo "FAIL: inline style attribute"
grep -rn 'onclick=\|onchange=\|onsubmit=' services/web/templates/ && echo "FAIL: inline event handler"
grep -rn '<img' services/web/templates/ | grep -v 'alt=' && echo "FAIL: <img> without alt"
grep -rn '<table' services/web/templates/ | grep -v 'role=' && echo "WARN: verify <table> is tabular data, not layout"
grep -rn '<script' services/web/templates/ | grep -v 'type="module"' && echo "WARN: script without type=module defer"
wc -l services/web/templates/**/*.hbs | awk '$1 > 300 { print "FAIL: " $2 " exceeds 300 lines" }'
```

Manual verification:

- Single `<h1>` per page, no skipped heading levels
- Skip link is the first child of `<body>`
- Every `<input>` has an associated `<label>`
- Every external `<a>` carries `rel="noopener noreferrer"`
- Decorative `<svg>` is `aria-hidden`; informative `<svg>` has `role="img"` and a label
- The page is usable with JavaScript disabled
- `type="module" defer` on every `<script>`

For JavaScript and CSS validation, see the checklists in
`javascript-coding-standards` and `css-coding-standards`.

## Quick Reference

| Task | Command |
|------|---------|
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Full publish | `systemprompt infra jobs run publish_pipeline` |
| Prerender pages | `systemprompt infra jobs run page_prerender` |
| Build | `just build` |
