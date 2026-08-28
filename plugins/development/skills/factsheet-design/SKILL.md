---
name: factsheet-design
description: "Print design system for systemprompt.io PDF factsheets and one-pagers. Light branded containers (never dark glassmorphism), print token table, sp-card asymmetric corners in points, full-width SVG diagram rules, WeasyPrint constraints, and the two-page budget discipline. Load before creating or editing any factsheet, one-pager, or PDF sales asset."
version: "1.0.0"
---

# Factsheet Print Design

## When to load this

Any work on the PDF one-pagers in
`/var/www/html/systemprompt-template/docs-internal/factsheet-build/`: creating a
new sheet, editing an existing one, authoring a diagram SVG, or touching
`build.py`. Load `commons:identity` and `commons:brand-voice` alongside it for
copy; this skill governs the visual layer only.

Note that directory is **gitignored**, so there is no history to recover from. A
regression is permanent unless caught before the next build.

## The rule that keeps getting broken

**Containers are light and brand-tinted. Never dark glassmorphism.**

The June 2026 sheets (`factsheet-salesforce.html`, `factsheet-gatwick.html`) used
a dark glass treatment: `linear-gradient(150deg, #241F1C, #14110F)`, a radial
orange glow, `backdrop-filter: blur(9px)`, translucent white tiles. That style is
**retired**. The house style since `factsheet-ceo.html` (July 2026) is white and
peach containers with warm hairlines and orange accents.

`factsheet-procurement.html` is the reference implementation. When in doubt, diff
against it.

The class names `.glass-panel` and `.glass-tile` survive the migration and are
still correct to use. Only their *styling* changed. Do not rename them; do not
restore their old bodies.

```css
/* CORRECT: branded container */
.glass-panel {
  position: relative; overflow: hidden; color: var(--ink);
  border: 0.5pt solid var(--line);
  border-radius: var(--corners-md);
  background: #FFFFFF;
  box-shadow: 0 1pt 3pt rgba(15,23,42,0.05);
}
.glass-tile {
  background: var(--brand-bg-2);
  border: 0.5pt solid #F5D9C2;
  border-radius: var(--corners-inner);
}

/* WRONG: retired dark glass. If you see this, it is a regression. */
.glass-panel {
  background:
    radial-gradient(130% 115% at 100% -10%, rgba(243,131,24,0.32), transparent 55%),
    linear-gradient(150deg, #241F1C 0%, #14110F 100%);
}
.glass-tile { backdrop-filter: blur(9px); }
```

The at-a-glance hero panel follows the same conversion: peach card, **white**
inner tiles, orange `ArchivoBlack` numerals.

```css
.sp-card.glance {
  color: var(--ink);
  border: 0.5pt solid #F5D9C2;
  background: var(--brand-bg-2);
  box-shadow: 0 1pt 3pt rgba(15,23,42,0.05);
  overflow: hidden;
}
.glance .grid > div {
  background: #FFFFFF;
  border: 0.5pt solid #F1DAC5;
  border-radius: var(--corners-inner);
  box-shadow: 0 0.5pt 1.5pt rgba(15,23,42,0.04);
  padding: 2.4mm 2.7mm;
}
.glance .n { font-family: 'ArchivoBlack','Inter',sans-serif; font-size: 14pt; color: var(--brand); }
```

**The one sanctioned dark element is the closing `.cta` bar.** Ed approved the
ink-filled CTA on the partner sheet as a deliberate closer. The procurement
lineage uses a peach CTA with a 3pt orange left rule instead. Either is
acceptable; pick one per sheet and do not mix.

## Print tokens

```css
:root {
  --ink: #0F172A;          /* body text, logo wordmark */
  --muted: #55606E;        /* secondary text */
  --muted-2: #8893A3;      /* tertiary, footers */
  --line: #E9E5DD;         /* warm hairline */
  --line-2: #F3F0EA;
  --paper: #FFFFFF;
  --paper-2: #FAFAF9;
  --band: #F3F0EA;
  --brand: #F38318;        /* primary orange */
  --brand-hi: #F7A34F;
  --brand-lo: #C46610;     /* orange on light, for text that must pass contrast */
  --brand-bg: #FFE8D5;     /* pill and icon-tile fill */
  --brand-bg-2: #FFF6EF;   /* softest peach, the container fill */
  --blue: #2A6FB5;
  --green: #158A54;

  --corners-md: 8pt 2.5pt 8pt 8pt;    /* TL TR BR BL */
  --corners-inner: 4pt 1pt 4pt 4pt;
  --corners-pill: 4pt 1pt 4pt 4pt;
}
html { background: #FCFBF9; }
```

Peach hairlines: `#F5D9C2` on peach fills, `#F1DAC5` on white tiles nested inside
peach. Blue lineage for upstream/system-of-record blocks: fill `#F3F8FC`, hairline
`#CFE1F1`, rule `#2A6FB5`.

Type: Inter 400/700 body at `8.25pt / 1.45`, ArchivoBlack for `h1` (17pt),
section numbers and big metrics, `ui-monospace` for code and emails.

## Asymmetric corners

The tight top-right corner is the brand signature, same rule as
`development:visual-design-system` but expressed in points for print. Roughly a
quarter of the other three corners. **Never symmetric** on a container.

```css
border-radius: 8pt 2.5pt 8pt 8pt;   /* TL TR BR BL, tight TR */
```

Circles (`50%`) and pills are the only exceptions.

## Diagram SVGs

1. **Full width.** `<div class="diagram">` with no `max-width` clamp. A diagram
   pinned to 56% of the column reads as cramped and is a defect. Control height
   by designing a flatter `viewBox`, not by shrinking the width.
2. **No dark ground rect.** The panels sit directly on the paper. Do not paint a
   `#241F1C` or gradient background behind them.
3. **Inline presentation attributes only.** WeasyPrint ignores `<style>` blocks
   *and* CSS inside inline SVG. Every fill, stroke, font-size and weight must be
   an attribute on the element.
4. **Flat fills.** Avoid gradients and opacity tricks; they render inconsistently.
   Use the token hexes directly.
5. Sizing: `.diagram svg { width: 100%; height: auto; display: block; }` and the
   `viewBox` sets the aspect. At the A4 text column (188mm), a `900 x H` viewBox
   renders `188 * H / 900` mm tall. A 900x240 box is about 50mm, which is the
   most a busy page 2 can usually afford.

Panel language, matching the containers: white fill, warm hairline, a coloured
header bar with white text (grey `#57534E` for the client layer, brand `#F38318`
for ours, blue `#2A6FB5` for upstream), peach sub-boxes for anything we own, a
2.5pt brand rule on the left of the block you want read first.

## Renderer

**Default to WeasyPrint.** It gives crisper Inter and supports CSS margin boxes,
so the running footer lives in the template:

```css
@page {
  size: A4; margin: 9mm 11mm 11mm 11mm;
  @bottom-left  { content: "AI you own · systemprompt.io"; font-family: 'Inter', sans-serif; font-size: 6pt; color: #8893A3; letter-spacing: 0.3pt; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: 'Inter', sans-serif; font-size: 6pt; font-weight: 700; color: #8893A3; }
}
```

Chromium is in `build.py` for exactly one reason: `backdrop-filter`, which
WeasyPrint cannot render. Since the house style has no `backdrop-filter`, **a new
sheet should never need Chromium.** If you find yourself adding
`("...", "...", "...", "chromium", "footer text")` to `TEMPLATES`, you have
probably reintroduced glassmorphism. Chromium sheets also need their footer
passed as `footer_left` because Chromium ignores CSS margin boxes.

Build everything with:

```bash
cd /var/www/html/systemprompt-template/docs-internal/factsheet-build && python3 build.py
```

There is no per-sheet flag; it rebuilds all of them. PDF bytes change on every
run because of embedded timestamps, so verify by page count and rendered output,
not by hash.

## The two-page budget

Every sheet is exactly **2 pages**. The printable height is **277mm** (A4 297mm
less 9mm and 11mm margins). Page 1 uses `<section class="page fill">` so blocks
distribute down the page; page 2 is a plain `<section class="page">`.

Measure before you guess. Sum-of-blocks in mm, at the true print width:

```python
from playwright.sync_api import sync_playwright
html = open('factsheet-<name>-inlined.html').read()
PX = round(188/25.4*96)   # A4 text column; a default 1280px viewport lies to you
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': PX, 'height': 1000})
    pg.set_content(html, wait_until="networkidle"); pg.emulate_media(media="print")
    for r in pg.evaluate("""()=>[...document.querySelectorAll('section.page')].map(s=>
        [+(s.getBoundingClientRect().height/3.7795).toFixed(1),
         [...s.children].map(c=>[(c.className||c.tagName).slice(0,16),
           +(c.getBoundingClientRect().height/3.7795).toFixed(1)])])"""): print(r)
    b.close()
```

This approximates WeasyPrint rather than matching it, so confirm with a real
build. Rasterise the result to look at it:

```python
import fitz
d = fitz.open('systemprompt-io-<name>-factsheet.pdf')
for i, p in enumerate(d): p.get_pixmap(dpi=150).save(f'preview-<name>/p-{i+1}.png')
```

`pdftoppm` is not installed; PyMuPDF and pypdfium2 are.

Trim levers, in the order that costs the least meaning: table row padding and
row count, footnote wording, body copy in the growth cards, then diagram
`viewBox` height. Shrinking the diagram's *width* is not a lever, see above.

## Checklist before declaring a sheet done

- [ ] Exactly 2 pages, confirmed from the built PDF.
- [ ] No `backdrop-filter`, no `#241F1C`, no `linear-gradient(150deg` in the template.
- [ ] Renderer is `weasyprint` in `build.py` unless there is a stated reason.
- [ ] Diagram is full width, has no dark ground, and uses inline attributes only.
- [ ] Every container uses `--corners-md` or `--corners-inner`; no symmetric radius.
- [ ] Footer reads correctly and shows "Page N of 2".
- [ ] Rasterised both pages and actually looked at them. No clipped or colliding text.
- [ ] The other sheets still build at 2 pages each (`build.py` rebuilds all).
- [ ] Copy passes `commons:brand-voice`: no em dashes, no banned cliches.
- [ ] Every printed figure has a source recorded in `STATE.md`.

## Where the state lives

`docs-internal/factsheet-build/STATE.md` is the running record: what each sheet
is for, which persona, the source table behind every printed number, layout
headroom notes, and open approval items. Update it in the same change as the
sheet. It is the only durable memory for a gitignored directory.
