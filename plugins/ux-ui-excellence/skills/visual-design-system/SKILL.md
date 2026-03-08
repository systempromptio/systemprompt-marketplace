---
name: visual-design-system
description: "World-class visual design system standards — OKLCH color science, fluid typography, elevation hierarchy, branded asymmetric corners, and dark mode implementation"
version: "1.0.0"
git_hash: "0000000"
---

# Visual Design System

## Preamble

This skill complements `frontend-coding-standards`. All architectural rules from that skill apply without exception: BEM naming (`.sp-{block}`), the `--sp-` prefix for custom properties, file organization, CSS-only preference, and the existing token set (`--sp-color-*`, `--sp-font-*`, `--sp-space-*`, `--sp-radius-*`, `--sp-transition-*`, `--sp-z-*`). Do not redefine those tokens.

This skill adds the **visual design quality layer** -- the difference between functional UI and world-class UI. It covers color science, fluid typography, elevation, surface hierarchy, branded identity, and dark mode.

---

## Branded Asymmetric Corner Pattern

**CORE brand element.** systemprompt.io cards and containers use asymmetric `border-radius` where the top-right corner is approximately 1/4 of the other corners. This "notch" is the visual signature that distinguishes systemprompt from generic designs.

```css
:root {
  /* Brand corner pattern — top-right is 1/4 of standard radius */
  --sp-corners-sm: var(--sp-radius-sm) calc(var(--sp-radius-sm) / 4) var(--sp-radius-sm) var(--sp-radius-sm);
  --sp-corners-md: var(--sp-radius-md) calc(var(--sp-radius-md) / 4) var(--sp-radius-md) var(--sp-radius-md);
  --sp-corners-lg: var(--sp-radius-lg) calc(var(--sp-radius-lg) / 4) var(--sp-radius-lg) var(--sp-radius-lg);
}
```

| Element Type | Token | Example |
|-------------|-------|---------|
| Badges, chips, tags | `--sp-corners-sm` | `border-radius: var(--sp-corners-sm)` |
| Cards, inputs, dropdowns | `--sp-corners-md` | `border-radius: var(--sp-corners-md)` |
| Modals, dialogs, panels | `--sp-corners-lg` | `border-radius: var(--sp-corners-lg)` |

```css
.sp-card {
  border-radius: var(--sp-corners-md); /* CORRECT: branded asymmetric */
  /* border-radius: var(--sp-radius-md); ← WRONG: symmetric, generic */
}

.sp-modal {
  border-radius: var(--sp-corners-lg);
  padding: var(--sp-space-6);
}

.sp-badge {
  border-radius: var(--sp-corners-sm);
  padding: var(--sp-space-1) var(--sp-space-2);
}
```

### Nested Radius Rule

Inner radius = outer radius - padding, per-corner. Clamp to prevent negatives:

```css
.sp-card { border-radius: var(--sp-corners-md); padding: var(--sp-space-4); }
.sp-card__media {
  border-radius: max(0px, calc(var(--sp-radius-md) - var(--sp-space-4)))
                 max(0px, calc(var(--sp-radius-md) / 4 - var(--sp-space-4))) 0 0;
}
```

**Rule: Cards MUST use `border-radius: var(--sp-corners-md)`, never symmetric `var(--sp-radius-md)`.**

---

## Three-Tier Token Architecture

Extends the existing `--sp-` tokens with primitive and component layers.

### Tier 1: Primitive Tokens (Raw Values) — never reference directly in component CSS

```css
:root {
  --sp-primitive-blue-50: oklch(0.97 0.01 250);
  --sp-primitive-blue-500: oklch(0.55 0.20 250);
  --sp-primitive-blue-700: oklch(0.40 0.18 250);
  --sp-primitive-blue-900: oklch(0.25 0.12 250);
  --sp-primitive-neutral-0: oklch(1.00 0 0);
  --sp-primitive-neutral-50: oklch(0.97 0.005 250);
  --sp-primitive-neutral-100: oklch(0.93 0.005 250);
  --sp-primitive-neutral-200: oklch(0.87 0.005 250);
  --sp-primitive-neutral-600: oklch(0.50 0.01 250);
  --sp-primitive-neutral-800: oklch(0.30 0.015 250);
  --sp-primitive-neutral-900: oklch(0.20 0.015 250);
  --sp-primitive-neutral-950: oklch(0.13 0.015 250);
  --sp-primitive-orange-500: oklch(0.65 0.18 55);
  --sp-primitive-green-500: oklch(0.60 0.18 145);
  --sp-primitive-amber-500: oklch(0.75 0.15 80);
  --sp-primitive-red-500: oklch(0.55 0.22 25);
}
```

### Tier 2: Semantic Tokens (Intent-Based)

```css
:root {
  --sp-color-primary: var(--sp-primitive-blue-500);
  --sp-color-primary-hover: var(--sp-primitive-blue-700);
  --sp-color-accent: var(--sp-primitive-orange-500);
  --sp-color-success: var(--sp-primitive-green-500);
  --sp-color-warning: var(--sp-primitive-amber-500);
  --sp-color-danger: var(--sp-primitive-red-500);
  --sp-color-text: var(--sp-primitive-neutral-900);
  --sp-color-text-secondary: var(--sp-primitive-neutral-600);
  --sp-color-bg: var(--sp-primitive-neutral-0);
  --sp-color-bg-surface: var(--sp-primitive-neutral-50);
  --sp-color-border: var(--sp-primitive-neutral-200);
}
```

### Tier 3: Component Tokens (Scoped) — defined on component selector, not `:root`

```css
.sp-button {
  --sp-button-bg: var(--sp-color-primary);
  --sp-button-text: var(--sp-primitive-neutral-0);
  --sp-button-radius: var(--sp-corners-sm);
  background: var(--sp-button-bg);
  color: var(--sp-button-text);
  border-radius: var(--sp-button-radius);
  padding: var(--sp-space-2) var(--sp-space-4);
}
```

**Rule: Component CSS references component or semantic tokens only. Never use primitives directly in component styles.**

---

## OKLCH Color System

OKLCH provides perceptual uniformity -- equal numeric changes produce equal visual changes. HSL `50%` lightness looks different across hues; OKLCH `0.50` is visually consistent. OKLCH also maps gracefully to P3 displays and produces natural `color-mix()` results.

### Derived States with `color-mix()`

```css
:root {
  --sp-color-primary: oklch(0.55 0.20 250);
  --sp-color-primary-hover: color-mix(in oklch, var(--sp-color-primary), black 15%);
  --sp-color-primary-active: color-mix(in oklch, var(--sp-color-primary), black 25%);
  --sp-color-primary-disabled: color-mix(in oklch, var(--sp-color-primary), transparent 50%);
  --sp-color-primary-subtle: color-mix(in oklch, var(--sp-color-primary), white 85%);
}
```

### Relative Color Syntax for Variations

```css
:root {
  --sp-color-primary-muted: oklch(from var(--sp-color-primary) l calc(c * 0.3) h);
  --sp-color-primary-tint: oklch(from var(--sp-color-primary) calc(l + 0.35) calc(c * 0.4) h);
}
```

### Contrast Requirements

| Context | Minimum Ratio |
|---------|--------------|
| Body text on background | 4.5:1 |
| Large text (>= 18pt bold) | 3:1 |
| UI elements (borders, icons) | 3:1 |
| Focus indicators | 3:1 |

---

## Dynamic Dark Mode with `light-dark()`

Use `light-dark()` to eliminate duplicate `:root` / `[data-theme="dark"]` blocks:

```css
:root {
  color-scheme: light dark;
  --sp-color-text: light-dark(var(--sp-primitive-neutral-900), var(--sp-primitive-neutral-100));
  --sp-color-text-secondary: light-dark(var(--sp-primitive-neutral-600), var(--sp-primitive-neutral-200));
  --sp-color-bg: light-dark(var(--sp-primitive-neutral-0), var(--sp-primitive-neutral-950));
  --sp-color-bg-surface: light-dark(var(--sp-primitive-neutral-50), var(--sp-primitive-neutral-900));
  --sp-color-border: light-dark(var(--sp-primitive-neutral-200), var(--sp-primitive-neutral-800));
  --sp-color-bg-elevated: light-dark(var(--sp-primitive-neutral-0), var(--sp-primitive-neutral-900));
  --sp-shadow-color: light-dark(oklch(0.30 0.02 250 / 0.12), oklch(0.00 0 0 / 0.40));
}

img:not([src$=".svg"]) {
  filter: light-dark(none, brightness(0.9) contrast(1.05));
}
```

Dark mode elevation relies more on surface color shifts than shadows.

### Manual Toggle Pattern

```css
[data-theme="light"] { color-scheme: light; }
[data-theme="dark"] { color-scheme: dark; }
```

```js
document.documentElement.dataset.theme =
  localStorage.getItem("sp-theme") ?? "auto";
```

### Dark Mode Testing Checklist

- [ ] Text meets 4.5:1 contrast in both modes
- [ ] Borders remain visible in dark mode
- [ ] Shadows perceptible but not blown out
- [ ] Images do not glare on dark backgrounds
- [ ] Focus indicators visible in both modes
- [ ] No pure black (#000) backgrounds -- use `--sp-primitive-neutral-950`

---

## Fluid Typography System

### Modular Scale: 1.25 (Major Third)

```css
:root {
  --sp-text-xs: clamp(0.7rem, 0.66rem + 0.2vw, 0.8rem);
  --sp-text-sm: clamp(0.8rem, 0.74rem + 0.3vw, 0.9rem);
  --sp-text-base: clamp(0.9rem, 0.84rem + 0.3vw, 1rem);
  --sp-text-md: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  --sp-text-lg: clamp(1.125rem, 1rem + 0.6vw, 1.5rem);
  --sp-text-xl: clamp(1.25rem, 1.05rem + 1vw, 1.875rem);
  --sp-text-2xl: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
  --sp-text-3xl: clamp(1.875rem, 1.4rem + 2.4vw, 3rem);
  --sp-text-4xl: clamp(2.25rem, 1.6rem + 3.2vw, 4rem);

  --sp-leading-tight: 1.1;   /* Display text, hero headings */
  --sp-leading-snug: 1.2;    /* Headings h1-h3 */
  --sp-leading-normal: 1.5;  /* Body text, paragraphs */
  --sp-leading-relaxed: 1.7; /* Small text, captions */

  --sp-tracking-tight: -0.02em;  /* Large headings (2xl+) */
  --sp-tracking-normal: 0;       /* Body text */
  --sp-tracking-wide: 0.05em;    /* Uppercase labels, overlines */

  --sp-font-normal: 400;
  --sp-font-medium: 500;
  --sp-font-semibold: 600;
  --sp-font-bold: 700;
}
```

### Measure and Readability

```css
.sp-prose { max-width: 65ch; font-size: var(--sp-text-base); line-height: var(--sp-leading-normal); }
.sp-prose h1, .sp-prose h2, .sp-prose h3 { line-height: var(--sp-leading-snug); letter-spacing: var(--sp-tracking-tight); }
```

| Weight | Token | Usage |
|--------|-------|-------|
| 400 | `--sp-font-normal` | Body text |
| 500 | `--sp-font-medium` | Labels, navigation |
| 600 | `--sp-font-semibold` | Subheadings, emphasis |
| 700 | `--sp-font-bold` | Headings, CTAs |

---

## Spacing and Vertical Rhythm

### 8px Base Grid

Existing tokens cover `--sp-space-1` through `--sp-space-8`. Extended scale for layout:

```css
:root {
  --sp-space-10: 2.5rem;  /* 40px */
  --sp-space-12: 3rem;    /* 48px */
  --sp-space-16: 4rem;    /* 64px */
  --sp-space-20: 5rem;    /* 80px */
  --sp-space-24: 6rem;    /* 96px */
  --sp-space-32: 8rem;    /* 128px */
}
```

### Spacing Usage Guide

| Token | Value | Use For |
|-------|-------|---------|
| `--sp-space-1` | 4px | Inline padding, icon gaps |
| `--sp-space-2` | 8px | Badge padding, tight gaps |
| `--sp-space-3` | 12px | Input padding, list items |
| `--sp-space-4` | 16px | Card padding, component gap |
| `--sp-space-6` | 24px | Section padding in cards |
| `--sp-space-8` | 32px | Section margins, grid gaps |
| `--sp-space-12` | 48px | Major section spacing |
| `--sp-space-16` | 64px | Page section breaks |
| `--sp-space-24` | 96px | Hero spacing |

### Breathing Room Principle

World-class = MORE whitespace. Dense layouts signal "enterprise"; generous spacing signals "premium."

```css
.sp-card--cramped { padding: var(--sp-space-3); gap: var(--sp-space-2); } /* Mediocre */
.sp-card { padding: var(--sp-space-6); gap: var(--sp-space-4); } /* World-class */
```

---

## Elevation and Depth System

### Shadow Hierarchy (OKLCH Colors)

```css
:root {
  --sp-shadow-xs: 0 1px 2px oklch(0.30 0.02 250 / 0.06);
  --sp-shadow-sm: 0 1px 3px oklch(0.30 0.02 250 / 0.08), 0 1px 2px oklch(0.30 0.02 250 / 0.06);
  --sp-shadow-md: 0 4px 6px oklch(0.30 0.02 250 / 0.08), 0 2px 4px oklch(0.30 0.02 250 / 0.06);
  --sp-shadow-lg: 0 10px 15px oklch(0.30 0.02 250 / 0.08), 0 4px 6px oklch(0.30 0.02 250 / 0.04);
  --sp-shadow-xl: 0 20px 25px oklch(0.30 0.02 250 / 0.10), 0 8px 10px oklch(0.30 0.02 250 / 0.05);
}
```

### Interactive Elevation (Cards Lift on Hover)

```css
.sp-card {
  box-shadow: var(--sp-shadow-sm);
  border-radius: var(--sp-corners-md);
  transition: box-shadow var(--sp-transition-fast), transform var(--sp-transition-fast);
}
.sp-card:hover { box-shadow: var(--sp-shadow-md); transform: translateY(-2px); }
.sp-card:active { box-shadow: var(--sp-shadow-xs); transform: translateY(0); }
```

### Glassmorphism (Sparingly -- Sticky Headers, Floating Toolbars Only)

```css
.sp-glass {
  background: oklch(1 0 0 / 0.7);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid oklch(1 0 0 / 0.2);
  border-radius: var(--sp-corners-md);
}
```

### Dark Mode Shadows — Increase opacity, use pure black

```css
@media (prefers-color-scheme: dark) {
  :root {
    --sp-shadow-sm: 0 1px 3px oklch(0 0 0 / 0.25), 0 1px 2px oklch(0 0 0 / 0.20);
    --sp-shadow-md: 0 4px 6px oklch(0 0 0 / 0.30), 0 2px 4px oklch(0 0 0 / 0.20);
    --sp-shadow-lg: 0 10px 15px oklch(0 0 0 / 0.30), 0 4px 6px oklch(0 0 0 / 0.15);
    --sp-shadow-xl: 0 20px 25px oklch(0 0 0 / 0.35), 0 8px 10px oklch(0 0 0 / 0.20);
  }
}
```

---

## Surface Hierarchy

### Three Levels

| Level | Token | Purpose | Example |
|-------|-------|---------|---------|
| Base | `--sp-color-bg` | Page background | `<main>` |
| Raised | `--sp-color-bg-surface` | Cards, panels | `.sp-card` |
| Overlay | `--sp-color-bg-elevated` | Modals, popovers | `.sp-modal` |

### Border Usage Rules

| Scenario | Rule |
|----------|------|
| Adjacent same-level surfaces | 1px `--sp-color-border` for separation |
| Elevated surface over base | No border -- shadow provides separation |
| Interactive container | Border on focus/hover only |
| Input fields | 1px `--sp-color-border`, 2px `--sp-color-primary` on focus |

### Surface Examples

```css
.sp-card {
  background: var(--sp-color-bg-surface); border-radius: var(--sp-corners-md);
  box-shadow: var(--sp-shadow-sm); padding: var(--sp-space-6);
}
.sp-modal {
  background: var(--sp-color-bg-elevated); border-radius: var(--sp-corners-lg);
  box-shadow: var(--sp-shadow-xl); padding: var(--sp-space-8);
}
.sp-input {
  background: var(--sp-color-bg); border: 1px solid var(--sp-color-border);
  border-radius: var(--sp-corners-sm); padding: var(--sp-space-2) var(--sp-space-3);
}
.sp-input:focus {
  border-color: var(--sp-color-primary);
  outline: 2px solid color-mix(in oklch, var(--sp-color-primary), transparent 70%);
}
```

### Radius Consistency (Branded Corners by Element Size)

| Element Size | Corner Token | Elements |
|-------------|-------------|----------|
| Small | `--sp-corners-sm` | Inputs, badges, chips, tags, tooltips |
| Medium | `--sp-corners-md` | Cards, dropdowns, panels, images |
| Large | `--sp-corners-lg` | Modals, dialogs, full-width banners |

Symmetric `border-radius` is reserved only for circles (`50%`) and pills (`9999px`).

---

## Visual Quality Benchmarks

| Dimension | Mediocre | World-Class |
|-----------|----------|-------------|
| Colors | Random hex, inconsistent contrast | OKLCH palette, semantic tokens, 4.5:1 minimum |
| Typography | Single font-size, no scale | Fluid `clamp()` scale, heading/body rhythm |
| Spacing | Arbitrary pixels | 8px grid, generous breathing room |
| Corners | Uniform `border-radius` | Branded asymmetric corners by element size |
| Shadows | Single `rgba` shadow | Multi-layer OKLCH, interactive elevation |
| Dark mode | `filter: invert(1)` | `light-dark()` tokens, contrast-verified |
| Surfaces | Flat, borders everywhere | Three-tier hierarchy with elevation |
| Whitespace | Cramped | Generous, intentional spacing |

### Measurable Criteria

- **0 hardcoded colors** in component CSS (all via tokens)
- **0 symmetric border-radius** on containers (all use `--sp-corners-*`)
- **4.5:1 minimum** text contrast ratio in both light and dark modes
- **3:1 minimum** UI element contrast (borders, icons, focus rings)
- **8px grid alignment** for all spacing values
- **Fluid type scale** with no fixed `font-size` in `px`

---

## Review Checklist

### Brand Identity
- [ ] Cards use branded asymmetric corners (`--sp-corners-*`), not symmetric radius
- [ ] Modals and dialogs use `--sp-corners-lg`
- [ ] Small elements (badges, chips) use `--sp-corners-sm`
- [ ] No symmetric `border-radius` on any container element
- [ ] Nested elements apply the inner radius = outer - padding rule

### Color System
- [ ] All colors defined using OKLCH
- [ ] No hardcoded hex/rgb/hsl values in component CSS
- [ ] Primitive tokens exist but are never directly referenced in components
- [ ] Semantic tokens map primitives to intent
- [ ] Component tokens scope semantics to specific UI
- [ ] Hover/active states use `color-mix()` or relative color syntax
- [ ] 4.5:1 contrast ratio for all text on backgrounds
- [ ] 3:1 contrast ratio for all UI elements

### Dark Mode
- [ ] `color-scheme: light dark` set on `:root`
- [ ] All dual-mode tokens use `light-dark()` function
- [ ] Shadows reduced/adjusted for dark backgrounds
- [ ] Images apply brightness/contrast filter in dark mode
- [ ] No pure black (`#000`) backgrounds
- [ ] Manual toggle sets `data-theme` and persists in `localStorage`
- [ ] Focus indicators visible in both modes

### Typography
- [ ] Fluid type scale uses `clamp()` with rem + vw
- [ ] Modular scale ratio is 1.25 (Major Third)
- [ ] Body text uses `--sp-leading-normal` (1.5) line height
- [ ] Headings use `--sp-leading-snug` (1.2) line height
- [ ] Prose blocks constrained to `max-width: 65ch`
- [ ] Large headings (2xl+) use `--sp-tracking-tight` (-0.02em)
- [ ] No fixed `font-size` values in px

### Spacing
- [ ] All spacing uses `--sp-space-*` tokens
- [ ] Values align to 8px grid
- [ ] Extended scale (`--sp-space-12` through `--sp-space-32`) used for layout sections
- [ ] Generous whitespace -- when in doubt, add more space

### Elevation and Surfaces
- [ ] Shadow tokens defined with OKLCH colors
- [ ] Cards use interactive elevation (lift on hover)
- [ ] Three-tier surface hierarchy: base, raised, overlay
- [ ] Elevated surfaces use shadow instead of borders for separation
- [ ] Glassmorphism used sparingly and only on appropriate overlays
- [ ] Dark mode shadows are darker and more diffuse
