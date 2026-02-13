# Synarch: Design System Specification (V3)

**Status:** `LOCKED`
**Aesthetic:** **Cyber-Sovereign Industrialism**
**Principle:** "The beauty of a weapon system." High-precision, zero-latency, information-dense.

---

## 1. The Physics (Core Primitives)

We define the physical laws of the interface.

### 1.1. Spatial System
*   **The Grid:** The foundational layer is NOT empty space. It is a coordinate system.
    *   *Implementation:* A CSS persistent background pattern of 1px dots or crosshairs on a 40px grid.
    *   *Color:* `rgba(39, 39, 42, 0.2)` (Zinc-800 at 20% opacity).
*   **Depth:** We do not use "drop shadows" to lift elements. We use **Layers** and **Borders**.
    *   *Layer 0 (Void):* `#0A0A0B` (Background)
    *   *Layer 1 (Plate):* `#000000` (Opaque components, strictly bordered)
    *   *Layer 2 (Overlay):* `rgba(255, 185, 0, 0.05)` (Active scanning zones)

### 1.2. The Edge (Borders & Radius)
*   **Borders:** Everything has a border. *Everything.*
    *   *Width:* `1px` exactly.
    *   *Color:* `var(--border-primary)` (`#27272A`).
*   **Radius:**
    *   **Global Radius:** `0px` (Sharp).
    *   **Input/Action Radius:** `2px` (Micro-machined).
    *   **Forbidden:** `>4px`.

---

## 2. The Spectrum (Color System)

Using CSS Variables for runtime theming.

```css
:root {
  /* The Void */
  --bg-void: #0A0A0B;      /* Main Background */
  --bg-plate: #121214;     /* Component Background */
  --bg-active: #18181B;    /* Hover State */

  /* The Structure */
  --border-primary: #27272A;  /* Zinc-800 */
  --border-active: #3F3F46;   /* Zinc-700 */
  --border-highlight: #FFB900; /* Amber-500 */

  /* The Signal (Brand) */
  --signal-amber: #FFB900;
  --signal-amber-dim: rgba(255, 185, 0, 0.2);

  /* Agent Signatures */
  --agent-synarch: #FFB900; /* Amber */
  --agent-thoth: #8B5CF6;   /* Violet */
  --agent-hermes: #06B6D4;  /* Cyan */
  --agent-hephaestus: #F43F5E; /* Rose */
  --agent-janus: #10B981;   /* Emerald */
}
```

---

## 3. Typography: "The Terminal"

**Font Stack:**
1.  **Headings:** `Space Grotesk` (Weights: 500, 700). *Kerning: Tight (`-0.02em`).*
2.  **UI:** `Geist Sans` (Weights: 400, 500).
3.  **Code/Logs:** `Geist Mono` or `JetBrains Mono`.

**Type Hierarchy:**
*   `text-display`: Space Grotesk, Uppercase, Tracking-wide. *Use for Module Titles.*
*   `text-mono-sm`: Geist Mono, 12px. *Use for vast majority of UI.*
*   `text-body`: Geist Sans, 14px, Zinc-400. *Use for readability.*

---

## 4. Components (Atomic Definitions)

### 4.1. The Data Plate (Card Replacement)
We replace "Cards" with "Data Plates". A Data Plate is an opaque block that obscures the grid.
*   **Classes:** `bg-plate border border-primary relative overflow-hidden`.
*   **Decoration:** Ideally has a "cut corner" or a "technical ID" stamped in the corner (e.g., `TXT-01`).

### 4.2. The Log Entry (Chat Bubble Replacement)
We reject the "Message Bubble". We use "Log Entries".
*   **Container:** Full width, bordered left (`border-l-2`).
*   **Border Color:** Derived from Agent ID (e.g., `border-l-amber-500` for Synarch).
*   **Background:** Transparent or extremely subtle gradient (`bg-gradient-to-r from-zinc-900/50 to-transparent`).
*   **Typography:** Monospace for the header (`[SYNARCH] 10:42:05`), Sans for the content.

### 4.3. The Input Console (Text Area Replacement)
*   **Style:** No background (`bg-transparent`).
*   **Border:** Bottom border only (`border-b border-primary`). Active state: `border-amber-500`.
*   **Caret:** Block cursor (`caret-amber-500`), blinking.
*   **Prefix:** `>_` prompt always visible.

---

## 5. Animation (Kinetics)

Motion must feel **mechanical**, not organic.

*   **Duration:** Fast (`150ms`).
*   **Easing:** `cubic-bezier(0.0, 0.0, 0.2, 1)` (Snap to finish).

### Keyframes
*   `animate-scan`: A vertical line scanning down the container.
*   `animate-blink`: Standard terminal blink (opacity 0 -> 100).
*   `animate-glitch`: Subtle text offset (rgb shift) on hover.

---

## 6. Iconography
*   **Set:** `Lucide React` (Stroke Width: 1.5px).
*   **Style:** Sharp angles where possible.
*   **Usage:** Sparse. Used only for navigational landmarks.

---

## 7. Implementation Directives (Frontend-PE)
*   **Tailwind Config:** Must extend `colors` and `backgroundImage` (for the grid).
*   **Global CSS:** Remove all browser default padding/margins. Set `html { background: var(--bg-void); }`.
*   **Responsiveness:** Mobile is a "Datapad". Desktop is a "Cockpit".
