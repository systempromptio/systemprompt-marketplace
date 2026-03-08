---
name: modern-css-patterns
description: "Production-ready modern CSS features — container queries, :has(), subgrid, scroll-driven animations, View Transitions, anchor positioning, and cascade layers"
version: "1.0.0"
git_hash: "0000000"
---

# Modern CSS Patterns

## Preamble

This skill complements `frontend-coding-standards`, which defines the CSS architecture baseline: BEM naming with `.sp-` prefix, design tokens with `--sp-` prefix, media queries, `prefers-reduced-motion`, and `prefers-color-scheme`. Nothing from that skill is repeated here.

This skill adds modern CSS techniques that elevate systemprompt.io to world-class visual quality. Every pattern uses the `--sp-` token system and `.sp-` BEM naming. Where border-radius appears, use the branded asymmetric corner tokens (`--sp-corners-sm`, `--sp-corners-md`, `--sp-corners-lg`) — these encode the systemprompt.io brand signature where the top-right corner is 1/4 of the other corners, producing a distinctive asymmetric shape.

---

## Container Queries

Container queries scope responsive behavior to a component's container rather than the viewport. Use them for component-level adaptation; reserve media queries for page-level layout shifts.

### Fundamentals

```css
/* Establish a containment context on a wrapper */
.sp-panel {
  container-type: inline-size;
  container-name: panel;
}

/* Respond to the container's inline size */
@container panel (min-width: 32rem) {
  .sp-panel__body {
    grid-template-columns: 1fr 1fr;
  }
}
```

### Card Adapting to Sidebar vs Main

```html
<aside class="sp-sidebar">
  <div class="sp-card">
    <img class="sp-card__image" src="thumb.webp" alt="Feature" />
    <h3 class="sp-card__title">Feature</h3>
    <p class="sp-card__text">Description of the feature.</p>
  </div>
</aside>
<main class="sp-main">
  <div class="sp-card">
    <img class="sp-card__image" src="thumb.webp" alt="Feature" />
    <h3 class="sp-card__title">Feature</h3>
    <p class="sp-card__text">Description of the feature.</p>
  </div>
</main>
```

```css
.sp-sidebar,
.sp-main {
  container-type: inline-size;
}

.sp-card {
  display: grid;
  gap: var(--sp-space-4);
  border-radius: var(--sp-corners-md);
}

/* Narrow container: stack vertically */
@container (max-width: 24rem) {
  .sp-card {
    grid-template-columns: 1fr;
  }

  .sp-card__image {
    aspect-ratio: 16 / 9;
    object-fit: cover;
  }
}

/* Wide container: image beside text */
@container (min-width: 24rem) {
  .sp-card {
    grid-template-columns: 10rem 1fr;
    align-items: start;
  }
}
```

### Responsive Table Cells

```css
.sp-table-wrapper {
  container-type: inline-size;
  container-name: table-area;
}

@container table-area (max-width: 30rem) {
  .sp-table__cell--secondary {
    display: none;
  }

  .sp-table__cell--primary {
    grid-column: 1 / -1;
  }
}
```

### Rules

| Rule | Rationale |
|------|-----------|
| Use `container-type: inline-size` on layout wrappers | Enables `@container` on children |
| Name containers with `container-name` when nesting | Prevents ambiguous container resolution |
| Container queries for components, media queries for page layout | Components re-render based on available space, not viewport |

---

## `:has()` Relational Selector

`:has()` enables parent selection and sibling-aware styling without JavaScript.

### Form Validation Without JS

```css
/* Highlight the form group when its input is invalid */
.sp-form-group:has(:invalid:not(:placeholder-shown)) {
  --sp-field-border: var(--sp-color-error);
}

.sp-form-group:has(:invalid:not(:placeholder-shown)) .sp-form-group__message {
  display: block;
  color: var(--sp-color-error);
}

/* Success state */
.sp-form-group:has(:valid:not(:placeholder-shown)) {
  --sp-field-border: var(--sp-color-success);
}
```

### Conditional Card Layout

```css
/* Cards with an image get a horizontal layout */
.sp-card:has(> .sp-card__image) {
  grid-template-columns: 12rem 1fr;
  border-radius: var(--sp-corners-md);
}

/* Cards without an image stay stacked */
.sp-card:not(:has(> .sp-card__image)) {
  grid-template-columns: 1fr;
  padding: var(--sp-space-6);
}
```

### Sibling-Aware Grid

```css
/* When the sidebar is present, adjust main content */
.sp-layout:has(> .sp-sidebar) > .sp-main {
  grid-column: 2 / -1;
}

.sp-layout:not(:has(> .sp-sidebar)) > .sp-main {
  grid-column: 1 / -1;
}
```

### Interactive State Escalation

```css
/* Disable the submit button when any required field is empty */
.sp-form:has(:required:placeholder-shown) .sp-form__submit {
  opacity: 0.5;
  pointer-events: none;
}

/* Highlight a nav item when its dropdown is open */
.sp-nav__item:has(> .sp-dropdown[open]) {
  background: var(--sp-color-surface-active);
}
```

---

## CSS Subgrid

Subgrid lets nested elements participate in a parent grid, aligning content across sibling items.

### Aligned Card Grid

```css
.sp-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
  gap: var(--sp-space-6);
}

.sp-card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3; /* heading, body, CTA — three rows */
  gap: var(--sp-space-4);
  border-radius: var(--sp-corners-lg);
  background: var(--sp-color-surface);
  padding: var(--sp-space-6);
}

.sp-card__title {
  align-self: end;
}

.sp-card__cta {
  align-self: start;
}
```

This ensures that across every card in the grid, headings align on one row, body content on the next, and CTAs on the last — regardless of content length.

### When NOT to Use Subgrid

| Avoid subgrid when | Reason |
|--------------------|--------|
| Children have independent sizing needs | Subgrid forces participation in the parent track |
| Deeply nested elements need alignment | Subgrid only works one level deep from the participating child |
| Content count varies per card | `grid-row: span N` must match actual row count |

---

## `@scope` for Subtree Styling

`@scope` constrains styles to a DOM subtree without Shadow DOM encapsulation.

### Basic Scope

```css
@scope (.sp-card) to (.sp-card__footer) {
  /* Styles apply inside .sp-card but stop before .sp-card__footer */
  a {
    color: var(--sp-color-link);
    text-decoration: underline;
  }

  p {
    color: var(--sp-color-text-secondary);
  }
}
```

### Proximity-Based Styling

When the same class name appears at multiple nesting levels, `@scope` resolves by proximity — the nearest scope root wins.

```css
@scope (.sp-theme--light) {
  .sp-text {
    color: var(--sp-color-text);
  }
}

@scope (.sp-theme--dark) {
  .sp-text {
    color: var(--sp-color-text-inverse);
  }
}
```

### When to Choose Each Approach

| Technique | Use when |
|-----------|----------|
| `@scope` | Styling third-party content or CMS-rendered HTML within a boundary |
| BEM | Component ownership is clear and names are unique |
| Shadow DOM | Full encapsulation needed (Web Components with their own lifecycle) |

---

## Anchor Positioning

Anchor positioning replaces JavaScript-based tooltip and popover placement with pure CSS.

### Complete Tooltip Pattern

```css
.sp-tooltip-trigger {
  anchor-name: --sp-trigger;
}

.sp-tooltip {
  position: fixed;
  position-anchor: --sp-trigger;
  position-area: top;
  margin-bottom: var(--sp-space-2);
  background: var(--sp-color-surface-inverse);
  color: var(--sp-color-text-inverse);
  padding: var(--sp-space-2) var(--sp-space-3);
  border-radius: var(--sp-corners-sm);
  width: max-content;
  max-width: 20rem;

  /* Fade in */
  opacity: 0;
  transition: opacity var(--sp-transition-fast);
}

.sp-tooltip-trigger:hover + .sp-tooltip,
.sp-tooltip-trigger:focus-visible + .sp-tooltip {
  opacity: 1;
}

/* Fallback positioning when top overflows */
@position-try --sp-below {
  position-area: bottom;
  margin-top: var(--sp-space-2);
  margin-bottom: 0;
}

.sp-tooltip {
  position-try-fallbacks: --sp-below;
}
```

### Rules

| Rule | Rationale |
|------|-----------|
| Prefix anchor names with `--sp-` | Consistent with token namespace |
| Always provide `@position-try` fallbacks | Content may overflow in any direction |
| Use `position: fixed` with `position-anchor` | Required for anchor-positioned elements |

---

## Scroll-Driven Animations

Scroll-driven animations bind animation progress to scroll position instead of time.

### Reading Progress Bar

```css
.sp-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--sp-color-accent);
  transform-origin: left;
  animation: sp-grow-width linear;
  animation-timeline: scroll(root);
}

@keyframes sp-grow-width {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
```

### Fade-In on Scroll (View Timeline)

```css
.sp-reveal {
  animation: sp-fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}

@keyframes sp-fade-in {
  from {
    opacity: 0;
    transform: translateY(var(--sp-space-6));
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Header Shrink on Scroll

```css
.sp-header {
  animation: sp-shrink-header linear;
  animation-timeline: scroll(root);
  animation-range: 0px 200px;
}

@keyframes sp-shrink-header {
  from {
    padding-block: var(--sp-space-6);
    font-size: var(--sp-text-xl);
  }
  to {
    padding-block: var(--sp-space-2);
    font-size: var(--sp-text-base);
  }
}
```

### Respecting Reduced Motion

All scroll-driven animations must be disabled under `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  .sp-reveal,
  .sp-progress-bar,
  .sp-header {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

---

## View Transitions API

View Transitions animate between DOM states with element morphing, using minimal JavaScript to trigger the transition and CSS for all visual control.

### Tab Crossfade

```css
/* Assign transition names to each tab panel */
.sp-tab-panel {
  view-transition-name: sp-panel;
}

/* Crossfade animation */
::view-transition-old(sp-panel) {
  animation: sp-fade-out 200ms ease-out;
}

::view-transition-new(sp-panel) {
  animation: sp-fade-in 200ms ease-in;
}

@keyframes sp-fade-out {
  to { opacity: 0; }
}

@keyframes sp-fade-in {
  from { opacity: 0; }
}
```

```javascript
function switchTab(panelId) {
  if (!document.startViewTransition) {
    updatePanel(panelId);
    return;
  }
  document.startViewTransition(() => updatePanel(panelId));
}

function updatePanel(panelId) {
  document.querySelectorAll('.sp-tab-panel').forEach(p => p.hidden = true);
  document.getElementById(panelId).hidden = false;
}
```

### List Reordering

```css
.sp-list-item {
  view-transition-name: var(--sp-vt-name);
}

::view-transition-group(sp-list-item) {
  animation-duration: 300ms;
  animation-timing-function: ease-in-out;
}
```

```javascript
function sortList(compareFn) {
  const list = document.querySelector('.sp-list');
  const items = [...list.querySelectorAll('.sp-list-item')];

  items.forEach((item, i) => {
    item.style.setProperty('--sp-vt-name', `sp-item-${i}`);
  });

  if (!document.startViewTransition) {
    reorder(list, items, compareFn);
    return;
  }
  document.startViewTransition(() => reorder(list, items, compareFn));
}

function reorder(list, items, compareFn) {
  items.sort(compareFn).forEach(item => list.appendChild(item));
}
```

### Rules

| Rule | Rationale |
|------|-----------|
| Always feature-detect `document.startViewTransition` | Graceful fallback for unsupported browsers |
| Keep DOM mutations inside the callback | The API snapshots before and after states |
| Use unique `view-transition-name` per morphing element | Shared names cause conflicts |

---

## `@starting-style` for Entry Animations

`@starting-style` defines the initial state for elements entering the DOM, enabling CSS-only entry animations without JavaScript.

### Dialog Entrance

```css
.sp-dialog[open] {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms ease, transform 300ms ease,
              display 300ms allow-discrete;

  @starting-style {
    opacity: 0;
    transform: translateY(calc(-1 * var(--sp-space-6)));
  }
}

.sp-dialog {
  opacity: 0;
  transform: translateY(calc(-1 * var(--sp-space-6)));
  transition: opacity 200ms ease, transform 200ms ease,
              display 200ms allow-discrete;
  border-radius: var(--sp-corners-lg);
}
```

### Toast Slide-In

```css
.sp-toast {
  position: fixed;
  bottom: var(--sp-space-6);
  right: var(--sp-space-6);
  translate: 0 0;
  opacity: 1;
  transition: translate 300ms ease, opacity 300ms ease,
              display 300ms allow-discrete;
  border-radius: var(--sp-corners-sm);

  @starting-style {
    translate: 100% 0;
    opacity: 0;
  }
}

/* Exit state — when removing, add this class before removing from DOM */
.sp-toast.is-exiting {
  translate: 100% 0;
  opacity: 0;
}
```

### Dynamic List Item Entry

```css
.sp-list-item {
  opacity: 1;
  max-height: 10rem;
  transition: opacity 250ms ease, max-height 250ms ease;

  @starting-style {
    opacity: 0;
    max-height: 0;
  }
}
```

### Key Requirement

Use `transition-behavior: allow-discrete` (or the shorthand `allow-discrete` in the `transition` declaration) when animating properties that toggle between discrete values such as `display: none` and `display: block`.

---

## Text Wrapping Control

Modern text wrapping properties improve typographic quality without JavaScript.

### Headings: `text-wrap: balance`

```css
.sp-heading,
.sp-card__title,
.sp-hero__title {
  text-wrap: balance;
}
```

Balanced wrapping distributes text evenly across lines, eliminating orphaned short last lines. The browser limits this to approximately 6 lines for performance — never apply to body text.

### Body Text: `text-wrap: pretty`

```css
.sp-body-text,
.sp-card__text,
.sp-article__content p {
  text-wrap: pretty;
}
```

Pretty wrapping avoids typographic orphans (single words on the last line) with minimal performance cost. Safe for all body text.

### Design System Rules

| Selector pattern | Property | Rationale |
|-----------------|----------|-----------|
| Headings (`h1`–`h4`, `.sp-heading`) | `text-wrap: balance` | Even line distribution |
| Body text (`p`, `.sp-body-text`) | `text-wrap: pretty` | Orphan prevention |
| Labels, captions, short strings | Neither | Single-line text needs no wrapping control |
| Preformatted code | Neither | Must preserve original line breaks |

---

## Cascade Layers (`@layer`)

Cascade layers give explicit ordering to stylesheet concerns, making specificity conflicts manageable at scale.

### Layer Architecture

```css
/* Declare layer order first — this line controls cascade priority */
@layer reset, tokens, base, components, utilities;

/* Reset — lowest priority */
@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
  }
}

/* Tokens — custom properties */
@layer tokens {
  :root {
    --sp-color-accent: #6366f1;
    --sp-color-surface: #ffffff;
    --sp-corners-sm: 0.125rem 0.03125rem 0.125rem 0.125rem;
    --sp-corners-md: 0.375rem 0.09375rem 0.375rem 0.375rem;
    --sp-corners-lg: 0.75rem 0.1875rem 0.75rem 0.75rem;
  }
}

/* Base — element defaults */
@layer base {
  body {
    font-family: var(--sp-font-body);
    color: var(--sp-color-text);
    background: var(--sp-color-bg);
  }
}

/* Components — BEM blocks */
@layer components {
  .sp-card {
    background: var(--sp-color-surface);
    border-radius: var(--sp-corners-md);
    padding: var(--sp-space-6);
  }
}

/* Utilities — highest priority overrides */
@layer utilities {
  .sp-u-sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
}
```

### Importing Third-Party Styles Into a Layer

```css
@layer vendor {
  @import url("third-party.css");
}
```

Third-party styles imported into the `vendor` layer will never override your `components` or `utilities` layers regardless of their specificity.

### Key Behaviours

| Behaviour | Implication |
|-----------|-------------|
| Earlier layers have lower priority | `reset` always loses to `utilities` |
| Unlayered styles beat all layers | Never leave styles unlayered — assign everything |
| Specificity still works within a layer | BEM keeps specificity flat inside `components` |
| `!important` reverses layer order | Avoid — this is why `!important` is banned except for `prefers-reduced-motion` |

---

## CSS Nesting

Native CSS nesting reduces repetition and co-locates related rules. It replaces preprocessor nesting.

### BEM Component With Native Nesting

```css
.sp-card {
  display: grid;
  gap: var(--sp-space-4);
  background: var(--sp-color-surface);
  border-radius: var(--sp-corners-md);
  padding: var(--sp-space-6);

  & .sp-card__title {
    font-size: var(--sp-text-lg);
    text-wrap: balance;
  }

  & .sp-card__text {
    color: var(--sp-color-text-secondary);
    text-wrap: pretty;
  }

  & .sp-card__cta {
    justify-self: start;
  }

  /* Modifier */
  &.sp-card--featured {
    border-left: 3px solid var(--sp-color-accent);
  }

  /* State */
  &.is-active {
    box-shadow: 0 0 0 2px var(--sp-color-accent);
  }

  /* Nested container query */
  @container (min-width: 32rem) {
    grid-template-columns: 1fr 1fr;
  }

  /* Nested media query */
  @media (prefers-color-scheme: dark) {
    background: var(--sp-color-surface-dark);
  }
}
```

### Rules

| Rule | Rationale |
|------|-----------|
| Maximum 3 levels of nesting depth | Deeper nesting obscures the resulting selector |
| Use `&` explicitly for compound selectors | `.sp-card { &.is-active {} }` not `.sp-card { .is-active {} }` |
| Nest media and container queries inside components | Co-locates responsive behavior with the component it affects |
| Do not nest unrelated selectors | Nesting must reflect DOM hierarchy or modifier relationships |

---

## Review Checklist

Before shipping CSS, verify these modernization opportunities:

- [ ] Layout containers have `container-type: inline-size` where child components need size adaptation
- [ ] Parent-dependent styles use `:has()` instead of JavaScript class toggling
- [ ] Card grids with aligned rows use `subgrid`
- [ ] Tooltips and popovers use anchor positioning instead of JS coordinate math
- [ ] Scroll-linked effects use `animation-timeline: scroll()` or `view()` instead of `IntersectionObserver` or scroll listeners
- [ ] Page state changes use View Transitions API with `startViewTransition()`
- [ ] Entry animations use `@starting-style` instead of JS-added animation classes
- [ ] Headings use `text-wrap: balance`, body text uses `text-wrap: pretty`
- [ ] Stylesheet concerns are organized into `@layer` declarations
- [ ] Component CSS uses native nesting (max 3 levels)
- [ ] All scroll and entry animations are disabled under `prefers-reduced-motion: reduce`
- [ ] All custom properties use the `--sp-` prefix
- [ ] All border-radius values use `--sp-corners-sm/md/lg` asymmetric tokens

### Old Pattern to Modern Pattern

| Old pattern | Modern replacement |
|-------------|-------------------|
| Media query for component sizing | `@container` query |
| JS class toggle for parent styling | `:has()` selector |
| Manual row alignment across cards | `subgrid` |
| BEM scoping alone for CMS content | `@scope` with boundary |
| JS `getBoundingClientRect()` for popover position | Anchor positioning |
| `IntersectionObserver` for scroll effects | `animation-timeline: view()` |
| JS scroll listener for progress bar | `animation-timeline: scroll()` |
| JS-added class for enter animation | `@starting-style` |
| No wrapping control | `text-wrap: balance` / `pretty` |
| Specificity wars with third-party CSS | `@layer` ordering |
| Sass/PostCSS nesting | Native CSS nesting |
