---
name: theme-design
description: "Color science, palette generation, typography systems, and design principles for world-class website themes"
version: "1.0.0"
git_hash: "0000000"
---

# Theme Design

World-class theme design principles for systemprompt.io. Follow without exception when creating, modifying, or reviewing theme colors, typography, spacing, and visual patterns.

## Core Principle

A theme is a systematic token-driven design system, not decoration. Every visual decision -- color, spacing, typography, shadow, motion -- derives from a coherent mathematical system. No arbitrary values. No "looks good enough." Every value has a reason traceable to the system.

---

## Color Spaces

### Why OKLCH

OKLCH is the primary color authoring format for all new theme work. It replaces HSL and hex for palette generation and color manipulation.

| Color Format | Syntax | Perceptually Uniform | Wide Gamut | Use |
|---|---|---|---|---|
| Hex | `#e8794a` | No | No | Legacy tokens only |
| HSL | `hsl(0, 0%, 35%)` | No | No | Legacy tokens only |
| OKLCH | `oklch(0.7 0.15 50)` | Yes | Yes | All new palettes |
| Display P3 | `color(display-p3 0.9 0.5 0.3)` | No | Yes | Only when P3 gamut needed |

**Rule**: All new color tokens MUST use `oklch()`. Existing HSL/hex tokens remain valid until migrated.

### OKLCH Anatomy

```
oklch(L C H)
      │ │ │
      │ │ └── Hue: 0-360 (color wheel angle)
      │ └──── Chroma: 0-0.4 (saturation intensity)
      └────── Lightness: 0-1 (0 = black, 1 = white)
```

| Channel | Range | What It Controls | Key Insight |
|---|---|---|---|
| Lightness (L) | 0 - 1 | How light or dark | 10% change = visually consistent across ALL hues |
| Chroma (C) | 0 - 0.4 | Color intensity | 0 = gray, higher = more vivid |
| Hue (H) | 0 - 360 | Color identity | Red ~30, Orange ~70, Yellow ~110, Green ~150, Blue ~250, Purple ~310 |

**Why it matters**: In HSL, `hsl(60, 100%, 50%)` (yellow) and `hsl(240, 100%, 50%)` (blue) have the same lightness value but look completely different in brightness. OKLCH fixes this -- equal lightness values produce equal perceived brightness across all hues.

---

## Palette Generation

### From One Brand Color to a Complete System

Every theme starts with a single primary brand color. The system derives everything else mathematically.

#### Step 1: Extract Primary Hue

Convert the brand color to OKLCH and extract its hue angle.

```css
/* Brand color: #e8794a → oklch(0.69 0.16 52) */
:root {
  --sp-brand-hue: 52;
  --sp-brand-chroma: 0.16;
}
```

#### Step 2: Generate Tonal Palette

Create 10 lightness stops for the primary hue. These are primitive tokens.

```css
:root {
  /* Primary tonal palette */
  --sp-primary-05: oklch(0.13 0.04 var(--sp-brand-hue));
  --sp-primary-10: oklch(0.22 0.06 var(--sp-brand-hue));
  --sp-primary-20: oklch(0.33 0.09 var(--sp-brand-hue));
  --sp-primary-30: oklch(0.44 0.12 var(--sp-brand-hue));
  --sp-primary-40: oklch(0.55 0.14 var(--sp-brand-hue));
  --sp-primary-50: oklch(0.64 0.16 var(--sp-brand-hue));
  --sp-primary-60: oklch(0.73 0.14 var(--sp-brand-hue));
  --sp-primary-70: oklch(0.81 0.11 var(--sp-brand-hue));
  --sp-primary-80: oklch(0.89 0.07 var(--sp-brand-hue));
  --sp-primary-90: oklch(0.95 0.03 var(--sp-brand-hue));
  --sp-primary-95: oklch(0.97 0.015 var(--sp-brand-hue));
}
```

**Rule**: Chroma decreases at extremes (very light and very dark stops) to avoid oversaturation and maintain usability.

#### Step 3: Derive Secondary and Tertiary Hues

Use hue rotation to create harmonious companion colors.

```css
:root {
  /* Secondary: analogous (+40 degrees) */
  --sp-secondary-hue: calc(var(--sp-brand-hue) + 40);

  /* Tertiary: complementary split (+150 degrees) */
  --sp-tertiary-hue: calc(var(--sp-brand-hue) + 150);
}
```

Generate the same 10-stop tonal palette for each derived hue.

#### Step 4: Generate Neutral Palette

Neutrals use the primary hue at near-zero chroma for subtle warmth/coolness.

```css
:root {
  /* Neutral palette (primary hue, minimal chroma) */
  --sp-neutral-05: oklch(0.13 0.005 var(--sp-brand-hue));
  --sp-neutral-10: oklch(0.22 0.005 var(--sp-brand-hue));
  --sp-neutral-20: oklch(0.33 0.008 var(--sp-brand-hue));
  --sp-neutral-30: oklch(0.44 0.008 var(--sp-brand-hue));
  --sp-neutral-40: oklch(0.55 0.008 var(--sp-brand-hue));
  --sp-neutral-50: oklch(0.64 0.008 var(--sp-brand-hue));
  --sp-neutral-60: oklch(0.73 0.008 var(--sp-brand-hue));
  --sp-neutral-70: oklch(0.81 0.006 var(--sp-brand-hue));
  --sp-neutral-80: oklch(0.89 0.005 var(--sp-brand-hue));
  --sp-neutral-90: oklch(0.95 0.003 var(--sp-brand-hue));
  --sp-neutral-95: oklch(0.97 0.002 var(--sp-brand-hue));
}
```

#### Step 5: Semantic Status Colors

Status colors (success, warning, danger) are fixed hues with consistent lightness.

```css
:root {
  --sp-success-hue: 155;  /* Green */
  --sp-warning-hue: 85;   /* Amber */
  --sp-danger-hue: 30;    /* Red */
  --sp-info-hue: 250;     /* Blue */
}
```

Generate a 5-stop tonal palette for each (10, 30, 50, 70, 90) for backgrounds, text, and accents.

---

## Color Harmony

| Harmony Type | Hue Offset | Character | Best For |
|---|---|---|---|
| Complementary | +180 | High contrast, energetic | CTAs, emphasis |
| Analogous | +/-30 | Harmonious, calm | Adjacent sections, gradients |
| Triadic | +/-120 | Balanced, vibrant | Multi-category dashboards |
| Split-complementary | +/-150 | Nuanced contrast | Secondary accents |
| Tetradic | +90, +180, +270 | Rich, complex | Only for large palettes with careful balance |

**Rule**: Most themes need only complementary or split-complementary. Analogous for subtle variation. Triadic and tetradic only for data-heavy dashboards.

---

## Contrast Requirements

| Context | Minimum Ratio | WCAG Level | Applies To |
|---|---|---|---|
| Body text | 4.5:1 | AA | All text under 18px or 14px bold |
| Large text | 3:1 | AA | Text 18px+ or 14px+ bold |
| UI components | 3:1 | AA | Borders, icons, focus rings against background |
| Enhanced text | 7:1 | AAA | When maximum readability required |

**Rules**:
- Every foreground/background semantic token pair MUST meet 4.5:1 minimum
- Color alone MUST NOT be the sole indicator of state -- use shape, icon, or text
- Test contrast at every tonal stop, not just the defaults
- Dark mode contrast must be verified independently

---

## `color-mix()` Patterns

Use `color-mix()` for dynamic color variations. Always mix in the `oklch` color space.

```css
/* Tinting (lighter) */
--sp-primary-tint: color-mix(in oklch, var(--sp-color-primary) 80%, white);

/* Shading (darker) */
--sp-primary-shade: color-mix(in oklch, var(--sp-color-primary) 80%, black);

/* Transparency */
--sp-primary-alpha-50: color-mix(in oklch, var(--sp-color-primary) 50%, transparent);

/* Hover state (subtle darkening) */
--sp-primary-hover: color-mix(in oklch, var(--sp-color-primary) 88%, black);

/* Active state (more darkening) */
--sp-primary-active: color-mix(in oklch, var(--sp-color-primary) 78%, black);

/* Disabled state (desaturated) */
--sp-primary-disabled: color-mix(in oklch, var(--sp-color-primary) 40%, oklch(0.7 0 0));
```

**Rule**: Always mix in `oklch` -- never `srgb`. OKLCH produces perceptually uniform results without muddy mid-tones.

---

## Typography

### Type Scale Ratios

Choose one ratio per project. All font sizes derive from it mathematically.

| Scale Name | Ratio | Character | Best For |
|---|---|---|---|
| Minor Second | 1.067 | Subtle, dense | Data tables, dashboards |
| Major Second | 1.125 | Compact, functional | Admin panels, tools |
| Minor Third | 1.200 | Balanced, readable | General websites |
| Major Third | 1.250 | Clear hierarchy | Marketing, content |
| Perfect Fourth | 1.333 | Strong hierarchy | Landing pages, editorial |
| Augmented Fourth | 1.414 | Dramatic | Portfolios, hero sections |
| Perfect Fifth | 1.500 | Bold hierarchy | Presentations, single-page |

**Rule**: systemprompt.io default is Minor Third (1.200). Override only with explicit justification.

### Fluid Typography with `clamp()`

Every text size token uses `clamp()` for seamless viewport scaling. No breakpoint-based font size changes.

```css
:root {
  /* Base scale: Minor Third (1.2) */
  /* Formula: clamp(min, preferred, max) */
  /* preferred = min + (max - min) * viewport-scaling-factor */

  --sp-text-xs:   clamp(0.694rem, 0.65rem + 0.22vw, 0.833rem);
  --sp-text-sm:   clamp(0.833rem, 0.78rem + 0.27vw, 1rem);
  --sp-text-base: clamp(1rem,     0.93rem + 0.33vw, 1.2rem);
  --sp-text-md:   clamp(1.2rem,   1.12rem + 0.40vw, 1.44rem);
  --sp-text-lg:   clamp(1.44rem,  1.34rem + 0.48vw, 1.728rem);
  --sp-text-xl:   clamp(1.728rem, 1.61rem + 0.58vw, 2.074rem);
  --sp-text-2xl:  clamp(2.074rem, 1.93rem + 0.69vw, 2.488rem);
  --sp-text-3xl:  clamp(2.488rem, 2.32rem + 0.83vw, 2.986rem);
}
```

**Rule**: Never use fixed `px` or `rem` for font sizes in components. Always reference a `--sp-text-*` token.

### Line Height

| Content Type | Line Height | Rationale |
|---|---|---|
| Body text | 1.5 - 1.7 | Readability for paragraphs |
| UI labels | 1.3 - 1.4 | Compact but readable |
| Headings | 1.1 - 1.25 | Tight for visual weight |
| Code | 1.5 - 1.6 | Scanning and alignment |

**Rule**: Line heights are unitless values. Never use `px` or `rem` for line-height.

### Font Pairing

| Rule | Rationale |
|---|---|
| Maximum 2 font families | Performance and visual cohesion |
| Maximum 4 font weights total | Each weight is a network request |
| Pair contrasting classifications | Serif + sans-serif, geometric + humanist |
| System font stack as default | Zero network cost, native feel |

**System font stacks**:

```css
:root {
  --sp-font-sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --sp-font-serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sp-font-mono: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
}
```

---

## Spacing Rhythm

All spacing derives from a 4px base unit via multiplication. No arbitrary spacing values.

```css
:root {
  --sp-space-px: 1px;          /* Borders only */
  --sp-space-0: 0;
  --sp-space-0-5: 0.125rem;   /* 2px */
  --sp-space-1: 0.25rem;      /* 4px - base unit */
  --sp-space-1-5: 0.375rem;   /* 6px */
  --sp-space-2: 0.5rem;       /* 8px */
  --sp-space-3: 0.75rem;      /* 12px */
  --sp-space-4: 1rem;         /* 16px */
  --sp-space-5: 1.25rem;      /* 20px */
  --sp-space-6: 1.5rem;       /* 24px */
  --sp-space-8: 2rem;         /* 32px */
  --sp-space-10: 2.5rem;      /* 40px */
  --sp-space-12: 3rem;        /* 48px */
  --sp-space-16: 4rem;        /* 64px */
  --sp-space-20: 5rem;        /* 80px */
  --sp-space-24: 6rem;        /* 96px */
}
```

**Rule**: Every margin, padding, and gap in component CSS MUST use a `--sp-space-*` token. No raw `px`, `rem`, or `em` values.

---

## Depth and Elevation

Shadows create depth. Use a 5-level elevation scale with consistent tokens.

```css
:root {
  --sp-shadow-xs:  0 1px 2px  oklch(0.2 0 0 / 0.05);
  --sp-shadow-sm:  0 1px 3px  oklch(0.2 0 0 / 0.10), 0 1px 2px oklch(0.2 0 0 / 0.06);
  --sp-shadow-md:  0 4px 6px  oklch(0.2 0 0 / 0.10), 0 2px 4px oklch(0.2 0 0 / 0.06);
  --sp-shadow-lg:  0 10px 15px oklch(0.2 0 0 / 0.10), 0 4px 6px oklch(0.2 0 0 / 0.05);
  --sp-shadow-xl:  0 20px 25px oklch(0.2 0 0 / 0.10), 0 8px 10px oklch(0.2 0 0 / 0.04);
  --sp-shadow-2xl: 0 25px 50px oklch(0.2 0 0 / 0.25);
}
```

| Level | Token | Use Case |
|---|---|---|
| 0 | none | Flat elements, embedded content |
| 1 | `--sp-shadow-xs` | Subtle lift: cards at rest |
| 2 | `--sp-shadow-sm` | Interactive default: buttons, inputs |
| 3 | `--sp-shadow-md` | Raised: hover cards, active selections |
| 4 | `--sp-shadow-lg` | Floating: dropdowns, popovers |
| 5 | `--sp-shadow-xl` | Overlay: modals, dialogs |

**Rules**:
- Shadows use oklch-based colors, not hardcoded `rgba`
- Higher elevation = larger blur, more offset, less opacity per layer
- Dark mode: reduce opacity by 50%, increase blur by 25% (see theme-engineering)

---

## Border Radius

```css
:root {
  --sp-radius-none: 0;
  --sp-radius-sm: 0.25rem;    /* 4px - subtle rounding */
  --sp-radius-md: 0.5rem;     /* 8px - default for cards, inputs */
  --sp-radius-lg: 0.75rem;    /* 12px - prominent rounding */
  --sp-radius-xl: 1rem;       /* 16px - large containers */
  --sp-radius-2xl: 1.5rem;    /* 24px - hero sections */
  --sp-radius-full: 9999px;   /* Pill shapes, avatars */
}
```

**Rule**: Pick one radius for interactive elements (buttons, inputs, cards) and use it consistently. Mixing `--sp-radius-sm` buttons with `--sp-radius-lg` inputs looks unintentional.

---

## Micro-Interactions

What separates functional from premium is the feeling of every interaction.

### Timing Rules

| Duration | Use Case |
|---|---|
| 50-100ms | Opacity changes, color shifts |
| 100-200ms | Button states, input focus |
| 200-300ms | Card hover, panel slide |
| 300-500ms | Modal enter, page transitions |

**Rule**: No transition exceeds 500ms. Users perceive anything longer as sluggish.

### Motion Tokens

```css
:root {
  --sp-motion-instant: 50ms;
  --sp-motion-fast: 150ms;
  --sp-motion-normal: 250ms;
  --sp-motion-slow: 400ms;

  --sp-ease-default: cubic-bezier(0.4, 0, 0.2, 1);   /* Material standard */
  --sp-ease-in: cubic-bezier(0.4, 0, 1, 1);           /* Exiting elements */
  --sp-ease-out: cubic-bezier(0, 0, 0.2, 1);          /* Entering elements */
  --sp-ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1); /* Playful emphasis */
}
```

### Easing Rules

| Action | Easing | Why |
|---|---|---|
| Element entering view | `--sp-ease-out` | Decelerates into resting position |
| Element exiting view | `--sp-ease-in` | Accelerates away naturally |
| State change (color, size) | `--sp-ease-default` | Smooth, neutral transition |
| Attention/delight | `--sp-ease-bounce` | Subtle overshoot for emphasis |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Rule**: This is the ONE acceptable use of `!important`. It is mandatory in every theme.

### Staggered Animations

For lists and grids, stagger child entrance by 50ms per item, maximum 300ms total.

```css
.sp-list__item {
  animation: sp-fade-in var(--sp-motion-normal) var(--sp-ease-out) both;
}

.sp-list__item:nth-child(1) { animation-delay: 0ms; }
.sp-list__item:nth-child(2) { animation-delay: 50ms; }
.sp-list__item:nth-child(3) { animation-delay: 100ms; }
.sp-list__item:nth-child(4) { animation-delay: 150ms; }
.sp-list__item:nth-child(5) { animation-delay: 200ms; }
.sp-list__item:nth-child(n+6) { animation-delay: 250ms; }

@keyframes sp-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

---

## Interactive State Consistency

Every interactive element MUST define all 5 states. No exceptions.

| State | Required Visual Change | CSS Selector |
|---|---|---|
| Default | Base appearance | `.sp-button` |
| Hover | Subtle darkening or lift | `.sp-button:hover` |
| Active / Pressed | Inset or compressed feel | `.sp-button:active` |
| Focus-visible | Visible ring (keyboard users) | `.sp-button:focus-visible` |
| Disabled | Reduced opacity + `not-allowed` cursor | `.sp-button:disabled` |

### Focus Ring Standard

```css
:focus-visible {
  outline: 2px solid var(--sp-color-focus, var(--sp-color-primary));
  outline-offset: 2px;
}
```

**Rules**:
- Focus ring MUST use `outline`, not `box-shadow` (outlines respect border-radius in modern browsers and don't affect layout)
- `outline-offset: 2px` ensures the ring is visible against the element
- NEVER use `:focus` alone -- always `:focus-visible` to avoid mouse click rings
- Focus ring must be visible in BOTH light and dark modes

### State Token Pattern

```css
.sp-button {
  background: var(--sp-color-primary);
  transition: background var(--sp-motion-fast) var(--sp-ease-default);
}

.sp-button:hover {
  background: color-mix(in oklch, var(--sp-color-primary) 88%, black);
}

.sp-button:active {
  background: color-mix(in oklch, var(--sp-color-primary) 78%, black);
}

.sp-button:focus-visible {
  outline: 2px solid var(--sp-color-focus, var(--sp-color-primary));
  outline-offset: 2px;
}

.sp-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Gradient Rules

| Rule | Rationale |
|---|---|
| Always interpolate in `oklch` | `background: linear-gradient(in oklch, ...)` prevents muddy mid-tones |
| Maximum 3 color stops | More creates visual noise |
| Same lightness for all stops | Ensures text remains readable |
| Test with a grayscale filter | If the gradient vanishes, lightness is consistent |

```css
/* Correct: OKLCH interpolation, consistent lightness */
.sp-gradient {
  background: linear-gradient(
    in oklch 135deg,
    oklch(0.6 0.15 250),
    oklch(0.6 0.15 310)
  );
}
```

---

## Quick Reference: Forbidden Patterns

| Forbidden | Use Instead |
|---|---|
| Raw hex/rgb/hsl in new tokens | `oklch()` |
| Hardcoded `px`/`rem` spacing | `--sp-space-*` tokens |
| Fixed `px` font sizes | `--sp-text-*` fluid tokens |
| `rgba()` in shadows | `oklch(L C H / alpha)` |
| Arbitrary border-radius | `--sp-radius-*` tokens |
| `transition: all` | Transition specific properties only |
| Transitions over 500ms | Max `--sp-motion-slow` (400ms) |
| `:focus` without `:focus-visible` | `:focus-visible` only |
| Color as sole state indicator | Pair with shape, icon, or text |
| Linear easing on UI elements | Use `--sp-ease-*` curves |
