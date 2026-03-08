---
name: theme-audit
description: "Checklists and procedures for reviewing, debugging, and improving existing website themes"
version: "1.0.0"
git_hash: "3c4f35d"
---

# Theme Audit

Systematic evaluation procedures for reviewing and improving systemprompt.io website themes. Use these checklists when creating, modifying, or reviewing any theme work.

## Core Principle

A theme audit evaluates every layer of the token system against objective, measurable criteria. No subjective "looks good" assessments. Every check has a pass/fail condition and a specific fix when it fails.

---

## Quick Audit Checklist

Run through all sections when reviewing any theme change. Each check has a pass criteria and test method.

### Token System Health

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| T1 | All custom properties use `--sp-` prefix | Zero unprefixed `--` declarations | `grep -rn "^\s*--[^s]" css/` and `grep -rn "^\s*--s[^p]" css/` return nothing |
| T2 | No hardcoded colors in component CSS | Zero hex/rgb/hsl values outside `tokens-primitive.css` | `grep -rn "#[0-9a-fA-F]\{3,8\}\|rgb(\|hsl(" css/components/ css/pages/` returns nothing |
| T3 | No hardcoded spacing in component CSS | Zero raw px/rem outside token files | `grep -rn "[0-9]px\|[0-9]rem\|[0-9]em" css/components/` returns only `0` values |
| T4 | Semantic tokens reference primitives | All semantic values use `var(--sp-...)` | Inspect `tokens-semantic.css` -- no raw oklch/hex/rgb values |
| T5 | No duplicate token definitions | Each `--sp-` name declared exactly once per scope | `grep -roh "\--sp-[a-z-]*:" css/ \| sort \| uniq -d` returns nothing |
| T6 | Token naming follows convention | All match `--sp-{category}-{property}[-{modifier}][-{state}]` | Manual review of token files |
| T7 | All token files load in correct order | primitive → semantic → component | Check `required_assets()` load order |
| T8 | No orphan tokens | Every defined token is used at least once | Compare definitions vs. usages |

### Color Quality

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| C1 | New colors use OKLCH | Zero new tokens with hex/hsl format | Review `tokens-primitive.css` for format |
| C2 | All text/bg pairs meet 4.5:1 contrast | WCAG AA pass for every semantic pair | Browser DevTools contrast checker or axe |
| C3 | Large text pairs meet 3:1 contrast | Text 18px+ or 14px+ bold | Test with accessibility tool |
| C4 | UI components meet 3:1 against adjacent | Borders, icons, focus rings | Visual inspection + contrast tool |
| C5 | Color is not sole state indicator | Shape, icon, or text also changes | Visual inspection of all interactive states |
| C6 | Dark mode colors are desaturated | Chroma reduced 10-20% vs light mode | Compare oklch chroma values |
| C7 | Dark mode surfaces follow elevation | Higher surface = higher lightness | Compare `--sp-color-bg-*` lightness values |
| C8 | No pure black backgrounds in dark mode | Minimum lightness 0.13 | Check `--sp-color-bg` in dark mode |
| C9 | Focus indicators visible in both modes | Ring visible on all backgrounds | Toggle dark mode, tab through UI |
| C10 | Status colors accessible in both modes | Success/warning/danger meet contrast | Test each status on light and dark bg |
| C11 | Gradients use `in oklch` interpolation | No muddy mid-tones | Inspect gradient CSS for `in oklch` |
| C12 | `color-mix()` uses `in oklch` | Not `in srgb` | Search for `color-mix` declarations |

### Typography Quality

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| Y1 | Type scale uses consistent ratio | All sizes derivable from base * ratio^n | Calculate ratios between adjacent sizes |
| Y2 | Fluid typography uses `clamp()` | All `--sp-text-*` tokens use clamp | Inspect token definitions |
| Y3 | Maximum 2 font families loaded | Network tab shows ≤ 2 font requests | Browser DevTools Network tab |
| Y4 | Maximum 4 font weights total | Combined weights across families ≤ 4 | Count `@font-face` or system fallbacks |
| Y5 | Body line height 1.5-1.7 (unitless) | No `px` or `rem` line-heights | Inspect body text computed style |
| Y6 | Heading line height 1.1-1.25 | Tighter than body, unitless | Inspect heading computed style |
| Y7 | No fixed `px` font sizes in components | All sizes reference `--sp-text-*` | `grep -rn "font-size:.*px\|font-size:.*rem" css/components/` |

### Spacing and Layout

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| S1 | All spacing uses `--sp-space-*` tokens | Zero raw px/rem in margin/padding/gap | Grep component CSS for raw values |
| S2 | Spacing follows consistent rhythm | All values exist on the spacing scale | Compare used values to token scale |
| S3 | No orphan spacing values | No one-off px/rem values | Grep for non-token numeric values |
| S4 | Container queries used where appropriate | Components adapt to container, not viewport | Review responsive components |
| S5 | Border radius consistent per element type | Same radius for buttons, inputs, cards | Compare radius values across similar elements |

### Motion and Interaction

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| M1 | All transitions use `--sp-motion-*` tokens | No hardcoded `ms` or `s` durations | Grep for raw duration values |
| M2 | No transition exceeds 500ms | Max is `--sp-motion-slow` (400ms) | Inspect transition declarations |
| M3 | `prefers-reduced-motion` respected | Global reduced-motion rule present | Grep for `prefers-reduced-motion` |
| M4 | Every interactive element has 5 states | hover, active, focus-visible, disabled | Inspect each component's CSS |
| M5 | Hover and focus-visible are distinct | Different visual treatment | Tab + hover comparison |
| M6 | Disabled state has opacity + cursor | `opacity` reduced, `cursor: not-allowed` | Inspect disabled elements |
| M7 | Focus uses `outline`, not `box-shadow` | `:focus-visible` with `outline` | Grep for focus styles |
| M8 | No `transition: all` | Specific properties listed | Grep for `transition:\s*all` |
| M9 | Easing uses `--sp-ease-*` tokens | No raw `cubic-bezier` in components | Grep component CSS for cubic-bezier |

### Dark Mode

| # | Check | Pass Criteria | How to Test |
|---|---|---|---|
| D1 | Only semantic tokens change | Primitive and component tokens identical | Diff light vs dark token values |
| D2 | No pure black backgrounds | Minimum lightness 0.13 | Check dark mode `--sp-color-bg` |
| D3 | Surface elevation model correct | bg < surface < surface-raised < overlay | Compare lightness values |
| D4 | Shadows adjusted | Opacity increased, blur increased | Compare shadow tokens in dark mode |
| D5 | Primary colors use lighter stops | Maintains contrast on dark bg | Check `--sp-color-primary` in dark mode |
| D6 | Form inputs have visible borders | Not invisible on dark surface | Visual check of all form elements |
| D7 | Images/media handled appropriately | Consider brightness filter or bg | Visual check of embedded media |
| D8 | Manual toggle works | `.dark` class overrides OS preference | Test toggle button |
| D9 | Preference persisted | `localStorage` stores `sp-theme` | Check storage after toggle |
| D10 | No flash on page load | Theme applied before first paint | Hard refresh with dark preference |
| D11 | Both `:root:not(.light)` and `.dark` work | OS preference + manual toggle both functional | Test all combinations |

---

## Deep Audit Procedures

### Procedure 1: Color Token Audit

Use when adding new colors or after a brand change.

1. **Inventory all token definitions**:
   ```bash
   grep -rn "^  --sp-color" storage/files/css/core/tokens-*.css
   ```

2. **Categorize each token** into primitive / semantic / component tier

3. **Verify tier references**:
   - Primitive tokens: raw oklch values only
   - Semantic tokens: `var()` references to primitives only
   - Component tokens: `var()` references to semantic tokens only

4. **Find orphaned tokens** (defined but never used):
   ```bash
   # Get all definitions
   grep -roh "\--sp-color-[a-z-]*" css/core/ | sort -u > /tmp/defined.txt
   # Get all usages
   grep -roh "\--sp-color-[a-z-]*" css/components/ css/pages/ css/layout/ | sort -u > /tmp/used.txt
   # Find orphans
   comm -23 /tmp/defined.txt /tmp/used.txt
   ```

5. **Find missing tokens** (hardcoded values that should be tokenized):
   ```bash
   grep -rn "#[0-9a-fA-F]\{3,8\}\|oklch(\|hsl(\|rgb(" \
     css/components/ css/pages/ css/layout/
   ```

6. **Validate contrast ratios** for every semantic fg/bg pair:
   - `--sp-color-text` on `--sp-color-bg` → must be ≥ 4.5:1
   - `--sp-color-text-muted` on `--sp-color-bg` → must be ≥ 4.5:1
   - `--sp-color-on-primary` on `--sp-color-primary` → must be ≥ 4.5:1
   - Repeat for every foreground/background combination used

7. **Repeat steps 3-6 for dark mode** by inspecting the `.dark` / `@media (prefers-color-scheme: dark)` reassignment block

### Procedure 2: Consistency Audit

Use when reviewing an established theme for quality issues.

1. **Identify all similar components** (buttons, cards, inputs, links)

2. **Verify they use the same semantic tokens**:
   ```bash
   grep -A5 "\.sp-button\b" css/components/*.css
   grep -A5 "\.sp-card\b" css/components/*.css
   # Compare: do buttons and cards use the same bg/border tokens?
   ```

3. **Check hover state consistency**:
   - In light mode: all hovers darken (mix with black)
   - In dark mode: all hovers lighten (mix with white)
   - No component hovers in the opposite direction

4. **Check border usage**:
   - All borders use `--sp-color-border` or `--sp-color-border-subtle`
   - No hardcoded border colors
   - Same border-width across similar components

5. **Check spacing consistency**:
   - Cards all use the same internal padding
   - Lists all use the same gap
   - Sections all use the same vertical spacing

### Procedure 3: Performance Audit

Use before deploying theme changes.

| Check | How | Pass Criteria |
|---|---|---|
| Total CSS file count | `find css/ -name "*.css" \| wc -l` | Under 30 files |
| Total CSS size | `find css/ -name "*.css" -exec wc -c {} + \| tail -1` | Under 100KB total |
| Largest CSS file | `wc -l css/**/*.css \| sort -n \| tail -5` | Under 200 lines each |
| No `@import` statements | `grep -rn "@import" css/` | Zero matches |
| Font loading strategy | Check `@font-face` for `font-display` | `font-display: swap` on all |
| Unused CSS rules | Browser Coverage tool | Under 30% unused |
| No duplicate selectors | `grep -roh "^\.[a-z-]*" css/ \| sort \| uniq -d` | Zero duplicates across files |

---

## Common Theme Problems and Fixes

| Problem | Symptoms | Root Cause | Fix |
|---|---|---|---|
| Washed-out dark mode | Colors look gray, lifeless | Chroma too low or surfaces all same lightness | Increase chroma slightly; ensure 0.04+ lightness difference between surface levels |
| Inconsistent hover states | Some elements darken on hover, others lighten | No standard hover pattern | Standardize: light mode uses `color-mix(... 88%, black)`, dark mode uses `color-mix(... 88%, white)` |
| Invisible focus rings | Keyboard navigation appears broken | Focus ring color matches background, or `:focus` used instead of `:focus-visible` | Use `--sp-color-focus` token with `outline` + `outline-offset: 2px`; test on all backgrounds |
| Jarring theme switch | Flash or sudden change when toggling | No transition on color properties | Add `transition: background-color 200ms, color 200ms` on `body`; add `<head>` flash prevention script |
| Spacing chaos | Uneven visual rhythm, cramped/sparse areas | Hardcoded px/rem values throughout | Audit all spacing, replace with `--sp-space-*` tokens |
| Color drift | Similar elements use slightly different colors | Tokens bypassed, raw values used | Grep for hardcoded colors, replace with semantic tokens |
| Muddy gradients | Gradient mid-tones look gray or brownish | Interpolating in sRGB color space | Switch to `linear-gradient(in oklch, ...)` |
| Type size inconsistency | Text sizes don't feel related | No mathematical scale, arbitrary sizes | Adopt a type scale ratio, replace all sizes with `--sp-text-*` tokens |
| Dark mode flash | White flash on page load for dark mode users | Theme class applied too late | Add inline `<script>` in `<head>` before stylesheets |
| Broken status colors in dark mode | Success/warning/danger unreadable on dark bg | Same tonal stops used for both modes | Use lighter stops (70 instead of 50) for status colors in dark mode |
| Shadows invisible in dark mode | No depth perception | Light-mode shadow values don't work on dark bg | Increase opacity, increase blur radius for dark mode shadows |
| Border-radius inconsistency | Buttons have different radius than inputs | No shared radius token | Use `--sp-radius-md` consistently for all interactive elements |

---

## Audit Reporting Template

Use this structure when documenting theme audit findings.

```markdown
# Theme Audit Report

**Date**: YYYY-MM-DD
**Scope**: [Files/components reviewed]
**Auditor**: [Name]

## Summary

| Category | Score | Critical Issues |
|---|---|---|
| Token System | ✅ / ⚠️ / ❌ | [count] |
| Color Quality | ✅ / ⚠️ / ❌ | [count] |
| Typography | ✅ / ⚠️ / ❌ | [count] |
| Spacing | ✅ / ⚠️ / ❌ | [count] |
| Motion | ✅ / ⚠️ / ❌ | [count] |
| Dark Mode | ✅ / ⚠️ / ❌ | [count] |

Scoring: ✅ = all checks pass, ⚠️ = minor issues, ❌ = critical failures

## Critical Issues (must fix)

1. **[Check ID]**: [Description of failure]
   - **Found**: [What was observed]
   - **Expected**: [What should be]
   - **Fix**: [Specific action to take]
   - **Files**: [Affected file paths]

## Improvements (should fix)

1. **[Check ID]**: [Description]
   - **Impact**: [Visual/performance/accessibility impact]
   - **Fix**: [Action]

## Token Migration Plan (if needed)

| Current Token | Current Value | New Token | New Value |
|---|---|---|---|
| `--sp-color-X` | `#hexval` | `--sp-color-X` | `oklch(...)` |

## Verification Steps

1. [ ] Run all grep checks from Quick Audit
2. [ ] Test light and dark modes
3. [ ] Run browser contrast checker
4. [ ] Test keyboard navigation (focus rings)
5. [ ] Test with prefers-reduced-motion
6. [ ] Performance: check total CSS size
7. [ ] Visual regression: screenshot comparison
```

---

## Pre-Commit Theme Checklist

Run before committing any theme changes.

- [ ] All new tokens use OKLCH format
- [ ] All new tokens have `--sp-` prefix
- [ ] Token naming follows `--sp-{category}-{property}[-{modifier}][-{state}]`
- [ ] Both light and dark mode values defined for new semantic tokens
- [ ] Contrast ratios verified for all new color pairs (4.5:1 minimum)
- [ ] No hardcoded colors, spacing, or sizes in component CSS
- [ ] Interactive elements have all 5 states (default, hover, active, focus-visible, disabled)
- [ ] `prefers-reduced-motion` respected for new animations
- [ ] No file exceeds 200 lines
- [ ] Token files load in correct order (primitive → semantic → component)
- [ ] Tested in browser: both light and dark modes
- [ ] Tested keyboard navigation: focus rings visible

---

## Quick Reference: Grep Commands

```bash
# Hardcoded colors (should be zero outside token files)
grep -rn "#[0-9a-fA-F]\{3,8\}\|rgb(\|hsl(" css/components/ css/pages/

# Unprefixed custom properties
grep -rn "^\s*--[^s]" css/
grep -rn "^\s*--s[^p]" css/

# Hardcoded spacing
grep -rn "[1-9][0-9]*px\|[0-9]*\.[0-9]*rem" css/components/ css/pages/

# Hardcoded font sizes
grep -rn "font-size:.*[0-9]px\|font-size:.*[0-9]rem" css/components/

# Transition: all (forbidden)
grep -rn "transition:\s*all" css/

# Missing reduced-motion
grep -rL "prefers-reduced-motion" css/

# Duplicate token definitions
grep -roh "\--sp-[a-z-]*:" css/core/ | sort | uniq -d

# Focus without focus-visible
grep -rn ":focus[^-]" css/

# Raw cubic-bezier in components
grep -rn "cubic-bezier" css/components/ css/pages/
```
