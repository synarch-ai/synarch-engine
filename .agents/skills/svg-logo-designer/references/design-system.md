# Design System Reference

## Table of Contents

1. Color Psychology & Palette Construction
2. Color Combination Strategies
3. Contrast & Accessibility Rules
4. Typography in Logos
5. Visual Style Patterns
6. Logo Type Deep Dive
7. Spacing, Proportion & Optical Adjustment
8. Design Token Specification
9. Figma-Ready Spec Sheet Template
10. Brand Guidelines Document Template

---

## 1. Color Psychology & Palette Construction

Select colors based on brand mood and industry. These are starting points -- always adapt to context.

### Primary Palette Associations

| Color | Hex Range | Conveys | Strong Industries |
|-------|-----------|---------|-------------------|
| Deep Blue | #0A2463, #1B3A6B | Trust, authority, stability | Finance, enterprise tech, healthcare, legal |
| Bright Blue | #2563EB, #3B82F6 | Innovation, clarity, reliability | SaaS, cloud, communications |
| Teal | #0D9488, #14B8A6 | Balance, calm, sophistication | Wellness, fintech, sustainability |
| Emerald | #059669, #10B981 | Growth, health, renewal | Environment, agriculture, wellness, finance |
| Lime | #65A30D, #84CC16 | Energy, freshness, youth | Food & bev, startups, fitness |
| Red | #DC2626, #EF4444 | Passion, urgency, power | Food, entertainment, sports, media |
| Coral | #F97066, #FB7185 | Warmth, approachability, modern | Lifestyle, beauty, social |
| Orange | #EA580C, #F97316 | Friendly, energetic, affordable | Retail, food, children, creative |
| Amber | #D97706, #F59E0B | Optimism, premium, attention | Food, energy, luxury-adjacent |
| Purple | #7C3AED, #8B5CF6 | Creativity, luxury, wisdom | Beauty, creative agencies, education |
| Violet | #6D28D9, #A78BFA | Innovation, digital, mystique | Tech, gaming, crypto |
| Magenta | #DB2777, #EC4899 | Bold, contemporary, expressive | Fashion, beauty, entertainment |
| Near-Black | #0F172A, #1E293B | Sophistication, power, timelessness | Luxury, fashion, premium tech |
| Warm Gray | #78716C, #A8A29E | Neutral, professional, balanced | Consulting, architecture, law |
| Slate | #475569, #64748B | Modern neutral, tech-forward | SaaS, developer tools |

### Emotional Mapping Matrix

Use this when translating the user's emotional keywords into color direction:

| Emotional Keyword | Primary Color Direction | Secondary Pair |
|-------------------|------------------------|---------------|
| Bold / Powerful | Deep Blue, Near-Black, Red | + Amber or White accent |
| Elegant / Refined | Near-Black, Deep Blue, Purple | + Gold (#C9A84C) or Warm Gray |
| Playful / Friendly | Orange, Coral, Lime | + Bright Blue or Amber |
| Trustworthy / Reliable | Deep Blue, Teal, Emerald | + Slate or Warm Gray |
| Innovative / Cutting-edge | Violet, Bright Blue, Magenta | + Near-Black or Teal |
| Warm / Approachable | Coral, Orange, Amber | + Emerald or Warm Gray |
| Clean / Minimalist | Slate, Near-Black, Bright Blue | + White space as primary element |
| Organic / Natural | Emerald, Lime, Teal | + Warm Gray or Amber |
| Futuristic / Digital | Violet, Bright Blue, Teal | + Magenta or Near-Black |
| Heritage / Traditional | Deep Blue, Near-Black, Warm Gray | + Gold or Slab typography |
| Rebellious / Edgy | Red, Near-Black, Magenta | + High contrast, angular forms |
| Premium / Luxury | Near-Black, Purple, Deep Blue | + Gold, minimal palette |

---

## 2. Color Combination Strategies

**Monochromatic**: One hue, varying lightness/saturation. Safest, most cohesive.
- Example: #1E40AF, #3B82F6, #93C5FD (blue scale)
- Best for: minimalist brands, tech, premium

**Complementary**: Opposite hues. High contrast, high energy.
- Example: #2563EB + #F59E0B (blue + amber)
- Best for: dynamic brands, consumer-facing, food

**Analogous**: Adjacent hues. Harmonious, natural.
- Example: #0D9488 + #2563EB (teal + blue)
- Best for: wellness, nature, calm brands

**Split-complementary**: One hue + two adjacent to its complement. Balanced contrast.
- Example: #7C3AED + #059669 + #F59E0B (purple + emerald + amber)
- Best for: creative agencies, multi-service brands

**Neutral + accent**: Grays/blacks with one strong color. Professional, focused.
- Example: #1E293B + #EF4444 (slate + red accent)
- Best for: consulting, law, enterprise, editorial

**Duotone gradient**: Two brand colors blending. Modern, digital-native.
- Example: #4F46E5 to #EC4899 (indigo to pink)
- Best for: tech startups, creative tech, social platforms

---

## 3. Contrast & Accessibility Rules

- Logo must achieve WCAG AA contrast (4.5:1) against its intended background
- Test every color variant: full-color on white, full-color on dark, mono on both
- For text in logos: minimum 4.5:1 contrast ratio
- For decorative elements: minimum 3:1
- Use a contrast checker for every color pair in the system
- Consider deuteranopia, protanopia, and tritanopia -- the logo should remain distinguishable

---

## 4. Typography in Logos

### Font Category Guide

| Category | Conveys | Best For | System Fallbacks |
|----------|---------|----------|-----------------|
| Geometric Sans | Modern, clean, tech | Tech, startups, digital | Arial, Helvetica |
| Humanist Sans | Warm, approachable, clear | Healthcare, education, consumer | Verdana, Calibri |
| Neo-Grotesque | Neutral, universal, corporate | Enterprise, government | Arial, Helvetica |
| Slab Serif | Strong, reliable, grounded | Construction, manufacturing, sports | Georgia, Rockwell |
| Modern Serif | Elegant, editorial, premium | Luxury, media, fashion | Georgia, Times New Roman |
| Old-Style Serif | Traditional, scholarly, trustworthy | Law, finance, education | Garamond, Palatino |
| Display / Decorative | Unique, expressive, memorable | Entertainment, food, creative | (convert to paths) |
| Monospace | Technical, code, precise | Developer tools, engineering | Courier New, Consolas |
| Handwritten / Script | Personal, artisan, organic | Boutique, food, creative | (convert to paths) |

### Logo Typography Rules

1. **Maximum 2 typefaces** per logo. One for brand name, optionally one for tagline.
2. **Convert non-system fonts to paths** in SVG for portability.
3. **Letter-spacing matters** -- adjust tracking for readability at small sizes. Looser for uppercase, tighter for lowercase.
4. **Weight contrast** -- if using two weights, make the difference significant (700 + 300, not 500 + 400).
5. **Case conventions:**
   - ALL CAPS: authority, modern, geometric (needs wider letter-spacing, +0.05em to +0.15em)
   - Title Case: traditional, approachable
   - lowercase: friendly, modern, casual (Google, facebook)

### Typography-to-Mood Mapping

| Mood Keywords | Recommended Category | Weight | Spacing |
|---------------|---------------------|--------|---------|
| Modern, clean, innovative | Geometric Sans | 500-700 | +0.02em to +0.08em |
| Warm, human, approachable | Humanist Sans | 400-600 | Normal to +0.02em |
| Strong, grounded, reliable | Slab Serif | 600-800 | +0.02em to +0.05em |
| Elegant, premium, editorial | Modern Serif | 300-500 | +0.05em to +0.12em |
| Playful, creative, unique | Display | 400-700 | Varies by face |
| Technical, precise, code | Monospace | 400-500 | Normal |

---

## 5. Visual Style Patterns

### Minimalist
- Maximum 2-3 elements
- Generous white space
- Thin to medium stroke weights (1-3px at viewBox scale)
- Limited color (1-2 colors)
- Clean geometric shapes
- No gradients, no textures
- **SVG tip**: Fewer path nodes = cleaner rendering at small sizes

### Geometric
- Precise mathematical shapes
- Grid-based construction (use golden ratio or 8px grid)
- Symmetry or golden ratio proportions
- Sharp corners or perfectly rounded
- Often monochromatic or limited palette
- **SVG tip**: Use `<polygon>`, `<circle>`, `<rect>` for precision

### Organic / Flowing
- Curved, natural forms using cubic beziers
- Asymmetric balance
- Hand-drawn quality (but clean)
- Softer color palettes
- Rounded terminals and joins
- **SVG tip**: Use `stroke-linecap="round"` and `stroke-linejoin="round"`

### Bold / Heavy
- Thick strokes (4-8px+) and solid fills
- High contrast
- Strong silhouette (test: squint test -- still recognizable?)
- Works well at any size
- Often uses negative space
- **SVG tip**: Test with `fill` only, no strokes for maximum impact

### Elegant / Refined
- Thin strokes (0.5-2px), delicate details
- Generous spacing
- Serif or thin sans typography
- Muted, sophisticated colors
- Minimal elements, maximum restraint
- **SVG tip**: May need `shape-rendering="geometricPrecision"` for thin lines

### Tech / Futuristic
- Circuit-board patterns, grid structures, node-connection motifs
- Gradient or glow effects (use SVG filters sparingly)
- Angular, sharp forms
- Blues, purples, cyans
- Forward-leaning or dynamic composition
- **SVG tip**: `<linearGradient>` with subtle angle, `filter` for glow

### Vintage / Retro
- Badge or stamp shapes
- Ornamental details, borders, banners
- Earth tones, muted palettes
- Serif or slab-serif typography
- Layered appearance via SVG pattern fills
- **SVG tip**: Multiple concentric borders via nested `<rect>` or `<circle>` with decreasing radii

### Brutalist / Raw
- Rough, unpolished aesthetic
- High contrast, stark colors (often black + one loud color)
- Heavy type, often geometric sans at extreme weights
- Asymmetric, unconventional layout, overlapping elements
- Anti-design sensibility
- **SVG tip**: `transform="rotate(...)"` for off-kilter placement

---

## 6. Logo Type Deep Dive

### Wordmark Construction
- Baseline alignment is critical
- Optical kerning > metric kerning (adjust spacing visually, not mathematically)
- Consider custom ligatures or letter modifications for uniqueness
- Negative space within/between letters can embed symbols (FedEx arrow principle)
- Test readability at 100px, 50px, 32px widths

### Lettermark Construction
- Each letter must be recognizable individually
- Consider how letters interact: overlap, connect, stack, interlock
- Monogram styles: interlocking, stacked, side-by-side, contained in shape
- Works best with 2-3 letters
- Must be more distinctive than the letters alone

### Pictorial Mark Construction
- Must be recognizable without text
- Test at 16px, 32px, 64px, 128px, 256px, 512px
- Single continuous form is stronger than multiple disconnected pieces
- Consider positive/negative space interplay (FedEx arrow, NBC peacock, WWF panda)
- Silhouette test: fill with solid black -- still recognizable?

### Abstract Mark Construction
- Must feel intentional, not random
- Should suggest movement, connection, or transformation
- Geometric forms scale better than organic ones
- Must be ownable -- avoid generic shapes (circles alone, basic triangles)
- Test: can someone sketch this from memory after seeing it once?

### Combination Mark Construction
- Icon and text should feel like one unit, not two separate pieces
- Establish clear visual hierarchy (usually icon > name > tagline)
- Icon should work independently when separated
- Maintain consistent proportional relationship across layouts
- The gap between icon and text is as important as the elements themselves

### Emblem Construction
- Outer shape contains all elements
- Text follows the shape (curved, arched, or contained)
- More detail-tolerant than other types (but still test small)
- Consider simplified "responsive" versions for small sizes
- Common shapes: circle, shield, badge, crest, ribbon

---

## 7. Spacing, Proportion & Optical Adjustment

### Golden Ratio (1:1.618)
Use for proportional relationships between icon and text, or between logo elements. If icon width = 40px, text area width = ~65px.

### Clear Space
- Minimum clear space = height of the icon element (or cap-height of the wordmark)
- Apply equally on all sides
- No other visual elements should intrude
- Express as a CSS custom property: `--logo-clearspace`

### Optical Sizing
- **Small (< 32px)**: Increase stroke weights, simplify details, increase spacing, remove fine elements
- **Medium (32-128px)**: Standard rendering, full detail
- **Large (> 200px)**: Fine details become visible, precision matters, consider adding subtle refinements
- Test at: 16px, 32px, 64px, 128px, 256px, 512px

### Optical Alignment
- Circular and triangular elements appear smaller than squares at the same dimension
- Overshoot round elements by ~3-5% beyond the bounding box for visual alignment
- Pointed shapes (triangles, arrows) should extend ~5-8% beyond baseline for optical centering
- Horizontal center is slightly above mathematical center (~45% from top for visual balance)

---

## 8. Design Token Specification

After final concept approval, generate tokens in all three formats:

### CSS Custom Properties

```css
:root {
  /* === Brand Colors === */
  --brand-primary: #HEXVAL;
  --brand-primary-rgb: R, G, B;        /* for rgba() usage */
  --brand-primary-light: #HEXVAL;
  --brand-primary-dark: #HEXVAL;
  --brand-secondary: #HEXVAL;
  --brand-secondary-rgb: R, G, B;
  --brand-accent: #HEXVAL;

  /* === Text Colors === */
  --brand-text-default: #1E293B;
  --brand-text-muted: #64748B;
  --brand-text-inverse: #FFFFFF;

  /* === Background Colors === */
  --brand-bg-light: #FFFFFF;
  --brand-bg-dark: #0F172A;
  --brand-bg-surface: #F8FAFC;

  /* === Typography === */
  --brand-font-primary: 'FontName', SystemFallback, sans-serif;
  --brand-font-weight-bold: 700;
  --brand-font-weight-medium: 500;
  --brand-font-weight-regular: 400;
  --brand-letter-spacing-brand: 0.02em;
  --brand-letter-spacing-caps: 0.08em;

  /* === Logo Sizing === */
  --logo-clearspace: 1em;
  --logo-min-width-digital: 100px;
  --logo-min-width-print: 1in;
  --logo-max-width-header: 200px;
}
```

### JSON Tokens (Design Tokens Community Group format)

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "color": {
    "brand": {
      "primary": { "$value": "#HEXVAL", "$type": "color", "$description": "Main brand color -- [rationale]" },
      "primary-light": { "$value": "#HEXVAL", "$type": "color" },
      "primary-dark": { "$value": "#HEXVAL", "$type": "color" },
      "secondary": { "$value": "#HEXVAL", "$type": "color", "$description": "[rationale]" },
      "accent": { "$value": "#HEXVAL", "$type": "color" }
    },
    "text": {
      "default": { "$value": "#1E293B", "$type": "color" },
      "muted": { "$value": "#64748B", "$type": "color" },
      "inverse": { "$value": "#FFFFFF", "$type": "color" }
    },
    "background": {
      "light": { "$value": "#FFFFFF", "$type": "color" },
      "dark": { "$value": "#0F172A", "$type": "color" },
      "surface": { "$value": "#F8FAFC", "$type": "color" }
    }
  },
  "typography": {
    "fontFamily": {
      "primary": { "$value": "FontName, SystemFallback, sans-serif", "$type": "fontFamily" }
    },
    "fontWeight": {
      "bold": { "$value": 700, "$type": "fontWeight" },
      "medium": { "$value": 500, "$type": "fontWeight" },
      "regular": { "$value": 400, "$type": "fontWeight" }
    },
    "letterSpacing": {
      "brand": { "$value": "0.02em", "$type": "dimension" },
      "caps": { "$value": "0.08em", "$type": "dimension" }
    }
  },
  "spacing": {
    "logoClearspace": { "$value": "1em", "$type": "dimension" },
    "logoMinWidth": { "$value": "100px", "$type": "dimension" }
  }
}
```

---

## 9. Figma-Ready Spec Sheet Template

Present this structured specification with every final delivery:

```markdown
# Brand Identity Spec Sheet: [Brand Name]

## Color Palette

| Swatch | Name | Hex | RGB | Usage |
|--------|------|-----|-----|-------|
| [show] | Primary | #HEXVAL | rgb(R,G,B) | Logo mark, primary CTA, key UI |
| [show] | Primary Light | #HEXVAL | rgb(R,G,B) | Hover states, backgrounds |
| [show] | Primary Dark | #HEXVAL | rgb(R,G,B) | Active states, headers |
| [show] | Secondary | #HEXVAL | rgb(R,G,B) | Supporting elements |
| [show] | Accent | #HEXVAL | rgb(R,G,B) | Highlights, badges |

## Typography

| Element | Font | Weight | Size (relative) | Letter-spacing | Case |
|---------|------|--------|-----------------|----------------|------|
| Brand name | [Font] | 700 | 1em | 0.02em | [CAPS/Title/lower] |
| Tagline | [Font] | 400 | 0.4em | 0.04em | [as specified] |

## Logo Dimensions

| Layout | ViewBox | Aspect Ratio | Min Width (Digital) | Min Width (Print) |
|--------|---------|-------------|--------------------|--------------------|
| Horizontal | 0 0 400 120 | 3.33:1 | 200px | 2in |
| Vertical | 0 0 200 260 | 1:1.3 | 120px | 1.5in |
| Square/Icon | 0 0 100 100 | 1:1 | 32px | 0.5in |
| Text only | 0 0 300 60 | 5:1 | 150px | 1.5in |

## Clear Space

Minimum clear space on all sides = height of the icon element.
Expressed as: [X]px at standard logo size, or [ratio] of total logo height.

## Color Usage Rules

| Context | Variant | Background |
|---------|---------|-----------|
| Website header | Full color | White/light |
| Dark mode UI | Reversed | Dark (#0F172A) |
| Print (color) | Full color | White paper |
| Print (B&W) | Mono dark | White paper |
| Watermark | Mono light @ 20% opacity | Over photography |
| Social avatar | Icon-only, full color | White circle |

## Incorrect Usage

- Do not stretch, skew, or rotate
- Do not change individual element colors
- Do not add drop shadows, outlines, or effects
- Do not place on busy backgrounds without clear space
- Do not recreate or approximate -- always use the provided files
- Do not use the icon-only version where horizontal lockup fits
```

---

## 10. Brand Guidelines Document Template

For comprehensive deliveries, generate a `brand-spec.md` using this structure:

```markdown
# [Brand Name] Brand Identity Guidelines

## 1. Logo Overview
[Design rationale, concept name, what it communicates]

## 2. Logo Variations
[List all available layouts with thumbnails/descriptions]

## 3. Color System
[Full palette with hex, RGB, usage rules, accessibility notes]

## 4. Typography
[Font specifications, weights, spacing, case rules]

## 5. Clear Space & Sizing
[Minimum sizes, clear space rules, optical guidelines]

## 6. Usage Rules
[Do's and don'ts with explicit examples]

## 7. Color Variants
[Full color, mono dark, mono light, reversed -- when to use each]

## 8. File Inventory
[Complete list of delivered files with paths and descriptions]

## 9. Technical Implementation
[Web usage (inline SVG, img, CSS), responsive patterns, export instructions]

## 10. Design Tokens
[CSS custom properties, JSON tokens, integration instructions]
```
