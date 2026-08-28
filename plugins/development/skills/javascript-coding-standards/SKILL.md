---
name: javascript-coding-standards
description: "JavaScript coding standards for systemprompt.io — native ES modules, Web Components, the two sanctioned rendering architectures, state ownership, forbidden constructs, comment rules, and file limits. Canonical source of truth for all JS. Load before writing or reviewing any JavaScript."
version: "1.0.0"
git_hash: "0d054c8"
---

# JavaScript Coding Standards

All JavaScript standards for systemprompt.io. Follow without exception.

This skill is **canonical for JavaScript**. `frontend-coding-standards` owns HTML
and the asset-registration workflow; `css-coding-standards` owns CSS; the four
design skills (`visual-design-system`, `component-patterns`,
`modern-css-patterns`, `ux-interaction-patterns`) own visual and interaction
design. None of them restate the rules below, and where any of them appears to,
this skill wins.

## Core Principle

Framework-free, build-free, native ES modules. Every module is one
responsibility, imported explicitly, with no side effects at load. The code
documents itself; the only prose it carries is a *why* the code cannot express.
There is exactly one implementation of each concern and no compatibility layer
bridging to an older one.

## Code Locations

Two runtimes exist, with different rendering rules and the same language rules.
Know which one you are in before writing a line.

| Context | Path | Runtime | Rendering architecture |
|---------|------|---------|------------------------|
| App shell | `bin/bridge/web/js/` (systemprompt-core) | Desktop webview, IPC to a Rust host, no server round-trip | **B — render-to-string + keyed patch** |
| Static site | `storage/files/js/` (systemprompt-web) | Progressive enhancement over server-rendered Handlebars | **A — `<template>` + cloneNode** |
| Sandboxed widget | `crates/domain/mcp/.../ui_renderer/templates/assets/js/` | Opaque-origin iframe, assets inlined into a Rust string | **A**, with the module carve-out below |

Layout inside any of them: `components/` (Web Components and UI modules),
`services/` (transport, data, shared state owners), `utils/` (pure helpers),
`pages/` or `index.js` (entry points only).

---

## The two sanctioned rendering architectures

HTML is generated in exactly two ways. Anything else — `innerHTML +=`, string
concatenation in a loop, `document.write`, unescaped interpolation — is a
violation regardless of context.

### A — `<template>` + `cloneNode` (progressive enhancement)

The server owns the markup; JS clones a `<template>` already present in the
document and fills it via DOM API and `textContent`. Reusable interactive
widgets are Web Components with Shadow DOM, a **static template singleton**, and
**Adopted StyleSheets** (`new CSSStyleSheet()` + `adoptedStyleSheets`) so styles
are parsed once and shared across all instances.

Use when the page is server-rendered and JS is an enhancement. This is the
default for anything a user can reach with JS disabled.

### B — escaped render-to-string + keyed reconciler (state-driven shell)

The component owns its markup. `render()` returns an HTML **string** built from
template literals; a keyed patcher diffs it into the light DOM in place. Every
interpolated value passes through `escapeHtml()` or `attr()` at the boundary —
no exceptions, and an un-escaped `${}` carrying anything but a literal is a
High-severity finding.

Use when state arrives asynchronously and continuously (an IPC event stream, a
polling probe) and full replacement would destroy focus, scroll position, and
in-progress edits. The reference implementation is `SpElement` in
`bin/bridge/web/js/components/sp-element.js`.

Architecture B requires all of:

| Requirement | Why |
|---|---|
| Re-render patches in place; only the first paint may assign `innerHTML` | Full replacement discards scroll, focus and half-edited form state on every state tick |
| A custom element or `[data-preserve]` node owns its own children — sync attributes, do not recurse | Recursing wipes content the child rendered for itself |
| Nodes that reorder carry `data-key` | Keyed nodes move with their state instead of being rebuilt |
| Re-render is scheduled, not synchronous (`queueMicrotask`, coalesced) | One state burst must produce one paint |
| Every subscription taken in `connectedCallback` is released in `disconnectedCallback` | The base class holds the unsubscribe list; a leaked listener outlives the element |

**Do not mix them within one component.** A component is A or B, and the choice
follows its context row above.

### Escaping

| Construct | Resolution |
|---|---|
| `${value}` interpolated into an HTML string | `${escapeHtml(value)}` |
| `${value}` interpolated into an attribute position | `${attr("name", value)}` — it handles quoting, booleans and null |
| `innerHTML` assigned from concatenated user or host data | Architecture A, or a patched render under B |
| A shared `escapeHtml` reimplemented locally | Import the one in the app's base module |

---

## Module standards

Native ES Modules. **Named exports only** — no default exports. One module, one
responsibility. Import paths carry the `.js` extension. No bundler, no
transpilation, no import maps.

Module top level declares and exports. It does not run: no side effects at load,
no `addEventListener` at module scope, no work outside a function. Entry points
(`index.js`, `pages/*.js`) are the only place initialisation is called, and
custom-element registration (`customElements.define`) is the one sanctioned
load-time effect.

**Carve-out — sandboxed iframe widgets.** Files under
`crates/domain/mcp/src/services/ui_renderer/templates/assets/js/` are inlined
into an opaque-origin iframe with no module loader, so an IIFE plus a namespaced
global object literal is permitted **there and nowhere else**. They read their
configuration from host-injected `window.*` globals for the same reason. Every
other rule in this document applies to them unchanged. If that runtime ever
gains module support, the carve-out is deleted, not extended.

## Language rules

| Rule | Standard |
|------|----------|
| Declaration | `const` by default, `let` only when reassigned; `var` banned |
| Equality | `===` always; only `== null` is acceptable |
| Functions | Arrow functions for non-methods |
| Async | `async`/`await` with `try`/`catch`; no `.then().catch()` chains |
| Strings | Template literals for interpolation |
| Iteration | `for...of` for arrays; `.map`/`.filter`/`.flatMap` for transforms |
| Destructuring | Required for object/array access with 2+ properties |
| Spread | Prefer `...` over `Object.assign` |
| Nullish | `?.` and `??` over manual null checks |
| Guard clauses | **Preferred** where they flatten nesting — bail early, then write the happy path unindented |
| Nesting depth | Maximum 3 levels inside a function body; extract a named function past that |
| Semicolons | Required |
| Trailing commas | Required in multiline constructs |
| Indentation | 2 spaces |

### Modern API preferences

Legacy equivalents are forbidden.

| Legacy (forbidden) | Modern (required) |
|---|---|
| `JSON.parse(JSON.stringify(obj))` | `structuredClone(obj)` |
| `el.appendChild(node)` | `el.append(node)` |
| `el.removeChild(child)` | `child.remove()` |
| `el.replaceChild(new, old)` | `old.replaceWith(new)` |
| `el.insertAdjacentElement('beforebegin', n)` | `el.before(n)` / `el.after(n)` |
| `Array.from(x).map(fn)` | `Array.from(x, fn)` |
| `array.indexOf(x) !== -1` | `array.includes(x)` |
| `Object.keys(x).forEach(fn)` | `for (const [k, v] of Object.entries(x))` |
| `el.getAttribute('id')` | `el.id` |
| `setTimeout` for animation | `requestAnimationFrame` |

## Forbidden Constructs

Each ban is paired with its resolution and, where one exists, its named
allowlist. Nothing outside the named allowlist is exempt.

| Construct | Resolution |
|-----------|------------|
| `var` | `const` / `let` |
| `==` loose equality | `===` (only `== null` acceptable) |
| `eval()`, `with`, `document.write()`, sync `XMLHttpRequest` | Remove — forbidden outright |
| `arguments` object | Rest parameters (`...args`) |
| Default exports | Named exports |
| jQuery, any framework, any bundler or transpiler | Vanilla platform APIs |
| Unescaped `${}` in an HTML string | `escapeHtml()` / `attr()` — **High severity** |
| `innerHTML +=`, HTML built by concatenation in a loop | Architecture A or B |
| `innerHTML` on re-render under Architecture B | Patch in place; first paint only |
| `this.shadowRoot.innerHTML` in a Web Component | Static `<template>` singleton + `cloneNode` |
| Per-instance `<style>` in Shadow DOM | `new CSSStyleSheet()` + `adoptedStyleSheets` — parsed once, shared |
| Global `window.*` assignment | Module scope. Allowlist: `ui_renderer/templates/assets/js/**` host-injected config only |
| IIFE / global object-literal modules | Native ESM. Allowlist: `ui_renderer/templates/assets/js/**` |
| Side effects at module top level | Wrap in an exported `init()`; call from the entry point. `customElements.define` is exempt |
| Inline event handlers (`onclick=`) | `addEventListener`, or `data-action` delegation |
| Binding behaviour to a CSS class or `#id` | `[data-*]` hooks — classes are for CSS, data attributes are for JS |
| Ad-hoc `addEventListener` per element in a list | One delegated listener on the container, dispatched by `data-action` |
| `data-action` bound to `click` only | Also bind `keydown` for Enter/Space when the trigger is not a `<button>`/`<a>`/`<summary>`/`<input>` — click-only delegation is mouse-only and silently unreachable by keyboard |
| Subscription taken without a matching teardown | Register it with the base class's unsubscribe list |
| Per-module `keydown`/Escape handler for an overlay | Escape and focus-trap live in the single overlay owner |
| `let overlay = null` state in a feature module | The shared overlay/portal service owns it |
| Two modules tracking the same open/close state | One module owns each piece of state; others subscribe |
| Duplicate toast / dialog / dropdown implementations | Use the single shared component |
| Raw `fetch()` in a feature or page module | The app's transport service (`services/api.js`, `bridge.js`) |
| Hardcoded API base URLs, manual `credentials: 'include'` | The transport wrapper owns both |
| `.catch(() => {})` or `.catch(() => ({}))` | Handle visibly — surface state, or let it propagate |
| `console.log` left in committed code | Remove. `console.error` in a teardown/last-resort path is permitted |
| `alert()` / `confirm()` / `prompt()` | A real UI component |
| `new Array()`, `new Object()` | `[]`, `{}` |
| `for...in` over an array | `for...of` or an array method |
| Inline `style` set from JS | `classList`, `dataset`, or a CSS custom property |
| CSS strings in JS | `.css` files; `CSSStyleSheet.replaceSync()` for Shadow DOM only |
| Unused imports | Remove — every import must be referenced |
| Reimplementing a shared utility | Import it from `utils/` or `services/` |
| Re-export shims (`export { newFn as oldFn }`) | Update every import site, delete the shim |
| Any module named `*-compat`, `*-legacy`, `*-shim` | Migrate the callers, delete the file |
| A second implementation kept "until callers migrate" | Land the new form and delete the old in the same change |

## Comment Rules

The rule is the Rust rule. **WHAT-comments are banned and stripped on sight; a
non-obvious WHY is permitted, required where the intent is not derivable from
the code, and rare.** A comment that restates the line below it is noise.

| Comment | Verdict |
|---|---|
| `// Loop over the rows` | Delete — the loop says so |
| `// Set the flag to true` | Delete |
| `// Re-renders patch in place. Blowing away innerHTML on every state event is what made the window flicker, and it also discarded scroll position, focus, and half-edited form state.` | Keep — a bug this shape exists to prevent, unrecoverable from the code |
| `// Only click was bound, so a data-action on anything but a real <button> was mouse-only — which is how the marketplace pane became unreachable by keyboard.` | Keep — a hidden accessibility constraint |
| `// A focus indicator must reach 3:1 (WCAG 1.4.11); --sp-accent-soft measures 1.17:1 and cannot be the ring.` | Keep — an external constraint with measured evidence |
| `// TODO`, `// FIXME`, `// HACK` | Banned. Finish the work or open a ticket; never commit the marker |
| A comment narrating a change ("now uses X instead of Y") | Delete — that is what the commit message is for |

A file-head block comment describing a non-obvious module-wide invariant (the
assumptions a reconciler makes, the contract of a transport) is permitted and
valuable. `bin/bridge/web/js/components/sp-element.js` is the reference for
comment quality in this codebase — read it before writing any.

## File Limits

| Unit | Limit |
|------|-------|
| JS file | 150 lines |
| Function | 30 lines |
| Parameters | 4 — past that, take an options object |
| Nesting depth | 3 |

A file over the limit is split by responsibility, not by cutting it in half. A
Web Component whose `render()` alone exceeds the limit is two components.
Generated or vendored output is exempt; fix the source that produced it.

## Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Variables, functions | camelCase | `fetchUserData`, `isVisible` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES` |
| Classes, Web Components | PascalCase | `SpAgentDrawer` |
| Custom elements | kebab-case, `sp-` prefix | `<sp-agent-drawer>` |
| Files | kebab-case, matching the element | `sp-agent-drawer.js` |
| Custom events | kebab-case, `sp-` prefix | `sp-i18n-ready` |
| JS hooks | `data-` attributes | `data-action`, `data-key`, `data-preserve` |
| Private-by-convention fields | leading `_` | `_unsubs`, `_scheduled` |
| Booleans | `is`/`has`/`can` prefix | `isReady`, `hasProfile` |
| Async functions | verb naming the effect | `loadProfile`, not `profileData` |

Allowed abbreviations: `el`, `btn`, `nav`, `img`, `src`, `url`, `api`, `dom`,
`fn`, `ctx`, `req`, `res`, `err`, `cfg`, `js`, `css`, `unsub`, `evt`.

## Accessibility Requirements

Non-negotiable, and audited at the same severity as correctness.

- Every interactive element is reachable and operable by keyboard. A `data-action`
  on a non-native control must handle Enter and Space.
- Focus is visible on every focusable element, and the indicator meets WCAG
  1.4.11 (3:1 against its background).
- An overlay traps focus while open, restores it to the trigger on close, and
  closes on Escape — implemented once, in the overlay owner.
- Dynamic state changes that matter are announced (`aria-live`, `aria-expanded`,
  `aria-selected`), not conveyed by colour or position alone.
- `prefers-reduced-motion` is honoured; see `css-coding-standards`.

## Review Checklist

- [ ] Which architecture (A or B) is this component, and is it consistent?
- [ ] Every interpolation into HTML escaped at the boundary?
- [ ] Named exports only, no top-level side effects?
- [ ] Every subscription and listener released on teardown?
- [ ] One owner for each piece of state?
- [ ] Every comment a *why* that the code cannot express?
- [ ] File under 150 lines, functions under 30, nesting under 4?
- [ ] Keyboard-operable, focus-visible, Escape-closable?
- [ ] Any shim, compat module, or second implementation introduced? (Reject.)
