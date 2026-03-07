---
name: frontend-coding-standards
description: "Front-end coding standards for systemprompt.io - JavaScript, CSS, and HTML for static site generation with modular vanilla JS and Web Components"
version: "1.2.0"
git_hash: "efcef61"
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

All CSS in `storage/files/css/`. One component per file. Register in `required_assets()`. No monolithic bundle files -- every file stays under 200 lines. If a file grows beyond 200 lines, split by component or concern.

```
storage/files/css/
├── core/
│   ├── tokens.css            # Design tokens (custom properties only)
│   ├── reset.css             # CSS reset, base element styles
│   └── typography.css        # Font stacks, text sizes, line heights
├── layout/
│   ├── grid.css              # Page grid systems
│   ├── sidebar.css           # Sidebar layout
│   └── header.css            # Header layout
├── components/
│   ├── card.css              # .sp-card component
│   ├── nav.css               # .sp-nav component
│   ├── button.css            # .sp-button component
│   ├── badge.css             # .sp-badge component
│   ├── table.css             # .sp-table component
│   └── panel.css             # .sp-panel component
├── admin/
│   ├── control-center.css    # Control center page styles
│   ├── entity-table.css      # Entity table patterns
│   └── side-panel.css        # Side panel overlay
└── pages/
    ├── blog.css              # Blog-specific styles
    └── docs.css              # Documentation-specific styles
```

### Forbidden: Monolithic CSS Bundles

Never create or maintain a single large CSS file (e.g., `admin-bundle.css`) containing thousands of lines of styles for multiple components. Split into focused files by component. Each authored source file must be under 200 lines. Auto-generated or bundled output files are exempt from line limits -- violations must be fixed in the source modules that feed the bundle, not in the output.

### Design Tokens

All design values as CSS custom properties. Every custom property must use the `--sp-` prefix. No unprefixed custom properties like `--bg-base`, `--text-primary`, or `--space-1` -- these collide with third-party CSS and are impossible to grep for.

```css
:root {
  /* Colors */
  --sp-color-primary: hsl(0, 0%, 35%);
  --sp-color-text: #111111;
  --sp-color-text-secondary: #6b6b6b;
  --sp-color-bg: #ffffff;
  --sp-color-bg-surface: #f5f5f5;
  --sp-color-border: hsl(0, 0%, 85%);
  --sp-color-accent: #e8794a;
  --sp-color-success: #16a34a;
  --sp-color-warning: #f59e0b;
  --sp-color-danger: #ef4444;

  /* Typography */
  --sp-font-sans: system-ui, -apple-system, sans-serif;
  --sp-font-mono: ui-monospace, monospace;

  /* Spacing (use for all margin, padding, gap) */
  --sp-space-1: 0.25rem;
  --sp-space-2: 0.5rem;
  --sp-space-3: 0.75rem;
  --sp-space-4: 1rem;
  --sp-space-6: 1.5rem;
  --sp-space-8: 2rem;

  /* Borders */
  --sp-radius-sm: 0.25rem;
  --sp-radius-md: 0.5rem;
  --sp-radius-lg: 1rem;

  /* Motion */
  --sp-transition-fast: 150ms ease;

  /* Z-index scale */
  --sp-z-sticky: 1;
  --sp-z-dropdown: 100;
  --sp-z-sidebar: 900;
  --sp-z-modal: 1000;
  --sp-z-toast: 1100;
}
```

### Token Usage Rules

| Rule | Rationale |
|------|-----------|
| Every custom property starts with `--sp-` | Namespace prevents collisions, enables grep |
| No hardcoded hex/rgb colors in component CSS | Use `--sp-color-*` tokens |
| No hardcoded pixel spacing values | Use `--sp-space-*` tokens |
| No hardcoded `z-index` numbers | Use `--sp-z-*` tokens |
| No hardcoded `border-radius` values | Use `--sp-radius-*` tokens |
| Fallback values only in the token definition file | Components assume tokens exist -- no `var(--sp-color-bg, #fff)` fallbacks scattered everywhere |

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
| `!important` | Increase specificity or restructure selectors (only exception: `prefers-reduced-motion` reset) |
| `@import` | Use `<link>` tags for separate files |
| `float` for layout | Use Flexbox or Grid |
| Magic numbers (hardcoded `px` values) | Use `--sp-space-*` or `--sp-radius-*` tokens |
| `z-index` hardcoded numbers | Use `--sp-z-*` custom properties |
| `px` for font sizes | Use `rem` or `--sp-text-*` tokens |
| ID selectors for styling | Use class selectors |
| `-webkit-` vendor prefixes | Use standard properties only. Allowed exceptions (no standard alternative): `-webkit-line-clamp`, `-webkit-box-orient`, `-webkit-box` (required for line-clamp), `::-webkit-details-marker`, `::-webkit-scrollbar` family |
| Inline `style` from JS | Use `classList` or `dataset` |
| Unprefixed custom properties (`--bg-base`) | Use `--sp-` prefix on all custom properties |
| Hardcoded hex/rgb colors in component CSS | Use `--sp-color-*` tokens from `core/tokens.css` |
| CSS files over 200 lines | Split by component or concern |
| Monolithic bundle files | Split into focused component files |
| `var()` fallback values in component CSS | Tokens are defined centrally -- components don't need fallbacks |
| Hardcoded spacing (`padding: 32px`) | Use tokens: `padding: var(--sp-space-8)` |

### Exceptions

| Context | What's Allowed | Why |
|---------|---------------|-----|
| `@media (prefers-reduced-motion: reduce)` | `!important` on `animation-duration` and `transition-duration` | Must override all animations regardless of specificity |
| `-webkit-line-clamp` pattern | `-webkit-box`, `-webkit-box-orient`, `-webkit-line-clamp` | No standard `line-clamp` property yet |
| Scrollbar styling | `::-webkit-scrollbar` family | Only way to style scrollbars in WebKit/Blink |
| Summary marker | `::-webkit-details-marker` | Only way to hide default `<details>` marker in Safari |
| `@media print` | Hardcoded colors, `!important` for visibility | CSS custom properties may not resolve in all print engines; print requires explicit overrides |
| Auto-generated/bundled output | Line limit and comment rules exempt | Fix violations in source modules, not generated output |

---

## Architecture -- Event System

All interactive behavior flows through a single, centralized event delegation system. Every page has exactly one event registry. No module registers its own `document.addEventListener('click')` independently.

### The Event Registry Pattern

One file per page owns all delegated events. It maps `data-action` values to handler functions imported from feature modules.

```
storage/files/js/
├── events/
│   ├── admin-events.js      # All admin page event bindings
│   └── public-events.js     # All public page event bindings
├── handlers/
│   ├── dropdown.js           # Exports handler functions only
│   ├── delete-entity.js      # Exports handler functions only
│   └── modal.js              # Exports handler functions only
```

**Event registry (single source of truth for all click delegation):**

```javascript
import { handleDropdownToggle, handleDropdownAction } from '../handlers/dropdown.js';
import { handleDelete } from '../handlers/delete-entity.js';
import { handleModalOpen, handleModalClose } from '../handlers/modal.js';

const CLICK_ACTIONS = {
  menu: handleDropdownToggle,
  delete: handleDelete,
  'modal-open': handleModalOpen,
  'modal-close': handleModalClose,
};

export const initEvents = () => {
  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-action]');
    if (trigger) {
      CLICK_ACTIONS[trigger.dataset.action]?.(trigger, e);
    }
  });
};
```

**Handler modules export pure functions -- they never register listeners:**

```javascript
export const handleDropdownToggle = (trigger, e) => {
  e.stopPropagation();
  const menu = document.getElementById(trigger.dataset.target);
  if (menu) {
    const isOpen = !menu.hidden;
    closeAllDropdowns();
    if (!isOpen) menu.hidden = false;
  }
};
```

### Rules

| Rule | Rationale |
|------|-----------|
| One event registry per page entry point | Prevents duplicate listeners and missing bindings |
| Handler modules export functions, never call `addEventListener` | Keeps binding ownership in one place |
| All interactive elements use `data-action` | Uniform hook, discoverable, no hidden bindings |
| Every `data-action` value must exist in the registry | Dead actions are bugs -- fail loud |
| No `document.addEventListener('click')` outside the registry | Prevents the scattered-listener problem |
| No anonymous inline handlers | Every handler is named, importable, testable |

### Forbidden: Scattered Listener Registration

```javascript
export const initDropdown = () => {
  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-action="menu"]');
    if (trigger) open(trigger);
  });
};
```

**Why this is wrong:** Every module that does this creates an invisible, undiscoverable listener. When the `init` call is missing from bootstrap, the feature silently breaks. When multiple modules listen for the same event, they conflict. The event registry eliminates this entire class of bugs.

---

## Architecture -- Component Initialization

Page entry points are the single place where all features are initialized. No feature initializes itself on import. No side effects at module top level.

### Page Entry Point Pattern

```javascript
import { initEvents } from '../events/admin-events.js';
import { initPortal } from '../services/portal.js';

initPortal();
initEvents();
```

### Rules

| Rule | Rationale |
|------|-----------|
| Feature modules export `init` functions, never self-execute | Page entry point controls initialization order |
| No side effects at module top level | Importing a module must not change DOM or register listeners |
| Every `init*` call lives in the page entry point | One file to audit for "what runs on this page" |
| `init` functions are idempotent | Calling twice must not duplicate listeners or DOM nodes |

### Forbidden: Self-Initializing Modules

```javascript
const portal = document.createElement('div');
document.body.appendChild(portal);

document.addEventListener('click', handler);
```

**Why this is wrong:** This code runs on import. If the module is imported but the feature isn't needed, it still mutates the DOM. If it's imported twice (directly and transitively), it creates duplicate state. Initialization belongs in an explicit `init()` call from the page entry point.

---

## Architecture -- Overlay and Portal Pattern

Dropdowns, modals, tooltips, and toasts that render outside their DOM parent use a single shared portal. The portal is a positioned container that overlays host content.

### Standard Portal

```javascript
let portalEl = null;

export const initPortal = () => {
  if (portalEl) return;
  portalEl = document.createElement('div');
  portalEl.id = 'sp-portal';
  portalEl.setAttribute('data-portal', '');
  document.body.appendChild(portalEl);
};

export const getPortal = () => portalEl;
```

### Overlay Lifecycle

Every overlay follows open/position/close with cleanup:

```javascript
import { getPortal } from '../services/portal.js';

let activeOverlay = null;

export const openOverlay = (triggerEl, contentEl) => {
  closeOverlay();
  const clone = contentEl.cloneNode(true);
  clone.hidden = false;
  positionRelativeTo(clone, triggerEl);
  getPortal().appendChild(clone);
  activeOverlay = { trigger: triggerEl, element: clone };
};

export const closeOverlay = () => {
  if (activeOverlay) {
    activeOverlay.element.remove();
    activeOverlay = null;
  }
};
```

### Rules

| Rule | Rationale |
|------|-----------|
| One portal element for the entire page | Prevents z-index wars and stacking context bugs |
| `initPortal()` called from page entry point | Explicit, predictable, no side effects on import |
| Every `open` has a corresponding `close` that removes DOM nodes | Prevents leaked elements |
| Overlay state is module-scoped (`activeOverlay`) | Single source of truth for what's open |
| Position overlays with `getBoundingClientRect()` + portal offset | Works regardless of DOM nesting |
| Cloned content uses event delegation (not cloned listeners) | Cloned nodes lose `addEventListener` bindings -- delegation handles them |

### Forbidden: Ad-Hoc Overlay Patterns

| Anti-Pattern | Resolution |
|--------------|------------|
| Creating a new container div per overlay type | Use the shared portal |
| Toggling `display` on in-place elements for overlays | Clone into portal for correct stacking |
| Relying on cloned event listeners | Use event delegation via the event registry |
| Multiple `z-index` layers across components | Single portal with `z-index` on `#sp-portal` only |
| Opening without tracking active state | Always track in module-scoped variable for cleanup |

---

## Architecture -- State Ownership

Every piece of UI state has exactly one owner. No two modules may independently track the same state.

### Rules

| Rule | Rationale |
|------|-----------|
| State lives in the module that manages the feature | Dropdown open/close state lives in `dropdown.js` |
| DOM is the source of truth for visibility | Check `hidden` attribute, not a JS boolean |
| No global state objects or event buses | Direct imports between modules |
| Custom events (`sp-*`) for cross-feature communication | Loose coupling when features genuinely need to react to each other |
| `dataset` attributes for element-specific config | `data-target`, `data-entity-id` -- not JS lookups |

### Cross-Feature Communication

When one feature must react to another (e.g., close dropdown when modal opens), use custom events:

```javascript
export const openModal = (trigger) => {
  document.dispatchEvent(new CustomEvent('sp-overlay-open', { detail: { type: 'modal' } }));
};

document.addEventListener('sp-overlay-open', closeOverlay);
```

---

## Architecture -- Single Implementation Rule

Every UI capability has exactly one implementation. Duplicate systems are the most expensive form of tech debt -- they fragment behavior, multiply bugs, and confuse contributors.

### One Implementation Per Concern

| Concern | Single Owner | Forbidden Duplicates |
|---------|-------------|---------------------|
| Toast notifications | `sp-toast` Web Component | No imperative `toast.js` creating DOM manually |
| Confirm dialogs | `sp-confirm-dialog` Web Component | No imperative `confirm.js` building overlays |
| Dropdowns/menus | `services/dropdown.js` | No per-page dropdown implementations |
| Modals/overlays | Shared portal + overlay service | No `let overlay = null` in each feature module |
| Side panels | `services/entity-common.js` | No per-page panel open/close logic |
| Table row expansion | `sp-expand-row` component | No per-page `data-expand-row` click handlers |

### Rules

| Rule | Rationale |
|------|-----------|
| Web Components over imperative DOM builders | Encapsulated, reusable, self-contained lifecycle |
| When a Web Component exists, delete the imperative version | Two implementations = two bug surfaces |
| New UI patterns start as shared services | Prevent per-page reimplementation |
| Audit before building | Search `services/` and `components/` before writing new overlay/toast/dialog code |

### Forbidden: Per-Page Reimplementation

```javascript
let overlay = null;
const openOverlay = () => {
  overlay = document.createElement('div');
  overlay.className = 'custom-overlay';
  document.body.appendChild(overlay);
};
```

**Why this is wrong:** Every module that creates its own overlay div, tracks its own `let overlay = null` state, and appends to `document.body` independently produces a parallel system that doesn't coordinate with other overlays, doesn't share z-index management, and duplicates open/close/cleanup logic. Use the shared portal and overlay service.

---

## Architecture -- API and Fetch Pattern

All HTTP requests go through a single API wrapper. No raw `fetch()` calls in page or feature modules.

### The API Service

```javascript
export const API_BASE = '/api/public/admin';

export const apiFetch = async (path, options = {}) => {
  const resp = await fetch(API_BASE + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!resp.ok) {
    const text = await resp.text();
    const err = new Error(text || resp.statusText);
    showToast(err.message, 'error');
    throw err;
  }
  return resp.json();
};
```

### Rules

| Rule | Rationale |
|------|-----------|
| All requests use `apiFetch()` or `apiGet()` | Consistent headers, credentials, error handling |
| No raw `fetch()` in page modules | Prevents inconsistent error handling and missing credentials |
| No manual `credentials: 'include'` scattered across files | The wrapper handles this |
| Error handling lives in the wrapper | Pages don't need try/catch for toast display |
| Custom error handling uses the wrapper + post-processing | Override behavior by catching the thrown error, not by bypassing the wrapper |

### Forbidden: Raw Fetch in Page Modules

```javascript
const resp = await fetch('/api/public/admin/org/plugins', {
  method: 'DELETE',
  credentials: 'include',
});
const data = await resp.json().catch(() => ({}));
if (!resp.ok) showToast(data.error || 'Failed', 'error');
```

**Why this is wrong:** Every raw fetch call reinvents credential handling, content-type headers, error extraction, and toast display. When the API base URL changes, auth strategy changes, or error format changes, every call site needs updating. Use `apiFetch()`.

---

## Architecture -- Error Handling

Errors are handled consistently through layered responsibility. The API wrapper handles network/HTTP errors. Feature modules handle business logic errors. No silent failures.

### Error Handling Hierarchy

| Layer | Responsibility | Pattern |
|-------|---------------|---------|
| API wrapper (`apiFetch`) | HTTP errors, network failures | Shows error toast, throws error |
| Feature module | Business logic (validation, conflicts) | Catches thrown error, shows specific feedback |
| Page entry point | Initialization failures | Wraps `init*()` in try/catch as needed |

### Rules

| Rule | Rationale |
|------|-----------|
| No empty `.catch(() => {})` | Silent failures hide bugs and confuse users |
| No `.catch(() => ({}))` to swallow errors as empty objects | Masks whether the request succeeded |
| `async`/`await` with `try`/`catch` over `.then().catch()` chains | Readable, debuggable, consistent |
| Error messages come from the API response, not hardcoded strings | Accurate, localizable, maintainable |
| Failed operations must give user feedback | Toast, inline message, or state reset -- never silent |

### Forbidden: Silent and Inconsistent Error Handling

```javascript
apiFetch('/plugins/' + pid + '/env').catch(() => {});

const data = await resp.json().catch(() => ({}));
showToast(data.error || 'Failed to delete', 'error');
```

**Why this is wrong:** `.catch(() => {})` silently swallows errors. `.catch(() => ({}))` converts failures into empty success objects, making downstream code unable to distinguish success from failure. The hardcoded fallback message 'Failed to delete' will be wrong when the endpoint changes purpose.

---

## Architecture -- Escape Key and Focus Trap Consolidation

Escape key handling and click-outside-to-close must not be scattered across modules. These are cross-cutting concerns owned by the overlay system.

### Rules

| Rule | Rationale |
|------|-----------|
| One Escape key listener for the entire page | In the event registry or overlay manager |
| Escape closes the topmost overlay | Stack-based: modal over dropdown, Escape closes modal first |
| Click-outside-to-close lives in the overlay manager | Not in each feature module's init function |
| Each feature module exports `close()` but never registers its own Escape listener | Overlay manager calls `close()` on the active overlay |

### Forbidden: Per-Module Escape Handlers

```javascript
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && sidebar.classList.contains('open')) close();
});
```

**Why this is wrong:** When 5+ modules each register their own Escape handler, they all fire simultaneously. Order depends on registration timing. There's no concept of "which overlay is on top." The overlay manager should track a stack and close only the topmost.

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
| `innerHTML` for multi-element HTML | Use `<template>` elements with `cloneNode` and DOM API. In Web Components, use Adopted StyleSheets + static template singleton |
| `setTimeout` for animation | Use `requestAnimationFrame` |
| Global `window.*` assignments | Use module scope |
| `alert()` / `confirm()` / `prompt()` | Use custom UI components |
| Comments (`//`, `/* */`) | Delete -- code documents itself. Exception: comments inserted by build tools in generated output are acceptable |
| `console.log` in production | Remove before commit |
| `new Array()`, `new Object()` | Use literals `[]`, `{}` |
| `for...in` on arrays | Use `for...of` or array methods |
| HTML string building (multi-element) | Use `<template>` elements with `cloneNode` and DOM API |
| Inline `style` in JS-generated HTML | Use CSS classes defined in stylesheets |
| Unused imports | Remove -- every import must be referenced in the module |
| Reimplementing shared utilities | Reuse existing functions from `services/` and `utils/` |
| `document.addEventListener('click')` in feature modules | Register in the event registry only |
| Side effects at module top level | Wrap in `init()` function, call from page entry point |
| Multiple portal/container elements | Use single shared portal from `services/portal.js` |
| Handler modules calling `addEventListener` | Handlers export pure functions, registry binds them |
| Tracking overlay state in multiple modules | One module owns open/close state per overlay type |
| `cloneNode` without event delegation | Cloned nodes lose listeners -- use `data-action` delegation |
| Raw `fetch()` in page modules | Use `apiFetch()` or `apiGet()` from `services/api.js` |
| `.catch(() => {})` empty error handlers | Handle errors visibly -- toast, inline message, or state reset |
| `.catch(() => ({}))` swallowing errors as empty objects | Let errors propagate or handle them explicitly |
| `.then().catch()` chains | Use `async`/`await` with `try`/`catch` |
| Hardcoded API base URLs | Import `API_BASE` from `services/api.js` |
| Duplicate toast/dialog/overlay implementations | Use the single shared Web Component or service |
| Per-module `document.addEventListener('keydown', ... 'Escape')` | Escape handling lives in the overlay manager only |
| `let overlay = null` state in feature modules | Use the shared overlay/portal service |
| Manual `credentials: 'include'` on fetch calls | The `apiFetch()` wrapper handles credentials |
| Early returns (`if (!x) return;`) | Use structured `if`/`else` blocks -- handle all paths explicitly, never bail out with guard clauses |
| `this.shadowRoot.innerHTML` in Web Components | Use Adopted StyleSheets + static `<template>` singleton with `cloneNode` |
| Per-instance `<style>` in Shadow DOM via innerHTML | Use `new CSSStyleSheet()` + `adoptedStyleSheets` -- parsed once, shared across all instances |

## JavaScript -- DOM Patterns

Use `[data-*]` attributes for JS hooks. Never bind behavior to CSS classes or IDs.

### Event Delegation

```javascript
export function initCardActions(container) {
  container.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-action]');
    if (trigger) {
      const handlers = {
        expand: () => toggleExpand(trigger),
        copy: () => copyToClipboard(trigger),
        dismiss: () => trigger.closest('[data-dismissible]')?.remove(),
      };
      handlers[trigger.dataset.action]?.();
    }
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

## JavaScript -- HTML Rendering Hierarchy

HTML belongs in HTML templates, not in JavaScript strings. When JS must render dynamic content, use the approach matching the complexity:

| Complexity | Approach | Use For |
|-----------|----------|---------|
| Attribute/class toggle | Toggle class or attribute on existing element | Show/hide, active states, theme switching |
| Single element | `document.createElement` + `textContent` | Badge, status indicator, simple label |
| Structured content | `<template>` element + `cloneNode` + DOM API | Detail panels, form layouts, list items, cards |
| Reusable interactive widget | Web Component with Shadow DOM + Adopted StyleSheets + static template singleton | Dialogs, toasts, copy buttons, complex controls |

### The `<template>` Pattern

Place `<template>` elements in Handlebars templates. Clone and populate them from JavaScript using DOM API -- never build HTML strings.

**HTML template (in Handlebars):**

```html
<template id="tpl-detail-section">
  <div class="detail-section">
    <strong data-slot="label"></strong>
    <p class="detail-value" data-slot="value"></p>
  </div>
</template>

<template id="tpl-badge">
  <span class="badge badge-subtle" data-slot="text"></span>
</template>
```

**JavaScript (clone and populate):**

```javascript
const fillTemplate = (id, slots) => {
  const tpl = document.getElementById(id);
  if (tpl) {
    const frag = tpl.content.cloneNode(true);
    for (const [name, value] of Object.entries(slots)) {
      const el = frag.querySelector(`[data-slot="${name}"]`);
      if (el) el.textContent = value;
    }
    return frag;
  }
  return null;
};

const renderSkillDetail = (container, data) => {
  const section = fillTemplate('tpl-detail-section', {
    label: 'Description',
    value: data.description || 'No description',
  });
  if (section) container.appendChild(section);

  if (data.tags?.length) {
    for (const tag of data.tags) {
      const badge = fillTemplate('tpl-badge', { text: tag });
      if (badge) container.appendChild(badge);
    }
  }
};
```

### Anti-Pattern: HTML String Building

The following pattern is **forbidden** -- it mixes concerns, embeds inline styles, and is difficult to maintain:

```javascript
let html = '<div class="detail-section">' +
  '<strong>Description</strong>' +
  '<p style="margin:var(--space-1) 0;color:var(--text-secondary)">' +
  escapeHtml(data.description) + '</p></div>';
body.innerHTML = html;
```

**Why this is wrong:**
- HTML structure belongs in templates, not JS strings
- Inline `style` attributes bypass the CSS design token system
- String concatenation is error-prone and hard to read
- No separation of concerns between markup and behavior

### Using `document.createElement` for Simple Elements

For a single element with text content, use DOM API directly:

```javascript
const createBadge = (text, variant = 'subtle') => {
  const span = document.createElement('span');
  span.className = `badge badge-${variant}`;
  span.textContent = text;
  return span;
};
```

---

## JavaScript -- Web Components

ALL reusable UI elements must be Web Components. Use `sp-` prefix. Shadow DOM for style encapsulation. Private fields for internal state.

### Required Pattern: Adopted StyleSheets + Static Template Singleton

Web Components MUST separate styles, structure, and behavior. CSS and templates are created once at module scope and shared across all instances.

| Concern | Technique | Why |
|---------|-----------|-----|
| Styles | `new CSSStyleSheet()` + `adoptedStyleSheets` | Parsed once, shared across all instances -- no per-instance overhead |
| Structure | Static `<template>` element + `cloneNode(true)` | Created once at module scope, cloned per instance |
| Behavior | Private fields + `addEventListener` in `connectedCallback` | Clean encapsulation, no leaking state |

### Forbidden in Web Components

| Construct | Resolution |
|-----------|------------|
| `this.shadowRoot.innerHTML = \`...\`` | Use static template singleton with `cloneNode` |
| `<style>` inside innerHTML template literals | Use `new CSSStyleSheet()` + `adoptedStyleSheets` |
| Per-instance CSS parsing | Define stylesheet at module scope, share via `adoptedStyleSheets` |
| Inline HTML strings in `connectedCallback` | Create `<template>` at module scope, clone in callback |

### Example: SpCopyButton

```javascript
const sheet = new CSSStyleSheet();
sheet.replaceSync(`
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
`);

const template = document.createElement('template');
template.innerHTML = `
  <button type="button" aria-label="Copy to clipboard">
    <slot>Copy</slot>
  </button>
`;

export class SpCopyButton extends HTMLElement {
  #button;
  #timeout;

  static get observedAttributes() {
    return ['target'];
  }

  connectedCallback() {
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.adoptedStyleSheets = [sheet];
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    this.#button = this.shadowRoot.querySelector('button');
    this.#button.addEventListener('click', () => this.#copy());
  }

  disconnectedCallback() {
    clearTimeout(this.#timeout);
  }

  async #copy() {
    const target = document.querySelector(this.getAttribute('target'));
    if (target) {
      await navigator.clipboard.writeText(target.textContent);
      this.#button.setAttribute('data-copied', '');
      this.#button.setAttribute('aria-label', 'Copied');

      this.#timeout = setTimeout(() => {
        this.#button.removeAttribute('data-copied');
        this.#button.setAttribute('aria-label', 'Copy to clipboard');
      }, 2000);
    }
  }
}

customElements.define('sp-copy-button', SpCopyButton);
```

Usage in HTML: `<sp-copy-button target="[data-code-block]">Copy</sp-copy-button>`

### Why This Pattern

- **CSS parsed once** -- `CSSStyleSheet` is created at module scope, shared by every instance via `adoptedStyleSheets`. No re-parsing per element.
- **Template created once** -- The `<template>` element is built once at module scope. Each instance clones it with `cloneNode(true)` -- no HTML parsing per instance.
- **Clean separation** -- Styles, structure, and behavior live in distinct blocks. Easy to read, easy to maintain.
- **No innerHTML in connectedCallback** -- Eliminates the anti-pattern of mixing CSS + HTML in a template literal assigned to `shadowRoot.innerHTML`.

**Note:** The `template.innerHTML` assignment at module scope is acceptable because it runs exactly once (not per instance) and is the standard way to define a template element's content. This is categorically different from `this.shadowRoot.innerHTML` which runs per instance.

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

## Validation Checklist

Before committing any front-end code:

```bash
grep -rn 'var ' storage/files/js/ --include='*.js' && echo "FAIL: var keyword found"
grep -rn 'document\.write' storage/files/js/ --include='*.js' && echo "FAIL: document.write found"
grep -rn 'eval(' storage/files/js/ --include='*.js' && echo "FAIL: eval found"
grep -rn 'export default' storage/files/js/ --include='*.js' && echo "FAIL: default export found"
grep -rn '\.innerHTML\s*=' storage/files/js/ --include='*.js' && echo "WARN: innerHTML assignment"
grep -rn 'shadowRoot\.innerHTML' storage/files/js/ --include='*.js' && echo "FAIL: shadowRoot.innerHTML -- use adoptedStyleSheets + template.cloneNode"
grep -rn '!important' storage/files/css/ --include='*.css' | grep -v 'prefers-reduced-motion' && echo "FAIL: !important found outside reduced-motion reset"
wc -l storage/files/js/**/*.js | awk '$1 > 150 { print "FAIL: " $2 " exceeds 150 lines" }'
wc -l storage/files/css/**/*.css | awk '$1 > 200 { print "FAIL: " $2 " exceeds 200 lines" }'
grep -rn -- '--[a-z]' storage/files/css/ --include='*.css' | grep -v -- '--sp-' | grep -v -- '--webkit' | grep -v -- '--color-scheme' && echo "WARN: custom property missing --sp- prefix"
grep -rn '-webkit-' storage/files/css/ --include='*.css' | grep -v 'line-clamp\|box-orient\|-webkit-box\|scrollbar\|details-marker' && echo "WARN: vendor prefix -- use standard property"
grep -rn 'padding:\s*[0-9]\+px\|margin:\s*[0-9]\+px\|gap:\s*[0-9]\+px' storage/files/css/ --include='*.css' && echo "WARN: hardcoded px spacing -- use --sp-space-* tokens"
grep -rn '#[0-9a-fA-F]\{3,8\}' storage/files/css/components/ storage/files/css/admin/ storage/files/css/pages/ --include='*.css' && echo "WARN: hardcoded color in component CSS -- use --sp-color-* tokens"
grep -rn "html += \|html = '<\|\.innerHTML = '<" storage/files/js/ --include='*.js' && echo "WARN: HTML string building in JS -- use <template> elements"
grep -rn "style=\"" storage/files/js/ --include='*.js' && echo "FAIL: inline style attributes in JS strings"
grep -rn 'if\s*(!' storage/files/js/ --include='*.js' | grep 'return;' && echo "WARN: early return found -- use structured if/else blocks"
for f in storage/files/js/**/*.js; do
  while IFS= read -r line; do
    [[ "$line" =~ import.*\{(.+)\}.*from ]] && {
      IFS=',' read -ra names <<< "${BASH_REMATCH[1]}"
      for name in "${names[@]}"; do
        name=$(echo "$name" | xargs)
        count=$(grep -c "$name" "$f")
        [ "$count" -le 1 ] && echo "WARN: $f -- '$name' imported but possibly unused"
      done
    }
  done < "$f"
done
```

Architecture validation:

```bash
grep -rn "document\.addEventListener\s*(\s*['\"]click['\"]" storage/files/js/ --include='*.js' | grep -v '/events/' && echo "FAIL: click listener outside events/ registry"
grep -rn "document\.body\.appendChild\|document\.body\.insertBefore" storage/files/js/ --include='*.js' | grep -v '/services/portal' && echo "FAIL: DOM append outside portal service"
grep -rn "\.catch\s*(\s*(\s*)\s*=>\s*{}\s*)" storage/files/js/ --include='*.js' && echo "FAIL: empty .catch() handler -- silent error swallowing"
grep -rn "\.catch\s*(\s*(\s*)\s*=>\s*(\s*{}\s*)\s*)" storage/files/js/ --include='*.js' && echo "FAIL: .catch(() => ({})) -- error swallowed as empty object"
grep -rn "fetch\s*(" storage/files/js/pages/ --include='*.js' && echo "FAIL: raw fetch() in page module -- use apiFetch()"
grep -rn "credentials:\s*['\"]include['\"]" storage/files/js/ --include='*.js' | grep -v '/services/api' && echo "FAIL: manual credentials outside api.js wrapper"
grep -rn "let overlay\s*=\s*null\|let modal\s*=\s*null\|let popup\s*=\s*null" storage/files/js/ --include='*.js' | grep -v '/services/' && echo "FAIL: ad-hoc overlay state in feature module"
grep -rn "document\.addEventListener.*Escape" storage/files/js/ --include='*.js' | grep -v '/events/' | grep -v '/services/' && echo "FAIL: per-module Escape handler -- use overlay manager"
grep -rn "^\s*//\|/\*" storage/files/js/ --include='*.js' && echo "FAIL: comments found in JS"
for f in storage/files/js/handlers/*.js storage/files/js/services/*.js; do
  head -20 "$f" | grep -q "addEventListener" && echo "FAIL: $f registers listeners -- handlers export functions only"
done
```

Manual verification:

- All files under line limits
- Named exports only
- Every import is used in the module
- No HTML string building in JS (use `<template>` elements)
- No `shadowRoot.innerHTML` in Web Components -- use `adoptedStyleSheets` + static template `cloneNode`
- No early returns (`if (!x) return;`) -- use structured `if`/`else` control flow
- Web Components use module-scope `CSSStyleSheet` and `<template>` singletons, not per-instance parsing
- No inline `style` attributes in JS-generated HTML
- `type="module" defer` on all script tags
- Keyboard accessible (Tab through all interactive elements)
- Works without JavaScript (progressive enhancement)
- `prefers-reduced-motion` respected
- No comments in any JS or CSS file
- Every `data-action` value has a corresponding handler in the event registry
- No `document.addEventListener('click')` outside the event registry
- All overlays use the shared portal -- no ad-hoc containers
- Handler modules export pure functions -- no listener registration
- Page entry point is the only file calling `init*` functions
- No self-executing code at module top level (no side effects on import)
- No raw `fetch()` in page modules -- all requests through `apiFetch()`
- No empty `.catch(() => {})` or `.catch(() => ({}))` error swallowing
- No duplicate implementations (check: is there already a toast/dialog/overlay/panel service?)
- No per-module Escape key handlers -- overlay manager owns Escape
- No `let overlay = null` ad-hoc state in feature modules
- No hardcoded API base URLs -- import from `services/api.js`
- Web Component exists? Use it. Don't build an imperative alternative
- Every JS file under 150 lines, every function under 30 lines

## Quick Reference

| Task | Command |
|------|---------|
| Copy assets | `systemprompt infra jobs run copy_extension_assets` |
| Full publish | `systemprompt infra jobs run publish_pipeline` |
| Prerender pages | `systemprompt infra jobs run page_prerender` |
| Build | `just build` |
