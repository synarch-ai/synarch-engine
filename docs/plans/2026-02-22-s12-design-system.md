# S12: Mission Control Design System ("Opaque Nexus")

## Overview
This document outlines the design system architecture for the Synarch Engine Mission Control UI (Issue #13). Moving away from generic SaaS aesthetics, we are implementing the "Opaque Nexus" design system: a tactile, Glassmorphism + Claymorphism hybrid designed for a dark-mode "spatial computing" / "high-tech lab" feel.

## 1. Core Visual Directives
- **Theme:** Dark Mode Default. Rich, deep background meshes (Slate-950 base with Violet/Cyan radial glows) instead of flat colors.
- **Texture:** A global CSS-based SVG noise/grain overlay for a cinematic, physical feel.
- **Glass + Clay:** Elements float. They utilize heavy blur (`backdrop-blur-xl`), semi-transparent backgrounds (`bg-white/5`), and extreme border radii (`rounded-[2rem]`).
- **Tactility:** Shadows are used to create 3D depth.
  - *Resting State:* Outer drop shadows lift elements off the page; subtle inner highlights (`inset 0 1px 1px rgba(255,255,255,0.1)`) give them a "puffed" clay edge.
  - *Active/Hover State:* Elements depress inward using transform scaling (`scale-95`) and inverted shadows.

## 2. Typography
- **Display/Headers:** `Outfit` (or similar geometric sans). Gives a slightly wide, futuristic, yet highly legible look for titles and major metrics.
- **Data/Body:** `JetBrains Mono`. Used heavily in event streams, JSON payloads, and logs to emphasize the technical nature of the engine.

## 3. Tailwind Architecture
The design system will be codified entirely in `tailwind.config.ts` and `globals.css`.

### Custom Utilities
We will extend the Tailwind theme with custom utility classes:
- `boxShadow`:
  - `clay-sm`: Subtle puffed depth for badges/small buttons.
  - `clay-md`: Standard depth for glass cards.
  - `clay-pressed`: Inverted inset shadows for active states.
- `backgroundImage`:
  - `noise`: A subtle SVG noise pattern tile.
  - `nexus-gradient`: The default deep mesh gradient for the app root.

### Components (React)
1. **`GlassCard`**: The fundamental container. Wraps children in the frosted, puffy aesthetic.
2. **`TactileButton`**: Interactive element that physically "presses" into the screen on click.
3. **`NeonBadge`**: High-contrast, glowing status indicators (e.g., `text-cyan-400 bg-cyan-400/10 border-cyan-400/30`).
4. **`NoiseOverlay`**: A fixed, `pointer-events-none` div that sits at z-index 50, applying the texture to the entire screen.

## 4. Implementation Steps
1. Scaffold `tailwind.config.ts` in `apps/web`.
2. Define the global CSS variables and noise patterns in `globals.css`.
3. Create the `ui/` directory and build the primitive components.
4. Refactor `apps/web/app/page.tsx` (and any other placeholders) to use the new layout and primitives.
