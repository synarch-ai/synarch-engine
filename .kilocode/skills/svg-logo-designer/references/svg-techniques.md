# SVG Techniques Reference

## Table of Contents

1. SVG Boilerplate & ViewBox
2. Path Construction & Common Shapes
3. CSS Custom Properties in SVG
4. Gradients (Linear, Radial, Conic)
5. Text & Typography
6. Negative Space Techniques
7. Clip Paths & Masks
8. SVG Filters & Effects
9. Blend Modes
10. CSS-in-SVG Animations
11. Responsive SVG Patterns
12. Optimization Checklist
13. Color Variant Generation
14. Export Guide

---

## 1. SVG Boilerplate & ViewBox

Every logo SVG starts with this structure:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 [W] [H]"
     role="img" aria-labelledby="logo-title logo-desc">
  <title id="logo-title">[Brand Name] Logo</title>
  <desc id="logo-desc">[Brief visual description for screen readers]</desc>

  <defs>
    <style>
      :root {
        --brand-primary: #HEXVAL;
        --brand-secondary: #HEXVAL;
        --brand-text: #HEXVAL;
      }
      .brand-primary { fill: var(--brand-primary); }
      .brand-secondary { fill: var(--brand-secondary); }
      .brand-text { fill: var(--brand-text); }
    </style>
    <!-- Gradients, clip paths, filters, masks -->
  </defs>

  <g id="symbol">
    <!-- Icon / mark elements -->
  </g>

  <g id="wordmark">
    <!-- Text / typography elements -->
  </g>
</svg>
```

### ViewBox Guidelines

| Layout | Recommended viewBox | Notes |
|--------|-------------------|-------|
| Horizontal lockup | `0 0 400 120` | ~3.3:1 ratio |
| Vertical lockup | `0 0 200 260` | ~1:1.3, icon above text |
| Square / icon | `0 0 100 100` | 1:1, centered content |
| Circular | `0 0 100 100` | 1:1 with circle clip or boundary |
| Text only | `0 0 300 60` | ~5:1, adjust to text length |

Use even numbers for viewBox dimensions to avoid sub-pixel rendering issues.

---

## 2. Path Construction & Common Shapes

### When to Use Shapes vs Paths

Use semantic shapes (`<circle>`, `<rect>`, `<polygon>`) for clarity. Convert to `<path>` only when combining, morphing, or optimizing file size.

### Path Commands Reference

| Command | Parameters | Description |
|---------|-----------|-------------|
| M/m | x,y | Move to point |
| L/l | x,y | Line to point |
| H/h | x | Horizontal line |
| V/v | y | Vertical line |
| C/c | x1,y1 x2,y2 x,y | Cubic bezier curve |
| S/s | x2,y2 x,y | Smooth cubic bezier (mirrors previous control point) |
| Q/q | x1,y1 x,y | Quadratic bezier curve |
| T/t | x,y | Smooth quadratic bezier |
| A/a | rx,ry rot large,sweep x,y | Arc |
| Z | | Close path |

Uppercase = absolute coordinates. Lowercase = relative to current point.

### Constructing Common Logo Shapes

**Hexagon:**
```xml
<polygon points="50,5 93,27 93,73 50,95 7,73 7,27" />
```

**Shield:**
```xml
<path d="M50,5 L90,25 L90,55 Q90,85 50,95 Q10,85 10,55 L10,25 Z" />
```

**Infinity / figure-8:**
```xml
<path d="M50,40 C30,20 5,20 5,40 C5,60 30,60 50,40
         C70,20 95,20 95,40 C95,60 70,60 50,40 Z"
      fill="none" stroke="currentColor" stroke-width="4" />
```

**Chevron / arrow:**
```xml
<path d="M20,10 L50,40 L80,10 L80,20 L50,50 L20,20 Z" />
```

**Leaf / organic:**
```xml
<path d="M50,10 Q80,30 80,60 Q80,90 50,90 Q20,90 20,60 Q20,30 50,10 Z" />
```

**Star (5-point):**
```xml
<polygon points="50,5 61,35 95,35 68,57 79,90 50,70 21,90 32,57 5,35 39,35" />
```

**Rounded triangle:**
```xml
<path d="M50,10 Q55,10 80,55 Q85,63 80,70 L20,70 Q15,63 20,55 Q45,10 50,10 Z" />
```

**Circle with gap (progress ring / arc logo):**
```xml
<path d="M50,5 A45,45 0 1,1 15,72.5" fill="none" stroke="var(--brand-primary)"
      stroke-width="6" stroke-linecap="round" />
```

**Diamond / rhombus:**
```xml
<polygon points="50,5 95,50 50,95 5,50" />
```

**Rounded rectangle (pill):**
```xml
<rect x="10" y="30" width="80" height="40" rx="20" ry="20" />
```

---

## 3. CSS Custom Properties in SVG

Use custom properties inside SVGs for easy theming and design token integration:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <style>
      /* Define brand tokens -- these can be overridden by parent CSS */
      svg {
        --brand-primary: #4F46E5;
        --brand-secondary: #10B981;
        --brand-text: #1E293B;
        --brand-bg: transparent;
      }
      .primary { fill: var(--brand-primary); }
      .secondary { fill: var(--brand-secondary); }
      .text-fill { fill: var(--brand-text); }
    </style>
  </defs>

  <circle cx="50" cy="50" r="40" class="primary" />
  <text x="50" y="55" text-anchor="middle" class="text-fill"
        font-family="Arial, sans-serif" font-size="16" font-weight="700">
    BRAND
  </text>
</svg>
```

**Theming advantage:** When this SVG is inline in HTML, the parent page's CSS can override the custom properties:

```css
/* Dark mode override */
@media (prefers-color-scheme: dark) {
  svg {
    --brand-primary: #818CF8;
    --brand-text: #F1F5F9;
  }
}
```

---

## 4. Gradients

### Linear Gradient

```xml
<defs>
  <linearGradient id="grad-primary" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="var(--brand-primary)" />
    <stop offset="100%" stop-color="var(--brand-secondary)" />
  </linearGradient>
</defs>
<circle cx="50" cy="50" r="40" fill="url(#grad-primary)" />
```

**Direction presets:**
- Top to bottom: `x1="0%" y1="0%" x2="0%" y2="100%"`
- Left to right: `x1="0%" y1="0%" x2="100%" y2="0%"`
- Diagonal (135deg): `x1="0%" y1="0%" x2="100%" y2="100%"`
- Diagonal (45deg): `x1="0%" y1="100%" x2="100%" y2="0%"`

### Radial Gradient

```xml
<defs>
  <radialGradient id="grad-glow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#60A5FA" />
    <stop offset="100%" stop-color="#2563EB" />
  </radialGradient>
</defs>
```

### Off-Center Radial (spotlight effect)

```xml
<defs>
  <radialGradient id="grad-spot" cx="30%" cy="30%" r="70%" fx="30%" fy="30%">
    <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.3" />
    <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0" />
  </radialGradient>
</defs>
<!-- Layer over a colored shape for a highlight effect -->
<circle cx="50" cy="50" r="40" fill="url(#grad-spot)" />
```

### Gradient Rules for Logos

- Use gradients sparingly -- flat color is more versatile
- Always provide a flat-color fallback version
- Limit stops to 2-3 for logo use
- Ensure sufficient contrast at both gradient endpoints
- Test grayscale rendering

---

## 5. Text & Typography

### System Font Approach

```xml
<text x="100" y="50" font-family="Arial, Helvetica, sans-serif"
      font-size="36" font-weight="700" fill="var(--brand-text)"
      letter-spacing="2" text-anchor="middle">BRAND</text>
```

### Path-Converted Text (fully portable)

Convert in a design tool or construct manually for font-independent rendering:

```xml
<!-- Letter "A" as path (simplified) -->
<path d="M10,40 L20,10 L30,40 M14,30 L26,30" fill="none"
      stroke="var(--brand-text)" stroke-width="3" stroke-linecap="round" />
```

### Curved Text (for emblems)

```xml
<defs>
  <path id="text-curve" d="M20,80 A40,40 0 0,1 80,80" fill="none" />
</defs>
<text font-family="Arial, sans-serif" font-size="10" fill="var(--brand-text)">
  <textPath href="#text-curve" startOffset="50%" text-anchor="middle">
    BRAND NAME
  </textPath>
</text>
```

### Typography Spacing

- `letter-spacing`: +1-4px for uppercase wordmarks, normal or -0.5px for lowercase
- `word-spacing`: Adjust for multi-word brand names
- `text-anchor`: `middle` for centered, `start` for left-aligned
- `dominant-baseline`: `central` for vertical centering with other elements

---

## 6. Negative Space Techniques

Negative space is the hallmark of expert logo design.

**Counter-form**: Space inside/between letters forms a recognizable shape.
```xml
<!-- Two shapes where the gap reads as an arrow -->
<rect x="10" y="10" width="35" height="80" class="primary" />
<rect x="55" y="10" width="35" height="80" class="primary" />
<!-- The gap between rectangles forms the secondary image -->
```

**Figure-ground reversal**: Two images depending on viewer focus.

**Embedded symbol**: Smaller symbol hidden within letterforms or the main shape.

**Implementation pattern**: Use two overlapping shapes where the overlap creates the hidden element:
```xml
<circle cx="40" cy="50" r="30" class="primary" />
<circle cx="60" cy="50" r="30" class="primary" />
<!-- The vesica piscis overlap creates an eye/leaf shape -->
```

---

## 7. Clip Paths & Masks

### Circular Crop (avatar/icon)

```xml
<defs>
  <clipPath id="circle-crop">
    <circle cx="50" cy="50" r="48" />
  </clipPath>
</defs>
<g clip-path="url(#circle-crop)">
  <!-- Logo content -->
</g>
```

### Rounded Rectangle Crop (app icon)

```xml
<defs>
  <clipPath id="rounded-crop">
    <rect x="2" y="2" width="96" height="96" rx="20" ry="20" />
  </clipPath>
</defs>
```

### Mask for Transparency Effects

```xml
<defs>
  <mask id="fade-mask">
    <linearGradient id="mask-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="white" />
      <stop offset="100%" stop-color="black" />
    </linearGradient>
    <rect width="100" height="100" fill="url(#mask-grad)" />
  </mask>
</defs>
<g mask="url(#fade-mask)">
  <!-- Content fades from fully visible (left) to invisible (right) -->
</g>
```

### Text as Clip Path (text knockout)

```xml
<defs>
  <clipPath id="text-clip">
    <text x="50" y="60" text-anchor="middle"
          font-family="Arial, sans-serif" font-size="48" font-weight="900">
      BRAND
    </text>
  </clipPath>
</defs>
<!-- Gradient visible only through the text shape -->
<rect width="100" height="100" fill="url(#grad-primary)"
      clip-path="url(#text-clip)" />
```

---

## 8. SVG Filters & Effects

Use sparingly in logos. Filters add visual richness but increase complexity and rendering cost.

### Subtle Drop Shadow

```xml
<defs>
  <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">
    <feDropShadow dx="0" dy="2" stdDeviation="3"
                  flood-color="#000000" flood-opacity="0.15" />
  </filter>
</defs>
<g filter="url(#shadow)">
  <!-- Logo content -->
</g>
```

### Inner Shadow (inset effect)

```xml
<defs>
  <filter id="inner-shadow">
    <feComponentTransfer in="SourceAlpha">
      <feFuncA type="table" tableValues="1 0" />
    </feComponentTransfer>
    <feGaussianBlur stdDeviation="2" />
    <feOffset dx="1" dy="2" result="offsetblur" />
    <feFlood flood-color="#000000" flood-opacity="0.2" result="color" />
    <feComposite in2="offsetblur" operator="in" />
    <feComposite in2="SourceAlpha" operator="in" />
    <feMerge>
      <feMergeNode in="SourceGraphic" />
      <feMergeNode />
    </feMerge>
  </filter>
</defs>
```

### Glow Effect (for tech/futuristic logos)

```xml
<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur" />
    <feFlood flood-color="#4F46E5" flood-opacity="0.6" result="color" />
    <feComposite in="color" in2="blur" operator="in" result="glow" />
    <feMerge>
      <feMergeNode in="glow" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
```

### Noise Texture (for vintage/organic feel)

```xml
<defs>
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65"
                  numOctaves="3" stitchTiles="stitch" />
    <feColorMatrix type="saturate" values="0" />
    <feBlend in="SourceGraphic" mode="multiply" />
  </filter>
</defs>
```

### Emboss / Letterpress Effect

```xml
<defs>
  <filter id="emboss">
    <feGaussianBlur in="SourceAlpha" stdDeviation="1" result="blur" />
    <feSpecularLighting in="blur" surfaceScale="2" specularConstant="0.5"
                         specularExponent="10" lighting-color="#FFFFFF"
                         result="specular">
      <fePointLight x="-5000" y="-10000" z="20000" />
    </feSpecularLighting>
    <feComposite in="specular" in2="SourceAlpha" operator="in" result="litShape" />
    <feMerge>
      <feMergeNode in="SourceGraphic" />
      <feMergeNode in="litShape" />
    </feMerge>
  </filter>
</defs>
```

### Filter Usage Rules for Logos

- Filters are for **presentation versions only**, not the canonical logo
- Always have a filter-free version as the primary deliverable
- Filters may not render consistently across all SVG viewers
- If using filters, keep `filter` region generous (x/y negative, width/height > 120%)
- Test in Chrome, Firefox, Safari, and at least one native SVG viewer

---

## 9. Blend Modes

SVG supports CSS-like blend modes via `mix-blend-mode` or the `feBlend` filter primitive.

### CSS Blend Modes in SVG

```xml
<circle cx="40" cy="50" r="30" fill="#4F46E5" />
<circle cx="60" cy="50" r="30" fill="#EC4899" style="mix-blend-mode: multiply;" />
<!-- Overlap area creates a rich purple blend -->
```

### Common Blend Modes for Logos

| Mode | Effect | Use Case |
|------|--------|----------|
| `multiply` | Darkens overlapping areas | Overlapping translucent shapes, depth |
| `screen` | Lightens overlapping areas | Glowing/light effects on dark |
| `overlay` | Combines multiply and screen | Texture application, rich overlaps |
| `soft-light` | Subtle tonal variation | Gentle shading, dimensional hints |
| `difference` | Subtracts colors | Dynamic inversion effects |

### Blend Mode Pattern: Overlapping Circles (Venn-style)

```xml
<g style="isolation: isolate;">
  <circle cx="40" cy="40" r="25" fill="#EF4444" opacity="0.8" />
  <circle cx="60" cy="40" r="25" fill="#3B82F6" opacity="0.8"
          style="mix-blend-mode: multiply;" />
  <circle cx="50" cy="58" r="25" fill="#10B981" opacity="0.8"
          style="mix-blend-mode: multiply;" />
</g>
```

### Blend Mode Rules

- `isolation: isolate` on the parent group prevents blending with elements outside the logo
- Blend modes may render differently across browsers -- test thoroughly
- Always have a flat-color fallback version
- Blend modes work best for digital/screen applications, not print

---

## 10. CSS-in-SVG Animations

For digital-first brands, subtle animations add life. Use only for web/screen versions.

### Hover State (when SVG is inline)

```xml
<defs>
  <style>
    .logo-icon {
      fill: var(--brand-primary);
      transition: fill 0.3s ease, transform 0.3s ease;
      transform-origin: center;
    }
    svg:hover .logo-icon {
      fill: var(--brand-primary-dark, #3730A3);
      transform: scale(1.05);
    }
  </style>
</defs>
```

### Subtle Pulse (for loading states or emphasis)

```xml
<defs>
  <style>
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    .logo-pulse {
      animation: pulse 2s ease-in-out infinite;
    }
  </style>
</defs>
<g class="logo-pulse">
  <!-- Logo content -->
</g>
```

### Draw-On Effect (path reveal)

```xml
<defs>
  <style>
    @keyframes draw {
      from { stroke-dashoffset: 300; }
      to { stroke-dashoffset: 0; }
    }
    .draw-path {
      stroke-dasharray: 300;
      stroke-dashoffset: 300;
      animation: draw 2s ease forwards;
    }
  </style>
</defs>
<path class="draw-path" d="M10,50 Q50,10 90,50 T170,50"
      fill="none" stroke="var(--brand-primary)" stroke-width="3" />
```

### Rotate Element (for abstract/geometric marks)

```xml
<defs>
  <style>
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .rotate-element {
      transform-origin: 50px 50px;
      animation: spin 20s linear infinite;
    }
  </style>
</defs>
```

### Color Shift (gradient animation)

```xml
<defs>
  <style>
    @keyframes color-shift {
      0% { stop-color: #4F46E5; }
      50% { stop-color: #7C3AED; }
      100% { stop-color: #4F46E5; }
    }
    .grad-stop-1 { animation: color-shift 4s ease-in-out infinite; }
  </style>
  <linearGradient id="animated-grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" class="grad-stop-1" stop-color="#4F46E5" />
    <stop offset="100%" stop-color="#EC4899" />
  </linearGradient>
</defs>
```

### Staggered Entrance (multi-element logos)

```xml
<defs>
  <style>
    @keyframes fade-up {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .element-1 { animation: fade-up 0.5s ease forwards; animation-delay: 0s; }
    .element-2 { animation: fade-up 0.5s ease forwards; animation-delay: 0.15s; opacity: 0; }
    .element-3 { animation: fade-up 0.5s ease forwards; animation-delay: 0.3s; opacity: 0; }
  </style>
</defs>
```

### Animation Rules for Logos

- Animations are for **web/digital versions only** -- never the canonical static logo
- Prefer `prefers-reduced-motion: reduce` media query to disable animations for accessibility:
```xml
<style>
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
  }
</style>
```
- Keep animations subtle (< 5% movement, slow timing)
- Draw-on and fade-in are safest for brand perception
- Spinning/pulsing can feel cheap -- use only when brand voice supports it
- Animation duration: 1-3s for entrances, 3-10s for loops

---

## 11. Responsive SVG Patterns

### Inline SVG (maximum control, theming support)

```html
<div class="logo" style="width: 200px;">
  <svg viewBox="0 0 400 120" style="width: 100%; height: auto;">
    <!-- logo content -->
  </svg>
</div>
```

### Image Tag (simpler, no theming)

```html
<img src="logo.svg" alt="Brand Name Logo" width="200" height="60" />
```

### CSS Background (decorative use)

```css
.logo {
  background: url('logo.svg') no-repeat center / contain;
  width: 200px;
  height: 60px;
}
```

### Responsive Sizing

```css
.logo-container {
  width: clamp(120px, 15vw, 240px);
}
.logo-container svg {
  width: 100%;
  height: auto;
}
```

### Dark Mode Support (inline SVG with custom properties)

```css
@media (prefers-color-scheme: dark) {
  .logo-container svg {
    --brand-primary: #818CF8;
    --brand-text: #F1F5F9;
  }
}
```

---

## 12. Optimization Checklist

Apply to every SVG before delivery:

1. **Remove default attributes**: `fill="black"` (default), `stroke="none"`, `opacity="1"`
2. **Reduce decimal precision**: 1-2 places max (`M50.3,22.7` not `M50.2847,22.6913`)
3. **Combine identical fills**: Group under a styled `<g>` or shared class
4. **Remove empty groups**: No `<g>` without children or attributes
5. **Use shorthand path commands**: `H` and `V` instead of `L` for single-axis movement
6. **Remove metadata**: No `<metadata>`, editor comments, or generator stamps
7. **Minimize nesting**: Flatten unnecessary group hierarchies
8. **Use `<use>` for repeated elements**: Define once in `<defs>`, reference with `<use>`
9. **Remove invisible elements**: Nothing with `display: none` or `opacity: 0` in final output
10. **Validate**: Every SVG should be valid XML

```xml
<!-- Before -->
<g>
  <g>
    <path d="M 10.00000 20.00000 L 30.00000 20.00000 L 30.00000 40.00000"
          fill="black" stroke="none" opacity="1" />
  </g>
</g>

<!-- After -->
<path d="M10,20 H30 V40" />
```

---

## 13. Color Variant Generation

### Monochrome Dark

```xml
<style>
  svg { --brand-primary: #1A1A2E; --brand-secondary: #1A1A2E; --brand-text: #1A1A2E; }
</style>
```

### Monochrome Light

```xml
<style>
  svg { --brand-primary: #FFFFFF; --brand-secondary: #FFFFFF; --brand-text: #FFFFFF; }
</style>
```

### Reversed (dark background)

- Swap light/dark relationships
- Text becomes white
- Colored elements may need brightness/saturation boost for contrast
- Test against #0F172A, #1E293B, and true #000000

### Single-Color Print

```xml
<style>
  svg { --brand-primary: #000000; --brand-secondary: #666666; --brand-text: #000000; }
</style>
```

---

## 14. Export Guide

### SVG to PNG

**Inkscape:**
```bash
inkscape logo.svg -o logo.png -w 1000
inkscape logo.svg -o logo@2x.png -w 2000
```

**ImageMagick:**
```bash
convert -background none -density 300 logo.svg logo.png
```

**rsvg-convert:**
```bash
rsvg-convert -w 1000 logo.svg > logo.png
```

### Recommended Export Sizes

| Use Case | Dimensions |
|----------|-----------|
| Favicon | 16x16, 32x32, 48x48 |
| App icon (iOS) | 1024x1024 |
| App icon (Android) | 512x512 |
| Social media profile | 400x400 |
| Social media banner | 1500x500 |
| Website header | 200-400px wide |
| Print (business card) | 300 DPI, vector preferred |
| Print (signage) | Vector, no raster |
| Open Graph image | 1200x630 |
