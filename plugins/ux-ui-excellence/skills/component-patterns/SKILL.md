---
name: component-patterns
description: "World-class component visual patterns — cards, tables, forms, navigation, dashboards, data visualization, empty states, and feedback components with branded asymmetric corners"
version: "1.0.0"
git_hash: "0000000"
---

# Component Visual Patterns

World-class component visual recipes for systemprompt.io. Follow without exception when building, modifying, or reviewing component visuals.

## Preamble — Skill Relationships

This skill provides **visual design patterns** for specific component types. It combines tokens, techniques, and interaction patterns into ready-to-use component recipes.

**Complementary skills (do not duplicate their content):**

| Skill | Covers | This Skill Adds |
|---|---|---|
| `frontend-coding-standards` | Web Component architecture, BEM `.sp-*` naming, event delegation, accessibility | Visual styling for those components |
| `visual-design-system` | Design tokens, color system, typography scale | Token application in component context |
| `modern-css-patterns` | CSS techniques (container queries, grid, has(), nesting) | Technique composition into component recipes |
| `ux-interaction-patterns` | Animation, transitions, micro-interactions, UX flows | Static visual structure that animations enhance |

**Rule**: If a pattern is about *structure/architecture*, defer to `frontend-coding-standards`. If about *tokens/color/type*, defer to `visual-design-system`. If about *CSS technique*, defer to `modern-css-patterns`. If about *motion/UX behavior*, defer to `ux-interaction-patterns`. This skill is the **visual assembly layer**.

---

## Branded Asymmetric Corners

systemprompt.io uses **asymmetric border-radius** as its visual signature. The top-right corner is approximately 1/4 of the other corners, creating a distinctive branded shape.

```css
/* Corner tokens — use these, NEVER symmetric border-radius */
--sp-corners-sm: 6px 2px 6px 6px;   /* small elements: badges, chips, tags */
--sp-corners-md: 12px 3px 12px 12px; /* cards, containers (default) */
--sp-corners-lg: 20px 5px 20px 20px; /* modals, dialogs, sheets */
```

**Rule**: Every card, container, modal, dialog, dropdown, and panel MUST use `border-radius: var(--sp-corners-md)` (or `sm`/`lg` as appropriate). Never use symmetric `border-radius` values. This is non-negotiable.

---

## Card Patterns

### Standard Card

The foundational content container. Image (optional), header, body, footer in vertical stack.

```html
<div class="sp-card">
  <div class="sp-card__media">
    <img src="image.webp" alt="Descriptive text" class="sp-card__image" />
  </div>
  <div class="sp-card__header">
    <h3 class="sp-card__title">Card Title</h3>
    <span class="sp-card__badge">Label</span>
  </div>
  <div class="sp-card__body">
    <p class="sp-card__text">Card description content.</p>
  </div>
  <div class="sp-card__footer">
    <button class="sp-btn sp-btn--secondary">Cancel</button>
    <button class="sp-btn sp-btn--primary">Action</button>
  </div>
</div>
```

```css
.sp-card {
  border-radius: var(--sp-corners-md);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-sm);
  overflow: hidden;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.sp-card:hover {
  box-shadow: var(--sp-shadow-md);
  transform: translateY(-1px);
}

.sp-card__media {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.sp-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sp-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-space-5) var(--sp-space-5) 0;
}

.sp-card__title {
  font-size: var(--sp-font-size-lg);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text);
  margin: 0;
}

.sp-card__body {
  padding: var(--sp-space-3) var(--sp-space-5);
}

.sp-card__text {
  color: var(--sp-color-text-secondary);
  font-size: var(--sp-font-size-sm);
  line-height: var(--sp-line-height-relaxed);
  margin: 0;
}

.sp-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-space-3);
  padding: 0 var(--sp-space-5) var(--sp-space-5);
}
```

### Metric Card (KPI)

Compact card for key performance indicators. Large number dominates, delta indicator shows trend.

```html
<div class="sp-metric-card">
  <div class="sp-metric-card__header">
    <span class="sp-metric-card__label">Monthly Revenue</span>
    <span class="sp-metric-card__icon" aria-hidden="true">$</span>
  </div>
  <div class="sp-metric-card__value">
    <span class="sp-metric-card__number">42,380</span>
    <span class="sp-metric-card__unit">USD</span>
  </div>
  <div class="sp-metric-card__delta sp-metric-card__delta--up">
    <span class="sp-metric-card__arrow" aria-hidden="true"></span>
    <span class="sp-metric-card__percent">12.5%</span>
    <span class="sp-metric-card__period">vs last month</span>
  </div>
  <svg class="sp-metric-card__sparkline" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true">
    <polyline points="0,25 15,20 30,22 45,15 60,18 75,8 100,5" fill="none" stroke="currentColor" stroke-width="1.5" />
  </svg>
</div>
```

```css
.sp-metric-card {
  border-radius: var(--sp-corners-md);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-sm);
  padding: var(--sp-space-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-space-2);
}

.sp-metric-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sp-metric-card__label {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-muted);
  font-weight: var(--sp-font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sp-metric-card__icon {
  font-size: var(--sp-font-size-lg);
  color: var(--sp-color-text-muted);
}

.sp-metric-card__value {
  display: flex;
  align-items: baseline;
  gap: var(--sp-space-2);
}

.sp-metric-card__number {
  font-size: var(--sp-font-size-3xl);
  font-weight: var(--sp-font-weight-bold);
  color: var(--sp-color-text);
  line-height: 1;
}

.sp-metric-card__unit {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-muted);
}

.sp-metric-card__delta {
  display: flex;
  align-items: center;
  gap: var(--sp-space-1);
  font-size: var(--sp-font-size-sm);
}

.sp-metric-card__delta--up {
  color: var(--sp-color-success);
}

.sp-metric-card__delta--down {
  color: var(--sp-color-danger);
}

.sp-metric-card__delta--flat {
  color: var(--sp-color-text-muted);
}

.sp-metric-card__arrow {
  display: inline-block;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
}

.sp-metric-card__delta--up .sp-metric-card__arrow {
  border-bottom: 5px solid currentColor;
}

.sp-metric-card__delta--down .sp-metric-card__arrow {
  border-top: 5px solid currentColor;
}

.sp-metric-card__period {
  color: var(--sp-color-text-muted);
}

.sp-metric-card__sparkline {
  width: 100%;
  height: 30px;
  color: var(--sp-color-primary);
  margin-top: var(--sp-space-2);
}
```

### Bento Grid Layout

Varied-span grid for visual hierarchy. Featured items span multiple columns/rows.

```html
<div class="sp-bento">
  <div class="sp-bento__item sp-bento__item--featured">Featured</div>
  <div class="sp-bento__item">Standard</div>
  <div class="sp-bento__item">Standard</div>
  <div class="sp-bento__item sp-bento__item--wide">Wide</div>
  <div class="sp-bento__item">Standard</div>
  <div class="sp-bento__item sp-bento__item--tall">Tall</div>
</div>
```

```css
.sp-bento {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--sp-space-4);
}

.sp-bento__item {
  border-radius: var(--sp-corners-md);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-sm);
  padding: var(--sp-space-5);
  min-height: 200px;
}

.sp-bento__item--featured {
  grid-column: span 2;
  grid-row: span 2;
}

.sp-bento__item--wide {
  grid-column: span 2;
}

.sp-bento__item--tall {
  grid-row: span 2;
}

/* Collapse spans on narrow viewports */
@media (max-width: 640px) {
  .sp-bento__item--featured,
  .sp-bento__item--wide {
    grid-column: span 1;
  }

  .sp-bento__item--featured {
    grid-row: span 1;
  }
}
```

### Horizontal Card

Side-by-side image + content. Stacks on narrow containers.

```html
<div class="sp-card-horizontal">
  <div class="sp-card-horizontal__media">
    <img src="image.webp" alt="Description" class="sp-card-horizontal__image" />
  </div>
  <div class="sp-card-horizontal__content">
    <h3 class="sp-card-horizontal__title">Horizontal Card</h3>
    <p class="sp-card-horizontal__text">Content beside the image.</p>
    <button class="sp-btn sp-btn--primary sp-btn--sm">Action</button>
  </div>
</div>
```

```css
.sp-card-horizontal {
  container-type: inline-size;
  border-radius: var(--sp-corners-md);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-sm);
  overflow: hidden;
  display: grid;
  grid-template-columns: 240px 1fr;
}

.sp-card-horizontal__media {
  aspect-ratio: 1;
  overflow: hidden;
}

.sp-card-horizontal__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sp-card-horizontal__content {
  padding: var(--sp-space-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-space-3);
}

.sp-card-horizontal__title {
  font-size: var(--sp-font-size-lg);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text);
  margin: 0;
}

.sp-card-horizontal__text {
  color: var(--sp-color-text-secondary);
  font-size: var(--sp-font-size-sm);
  margin: 0;
  flex: 1;
}

/* Stack on narrow containers */
@container (max-width: 480px) {
  .sp-card-horizontal {
    grid-template-columns: 1fr;
  }

  .sp-card-horizontal__media {
    aspect-ratio: 16 / 9;
  }
}
```

---

## Table Patterns

### Standard Data Table

Sticky header, row hover, sort indicators.

```css
.sp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--sp-font-size-sm);
}

.sp-table__header {
  position: sticky;
  top: 0;
  z-index: 1;
}

.sp-table__header-cell {
  padding: var(--sp-space-3) var(--sp-space-4);
  text-align: left;
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text-muted);
  background: var(--sp-color-surface-alt);
  border-bottom: 2px solid var(--sp-color-border);
  white-space: nowrap;
  user-select: none;
  cursor: pointer;
}

.sp-table__header-cell--sortable::after {
  content: "";
  display: inline-block;
  width: 0;
  height: 0;
  margin-left: var(--sp-space-2);
  vertical-align: middle;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid var(--sp-color-text-muted);
  opacity: 0.3;
}

.sp-table__header-cell--asc::after {
  border-top: none;
  border-bottom: 5px solid var(--sp-color-primary);
  opacity: 1;
}

.sp-table__header-cell--desc::after {
  border-top: 5px solid var(--sp-color-primary);
  opacity: 1;
}

.sp-table__row {
  transition: background-color 0.15s ease;
}

.sp-table__row:hover {
  background: var(--sp-color-surface-hover);
}

.sp-table__row:nth-child(even) {
  background: var(--sp-color-surface-alt);
}

.sp-table__row:nth-child(even):hover {
  background: var(--sp-color-surface-hover);
}

.sp-table__cell {
  padding: var(--sp-space-3) var(--sp-space-4);
  border-bottom: 1px solid var(--sp-color-border-light);
  color: var(--sp-color-text);
  vertical-align: middle;
}
```

### Responsive Table

Collapse to card layout on narrow screens using `data-label` for mobile headers.

```html
<table class="sp-table sp-table--responsive">
  <thead class="sp-table__header">
    <tr>
      <th class="sp-table__header-cell">Name</th>
      <th class="sp-table__header-cell">Status</th>
      <th class="sp-table__header-cell">Amount</th>
    </tr>
  </thead>
  <tbody>
    <tr class="sp-table__row">
      <td class="sp-table__cell" data-label="Name">Alice</td>
      <td class="sp-table__cell" data-label="Status">Active</td>
      <td class="sp-table__cell" data-label="Amount">$1,200</td>
    </tr>
  </tbody>
</table>
```

```css
@media (max-width: 640px) {
  .sp-table--responsive .sp-table__header {
    display: none;
  }

  .sp-table--responsive .sp-table__row {
    display: block;
    border-radius: var(--sp-corners-md);
    background: var(--sp-color-surface);
    box-shadow: var(--sp-shadow-sm);
    margin-bottom: var(--sp-space-3);
    padding: var(--sp-space-4);
  }

  .sp-table--responsive .sp-table__cell {
    display: flex;
    justify-content: space-between;
    padding: var(--sp-space-2) 0;
    border-bottom: 1px solid var(--sp-color-border-light);
  }

  .sp-table--responsive .sp-table__cell:last-child {
    border-bottom: none;
  }

  .sp-table--responsive .sp-table__cell::before {
    content: attr(data-label);
    font-weight: var(--sp-font-weight-semibold);
    color: var(--sp-color-text-muted);
    margin-right: var(--sp-space-4);
  }
}
```

### Expandable Rows

Click to reveal detail row with chevron rotation and left border accent.

```css
.sp-table__row--expandable {
  cursor: pointer;
}

.sp-table__row--expandable .sp-table__chevron {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-right: 2px solid var(--sp-color-text-muted);
  border-bottom: 2px solid var(--sp-color-text-muted);
  transform: rotate(-45deg);
  transition: transform 0.2s ease;
}

.sp-table__row--expandable[aria-expanded="true"] .sp-table__chevron {
  transform: rotate(45deg);
}

.sp-table__detail {
  display: none;
  background: var(--sp-color-surface-alt);
  border-left: 3px solid var(--sp-color-primary);
}

.sp-table__row--expandable[aria-expanded="true"] + .sp-table__detail {
  display: table-row;
}

.sp-table__detail-content {
  padding: var(--sp-space-4) var(--sp-space-5);
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-secondary);
}
```

---

## Form Patterns

### Input Group

Label above (never floating), help text, error message with clear visual states.

```html
<div class="sp-field">
  <label class="sp-field__label" for="email">Email Address</label>
  <input class="sp-field__input" type="email" id="email" aria-describedby="email-help email-error" />
  <span class="sp-field__help" id="email-help">We'll never share your email.</span>
  <span class="sp-field__error" id="email-error" role="alert" hidden>Please enter a valid email address.</span>
</div>
```

```css
.sp-field {
  display: flex;
  flex-direction: column;
  gap: var(--sp-space-1);
}

.sp-field__label {
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-medium);
  color: var(--sp-color-text);
}

.sp-field__input {
  padding: var(--sp-space-3) var(--sp-space-4);
  border: 1px solid var(--sp-color-border);
  border-radius: var(--sp-corners-sm);
  font-size: var(--sp-font-size-base);
  color: var(--sp-color-text);
  background: var(--sp-color-surface);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.sp-field__input:focus {
  outline: none;
  border-color: var(--sp-color-primary);
  box-shadow: 0 0 0 3px var(--sp-color-primary-alpha);
}

.sp-field__input[aria-invalid="true"] {
  border-color: var(--sp-color-danger);
  box-shadow: 0 0 0 3px var(--sp-color-danger-alpha);
}

.sp-field__input--success {
  border-color: var(--sp-color-success);
  box-shadow: 0 0 0 3px var(--sp-color-success-alpha);
}

.sp-field__help {
  font-size: var(--sp-font-size-xs);
  color: var(--sp-color-text-muted);
}

.sp-field__error {
  font-size: var(--sp-font-size-xs);
  color: var(--sp-color-danger);
  display: flex;
  align-items: center;
  gap: var(--sp-space-1);
}

.sp-field__error[hidden] {
  display: none;
}
```

### Inline Validation

Real-time feedback after first blur. Success shows green border + check, error shows red border + message slide.

```css
.sp-field__input:not(:placeholder-shown):valid {
  border-color: var(--sp-color-success);
}

.sp-field__input:not(:placeholder-shown):invalid {
  border-color: var(--sp-color-danger);
}

.sp-field__validation-icon {
  position: absolute;
  right: var(--sp-space-3);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--sp-font-size-base);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.sp-field__input--success ~ .sp-field__validation-icon--check {
  opacity: 1;
  color: var(--sp-color-success);
}

.sp-field__input[aria-invalid="true"] ~ .sp-field__validation-icon--x {
  opacity: 1;
  color: var(--sp-color-danger);
}

.sp-field__error {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.2s ease;
}

.sp-field__input[aria-invalid="true"] ~ .sp-field__error {
  max-height: 3em;
}
```

### Multi-Step Form

Step indicator with numbered circles and connecting lines.

```html
<div class="sp-stepper" role="navigation" aria-label="Form progress">
  <ol class="sp-stepper__list">
    <li class="sp-stepper__step sp-stepper__step--completed">
      <span class="sp-stepper__circle" aria-hidden="true">&#10003;</span>
      <span class="sp-stepper__label">Account</span>
    </li>
    <li class="sp-stepper__step sp-stepper__step--active" aria-current="step">
      <span class="sp-stepper__circle" aria-hidden="true">2</span>
      <span class="sp-stepper__label">Profile</span>
    </li>
    <li class="sp-stepper__step">
      <span class="sp-stepper__circle" aria-hidden="true">3</span>
      <span class="sp-stepper__label">Confirm</span>
    </li>
  </ol>
</div>
```

```css
.sp-stepper__list {
  display: flex;
  justify-content: center;
  list-style: none;
  padding: 0;
  margin: 0 0 var(--sp-space-6);
  counter-reset: step;
}

.sp-stepper__step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}

/* Connecting line */
.sp-stepper__step:not(:last-child)::after {
  content: "";
  position: absolute;
  top: 16px;
  left: calc(50% + 20px);
  width: calc(100% - 40px);
  height: 2px;
  background: var(--sp-color-border);
}

.sp-stepper__step--completed:not(:last-child)::after {
  background: var(--sp-color-primary);
}

.sp-stepper__circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--sp-color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text-muted);
  background: var(--sp-color-surface);
  position: relative;
  z-index: 1;
}

.sp-stepper__step--active .sp-stepper__circle {
  border-color: var(--sp-color-primary);
  background: var(--sp-color-primary);
  color: var(--sp-color-on-primary);
}

.sp-stepper__step--completed .sp-stepper__circle {
  border-color: var(--sp-color-primary);
  background: var(--sp-color-primary);
  color: var(--sp-color-on-primary);
}

.sp-stepper__label {
  margin-top: var(--sp-space-2);
  font-size: var(--sp-font-size-xs);
  color: var(--sp-color-text-muted);
}

.sp-stepper__step--active .sp-stepper__label {
  color: var(--sp-color-text);
  font-weight: var(--sp-font-weight-medium);
}
```

### Accessible Error Summary

Top-of-form error summary with links to each invalid field.

```html
<div class="sp-error-summary" role="alert" aria-labelledby="error-heading">
  <h2 class="sp-error-summary__title" id="error-heading">There are 2 errors in this form</h2>
  <ul class="sp-error-summary__list">
    <li class="sp-error-summary__item">
      <a class="sp-error-summary__link" href="#email">Email address is required</a>
    </li>
    <li class="sp-error-summary__item">
      <a class="sp-error-summary__link" href="#password">Password must be at least 8 characters</a>
    </li>
  </ul>
</div>
```

```css
.sp-error-summary {
  border-radius: var(--sp-corners-md);
  border: 1px solid var(--sp-color-danger);
  border-left: 4px solid var(--sp-color-danger);
  background: var(--sp-color-danger-surface);
  padding: var(--sp-space-4) var(--sp-space-5);
  margin-bottom: var(--sp-space-5);
}

.sp-error-summary__title {
  font-size: var(--sp-font-size-base);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-danger);
  margin: 0 0 var(--sp-space-3);
}

.sp-error-summary__list {
  margin: 0;
  padding-left: var(--sp-space-5);
}

.sp-error-summary__item {
  margin-bottom: var(--sp-space-1);
}

.sp-error-summary__link {
  color: var(--sp-color-danger);
  text-decoration: underline;
  font-size: var(--sp-font-size-sm);
}

.sp-error-summary__link:hover {
  text-decoration: none;
}
```

---

## Navigation Patterns

### Top Navigation Bar

Logo left, nav center/right, actions far right. Active state uses bottom border accent.

```css
.sp-navbar {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 var(--sp-space-5);
  background: var(--sp-color-surface);
  border-bottom: 1px solid var(--sp-color-border-light);
  position: sticky;
  top: 0;
  z-index: var(--sp-z-sticky);
}

.sp-navbar__brand {
  display: flex;
  align-items: center;
  gap: var(--sp-space-3);
  margin-right: auto;
}

.sp-navbar__nav {
  display: flex;
  align-items: center;
  gap: var(--sp-space-1);
  list-style: none;
  margin: 0;
  padding: 0;
  height: 100%;
}

.sp-navbar__link {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--sp-space-4);
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-medium);
  color: var(--sp-color-text-secondary);
  text-decoration: none;
  border-bottom: 3px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.sp-navbar__link:hover {
  color: var(--sp-color-text);
}

.sp-navbar__link--active {
  color: var(--sp-color-primary);
  border-bottom-color: var(--sp-color-primary);
}

.sp-navbar__actions {
  display: flex;
  align-items: center;
  gap: var(--sp-space-3);
  margin-left: auto;
}

/* Mobile hamburger */
.sp-navbar__toggle {
  display: none;
  background: none;
  border: none;
  padding: var(--sp-space-2);
  cursor: pointer;
}

@media (max-width: 768px) {
  .sp-navbar__nav {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    width: 280px;
    flex-direction: column;
    background: var(--sp-color-surface);
    box-shadow: var(--sp-shadow-lg);
    padding: var(--sp-space-4);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    height: auto;
    gap: 0;
  }

  .sp-navbar__nav--open {
    transform: translateX(0);
  }

  .sp-navbar__link {
    height: auto;
    padding: var(--sp-space-3) var(--sp-space-4);
    border-bottom: none;
    border-left: 3px solid transparent;
    border-radius: var(--sp-corners-sm);
  }

  .sp-navbar__link--active {
    border-left-color: var(--sp-color-primary);
    background: var(--sp-color-primary-alpha);
  }

  .sp-navbar__toggle {
    display: block;
  }
}
```

### Sidebar Navigation

Collapsible between expanded (240px) and icon-only (64px).

```css
.sp-sidebar {
  width: 260px;
  min-height: 100vh;
  background: var(--sp-color-surface);
  border-right: 1px solid var(--sp-color-border-light);
  padding: var(--sp-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--sp-space-1);
  transition: width 0.2s ease;
  overflow: hidden;
}

.sp-sidebar--collapsed {
  width: 64px;
  padding: var(--sp-space-4) var(--sp-space-2);
}

.sp-sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--sp-space-3);
  padding: var(--sp-space-3) var(--sp-space-4);
  border-radius: var(--sp-corners-sm);
  color: var(--sp-color-text-secondary);
  text-decoration: none;
  font-size: var(--sp-font-size-sm);
  white-space: nowrap;
  transition: background 0.15s ease, color 0.15s ease;
}

.sp-sidebar__link:hover {
  background: var(--sp-color-surface-hover);
  color: var(--sp-color-text);
}

.sp-sidebar__link--active {
  background: var(--sp-color-primary-alpha);
  color: var(--sp-color-primary);
  border-left: 3px solid var(--sp-color-primary);
}

.sp-sidebar__link-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.sp-sidebar--collapsed .sp-sidebar__link-text {
  display: none;
}

.sp-sidebar--collapsed .sp-sidebar__link {
  justify-content: center;
  padding: var(--sp-space-3);
}

.sp-sidebar__section-label {
  font-size: var(--sp-font-size-xs);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--sp-space-4) var(--sp-space-4) var(--sp-space-2);
}

.sp-sidebar--collapsed .sp-sidebar__section-label {
  display: none;
}
```

### Breadcrumbs

Separator-divided path with truncation for deep nesting.

```css
.sp-breadcrumbs {
  display: flex;
  align-items: center;
  gap: var(--sp-space-2);
  font-size: var(--sp-font-size-sm);
  padding: var(--sp-space-3) 0;
  overflow: hidden;
}

.sp-breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: var(--sp-space-2);
  white-space: nowrap;
}

.sp-breadcrumbs__link {
  color: var(--sp-color-text-muted);
  text-decoration: none;
  transition: color 0.15s ease;
}

.sp-breadcrumbs__link:hover {
  color: var(--sp-color-primary);
  text-decoration: underline;
}

.sp-breadcrumbs__separator {
  color: var(--sp-color-text-muted);
  font-size: var(--sp-font-size-xs);
}

.sp-breadcrumbs__current {
  color: var(--sp-color-text);
  font-weight: var(--sp-font-weight-medium);
}

/* Truncation for deep paths */
.sp-breadcrumbs__ellipsis {
  color: var(--sp-color-text-muted);
  cursor: pointer;
  padding: var(--sp-space-1) var(--sp-space-2);
  border-radius: var(--sp-corners-sm);
}

.sp-breadcrumbs__ellipsis:hover {
  background: var(--sp-color-surface-hover);
}
```

### Tabs

Bottom border sliding indicator with scrollable overflow.

```css
.sp-tabs {
  position: relative;
  border-bottom: 1px solid var(--sp-color-border-light);
  overflow-x: auto;
  scrollbar-width: none;
}

.sp-tabs::-webkit-scrollbar {
  display: none;
}

.sp-tabs__list {
  display: flex;
  gap: var(--sp-space-1);
  list-style: none;
  margin: 0;
  padding: 0;
}

.sp-tabs__tab {
  padding: var(--sp-space-3) var(--sp-space-4);
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-medium);
  color: var(--sp-color-text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.sp-tabs__tab:hover {
  color: var(--sp-color-text);
}

.sp-tabs__tab--active {
  color: var(--sp-color-primary);
  border-bottom-color: var(--sp-color-primary);
}

/* Fade edges for scroll indication */
.sp-tabs--scrollable::before,
.sp-tabs--scrollable::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  width: 40px;
  pointer-events: none;
  z-index: 1;
}

.sp-tabs--scrollable::before {
  left: 0;
  background: linear-gradient(to right, var(--sp-color-surface), transparent);
}

.sp-tabs--scrollable::after {
  right: 0;
  background: linear-gradient(to left, var(--sp-color-surface), transparent);
}
```

### Pagination

Current page highlighted, prev/next, ellipsis for long ranges.

```css
.sp-pagination {
  display: flex;
  align-items: center;
  gap: var(--sp-space-1);
  font-size: var(--sp-font-size-sm);
}

.sp-pagination__btn {
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--sp-space-2);
  border: 1px solid var(--sp-color-border);
  border-radius: var(--sp-corners-sm);
  background: var(--sp-color-surface);
  color: var(--sp-color-text);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.sp-pagination__btn:hover:not(:disabled) {
  background: var(--sp-color-surface-hover);
  border-color: var(--sp-color-primary);
}

.sp-pagination__btn--active {
  background: var(--sp-color-primary);
  border-color: var(--sp-color-primary);
  color: var(--sp-color-on-primary);
  font-weight: var(--sp-font-weight-semibold);
}

.sp-pagination__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.sp-pagination__ellipsis {
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sp-color-text-muted);
}
```

---

## Dashboard Layout Patterns

### Scanning Patterns

**F-pattern** (data-heavy dashboards): Users scan left-to-right across the top (KPIs), then down the left edge (nav/labels), with decreasing attention rightward. Place critical KPIs top-left, secondary metrics across the top row, and detail tables below.

**Z-pattern** (simpler dashboards): Users scan top-left to top-right, diagonally to bottom-left, then across to bottom-right. Place the logo/title top-left, primary action top-right, context bottom-left, CTA bottom-right.

### Dashboard Grid

Named grid areas for semantic layout.

```css
.sp-dashboard {
  display: grid;
  grid-template-areas:
    "kpi kpi kpi"
    "chart chart sidebar"
    "table table sidebar";
  grid-template-columns: 1fr 1fr 300px;
  grid-template-rows: auto 1fr 1fr;
  gap: var(--sp-space-4);
  padding: var(--sp-space-4);
  min-height: 100vh;
}

.sp-dashboard__kpi { grid-area: kpi; }
.sp-dashboard__chart { grid-area: chart; }
.sp-dashboard__sidebar { grid-area: sidebar; }
.sp-dashboard__table { grid-area: table; }

/* Responsive: single column on mobile */
@media (max-width: 768px) {
  .sp-dashboard {
    grid-template-areas:
      "kpi"
      "chart"
      "sidebar"
      "table";
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
}
```

### KPI Row

3-5 metric cards in equal columns. Never exceed 5 -- cognitive overload threshold.

```html
<div class="sp-kpi-row">
  <div class="sp-metric-card"><!-- ... --></div>
  <div class="sp-metric-card"><!-- ... --></div>
  <div class="sp-metric-card"><!-- ... --></div>
  <div class="sp-metric-card"><!-- ... --></div>
</div>
```

```css
.sp-kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--sp-space-4);
}

/* Cap at 5 columns */
@media (min-width: 1200px) {
  .sp-kpi-row {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    max-width: 1400px;
  }
}
```

### Data Density Guidelines

| Density | Line Height | Cell Padding | Font Size | Use Case |
|---|---|---|---|---|
| Low | 1.8 | `--sp-space-4` | `--sp-font-size-base` | Consumer dashboards, onboarding |
| Medium | 1.6 | `--sp-space-3` | `--sp-font-size-sm` | Business dashboards (default) |
| High | 1.4 | `--sp-space-2` | `--sp-font-size-xs` | Analyst tools, data exploration |

```css
.sp-density--low { --sp-density-padding: var(--sp-space-4); --sp-density-font: var(--sp-font-size-base); line-height: 1.8; }
.sp-density--medium { --sp-density-padding: var(--sp-space-3); --sp-density-font: var(--sp-font-size-sm); line-height: 1.6; }
.sp-density--high { --sp-density-padding: var(--sp-space-2); --sp-density-font: var(--sp-font-size-xs); line-height: 1.4; }
```

---

## Data Visualization Helpers

### Sparkline (SVG)

Inline SVG with gradient fill beneath the line.

```html
<svg class="sp-sparkline" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true" role="img">
  <defs>
    <linearGradient id="sp-spark-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--sp-color-primary)" stop-opacity="0.2" />
      <stop offset="100%" stop-color="var(--sp-color-primary)" stop-opacity="0" />
    </linearGradient>
  </defs>
  <polygon points="0,30 0,25 15,20 30,22 45,15 60,18 75,8 100,5 100,30" fill="url(#sp-spark-grad)" />
  <polyline points="0,25 15,20 30,22 45,15 60,18 75,8 100,5" fill="none" stroke="var(--sp-color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
</svg>
```

```css
.sp-sparkline {
  width: 100%;
  height: 30px;
  display: block;
}
```

### Progress Bar

CSS-only animated fill with color variants.

```html
<div class="sp-progress" role="progressbar" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100" aria-label="Upload progress">
  <div class="sp-progress__fill" style="width: 65%"></div>
</div>
```

```css
.sp-progress {
  height: 8px;
  border-radius: 999px;
  background: var(--sp-color-surface-alt);
  overflow: hidden;
}

.sp-progress__fill {
  height: 100%;
  border-radius: 999px;
  background: var(--sp-color-primary);
  transition: width 0.4s ease;
}

.sp-progress--success .sp-progress__fill { background: var(--sp-color-success); }
.sp-progress--warning .sp-progress__fill { background: var(--sp-color-warning); }
.sp-progress--danger .sp-progress__fill  { background: var(--sp-color-danger); }

/* Indeterminate animation */
.sp-progress--indeterminate .sp-progress__fill {
  width: 30%;
  animation: sp-progress-slide 1.5s ease-in-out infinite;
}

@keyframes sp-progress-slide {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}
```

### Status Indicator

Colored dot with optional pulse for live states.

```html
<span class="sp-status sp-status--active">
  <span class="sp-status__dot" aria-hidden="true"></span>
  <span class="sp-status__label">Active</span>
</span>
```

```css
.sp-status {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-space-2);
  font-size: var(--sp-font-size-sm);
}

.sp-status__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sp-status--active  .sp-status__dot { background: var(--sp-color-success); }
.sp-status--warning .sp-status__dot { background: var(--sp-color-warning); }
.sp-status--error   .sp-status__dot { background: var(--sp-color-danger); }
.sp-status--idle    .sp-status__dot { background: var(--sp-color-text-muted); }

/* Pulse for live */
.sp-status--live .sp-status__dot {
  animation: sp-pulse 2s ease-in-out infinite;
}

@keyframes sp-pulse {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.4; }
}
```

### Trend Arrow

Directional indicator using CSS triangles.

```css
.sp-trend {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-space-1);
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-medium);
}

.sp-trend__arrow {
  display: inline-block;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
}

.sp-trend--up {
  color: var(--sp-color-success);
}

.sp-trend--up .sp-trend__arrow {
  border-bottom: 6px solid currentColor;
}

.sp-trend--down {
  color: var(--sp-color-danger);
}

.sp-trend--down .sp-trend__arrow {
  border-top: 6px solid currentColor;
}

.sp-trend--flat {
  color: var(--sp-color-text-muted);
}

.sp-trend--flat .sp-trend__arrow {
  width: 10px;
  height: 2px;
  background: currentColor;
  border: none;
}
```

---

## Empty State Patterns

Centered layout: icon, heading, description, CTA. Used when a section has no data yet.

```html
<div class="sp-empty-state">
  <div class="sp-empty-state__icon" aria-hidden="true">
    <svg width="64" height="64" viewBox="0 0 64 64">
      <!-- illustration SVG -->
    </svg>
  </div>
  <h3 class="sp-empty-state__title">No projects yet</h3>
  <p class="sp-empty-state__description">Create your first project to get started building with systemprompt.</p>
  <button class="sp-btn sp-btn--primary">Create Project</button>
</div>
```

```css
.sp-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--sp-space-8) var(--sp-space-5);
  max-width: 400px;
  margin: 0 auto;
}

.sp-empty-state__icon {
  width: 120px;
  max-width: 200px;
  margin-bottom: var(--sp-space-5);
  color: var(--sp-color-text-muted);
  opacity: 0.6;
}

.sp-empty-state__icon svg {
  width: 100%;
  height: auto;
}

.sp-empty-state__title {
  font-size: var(--sp-font-size-lg);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text);
  margin: 0 0 var(--sp-space-2);
}

.sp-empty-state__description {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-muted);
  line-height: var(--sp-line-height-relaxed);
  margin: 0 0 var(--sp-space-5);
}
```

---

## Feedback Patterns

### Toast Notification

Bottom-right stacked, auto-dismiss. Info/success dismiss in 5s, errors persist.

```html
<div class="sp-toast-container" aria-live="polite" aria-relevant="additions">
  <div class="sp-toast sp-toast--success" role="status">
    <span class="sp-toast__icon" aria-hidden="true">&#10003;</span>
    <div class="sp-toast__content">
      <span class="sp-toast__message">Settings saved successfully.</span>
      <button class="sp-toast__action">Undo</button>
    </div>
    <button class="sp-toast__close" aria-label="Dismiss notification">&times;</button>
  </div>
</div>
```

```css
.sp-toast-container {
  position: fixed;
  bottom: var(--sp-space-5);
  right: var(--sp-space-5);
  z-index: var(--sp-z-toast);
  display: flex;
  flex-direction: column-reverse;
  gap: var(--sp-space-3);
  max-width: 420px;
}

.sp-toast {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-space-3);
  padding: var(--sp-space-4);
  border-radius: var(--sp-corners-md);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-lg);
  animation: sp-toast-in 0.3s ease forwards;
}

.sp-toast--exiting {
  animation: sp-toast-out 0.2s ease forwards;
}

@keyframes sp-toast-in {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}

@keyframes sp-toast-out {
  from { transform: translateX(0); opacity: 1; }
  to   { transform: translateX(100%); opacity: 0; }
}

.sp-toast__icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--sp-font-size-sm);
}

.sp-toast--success .sp-toast__icon { color: var(--sp-color-success); }
.sp-toast--error   .sp-toast__icon { color: var(--sp-color-danger); }
.sp-toast--warning .sp-toast__icon { color: var(--sp-color-warning); }
.sp-toast--info    .sp-toast__icon { color: var(--sp-color-info); }

.sp-toast__content {
  flex: 1;
}

.sp-toast__message {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text);
}

.sp-toast__action {
  background: none;
  border: none;
  color: var(--sp-color-primary);
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-medium);
  cursor: pointer;
  padding: 0;
  margin-left: var(--sp-space-2);
}

.sp-toast__close {
  background: none;
  border: none;
  color: var(--sp-color-text-muted);
  font-size: var(--sp-font-size-lg);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
```

### Inline Alert

Full-width alert with left border accent and tinted background.

```html
<div class="sp-alert sp-alert--warning" role="alert">
  <span class="sp-alert__icon" aria-hidden="true">&#9888;</span>
  <div class="sp-alert__content">
    <strong class="sp-alert__title">Rate limit approaching</strong>
    <p class="sp-alert__message">You have used 90% of your API quota for this month.</p>
  </div>
</div>
```

```css
.sp-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-space-3);
  padding: var(--sp-space-4) var(--sp-space-5);
  border-radius: var(--sp-corners-sm);
  border-left: 4px solid;
}

.sp-alert--info {
  background: var(--sp-color-info-surface);
  border-left-color: var(--sp-color-info);
}

.sp-alert--success {
  background: var(--sp-color-success-surface);
  border-left-color: var(--sp-color-success);
}

.sp-alert--warning {
  background: var(--sp-color-warning-surface);
  border-left-color: var(--sp-color-warning);
}

.sp-alert--error {
  background: var(--sp-color-danger-surface);
  border-left-color: var(--sp-color-danger);
}

.sp-alert__icon {
  flex-shrink: 0;
  font-size: var(--sp-font-size-lg);
}

.sp-alert--info    .sp-alert__icon { color: var(--sp-color-info); }
.sp-alert--success .sp-alert__icon { color: var(--sp-color-success); }
.sp-alert--warning .sp-alert__icon { color: var(--sp-color-warning); }
.sp-alert--error   .sp-alert__icon { color: var(--sp-color-danger); }

.sp-alert__title {
  font-size: var(--sp-font-size-sm);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text);
  display: block;
  margin-bottom: var(--sp-space-1);
}

.sp-alert__message {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-secondary);
  margin: 0;
}
```

### Confirmation Dialog

Centered modal with backdrop. Uses branded `--sp-corners-lg` for the dialog container.

```html
<div class="sp-dialog-backdrop" aria-hidden="true"></div>
<dialog class="sp-dialog" role="alertdialog" aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <h2 class="sp-dialog__title" id="dialog-title">Delete Project?</h2>
  <p class="sp-dialog__description" id="dialog-desc">This action cannot be undone. All data associated with this project will be permanently removed.</p>
  <div class="sp-dialog__actions">
    <button class="sp-btn sp-btn--secondary">Cancel</button>
    <button class="sp-btn sp-btn--danger">Delete Project</button>
  </div>
</dialog>
```

```css
.sp-dialog-backdrop {
  position: fixed;
  inset: 0;
  background: oklch(0 0 0 / 0.5);
  z-index: var(--sp-z-modal);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.sp-dialog-backdrop--visible {
  opacity: 1;
}

.sp-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: calc(var(--sp-z-modal) + 1);
  border-radius: var(--sp-corners-lg);
  background: var(--sp-color-surface);
  box-shadow: var(--sp-shadow-xl);
  padding: var(--sp-space-6);
  max-width: 480px;
  width: calc(100% - var(--sp-space-8));
  border: none;
}

.sp-dialog__title {
  font-size: var(--sp-font-size-lg);
  font-weight: var(--sp-font-weight-semibold);
  color: var(--sp-color-text);
  margin: 0 0 var(--sp-space-3);
}

.sp-dialog__description {
  font-size: var(--sp-font-size-sm);
  color: var(--sp-color-text-secondary);
  line-height: var(--sp-line-height-relaxed);
  margin: 0 0 var(--sp-space-5);
}

.sp-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-space-3);
}

.sp-btn--danger {
  background: var(--sp-color-danger);
  color: var(--sp-color-on-danger);
  border: none;
}

.sp-btn--danger:hover {
  background: var(--sp-color-danger-hover);
}
```

---

## Visual Quality Benchmarks

What separates world-class from mediocre at the component level. Use these as measurable audit criteria.

| Dimension | Mediocre | World-Class | How to Measure |
|---|---|---|---|
| **Spacing consistency** | Mixed arbitrary values | Every value from `--sp-space-*` scale | Grep for hardcoded px/rem in padding/margin/gap |
| **Corner branding** | Symmetric `border-radius` | Asymmetric `var(--sp-corners-*)` on all containers | Grep for `border-radius` not using corner tokens |
| **Shadow depth** | No shadows or single flat shadow | Layered shadows that shift on interaction | Check hover states have shadow elevation change |
| **Color semantics** | Raw color values | All colors from semantic tokens (`--sp-color-*`) | Zero raw hex/rgb/hsl in component CSS |
| **Typography scale** | Arbitrary font sizes | All sizes from `--sp-font-size-*` scale | Grep for hardcoded font-size values |
| **Hover feedback** | No hover states | Every interactive element has visible hover change | Tab/hover through every clickable element |
| **Focus visibility** | Browser default or none | Custom focus ring matching brand (3px primary ring) | Keyboard-navigate entire interface |
| **Loading states** | Content jump on load | Skeleton screens or progressive reveal | Load page on throttled network |
| **Empty states** | Blank area or raw "No data" | Designed empty state with icon + CTA | Navigate to every empty-capable section |
| **Responsive behavior** | Broken on narrow screens | Container-query-driven layout adaptation | Test at 320px, 768px, 1024px, 1440px |
| **Animation purpose** | Decorative or excessive | Functional (guide attention, confirm action) | Each animation answers "what does this communicate?" |
| **Density control** | One-size-fits-all | Adjustable via density modifier classes | Toggle density classes and verify padding/font changes |

---

## Review Checklist

Run through this checklist when reviewing any component implementation.

### Branding
- [ ] All cards/containers use branded asymmetric corners (`--sp-corners-*`), not symmetric `border-radius`
- [ ] Modal/dialog uses `--sp-corners-lg`, cards use `--sp-corners-md`, small elements use `--sp-corners-sm`
- [ ] No hardcoded `border-radius` pixel values on containers

### Token Usage
- [ ] Zero hardcoded color values -- all from `--sp-color-*`
- [ ] Zero hardcoded spacing -- all from `--sp-space-*`
- [ ] Zero hardcoded font sizes -- all from `--sp-font-size-*`
- [ ] Shadows use `--sp-shadow-*` tokens

### Component Structure
- [ ] BEM naming follows `.sp-block__element--modifier` convention
- [ ] Interactive elements have hover, focus, and active states
- [ ] Disabled states reduce opacity and set `cursor: not-allowed`
- [ ] Card hover includes `translateY(-1px)` + shadow elevation

### Responsive
- [ ] Tables collapse to card layout on narrow screens
- [ ] Horizontal cards stack vertically via container query
- [ ] Navigation switches to mobile pattern at breakpoint
- [ ] Bento grid spans collapse to single column

### Accessibility
- [ ] `role` attributes on custom widgets (alert, dialog, progressbar, status)
- [ ] `aria-label` or `aria-labelledby` on all interactive regions
- [ ] `aria-expanded` on expandable triggers
- [ ] `aria-current` on active navigation items
- [ ] `aria-live` on toast containers
- [ ] Error messages use `role="alert"`
- [ ] Decorative icons use `aria-hidden="true"`

### Feedback
- [ ] Form errors show inline + summary with field links
- [ ] Toast auto-dismiss: 5s for info/success, persistent for errors
- [ ] Confirmation dialogs for destructive actions
- [ ] Loading states for async operations (skeleton or spinner)

### Data Visualization
- [ ] Sparklines use fixed `viewBox` with responsive width
- [ ] Progress bars have `role="progressbar"` with `aria-valuenow`
- [ ] Status dots use semantic colors matching state meaning
- [ ] Trend arrows use CSS (not images) for performance
