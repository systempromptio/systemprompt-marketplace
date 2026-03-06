---
name: frontend-coding-standards
description: "Front-end coding standards for systemprompt.io - JavaScript, CSS, and HTML for static site generation with modular vanilla JS and Web Components"
---

# Front-End Coding Standards

All front-end code standards for systemprompt.io. Follow without exception.

## Core Principle

systemprompt.io uses progressive enhancement with static HTML/CSS and minimal vanilla JavaScript. Every front-end file must be modular, framework-free, and enhance -- never replace -- server-rendered content. CSS-only solutions are always preferred over JavaScript. No frameworks, no build tools, no transpilation.

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

### Template Syntax

Handlebars templates use `{{VAR}}` for escaped output and `{{{VAR}}}` for raw HTML. Template variables are provided by `PageDataProvider` and `ComponentRenderer` traits.

---

## CSS Standards

### File Organization

All CSS in `storage/files/css/`. One component per file. Register in `required_assets()`.

```
storage/files/css/
├── main.css              # Global resets, tokens, typography
├── layout.css            # Page layout, grid systems
├── components/
│   ├── card.css          # .sp-card component
│   ├── nav.css           # .sp-nav component
│   └── button.css        # .sp-button component
└── pages/
    ├── blog.css          # Blog-specific styles
    └── docs.css          # Documentation-specific styles
```

### Design Tokens

All design values as CSS custom properties with `--sp-` prefix:

```css
:root {
  --sp-color-primary: hsl(0, 0%, 35%);
  --sp-color-text: #111111;
  --sp-color-bg: #ffffff;
  --sp-color-border: hsl(0, 0%, 85%);
  --sp-font-sans: system-ui, -apple-system, sans-serif;
  --sp-font-mono: ui-monospace, monospace;
  --sp-space-xs: 0.25rem;
  --sp-space-sm: 0.5rem;
  --sp-space-md: 1rem;
  --sp-space-lg: 2rem;
  --sp-radius-sm: 0.25rem;
  --sp-radius-md: 0.5rem;
  --sp-transition-fast: 150ms ease;
}
```

### Naming Convention

BEM-inspired with `sp-` prefix:

| Type | Pattern | Example |
|------|---------|---------|
| Block | `.sp-{block}` | `.sp-card` |
| Element | `.sp-{block}__{element}` | `.sp-card__title` |
| Modifier | `.sp-{block}--{modifier}` | `.sp-card--featured` |
| State | `.is-{state}` | `.is-active`, `.is-visible` |
| Utility | `.sp-u-{utility}` | `.sp-u-sr-only` |

### CSS-First Patterns

JavaScript toggles classes or attributes. CSS implements all visual changes.

| Need | CSS Implementation | JS Role |
|------|--------------------|---------|
| Show/hide | `[hidden] { display: none; }` | Toggle `hidden` attribute |
| Animation | `transition` on class change | Add/remove trigger class |
| Responsive | `@media` / `@container` queries | None |
| Theme | `:root` / `.dark` custom properties | Toggle `.dark` on `<html>` |
| Scroll effects | `scroll-snap`, `position: sticky` | None |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` | None |

### Required Media Queries

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-color-scheme: dark) {
  :root {
    --sp-color-text: #e0e0e0;
    --sp-color-bg: #1a1a1a;
  }
}
```

### Mobile-First Responsive

Write base styles for mobile. Add complexity with `min-width` breakpoints:

```css
.sp-grid {
  display: grid;
  gap: var(--sp-space-md);
  grid-template-columns: 1fr;
}

@media (min-width: 48rem) {
  .sp-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 64rem) {
  .sp-grid { grid-template-columns: repeat(3, 1fr); }
}
```

### Forbidden CSS

| Construct | Resolution |
|-----------|------------|
| `!important` | Increase specificity or restructure selectors |
| `@import` | Use `<link>` tags for separate files |
| `float` for layout | Use Flexbox or Grid |
| Magic numbers | Use CSS custom properties |
| `z-index` hardcoded > 10 | Use `--sp-z-*` custom properties |
| `px` for font sizes | Use `rem` |
| ID selectors for styling | Use class selectors |
| Vendor prefixes manually | Use only standard properties with broad support |
| Inline `style` from JS | Use `classList` or `dataset` |

---

## JavaScript -- ES Module Standards

All files are native ES Modules. Named exports only. One module per file with a single responsibility. Import paths must include the `.js` extension for browser compatibility.

```javascript
import { getStoredPreference, setStoredPreference } from '../utils/storage.js';
import { THEME_KEY, DARK_CLASS } from '../utils/constants.js';

export function initThemeToggle(toggleElement) {
  const saved = getStoredPreference(THEME_KEY);
  if (saved === 'dark') {
    document.documentElement.classList.add(DARK_CLASS);
  }

  toggleElement.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle(DARK_CLASS);
    setStoredPreference(THEME_KEY, isDark ? 'dark' : 'light');
  });
}
```

Module entry points for pages import and initialize components:

```javascript
import { initThemeToggle } from '../components/theme-toggle.js';
import { initLazyLoad } from '../utils/lazy-load.js';

const toggle = document.querySelector('[data-theme-toggle]');
if (toggle) initThemeToggle(toggle);

initLazyLoad();
```

## JavaScript -- Language Rules

| Rule | Standard |
|------|----------|
| Variable declaration | `const` by default, `let` when reassignment needed |
| Equality | `===` always (only `== null` acceptable) |
| Functions | Arrow functions for non-method functions |
| Async | `async`/`await` over callbacks or `.then()` chains |
| Strings | Template literals for interpolation, single quotes otherwise |
| Iteration | `for...of` for arrays, array methods (`.map`, `.filter`) for transforms |
| Destructuring | Required for object/array access with 2+ properties |
| Spread | Prefer spread `...` over `Object.assign` |
| Optional chaining | Use `?.` and `??` over manual null checks |
| Indentation | 2 spaces |
| Semicolons | Required |
| Trailing commas | Required in multiline constructs |
| Comments | Forbidden -- code documents itself |

## JavaScript -- Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Variables, functions | camelCase | `fetchUserData`, `isVisible` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `API_BASE_URL` |
| Classes, Web Components | PascalCase | `ThemeToggle`, `SearchDialog` |
| Custom elements | kebab-case with `sp-` prefix | `<sp-theme-toggle>` |
| Files | kebab-case | `theme-toggle.js`, `api-client.js` |
| CSS custom properties | `--sp-` prefix | `--sp-color-primary` |
| Custom events | kebab-case with `sp-` prefix | `sp-theme-changed` |
| Data attributes | `data-` prefix | `data-action`, `data-target` |

### Allowed Abbreviations

`el`, `btn`, `nav`, `img`, `src`, `url`, `api`, `dom`, `fn`, `ctx`, `req`, `res`, `err`, `cfg`, `js`, `css`

## JavaScript -- Forbidden Constructs

| Construct | Resolution |
|-----------|------------|
| `var` keyword | Use `const` or `let` |
| `==` loose equality | Use `===` (only `== null` acceptable) |
| `eval()` | Remove -- forbidden |
| `document.write()` | Use DOM API methods |
| Inline event handlers (`onclick=`) | Use `addEventListener()` |
| Synchronous `XMLHttpRequest` | Use `fetch` with `async`/`await` |
| `with` statement | Remove -- forbidden |
| `arguments` object | Use rest parameters (`...args`) |
| `default export` | Use named exports |
| jQuery or legacy libraries | Use vanilla JS APIs |
| `innerHTML` with user input | Use `textContent` or sanitized templates |
| `setTimeout` for animation | Use `requestAnimationFrame` |
| Global `window.*` assignments | Use module scope |
| `alert()` / `confirm()` / `prompt()` | Use custom UI components |
| Comments (`//`, `/* */`) | Delete -- code documents itself |
| `console.log` in production | Remove before commit |
| `new Array()`, `new Object()` | Use literals `[]`, `{}` |
| `for...in` on arrays | Use `for...of` or array methods |

## JavaScript -- DOM Patterns

Use `[data-*]` attributes for JS hooks. Never bind behavior to CSS classes or IDs.

### Event Delegation

```javascript
export function initCardActions(container) {
  container.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-action]');
    if (!trigger) return;

    const handlers = {
      expand: () => toggleExpand(trigger),
      copy: () => copyToClipboard(trigger),
      dismiss: () => trigger.closest('[data-dismissible]')?.remove(),
    };

    handlers[trigger.dataset.action]?.();
  });
}
```

### Scroll-Based Behavior

```javascript
export function initLazyLoad(selector = '[data-lazy-src]') {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const img = entry.target;
      img.src = img.dataset.lazySrc;
      observer.unobserve(img);
    }
  });

  for (const el of document.querySelectorAll(selector)) {
    observer.observe(el);
  }
}
```

### DOM Batch Updates

Group reads before writes to avoid layout thrashing:

```javascript
export function updateCardHeights(cards) {
  const heights = cards.map((card) => card.offsetHeight);
  const max = Math.max(...heights);

  requestAnimationFrame(() => {
    for (const card of cards) {
      card.style.minHeight = `${max}px`;
    }
  });
}
```

## JavaScript -- Web Components

ALL reusable UI elements must be Web Components. Use `sp-` prefix. Shadow DOM for style encapsulation. Private fields for internal state.

```javascript
export class SpCopyButton extends HTMLElement {
  #button;
  #timeout;

  static get observedAttributes() {
    return ['target'];
  }

  connectedCallback() {
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-block; }
        button {
          cursor: pointer;
          border: 1px solid var(--sp-color-border, #ccc);
          border-radius: var(--sp-radius-sm, 0.25rem);
          background: transparent;
          padding: var(--sp-space-xs, 0.25rem) var(--sp-space-sm, 0.5rem);
          font: inherit;
          transition: color var(--sp-transition-fast, 150ms ease);
        }
        button:hover { background: var(--sp-color-bg-hover, #f5f5f5); }
        button[data-copied] { color: var(--sp-color-success, #16a34a); }
      </style>
      <button type="button" aria-label="Copy to clipboard">
        <slot>Copy</slot>
      </button>
    `;
    this.#button = this.shadowRoot.querySelector('button');
    this.#button.addEventListener('click', () => this.#copy());
  }

  disconnectedCallback() {
    clearTimeout(this.#timeout);
  }

  async #copy() {
    const target = document.querySelector(this.getAttribute('target'));
    if (!target) return;

    await navigator.clipboard.writeText(target.textContent);
    this.#button.setAttribute('data-copied', '');
    this.#button.setAttribute('aria-label', 'Copied');

    this.#timeout = setTimeout(() => {
      this.#button.removeAttribute('data-copied');
      this.#button.setAttribute('aria-label', 'Copy to clipboard');
    }, 2000);
  }
}

customElements.define('sp-copy-button', SpCopyButton);
```

Usage in HTML: `<sp-copy-button target="[data-code-block]">Copy</sp-copy-button>`

---

## File Limits

| Metric | Limit |
|--------|-------|
| JavaScript source file | 150 lines |
| CSS file | 200 lines |
| HTML template | 300 lines |
| Function length | 30 lines |
| Parameters per function | 4 |
| Import statements per file | 10 |
| Nesting depth | 3 levels |
| Web Component methods | 10 per class |
| CSS selectors per rule | 3 |
| CSS nesting depth | 3 levels |

## Performance Requirements

| Requirement | Implementation |
|-------------|---------------|
| Non-blocking scripts | `type="module" defer` on all `<script>` tags |
| No render-blocking JS | Never place synchronous `<script>` in `<head>` |
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
  if (region == null) return;
  region.textContent = '';
  requestAnimationFrame(() => { region.textContent = message; });
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

## Validation Checklist

Before committing any front-end code:

```bash
grep -rn 'var ' storage/files/js/ --include='*.js' && echo "FAIL: var keyword found"
grep -rn 'document\.write' storage/files/js/ --include='*.js' && echo "FAIL: document.write found"
grep -rn 'eval(' storage/files/js/ --include='*.js' && echo "FAIL: eval found"
grep -rn 'export default' storage/files/js/ --include='*.js' && echo "FAIL: default export found"
grep -rn '\.innerHTML\s*=' storage/files/js/ --include='*.js' && echo "WARN: innerHTML assignment"
grep -rn '!important' storage/files/css/ --include='*.css' && echo "FAIL: !important found"
wc -l storage/files/js/**/*.js | awk '$1 > 150 { print "FAIL: " $2 " exceeds 150 lines" }'
wc -l storage/files/css/**/*.css | awk '$1 > 200 { print "FAIL: " $2 " exceeds 200 lines" }'
```

Manual verification:

- All files under line limits
- Named exports only
- `type="module" defer` on all script tags
- Keyboard accessible (Tab through all interactive elements)
- Works without JavaScript (progressive enhancement)
- `prefers-reduced-motion` respected
- No comments in any JS or CSS file

## Quick Reference

| Task | Command |
|------|---------|
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Full publish | `systemprompt infra jobs run publish_pipeline` |
| Prerender pages | `systemprompt infra jobs run page_prerender` |
| Build | `just build` |
