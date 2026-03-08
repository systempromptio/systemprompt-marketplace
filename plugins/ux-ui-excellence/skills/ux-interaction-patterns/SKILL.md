---
name: ux-interaction-patterns
description: "UX laws as code — micro-interactions, animation choreography, skeleton UIs, optimistic UI, and performance UX patterns for world-class user experience"
version: "1.0.0"
git_hash: "0000000"
---

# UX Interaction Patterns

UX interaction patterns for systemprompt.io. This skill complements `frontend-coding-standards` (which covers event delegation, Web Component lifecycle, basic ARIA/focus/keyboard, and `prefers-reduced-motion`). Nothing from that skill is repeated here. Follow without exception.

## Core Principle

The difference between software that "works" and software that "delights" is interaction quality. Every state change, every user action, every loading moment is an opportunity to build trust and reduce cognitive load. UX laws are not theory here — they are code rules with measurable thresholds.

---

## UX Laws as Code

These are implementation rules with hard numbers. Do not treat them as suggestions.

### Doherty Threshold — All Feedback Within 400ms

The system must acknowledge every user action within 400ms or the user perceives it as broken.

**Timing budget:**

| Elapsed Time | Required Response | Implementation |
|---|---|---|
| 0–100ms | Instant feedback | CSS `:active` state, optimistic UI |
| 100–300ms | Loading indicator | Inline spinner, progress bar |
| 300ms+ | Skeleton or progress | Skeleton UI, determinate progress |
| 1500ms+ | Explanatory text | "Loading your dashboard..." message |

**CSS transition durations by category:**

```css
:root {
  --sp-duration-instant: 50ms;    /* Checkbox, radio, toggle snap */
  --sp-duration-fast: 100ms;      /* Button press, hover highlight */
  --sp-duration-normal: 200ms;    /* Dropdown open, accordion expand */
  --sp-duration-moderate: 300ms;  /* Modal enter, sidebar slide */
  --sp-duration-slow: 400ms;      /* Page transition, card reorder */
  --sp-duration-slower: 600ms;    /* Emphasis animation, success */
}
```

**Rule**: Never use a raw `ms` value in a transition. Always reference a `--sp-duration-*` token.

### Fitts's Law — Target Size

Larger, closer targets are faster to hit. Every interactive element must meet minimum sizes.

```css
/* Minimum touch target — 24×24px absolute minimum */
.sp-btn--icon {
  min-width: 24px;
  min-height: 24px;
}

/* Primary actions — 44×44px minimum */
.sp-btn--primary {
  min-width: 44px;
  min-height: 44px;
  padding: 10px 20px;
}

/* Padding-based hit area expansion for small visual elements */
.sp-link--inline {
  padding: 8px;
  margin: -8px;
  /* Visual size stays the same, tap target grows */
}
```

**Rules:**
- Primary actions (submit, save, confirm): minimum 44x44px
- Secondary actions (icon buttons, toggles): minimum 24x24px
- Place frequent actions at screen edges and corners (infinite target width on edges)
- Destructive actions (delete, remove) must be physically distant from confirm/save

### Hick's Law — Choice Overload

Decision time increases logarithmically with the number of options. Limit visible choices.

```html
<!-- BAD: 12 actions in a flat toolbar -->
<div class="sp-toolbar">
  <button>Bold</button><button>Italic</button><button>Underline</button>
  <button>H1</button><button>H2</button><button>H3</button>
  <button>Link</button><button>Image</button><button>Code</button>
  <button>Quote</button><button>List</button><button>Table</button>
</div>

<!-- GOOD: 5 primary + grouped overflow -->
<div class="sp-toolbar">
  <button>Bold</button>
  <button>Italic</button>
  <button>Link</button>
  <button>Image</button>
  <button class="sp-toolbar__more" aria-expanded="false">
    More
    <!-- Remaining options in dropdown -->
  </button>
</div>
```

**Rules:**
- Maximum **7 +/- 2** visible options before grouping behind a disclosure
- Progressive disclosure: primary actions visible, secondary behind "More" or overflow menu
- Maximum **7** top-level navigation items
- Multi-step forms: show only the current step's fields

### Jakob's Law — Familiarity

Users spend most of their time on other sites. Match established conventions.

| Convention | Expected Placement | Implementation |
|---|---|---|
| Logo → home link | Top-left corner | `<a href="/" class="sp-logo">` |
| Search | Top-right area | Magnifying glass icon, `Ctrl+K` / `Cmd+K` shortcut |
| Primary navigation | Top horizontal or left sidebar | `<nav class="sp-nav">` |
| User menu | Top-right corner | Avatar dropdown |
| Close button | Top-right of modal/dialog | `<button class="sp-dialog__close">` |
| Back navigation | Top-left or breadcrumb | Left arrow or breadcrumb trail |

**Standard icon meanings — do not deviate:**
- Hamburger (three lines): open menu
- X: close/dismiss
- Magnifying glass: search
- Gear: settings
- Bell: notifications
- Plus: create new

### Peak-End Rule — Memory

Users judge an experience by its peak moment and its end. Optimise the final interaction.

```css
/* Success state celebration — the peak moment */
.sp-success-check {
  animation: sp-success-draw var(--sp-duration-slower) ease-out forwards;
}

@keyframes sp-success-draw {
  0% {
    stroke-dashoffset: 100;
    opacity: 0;
  }
  40% {
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
}
```

```html
<!-- SVG checkmark for success feedback -->
<svg class="sp-success-check" viewBox="0 0 24 24" width="48" height="48">
  <circle cx="12" cy="12" r="10" fill="none" stroke="var(--sp-color-success)" stroke-width="2" />
  <path d="M7 13l3 3 7-7" fill="none" stroke="var(--sp-color-success)"
        stroke-width="2" stroke-dasharray="100" />
</svg>
```

**Rules:**
- Page must be visually complete within **1.5s** (Largest Contentful Paint target)
- Success states must animate (checkmark draw, confetti, green flash) — never a static icon swap
- Error states must clearly explain recovery — never a dead end
- Form submission success: animate confirmation, then auto-redirect or clear form

### Miller's Law — Chunking

Working memory holds 7 +/- 2 items. Group related content visually.

```css
/* Group items with spacing — not borders alone */
.sp-metric-group {
  display: flex;
  gap: var(--sp-space-4);
}

/* Distinct groups separated by larger gaps */
.sp-dashboard__section + .sp-dashboard__section {
  margin-top: var(--sp-space-8);
}

/* Visual grouping with subtle background */
.sp-field-group {
  background: var(--sp-color-bg-surface);
  border-radius: var(--sp-radius-md);
  padding: var(--sp-space-4);
}
```

**Rules:**
- Dashboard metrics: groups of **3–5** cards maximum
- Form fields: group related inputs with fieldset/visual containers
- Lists longer than 7 items: add section headings or alphabetical dividers
- Phone numbers, card numbers: display with chunked spacing (`1234 5678 9012 3456`)

---

## Animation Timing Standards

Every animation in the system must use a timing token. These are non-negotiable.

| Category | Duration | Easing | Token | Example |
|---|---|---|---|---|
| Micro-feedback | 100–150ms | `ease-out` | `--sp-duration-fast` | Button press, toggle snap, checkbox |
| Content reveal | 200–300ms | `ease-out` | `--sp-duration-normal` | Dropdown open, accordion expand, tooltip |
| Layout shift | 250–400ms | `ease-in-out` | `--sp-duration-slow` | Card reorder, grid resize, sidebar |
| Page transition | 300–500ms | `ease-in-out` | `--sp-duration-slow` | Route change, modal enter/exit |
| Emphasis | 400–600ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` | `--sp-duration-slower` | Success animation, attention pulse |

**Easing tokens:**

```css
:root {
  --sp-ease-default: ease-out;
  --sp-ease-in-out: ease-in-out;
  --sp-ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --sp-ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

**Enter vs exit asymmetry:**
- Enter animations: use `ease-out` (fast start, gentle stop — element arrives)
- Exit animations: use `ease-in` (gentle start, fast finish — element leaves)
- Never use `linear` for UI transitions — it feels mechanical

---

## Micro-Interaction Recipes

Complete CSS for each. Copy directly into components.

### Button Press

```css
.sp-btn {
  transition:
    transform var(--sp-duration-fast) var(--sp-ease-default),
    background-color var(--sp-duration-fast) var(--sp-ease-default),
    box-shadow var(--sp-duration-fast) var(--sp-ease-default);
}

.sp-btn:hover {
  background-color: var(--sp-color-primary-hover);
  box-shadow: var(--sp-shadow-md);
}

.sp-btn:active {
  transform: scale(0.97);
  box-shadow: var(--sp-shadow-sm);
}

/* Focus ring only on keyboard navigation */
.sp-btn:focus-visible {
  outline: 2px solid var(--sp-color-ring);
  outline-offset: 2px;
}
```

### Form Field Focus

```css
.sp-input {
  border: 1px solid var(--sp-color-border);
  border-radius: var(--sp-radius-sm);
  padding: var(--sp-space-2) var(--sp-space-3);
  transition:
    border-color var(--sp-duration-fast) var(--sp-ease-default),
    box-shadow var(--sp-duration-fast) var(--sp-ease-default);
}

.sp-input:focus {
  border-color: var(--sp-color-primary);
  box-shadow: 0 0 0 3px oklch(from var(--sp-color-primary) l c h / 0.15);
  outline: none;
}

/* Floating label animation */
.sp-field__label {
  position: absolute;
  top: 50%;
  left: var(--sp-space-3);
  transform: translateY(-50%);
  transition:
    transform var(--sp-duration-normal) var(--sp-ease-default),
    font-size var(--sp-duration-normal) var(--sp-ease-default),
    color var(--sp-duration-normal) var(--sp-ease-default);
  pointer-events: none;
  color: var(--sp-color-text-muted);
}

.sp-input:focus + .sp-field__label,
.sp-input:not(:placeholder-shown) + .sp-field__label {
  transform: translateY(-130%);
  font-size: 0.75rem;
  color: var(--sp-color-primary);
}

/* Validation states */
.sp-input[aria-invalid="true"] {
  border-color: var(--sp-color-error);
}

.sp-input[aria-invalid="true"]:focus {
  box-shadow: 0 0 0 3px oklch(from var(--sp-color-error) l c h / 0.15);
}
```

### Card Hover

```css
.sp-card {
  border: 1px solid var(--sp-color-border);
  border-radius: var(--sp-radius-md);
  transition:
    transform var(--sp-duration-normal) var(--sp-ease-default),
    box-shadow var(--sp-duration-normal) var(--sp-ease-default),
    border-color var(--sp-duration-normal) var(--sp-ease-default);
}

.sp-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--sp-shadow-lg);
  border-color: var(--sp-color-border-strong);
}

.sp-card:active {
  transform: translateY(0);
  box-shadow: var(--sp-shadow-sm);
}
```

### Toggle Switch

```css
.sp-toggle {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--sp-color-bg-muted);
  position: relative;
  cursor: pointer;
  transition: background-color var(--sp-duration-normal) var(--sp-ease-in-out);
}

.sp-toggle[aria-checked="true"] {
  background: var(--sp-color-primary);
}

/* Thumb */
.sp-toggle::after {
  content: "";
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  top: 2px;
  left: 2px;
  transition: transform var(--sp-duration-normal) var(--sp-ease-bounce);
  box-shadow: var(--sp-shadow-sm);
}

.sp-toggle[aria-checked="true"]::after {
  transform: translateX(20px);
}
```

### Loading Button

```css
.sp-btn--loading {
  position: relative;
  pointer-events: none;
  /* Maintain width to prevent layout shift */
  min-width: var(--sp-btn-width, auto);
}

.sp-btn--loading .sp-btn__text {
  opacity: 0;
  transition: opacity var(--sp-duration-fast) var(--sp-ease-default);
}

.sp-btn--loading .sp-btn__spinner {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;
  transition: opacity var(--sp-duration-fast) var(--sp-ease-default);
}

/* Spinner keyframes */
@keyframes sp-spin {
  to { transform: rotate(360deg); }
}

.sp-btn__spinner::after {
  content: "";
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: sp-spin 600ms linear infinite;
}
```

```js
// Loading button state management
function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.style.setProperty('--sp-btn-width', `${button.offsetWidth}px`);
    button.classList.add('sp-btn--loading');
    button.setAttribute('aria-disabled', 'true');
  } else {
    button.classList.remove('sp-btn--loading');
    button.removeAttribute('aria-disabled');
  }
}
```

---

## Skeleton UI Patterns

Skeletons are always preferred over spinners. They preserve layout, reduce perceived wait time, and prevent Cumulative Layout Shift (CLS).

### Why Skeletons Over Spinners

| | Skeleton | Spinner |
|---|---|---|
| Layout preserved | Yes — matches final content dimensions | No — single centered element |
| Perceived speed | Faster — brain fills in expected content | Slower — empty void |
| CLS impact | Zero — same dimensions as real content | High — content pushes spinner away |
| User orientation | User sees page structure immediately | User has no context |

**Rule**: Spinners are permitted ONLY inside elements smaller than 48px (e.g., inline button loading). Everything else uses a skeleton.

### Shimmer Animation

```css
@keyframes sp-shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.sp-skeleton {
  background: linear-gradient(
    90deg,
    var(--sp-color-bg-muted) 25%,
    var(--sp-color-bg-surface) 50%,
    var(--sp-color-bg-muted) 75%
  );
  background-size: 200% 100%;
  animation: sp-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--sp-radius-sm);
}
```

### Skeleton Variants

```css
/* Text line */
.sp-skeleton--text {
  height: 1em;
  width: 100%;
  margin-bottom: 0.5em;
}

.sp-skeleton--text:last-child {
  width: 70%; /* Last line shorter for natural look */
}

/* Avatar */
.sp-skeleton--avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Card */
.sp-skeleton--card {
  height: 200px;
  border-radius: var(--sp-radius-md);
}

/* Table row */
.sp-skeleton--row {
  height: 48px;
  width: 100%;
  margin-bottom: 2px;
}
```

### Complete Skeleton Card

```html
<div class="sp-card sp-card--skeleton" aria-busy="true" aria-label="Loading content">
  <div class="sp-card__media sp-skeleton" style="height: 180px;"></div>
  <div class="sp-card__body">
    <div class="sp-skeleton sp-skeleton--text" style="width: 60%;"></div>
    <div class="sp-skeleton sp-skeleton--text"></div>
    <div class="sp-skeleton sp-skeleton--text"></div>
    <div class="sp-skeleton sp-skeleton--text" style="width: 70%;"></div>
  </div>
  <div class="sp-card__footer">
    <div class="sp-skeleton" style="width: 80px; height: 32px; border-radius: var(--sp-radius-sm);"></div>
  </div>
</div>
```

### Skeleton to Real Content Crossfade

```css
/* Content replaces skeleton with crossfade */
.sp-skeleton-container[aria-busy="true"] > :not(.sp-skeleton) {
  opacity: 0;
}

.sp-skeleton-container[aria-busy="false"] > .sp-skeleton {
  display: none;
}

.sp-skeleton-container[aria-busy="false"] > :not(.sp-skeleton) {
  animation: sp-fade-in var(--sp-duration-normal) var(--sp-ease-default) forwards;
}

@keyframes sp-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

```js
// Transition from skeleton to content
function revealContent(container) {
  container.setAttribute('aria-busy', 'false');
}
```

---

## Optimistic UI

Update the UI immediately on user action. Send the request in the background. Revert only if it fails.

### When to Use

| Use Optimistic UI | Do NOT Use Optimistic UI |
|---|---|
| Toggling favorites, likes, bookmarks | Financial transactions (payments, transfers) |
| Updating user preferences | Destructive deletes with no undo |
| Sending messages (chat) | Actions requiring server-side validation |
| Reordering items (drag-and-drop) | Multi-step workflows (checkout, signup) |
| Marking notifications as read | Actions with rate limits or quotas |

### Implementation Pattern

```js
async function optimisticUpdate(element, updateFn, apiCall) {
  // 1. Capture previous state for rollback
  const previousState = element.cloneNode(true);
  const previousAriaLabel = element.getAttribute('aria-label');

  // 2. Apply optimistic update immediately
  updateFn(element);

  // 3. Show subtle saving indicator
  element.setAttribute('aria-label',
    `${previousAriaLabel} — saving`);

  try {
    // 4. Send request to server
    await apiCall();

    // 5. Confirm success (brief flash or checkmark)
    element.setAttribute('aria-label', previousAriaLabel);
    showToast('Saved', 'success');
  } catch (error) {
    // 6. Revert on failure
    element.replaceWith(previousState);
    showToast('Failed to save. Please try again.', 'error');
  }
}

// Example: Toggle favorite
const heart = document.querySelector('.sp-favorite-btn');
heart.addEventListener('click', () => {
  optimisticUpdate(
    heart,
    (el) => el.setAttribute('aria-pressed',
      el.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'),
    () => fetch('/api/favorites', { method: 'POST', body: JSON.stringify({ id: heart.dataset.id }) })
  );
});
```

### Saving Indicator CSS

```css
/* Subtle saving state */
.sp-saving-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-space-1);
  font-size: 0.75rem;
  color: var(--sp-color-text-muted);
  opacity: 0;
  transition: opacity var(--sp-duration-fast) var(--sp-ease-default);
}

.sp-saving-indicator[aria-hidden="false"] {
  opacity: 1;
}

.sp-saving-indicator::before {
  content: "";
  width: 8px;
  height: 8px;
  border: 1.5px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: sp-spin 600ms linear infinite;
}
```

---

## Loading State Hierarchy

Use the highest applicable level. Lower numbers are better UX.

| Priority | Pattern | When to Use | Example |
|---|---|---|---|
| 1 | **Optimistic UI** | Action likely succeeds (>95%) | Toggle, favorite, mark read |
| 2 | **Skeleton screen** | Initial page/view load | Dashboard first paint, feed load |
| 3 | **Inline skeleton** | Component-level data fetch | Single card refresh, table reload |
| 4 | **Progress bar** | Known duration/progress | File upload, multi-step wizard |
| 5 | **Inline spinner** | Tiny areas (<48px) only | Button submit, icon action |
| 6 | **Full-page loader** | **NEVER** | **Anti-pattern — always banned** |

```css
/* Determinate progress bar */
.sp-progress {
  width: 100%;
  height: 4px;
  background: var(--sp-color-bg-muted);
  border-radius: 2px;
  overflow: hidden;
}

.sp-progress__bar {
  height: 100%;
  background: var(--sp-color-primary);
  border-radius: 2px;
  transition: width var(--sp-duration-normal) var(--sp-ease-in-out);
}

/* Indeterminate progress bar */
.sp-progress--indeterminate .sp-progress__bar {
  width: 40%;
  animation: sp-progress-slide 1.5s ease-in-out infinite;
}

@keyframes sp-progress-slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}
```

**Rule**: If you find yourself reaching for a full-page spinner, stop. Use a skeleton of the target page instead. A full-page loader is always a design failure.

---

## Performance UX Patterns

These CSS and HTML patterns directly impact perceived performance and Core Web Vitals.

### Resource Prioritization

```html
<!-- Hero image: tell browser this is critical -->
<img src="hero.webp" alt="..." fetchpriority="high" loading="eager"
     width="1200" height="600" />

<!-- Below-fold images: lazy load -->
<img src="card.webp" alt="..." loading="lazy"
     width="400" height="300" />

<!-- Preconnect to API domain (saves ~100-200ms) -->
<link rel="preconnect" href="https://api.systemprompt.io" />
<link rel="dns-prefetch" href="https://api.systemprompt.io" />
```

### Content Containment

```css
/* Isolate off-screen sections — browser skips layout/paint */
.sp-section--below-fold {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px; /* Estimated height */
}

/* Full containment for independent widgets */
.sp-widget {
  contain: layout style paint;
}
```

### CLS Prevention

```css
/* Always set explicit dimensions on replaced elements */
.sp-card__media img,
.sp-card__media video {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
}

/* Reserve space for dynamically injected content */
.sp-ad-slot {
  min-height: 250px;
}

/* Prevent font-swap layout shift */
.sp-text--heading {
  font-size-adjust: 0.5;
}
```

### Font Loading

```css
/* Prevent FOIT (Flash of Invisible Text) */
@font-face {
  font-family: "SP Sans";
  src: url("/fonts/sp-sans.woff2") format("woff2");
  font-display: swap;
  size-adjust: 100%;
}
```

---

## Reduced Motion Alternatives

`prefers-reduced-motion` does NOT mean "remove all animation." It means provide alternative, non-vestibular-triggering animations. Replace motion with opacity. Keep the communication.

```css
/* DEFAULT: full animation */
.sp-modal {
  animation: sp-slide-up var(--sp-duration-moderate) var(--sp-ease-default);
}

@keyframes sp-slide-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* REDUCED MOTION: replace slide with fade — do NOT remove animation */
@media (prefers-reduced-motion: reduce) {
  .sp-modal {
    animation: sp-fade-in var(--sp-duration-normal) var(--sp-ease-default);
  }

  /* Override all durations to be shorter */
  :root {
    --sp-duration-fast: 50ms;
    --sp-duration-normal: 100ms;
    --sp-duration-moderate: 150ms;
    --sp-duration-slow: 200ms;
    --sp-duration-slower: 300ms;
  }
}
```

**Substitution rules for reduced motion:**

| Original Animation | Reduced Motion Alternative |
|---|---|
| `translateX/Y` (slide) | `opacity` (fade) |
| `scale` (bounce/pop) | `opacity` (fade) |
| `rotate` (spin) | Static final state, no animation |
| Parallax scrolling | Static positioning |
| Auto-playing carousels | Manual navigation only |
| Color/opacity transitions | **Keep as-is** — these are safe |
| `box-shadow` transitions | **Keep as-is** — these are safe |
| Progress bar fill | **Keep as-is** — these are safe |

```css
/* Safe transitions — keep for ALL users */
.sp-btn {
  transition:
    background-color var(--sp-duration-fast) var(--sp-ease-default),
    color var(--sp-duration-fast) var(--sp-ease-default),
    box-shadow var(--sp-duration-fast) var(--sp-ease-default);
  /* These do not trigger vestibular discomfort */
}

/* Accordion: replace slide with crossfade */
.sp-accordion__body {
  transition:
    max-height var(--sp-duration-normal) var(--sp-ease-default),
    opacity var(--sp-duration-normal) var(--sp-ease-default);
}

@media (prefers-reduced-motion: reduce) {
  .sp-accordion__body {
    transition: opacity var(--sp-duration-normal) var(--sp-ease-default);
    max-height: none !important; /* Skip slide, just crossfade */
  }
}
```

---

## Scroll Behavior

### Smooth Scrolling with Reduced Motion Override

```css
html {
  scroll-behavior: smooth;
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
}

/* Account for fixed headers */
html {
  scroll-padding-top: var(--sp-header-height, 64px);
}
```

### Carousel Scroll Snap

```css
.sp-carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  gap: var(--sp-space-4);
  -webkit-overflow-scrolling: touch;

  /* Hide scrollbar but keep functionality */
  scrollbar-width: none;
}

.sp-carousel::-webkit-scrollbar {
  display: none;
}

.sp-carousel__item {
  scroll-snap-align: start;
  flex: 0 0 auto;
  width: min(300px, 85vw);
}
```

```html
<div class="sp-carousel" role="region" aria-label="Featured items" tabindex="0">
  <div class="sp-carousel__item"><!-- Slide 1 --></div>
  <div class="sp-carousel__item"><!-- Slide 2 --></div>
  <div class="sp-carousel__item"><!-- Slide 3 --></div>
</div>

<!-- Scroll indicators -->
<div class="sp-carousel__nav" role="tablist" aria-label="Slide navigation">
  <button role="tab" aria-selected="true" aria-label="Slide 1"></button>
  <button role="tab" aria-selected="false" aria-label="Slide 2"></button>
  <button role="tab" aria-selected="false" aria-label="Slide 3"></button>
</div>
```

### Scroll-Driven Progress Indicator

```css
/* Page scroll progress bar */
.sp-scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--sp-color-primary);
  transform-origin: left;
  transform: scaleX(0);
  z-index: var(--sp-z-fixed);
  animation: sp-scroll-progress auto linear;
  animation-timeline: scroll();
}

@keyframes sp-scroll-progress {
  to {
    transform: scaleX(1);
  }
}
```

---

## Review Checklist

Run through this checklist before shipping any interactive UI.

### Timing and Feedback

- [ ] Every user action produces visible feedback within 100ms
- [ ] No transition uses a raw `ms` value — all use `--sp-duration-*` tokens
- [ ] Enter animations use `ease-out`, exit animations use `ease-in`
- [ ] No animation exceeds 600ms duration
- [ ] Loading states appear within 300ms for any async operation

### Target Size and Layout

- [ ] All interactive elements meet 24x24px minimum
- [ ] Primary actions meet 44x44px minimum
- [ ] Destructive actions are physically distant from confirm actions
- [ ] No more than 7 top-level navigation items
- [ ] No more than 7 +/- 2 visible options without grouping

### Loading and State

- [ ] Initial page loads use skeleton screens, not spinners
- [ ] Skeletons match the dimensions of real content
- [ ] Skeleton containers use `aria-busy="true"`
- [ ] High-probability actions use optimistic UI
- [ ] No full-page spinners exist anywhere
- [ ] Progress bars used for known-duration operations

### Animation and Motion

- [ ] `prefers-reduced-motion` has alternative animations, not `animation: none`
- [ ] Slide/scale animations replaced with fade for reduced motion
- [ ] Color and opacity transitions preserved for all users
- [ ] `scroll-behavior: smooth` has reduced-motion override
- [ ] Duration tokens shortened (not removed) for reduced motion

### Performance

- [ ] Hero images use `fetchpriority="high"`
- [ ] Below-fold images use `loading="lazy"`
- [ ] Off-screen sections use `content-visibility: auto`
- [ ] All images and videos have explicit `width`/`height` or `aspect-ratio`
- [ ] API domains use `<link rel="preconnect">`
- [ ] Fonts use `font-display: swap`
- [ ] No layout shift from dynamic content injection

### Conventions

- [ ] Logo links to home, top-left placement
- [ ] Close buttons top-right in modals/dialogs
- [ ] Standard icons used for standard actions
- [ ] Success states animate (not static icon swap)
- [ ] Form groups use visual chunking (spacing, backgrounds)

### "If You See X, Replace With Y"

| If You See... | Replace With... |
|---|---|
| Full-page spinner | Skeleton of the target page |
| `transition: all` | Explicit properties: `transition: opacity, transform` |
| `animation: none` in reduced motion | `animation: sp-fade-in` (fade alternative) |
| Raw `300ms` in transition | `var(--sp-duration-moderate)` |
| Inline spinner for page load | Skeleton screen |
| `ease` (default easing) | `ease-out` for enters, `ease-in` for exits |
| Interactive element <24px | Add padding-based hit area expansion |
| 10+ flat options in toolbar | Group behind progressive disclosure |
| Static success icon swap | Animated checkmark draw or celebration |
| `loading="lazy"` on hero image | `fetchpriority="high" loading="eager"` |
| `setTimeout` for animation delay | CSS `animation-delay` or `transition-delay` |
| `display: none` for hiding | `opacity` + `visibility` for animated hide |
| Scrollbar visible on carousels | `scrollbar-width: none` with scroll snap |
