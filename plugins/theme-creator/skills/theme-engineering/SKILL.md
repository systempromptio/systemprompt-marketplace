---
name: theme-engineering
description: "Design token architecture, CSS implementation patterns, dark mode systems, and advanced theming techniques"
version: "1.0.0"
git_hash: "3c4f35d"
---

# Theme Engineering

CSS implementation patterns and token architecture for systemprompt.io themes. This skill extends the conventions defined in `frontend-coding-standards`. Follow without exception.

## Core Principle

Every visual value in component CSS resolves through design tokens. A hardcoded color, spacing value, or font size in component CSS is a bug. The token system is the single source of truth for all visual decisions.

---

## Three-Tier Token Architecture

Tokens are organized in three tiers. Each tier has a specific purpose and change frequency.

| Tier | Purpose | Naming Pattern | Changes When | Example |
|---|---|---|---|---|
| **Primitive** | Raw values with no semantic meaning | `--sp-{color}-{stop}` | Brand identity changes | `--sp-blue-50: oklch(0.64 0.16 250)` |
| **Semantic** | Contextual meaning mapped to primitives | `--sp-color-{role}` | Theme or mode changes | `--sp-color-primary: var(--sp-blue-50)` |
| **Component** | Scoped overrides for specific components | `--sp-{component}-{property}` | Component redesign | `--sp-button-bg: var(--sp-color-primary)` |

### How Tiers Connect

```
Primitive:  --sp-blue-50: oklch(0.64 0.16 250);
                ↓
Semantic:   --sp-color-primary: var(--sp-blue-50);
                ↓
Component:  --sp-button-bg: var(--sp-color-primary);
                ↓
Usage:      .sp-button { background: var(--sp-button-bg); }
```

**Rules**:
- Component CSS NEVER references primitive tokens directly
- Semantic tokens ALWAYS reference primitives via `var()`
- Component tokens ALWAYS reference semantic tokens via `var()`
- Maximum 2 levels of `var()` nesting in any single declaration

---

## Token Naming Convention

```
--sp-{category}-{property}-{element}-{modifier}-{state}
```

Only include segments that apply. Most tokens use 2-3 segments.

| Segment | Values | Required |
|---|---|---|
| `category` | `color`, `space`, `text`, `radius`, `shadow`, `z`, `motion`, `font` | Yes |
| `property` | `bg`, `text`, `border`, `surface`, `on-primary`, `ring` | When needed |
| `element` | `button`, `card`, `input`, `nav`, `sidebar` | Component tier only |
| `modifier` | `sm`, `md`, `lg`, `subtle`, `strong`, `muted` | When needed |
| `state` | `hover`, `active`, `focus`, `disabled` | When needed |

**Examples**:

```css
/* Semantic tier */
--sp-color-bg:                /* Page background */
--sp-color-bg-surface:        /* Card/section background */
--sp-color-bg-surface-raised: /* Elevated surface */
--sp-color-text:              /* Primary text */
--sp-color-text-muted:        /* Secondary text */
--sp-color-border:            /* Default border */
--sp-color-border-subtle:     /* Faint divider */
--sp-color-primary:           /* Brand action color */
--sp-color-on-primary:        /* Text on primary backgrounds */

/* Component tier */
--sp-button-bg:               /* Button background */
--sp-button-bg-hover:         /* Button hover state */
--sp-card-bg:                 /* Card background */
--sp-input-border:            /* Input border */
--sp-input-border-focus:      /* Input focused border */
```

---

## Token File Organization

Extends the `storage/files/css/core/` structure from `frontend-coding-standards`.

```
storage/files/css/core/
├── tokens-primitive.css    # Raw OKLCH values, spacing scale, type scale
├── tokens-semantic.css     # Semantic mappings (light mode defaults)
├── tokens-component.css    # Component-level token overrides
├── reset.css               # CSS reset
└── typography.css          # Font stacks and type system
```

**Migration from existing `tokens.css`**: The current flat `tokens.css` maps to the semantic tier. Split it into three files:
1. Extract raw values into `tokens-primitive.css`
2. Keep semantic names in `tokens-semantic.css`, pointing to primitives
3. Move component-specific overrides to `tokens-component.css`

**Rule**: All three token files MUST be registered in `required_assets()` and loaded before any component CSS. Load order: primitive → semantic → component.

---

## Complete Semantic Token Template

This is the minimum set of semantic tokens every theme MUST define.

```css
/* tokens-semantic.css */
:root {
  /* === Backgrounds === */
  --sp-color-bg:              var(--sp-neutral-95);    /* Page background */
  --sp-color-bg-surface:      var(--sp-neutral-90);    /* Card, section */
  --sp-color-bg-surface-raised: var(--sp-neutral-95);  /* Elevated card */
  --sp-color-bg-overlay:      oklch(0.2 0 0 / 0.5);   /* Scrim behind modals */
  --sp-color-bg-subtle:       var(--sp-neutral-90);    /* Subtle highlight */

  /* === Text === */
  --sp-color-text:            var(--sp-neutral-10);    /* Primary text */
  --sp-color-text-muted:      var(--sp-neutral-40);    /* Secondary text */
  --sp-color-text-subtle:     var(--sp-neutral-50);    /* Tertiary text */
  --sp-color-text-inverse:    var(--sp-neutral-95);    /* Text on dark bg */

  /* === Borders === */
  --sp-color-border:          var(--sp-neutral-80);    /* Default border */
  --sp-color-border-subtle:   var(--sp-neutral-85);    /* Faint divider */
  --sp-color-border-strong:   var(--sp-neutral-60);    /* Emphasized border */

  /* === Brand / Action === */
  --sp-color-primary:         var(--sp-primary-50);    /* Primary action */
  --sp-color-primary-hover:   var(--sp-primary-40);    /* Primary hover */
  --sp-color-primary-active:  var(--sp-primary-30);    /* Primary pressed */
  --sp-color-on-primary:      var(--sp-neutral-95);    /* Text on primary */

  /* === Secondary === */
  --sp-color-secondary:       var(--sp-secondary-50);
  --sp-color-on-secondary:    var(--sp-neutral-95);

  /* === Status === */
  --sp-color-success:         var(--sp-success-50);
  --sp-color-success-bg:      var(--sp-success-90);
  --sp-color-warning:         var(--sp-warning-50);
  --sp-color-warning-bg:      var(--sp-warning-90);
  --sp-color-danger:          var(--sp-danger-50);
  --sp-color-danger-bg:       var(--sp-danger-90);
  --sp-color-info:            var(--sp-info-50);
  --sp-color-info-bg:         var(--sp-info-90);

  /* === Focus === */
  --sp-color-focus:           var(--sp-primary-50);

  /* === Shadows === */
  --sp-shadow-color:          oklch(0.2 0 0);
}
```

---

## Dark Mode Implementation

### Strategy: Semantic Token Reassignment

Dark mode changes ONLY semantic tokens. Primitive tokens and component tokens remain identical. This guarantees consistency -- the relationship between components and their semantic meanings stays the same.

### Light/Dark Pattern

```css
/* tokens-semantic.css */

/* Light mode (default) */
:root {
  --sp-color-bg:            var(--sp-neutral-95);
  --sp-color-bg-surface:    var(--sp-neutral-90);
  --sp-color-text:          var(--sp-neutral-10);
  --sp-color-text-muted:    var(--sp-neutral-40);
  --sp-color-border:        var(--sp-neutral-80);
  --sp-color-primary:       var(--sp-primary-50);
  --sp-color-on-primary:    var(--sp-neutral-95);
  --sp-shadow-color:        oklch(0.2 0 0);
}

/* Dark mode: OS preference */
@media (prefers-color-scheme: dark) {
  :root:not(.light) {
    --sp-color-bg:            var(--sp-neutral-10);
    --sp-color-bg-surface:    var(--sp-neutral-20);
    --sp-color-text:          var(--sp-neutral-90);
    --sp-color-text-muted:    var(--sp-neutral-60);
    --sp-color-border:        var(--sp-neutral-30);
    --sp-color-primary:       var(--sp-primary-70);
    --sp-color-on-primary:    var(--sp-neutral-10);
    --sp-shadow-color:        oklch(0 0 0);
  }
}

/* Dark mode: manual toggle */
.dark {
  --sp-color-bg:            var(--sp-neutral-10);
  --sp-color-bg-surface:    var(--sp-neutral-20);
  --sp-color-text:          var(--sp-neutral-90);
  --sp-color-text-muted:    var(--sp-neutral-60);
  --sp-color-border:        var(--sp-neutral-30);
  --sp-color-primary:       var(--sp-primary-70);
  --sp-color-on-primary:    var(--sp-neutral-10);
  --sp-shadow-color:        oklch(0 0 0);
}
```

**Why `:root:not(.light)`**: Allows manual override. If a user toggles to light mode explicitly, the `.light` class prevents the OS dark preference from overriding it.

### Dark Mode Design Rules

| Rule | Rationale |
|---|---|
| Never use pure black (`oklch(0 0 0)`) as background | Too harsh; minimum `oklch(0.13 ...)` |
| Reduce chroma by 10-20% on vibrant colors | Prevents eye strain on dark surfaces |
| Higher surfaces = lighter | Elevation model: `surface` < `surface-raised` < `surface-overlay` |
| Reduce shadow opacity by ~50% | Shadows are less visible on dark backgrounds |
| Increase shadow blur by ~25% | Compensates for reduced opacity, maintains depth |
| Primary colors shift to lighter tonal stops | Dark bg needs lighter foreground for contrast |
| Test all status colors independently | Success green on dark bg may need different stop |
| Form inputs must have visible borders | Default browser styles often vanish in dark mode |

### Surface Elevation in Dark Mode

| Surface Level | Light Mode Lightness | Dark Mode Lightness | Use |
|---|---|---|---|
| Base | 0.97 | 0.13 | Page background |
| Surface | 0.93 | 0.18 | Cards, sections |
| Surface Raised | 0.95 | 0.22 | Hover cards, selected items |
| Surface Overlay | 0.98 | 0.26 | Dropdowns, popovers |
| Surface Top | 1.0 | 0.30 | Modals, dialogs |

```css
/* Dark mode surfaces */
.dark {
  --sp-color-bg:              oklch(0.13 0.005 var(--sp-brand-hue));
  --sp-color-bg-surface:      oklch(0.18 0.005 var(--sp-brand-hue));
  --sp-color-bg-surface-raised: oklch(0.22 0.005 var(--sp-brand-hue));
  --sp-color-bg-overlay:      oklch(0.26 0.005 var(--sp-brand-hue));
  --sp-color-bg-top:          oklch(0.30 0.005 var(--sp-brand-hue));
}
```

### Dark Mode Shadow Adjustment

```css
.dark {
  --sp-shadow-xs:  0 1px 3px  oklch(0 0 0 / 0.20);
  --sp-shadow-sm:  0 2px 4px  oklch(0 0 0 / 0.25);
  --sp-shadow-md:  0 4px 8px  oklch(0 0 0 / 0.30);
  --sp-shadow-lg:  0 10px 20px oklch(0 0 0 / 0.35);
  --sp-shadow-xl:  0 20px 35px oklch(0 0 0 / 0.40);
}
```

---

## `light-dark()` Function

The native CSS `light-dark()` function simplifies two-value cases.

```css
:root {
  color-scheme: light dark;

  --sp-color-bg: light-dark(
    oklch(0.97 0.005 var(--sp-brand-hue)),
    oklch(0.13 0.005 var(--sp-brand-hue))
  );
}
```

| Use `light-dark()` When | Use Token Reassignment When |
|---|---|
| Simple two-value toggle | Manual `.dark` class toggle needed |
| No manual theme override | User can override OS preference |
| Fewer tokens to manage | Full token system with 3 tiers |

**Rule**: Use `light-dark()` for standalone utilities. Use the full semantic reassignment pattern for the core theme system to support manual toggling via `.dark` / `.light` classes.

---

## Container Queries for Contextual Theming

Components can adapt their visual treatment based on container context, not just viewport.

```css
/* Define container */
.sp-sidebar {
  container-type: inline-size;
  container-name: sidebar;
}

/* Respond to container size */
@container sidebar (max-width: 250px) {
  .sp-nav__label { display: none; }
  .sp-nav__icon { font-size: var(--sp-text-lg); }
}

@container sidebar (min-width: 251px) {
  .sp-nav__label { display: inline; }
  .sp-nav__icon { font-size: var(--sp-text-base); }
}
```

### Style Queries for Themed Regions

```css
/* Parent sets a theme context */
.sp-region--accent {
  --sp-region-theme: accent;
}

/* Children adapt (when browser support is available) */
@container style(--sp-region-theme: accent) {
  .sp-button {
    --sp-button-bg: var(--sp-color-accent);
  }
}
```

**Rule**: Style queries are emerging. Use container size queries freely. Use style queries only behind `@supports` until full browser support.

---

## Custom Property Inheritance

### Fallback Chains

Component tokens fall back to semantic tokens, which fall back to primitives.

```css
.sp-button {
  /* Falls back to semantic primary if no component token defined */
  background: var(--sp-button-bg, var(--sp-color-primary));
  color: var(--sp-button-text, var(--sp-color-on-primary));
  border-radius: var(--sp-button-radius, var(--sp-radius-md));
}
```

**Rule**: Maximum 2 levels of `var()` nesting. Deeper nesting is unreadable and hard to debug.

```css
/* Correct: 2 levels */
background: var(--sp-button-bg, var(--sp-color-primary));

/* Forbidden: 3+ levels */
background: var(--sp-button-bg, var(--sp-color-primary, var(--sp-blue-50)));
```

### Scoped Overrides

Override component tokens at the usage site without modifying the component CSS.

```css
/* A card with an accent background overrides child button tokens */
.sp-card--accent {
  --sp-button-bg: var(--sp-color-on-primary);
  --sp-button-text: var(--sp-color-primary);
}
```

---

## Theme Transitions

Smooth transitions between light/dark modes or theme changes.

```css
:root {
  --sp-motion-theme: 200ms;
}

/* Apply transitions to color-related properties only */
body {
  transition:
    background-color var(--sp-motion-theme) var(--sp-ease-default),
    color var(--sp-motion-theme) var(--sp-ease-default),
    border-color var(--sp-motion-theme) var(--sp-ease-default),
    box-shadow var(--sp-motion-theme) var(--sp-ease-default);
}
```

**Rules**:
- NEVER use `transition: all` -- it transitions layout properties and causes jank
- Only transition color-related properties: `background-color`, `color`, `border-color`, `box-shadow`, `outline-color`
- Respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  body {
    --sp-motion-theme: 0ms;
  }
}
```

---

## Theme Toggle Implementation

Minimal JavaScript for toggling between light and dark modes.

```javascript
// Theme toggle - add to page initialization
function initThemeToggle(toggleElement) {
  const root = document.documentElement;
  const stored = localStorage.getItem('sp-theme');

  if (stored) {
    root.classList.toggle('dark', stored === 'dark');
    root.classList.toggle('light', stored === 'light');
  }

  toggleElement.addEventListener('click', () => {
    const isDark = root.classList.toggle('dark');
    root.classList.toggle('light', !isDark);
    localStorage.setItem('sp-theme', isDark ? 'dark' : 'light');
  });
}
```

**Rules**:
- Store preference in `localStorage` with key `sp-theme`
- Apply stored preference before first paint (inline script in `<head>`) to prevent flash
- Toggle both `.dark` and `.light` classes to support the `:root:not(.light)` pattern

### Flash Prevention

```html
<!-- In <head>, before any stylesheet -->
<script>
  (function() {
    var t = localStorage.getItem('sp-theme');
    if (t === 'dark') document.documentElement.classList.add('dark');
    else if (t === 'light') document.documentElement.classList.add('light');
  })();
</script>
```

---

## Integration with Existing `--sp-` System

The three-tier architecture evolves the existing flat token system. No breaking changes.

### Migration Path

| Current Token | Maps To | Tier |
|---|---|---|
| `--sp-color-primary: hsl(0, 0%, 35%)` | `--sp-color-primary: var(--sp-neutral-40)` | Semantic |
| `--sp-color-text: #111111` | `--sp-color-text: var(--sp-neutral-10)` | Semantic |
| `--sp-color-bg: #ffffff` | `--sp-color-bg: var(--sp-neutral-95)` | Semantic |
| `--sp-color-accent: #e8794a` | `--sp-color-accent: var(--sp-primary-50)` | Semantic |
| `--sp-font-sans: system-ui, ...` | Unchanged | Semantic |
| `--sp-space-1: 0.25rem` | Unchanged | Primitive |
| `--sp-radius-sm: ...` | Unchanged | Primitive |

### What Changes

1. **New file**: `tokens-primitive.css` contains raw OKLCH palette values
2. **Renamed**: `tokens.css` → `tokens-semantic.css`, values become `var()` references to primitives
3. **New file**: `tokens-component.css` for component-level overrides (starts empty, grows as needed)
4. **Dark mode**: Add semantic reassignment block in `tokens-semantic.css`

### What Stays the Same

- All `--sp-` prefix conventions
- All BEM naming conventions (`.sp-{block}__element--modifier`)
- All file size limits (200 lines max)
- All forbidden patterns from `frontend-coding-standards`
- All z-index scale tokens
- Registration in `required_assets()`

---

## CSS Custom Properties Debugging

### Browser DevTools

1. Inspect any element → Computed tab → filter by `--sp-`
2. All resolved token values visible with inheritance chain
3. Toggle `.dark` class on `<html>` to test dark mode
4. Override any `--sp-` token in DevTools to preview changes

### Grep Commands for Token Auditing

```bash
# Find all primitive token definitions
grep -rn "^  --sp-.*oklch" storage/files/css/core/tokens-primitive.css

# Find hardcoded colors in component CSS (should be zero)
grep -rn "#[0-9a-fA-F]\{3,8\}\|rgb\|hsl" storage/files/css/components/ storage/files/css/pages/

# Find tokens defined but never used
# (compare definitions vs. usages)
grep -roh "\--sp-[a-z-]*" storage/files/css/ | sort | uniq -c | sort -n

# Find unprefixed custom properties
grep -rn "^\s*--[^s]" storage/files/css/
grep -rn "^\s*--s[^p]" storage/files/css/
```

---

## Quick Reference: Token Architecture Rules

| Rule | Rationale |
|---|---|
| Component CSS never uses primitive tokens | Semantic layer enables theme switching |
| Semantic tokens always reference primitives | Single source of truth for raw values |
| Maximum 2 `var()` nesting levels | Readability and debuggability |
| Dark mode changes only semantic tokens | Components automatically adapt |
| All token files loaded before component CSS | Cascading dependency order |
| No duplicate token definitions | Use grep to verify uniqueness |
| New tokens require both light and dark values | Incomplete themes cause visual bugs |
| Theme transitions only on color properties | Layout transitions cause jank |
| Store theme preference in `localStorage` | Persists across sessions |
| Prevent flash with inline `<head>` script | Applied before first render |
