# Synarch Logo Generation Prompts

Aligned with V3 Design System: **Cyber-Sovereign Industrialism**

---

## Prompt 1: The Mark (Primary Symbol)

**For Midjourney v6 / DALL-E / Ideogram:**

```
A complex, architectural blueprint, technical drawing logo for "Synarch" (SAMAS).

CONCEPT: "The Sovereign Schematic". A crown shape visualized as a high-fidelity
distributed system architecture diagram. It is not just a shape; it is a BLUEPRINT.

VISUALS:
- An isometric or orthographic projection of 7 interlocking agent nodes
- The nodes form a sharp, aggressive crown silhouette
- The connections between nodes are detailed data pipelines (thick and thin lines)
- Tiny, precise technical readouts (lines, numbers, crosshairs) surround the main shape
- The aesthetic is "Military-Industrial AI Control System"

STYLE:
- CAD (Computer-Aided Design) Wireframe
- Technical Blueprint
- 80s Cyberpunk Industrial Design (Alien / Blade Runner interfaces)
- Extremely high detail, fine lines, math-heavy look

COLOR:
- Main Lines: Electric Amber (#FFB900)
- Accent Lines: Dim Tungsten (#52525b)
- Background: SOLID VOID BLACK (#0A0A0B) - NO TRANSPARENCY, NO CHECKERBOARD

FEEL:
- "This is the architecture of a superior intelligence."
- Intimidatingly complex but organized.
- Precision engineering.
- Screams "Enterprise-Grade Autonomous System".

OUTPUT: High-contrast technical illustration. Solid black background.
```

---

## Prompt 2: The Wordmark

```
Design a typography-only logo for "SYNARCH" — all uppercase.

FONT DIRECTION:
- Based on Space Grotesk Black (700 weight) or similar geometric grotesque
- Wide tracking (+100 to +150 letter-spacing)
- The "Y" has perfectly symmetric 60-degree angles
- The "A" is flat-topped (no apex point — industrial, not classical)
- The "R" has a straight leg (not curved — mechanical)
- The "CH" pair kerned tightly to feel like one unit

TREATMENT:
- Pure letterforms. No icon integration.
- Optionally: a thin horizontal line running through the text
  at cap-height, like a redacted document or a datum line
- Alternatively: the "Y" could subtly incorporate the crown mark's
  top-center node (a small circle at the junction)

FEEL:
- Reads like it belongs on:
  1. A black terminal splash screen
  2. A keynote presentation title slide
  3. A GitHub organization header
  4. An invoice from a defense contractor
- NOT startup-cute. NOT rounded. NOT lowercase.

COLOR:
- Signal White #FAFAFA on Void Black #0A0A0B (primary)
- Amber #FFB900 on Void Black (branded version)
- Pure black on white (print version)

OUTPUT: Vector wordmark. No background.
```

---

## Prompt 3: Combined Lockup (Mark + Wordmark)

```
Combine the Distributed Crown mark with the SYNARCH wordmark into
a horizontal lockup:

[Crown Mark]  SYNARCH

RULES:
- Crown mark sits to the left, vertically centered with text
- Clear separation between mark and text (2x the width of one letter)
- Mark height equals cap-height of the wordmark
- Both in same color (amber or white, never mixed)
- A thin vertical divider line between mark and text (optional, 1px, #27272A)

SECONDARY LOCKUP (Stacked):
     [Crown Mark]
      SYNARCH

- Mark centered above wordmark
- 8px gap between mark bottom and text top
- For square formats (social avatars, app icons)
```

---

## Prompt 4: Favicon / App Icon

```
Design a square app icon for "Synarch" using ONLY the crown mark.

SPECS:
- The distributed crown mark centered in a square
- Background: Void Black #0A0A0B
- Mark color: Amber #FFB900
- Generous padding (mark occupies ~60% of the square)
- Sharp corners on the outer square (0px radius — matches brand)
- At 16x16px, still reads as "crown-like network"

SIZES NEEDED:
- 16x16 (favicon)
- 32x32 (browser tab)
- 180x180 (Apple touch)
- 512x512 (PWA)
- 1024x1024 (master)
```

---

## Prompt 5: GitHub Organization Banner

```
Design a GitHub organization header banner for "synarch-ai".

LAYOUT (1280x640px):
- Background: Void Black #0A0A0B with subtle 40px dot grid
  (dots at rgba(39,39,42,0.2) — from V3 design system)
- Left-aligned: Crown mark + SYNARCH wordmark lockup in Amber #FFB900
- Below wordmark: Tagline "Where agents rule together." in Signal White #FAFAFA
  using Space Grotesk 400 weight
- Right side: Subtle visualization of 6 connected nodes in agent colors
  (amber, violet, cyan, rose, emerald) — representing the agent council
- Bottom: thin 1px Amber line spanning full width

FEEL:
- Should look like the header of a classified briefing document
- "This is infrastructure. This is serious."
```

---

## Usage Notes

- **Always generate at least 4 variations** of each prompt
- **Test every logo at 16px** before selecting
- After generation, **vectorize in Figma or Illustrator** — AI generators produce raster, we need SVG
- The final logo files should be committed to `branding/assets/` as SVG + PNG exports

---

*"The crown is not worn by one. It is formed by many."*
