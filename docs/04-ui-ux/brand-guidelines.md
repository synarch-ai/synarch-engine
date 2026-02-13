# Synarch — Brand Guidelines & Logo Generation

---

## 1. Brand Identity

### The Name
**Synarch** — syn (together) + arch (rule/govern) = "Ruling Together"

### The Tagline
*"Where agents rule together."*

### The Essence
Synarch is the invisible command structure behind autonomous AI teams. It's not flashy consumer tech — it's **infrastructure for intelligence**. Think HashiCorp, Palantir, Vercel — not Notion or Figma.

### Brand Personality
| Attribute | Description |
|---|---|
| **Authoritative** | We command systems, not request them |
| **Precise** | Engineering precision, not marketing fluff |
| **Dark** | Power operates in shadows. Our UI is dark-first. |
| **Mythological** | Ancient wisdom meets cutting-edge AI |
| **Orchestrated** | Nothing is random. Everything is designed. |

---

## 2. Logo Generation Prompts

### Primary Logo (The Mark)

**For AI image generators (Midjourney/DALL-E/Ideogram):**

```
Design a minimalist, geometric logo mark for "Synarch" — an enterprise-grade
autonomous AI agent orchestration platform.

CONCEPT: A "Distributed Crown" — a crown formed by interconnected network
nodes. The crown represents sovereignty and governance. The nodes represent
distributed agents working in concert. The fusion symbolizes "ruling together."

STYLE:
- Ultra-clean geometric linework
- Mono-weight strokes (consistent line thickness)
- Works at 16px favicon AND billboard scale
- Single color (works in pure white on dark, or pure dark on white)
- NO gradients, NO 3D effects, NO photorealism
- Think: Stripe's logo precision meets Palantir's authority

GEOMETRY:
- 5-7 nodes arranged in a crown/chevron formation
- Thin connecting lines between nodes (network topology)
- The overall silhouette should read as a crown from distance
- Up close, it's clearly a network graph
- Slight upward momentum (ascending, not static)

VIBES:
- HashiCorp meets ancient Greek architecture
- Enterprise infrastructure, not consumer app
- "This company controls systems that control systems"
- Dark mode native — designed to glow on black backgrounds

DO NOT:
- Use literal crowns with jewels
- Use robot/AI faces
- Use brain imagery
- Use circuit board patterns
- Use generic "S" lettermarks
- Use any color — monochrome only

OUTPUT: Vector-ready, SVG-compatible, pure geometric construction.
Background: transparent.
```

### Wordmark

```
Design a clean wordmark for "SYNARCH" in all capitals.

FONT CHARACTERISTICS:
- Geometric sans-serif (think: Euclid Circular, GT America, Inter Display)
- Medium to semibold weight
- Wide letter-spacing (tracking: +80 to +120)
- The "Y" and "A" should have subtle geometric angles
  that echo the crown/network mark
- Monospaced feel but proportional — engineered, not decorative

STYLE:
- Pure typography, no icon integration
- Works standalone without the mark
- Looks like it belongs on:
  - A CLI terminal header
  - A conference keynote slide
  - A GitHub organization banner
  - A developer documentation site

DO NOT:
- Use script/handwritten fonts
- Use serif fonts
- Add any effects (shadows, outlines, 3D)
- Use lowercase
```

---

## 3. Color System

### Primary Palette (Dark-First)

```css
:root {
  /* Backgrounds */
  --synarch-black:     #0A0A0F;    /* Deep space black — primary bg */
  --synarch-dark:      #111118;    /* Elevated surface */
  --synarch-surface:   #1A1A24;    /* Cards, panels */
  
  /* Brand Accent */
  --synarch-indigo:    #6366F1;    /* Primary action — confident, not loud */
  --synarch-violet:    #8B5CF6;    /* Secondary accent — hover states */
  
  /* Status Colors (Agent States) */
  --synarch-green:     #22C55E;    /* Active / Success / Approved */
  --synarch-amber:     #F59E0B;    /* Thinking / Processing / Warning */
  --synarch-red:       #EF4444;    /* Error / Rejected / Critical */
  --synarch-blue:      #3B82F6;    /* Info / Delegating */
  
  /* Text */
  --synarch-text:      #E2E8F0;    /* Primary text (slate-200) */
  --synarch-muted:     #94A3B8;    /* Secondary text (slate-400) */
  --synarch-dim:       #475569;    /* Tertiary text (slate-600) */
  
  /* Agent Identity Colors (for dashboard) */
  --agent-synarch:     #6366F1;    /* Indigo — the CEO */
  --agent-zeus:        #F59E0B;    /* Amber — lightning */
  --agent-thoth:       #8B5CF6;    /* Violet — wisdom */
  --agent-hermes:      #22C55E;    /* Green — speed */
  --agent-hephaestus:  #EF4444;    /* Red — forge fire */
  --agent-janus:       #06B6D4;    /* Cyan — dual nature */
}
```

### Color Rules
1. **Dark mode is the default.** Light mode is Phase 2.
2. **Indigo is the brand.** Use sparingly — only for primary CTAs and the Synarch agent.
3. **Each agent has ONE color** — used in the Thought Stream, topology graph, and task board.
4. **Never use color alone** to convey meaning (accessibility).

---

## 4. Typography

### Font Stack

```css
/* Headings — sharp, geometric, authoritative */
--font-heading: 'Geist', 'Inter Display', 'SF Pro Display', system-ui;

/* Body — readable, engineered */
--font-body: 'Geist', 'Inter', 'SF Pro Text', system-ui;

/* Code / Agent Logs — the CLI feel */
--font-mono: 'Geist Mono', 'JetBrains Mono', 'SF Mono', monospace;
```

### Type Scale
- Agent names in logs: `font-mono`, uppercase, color-coded
- Dashboard headers: `font-heading`, semibold, large
- Mission status: `font-mono`, medium
- Body text: `font-body`, regular, slate-200

---

## 5. Design Principles

1. **Infrastructure Aesthetic** — We look like Vercel/Stripe, not Canva/Notion
2. **Dark-First** — Every screen designed on `#0A0A0F` first
3. **Data-Dense** — Show more, not less. Developers want information, not whitespace
4. **Terminal Energy** — The Thought Stream should feel like watching `docker logs`
5. **Mythology Subtle** — Agent names (Zeus, Thoth) add character but UI doesn't look "Greek"
6. **Motion = Information** — Animations only when they convey state change (agent thinking, task completing)

---

## 6. Application Examples

### GitHub Organization Banner
```
[SYNARCH logo mark]  SYNARCH
Where agents rule together.
──────────────────────────
The autonomous multi-agent orchestration engine.
```

### CLI Output
```
$ synarch start
  ⚡ Synarch Engine v0.1.0
  ✅ NATS connected (synarch.agent.>)
  ✅ PostgreSQL ready (checkpoints enabled)
  ✅ Agents online: Synarch, Zeus, Thoth, Hermes, Hephaestus, Janus
  🌐 Mission Control: http://localhost:3000
  
  Awaiting orders from God...
```

### Dashboard Header
```
┌─────────────────────────────────────────┐
│ ⬡ SYNARCH ENGINE  ·  Mission Control    │
│                                         │
│ Agents: 6 online  ·  Mission: m-001     │
│ Status: EXECUTING  ·  Cost: $0.04       │
└─────────────────────────────────────────┘
```

---

*"The crown is not worn by one. It is formed by many."*
