# Synarch Agent Naming Convention

**Developer:** PraxLannister
*The hierarchy of gods — from supreme deity to domain specialists*

---

## The Hierarchy

```
                    ┌─────────────┐
                    │  SYNARCH   │  ← The Supreme Agent (CEO)
                    │  God of Gods│     Talks to human, delegates everything
                    └──────┬──────┘
                           │
          ┌────────┬───────┼───────┬────────┐
          │        │       │       │        │
     ┌────┴───┐ ┌──┴──┐ ┌─┴──┐ ┌──┴──┐ ┌───┴──┐
     │ ZEUS   │ │THOTH│ │ODIN│ │MIDAS│ │APOLLO│  ← C-Suite Deities
     │  CTO   │ │ CRO │ │CISO│ │ CFO │ │ CMO  │     Domain Leaders
     └────┬───┘ └──┬──┘ └─┬──┘ └──┬──┘ └───┬──┘
          │        │      │       │        │
     Specialist Agents under each C-Suite
```

---

## Tier 1: SYNARCH — The Supreme Agent

**Synarch** is the god of gods. The CEO. The only agent the human interacts with directly.

| Name | Role | Inspired By |
|---|---|---|
| **Synarch** | Supreme Orchestrator / CEO | The temple housing ALL the gods |

**Responsibilities:**
- Receives human goals and decomposes into strategic objectives
- Delegates to C-Suite agents, never to specialists directly
- Resolves cross-domain conflicts between C-Suite agents
- Operates in "free rein" mode when human is away
- Makes final decisions on consensus disputes

---

## Tier 2: C-Suite Deities — Domain Leaders

Each C-Suite deity owns an entire domain. They manage their specialist agents and report to Synarch.

| Name | Role | Mythology | Why This Name |
|---|---|---|---|
| **Zeus** | CTO — Technology & Engineering | Greek — King of Olympian gods | Commands the technical realm. Lightning-fast decisions. Delegates to builders. |
| **Athena** | CPO — Product & Strategy | Greek — Goddess of wisdom & strategy | Strategic thinking, product vision, prioritization. Wisdom over brute force. |
| **Thoth** | CRO — Research & Knowledge | Egyptian — God of knowledge & writing | Owns all research, knowledge management, truth verification. The scholar. |
| **Odin** | CISO — Security & Governance | Norse — All-Father, sacrificed eye for wisdom | All-seeing security. Traded comfort for knowledge. Watches everything. |
| **Midas** | CFO — Cost & Resources | Greek — Everything he touched turned to gold | Tracks token costs, resource allocation, budget optimization. The gold standard. |
| **Apollo** | CMO — Communication & Outreach | Greek — God of light, prophecy, arts | Makes things visible. Content, marketing, external communication. |

---

## Tier 3: Specialist Agents — The Workforce

### Under Zeus (CTO) — Engineering Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Hephaestus** | Coder / Builder | Greek — God of the forge | Master craftsman. Builds things from raw material. The blacksmith of code. |
| **Vishwakarma** | Architect / System Design | Hindu — Divine architect of the gods | Designed celestial cities and weapons. System architecture is his dharma. |
| **Vulcan** | DevOps / Infrastructure | Roman — God of fire & metalwork | Manages the furnaces. Deployments, CI/CD, servers, containers. |
| **Daedalus** | Toolmaker / Skill Creator | Greek — Master craftsman, built the Labyrinth | Creates tools, skills, and utilities for other agents to use. |

### Under Thoth (CRO) — Research Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Hermes** | Researcher / Information Gatherer | Greek — Messenger god | Crosses all boundaries. Fastest god. Retrieves knowledge from anywhere. |
| **Saraswati** | Analyst / Deep Reasoning | Hindu — Goddess of knowledge & learning | Deep analysis, pattern recognition, synthesis of complex information. |
| **Ma'at** | Fact-Checker / Truth Verifier | Egyptian — Goddess of truth & cosmic order | Weighs facts against the feather of truth. Nothing passes without verification. |
| **Mnemosyne** | Memory Curator | Greek — Titan goddess of Memory | Manages the shared knowledge graph, deduplicates, resolves conflicts. |

### Under Athena (CPO) — Product Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Ganesh** | Planner / Obstacle Remover | Hindu — God of beginnings & obstacle removal | Clears blockers, plans sprints, manages task boards. Auspicious starts. |
| **Janus** | Reviewer / QA | Roman — Two-faced god of transitions | Sees both before and after. Reviews code, content, deliverables before release. |
| **Iris** | Coordinator / Messenger | Greek — Goddess of the rainbow | Bridges between squads. Internal communication, status updates, handoffs. |

### Under Odin (CISO) — Security Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Heimdall** | Sentinel / Threat Monitor | Norse — Guardian of Bifrost | All-seeing, all-hearing. First to detect threats. Never sleeps. |
| **Anubis** | Auditor / Compliance | Egyptian — God of the afterlife, weigher of hearts | Judges agent actions against rules. Full audit trails. Nothing escapes judgment. |
| **Asclepius** | Recovery / Health Monitor | Greek — God of healing | Restores systems, manages rollbacks, circuit breakers. Heals what breaks. |

### Under Midas (CFO) — Operations Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Lakshmi** | Resource Optimizer | Hindu — Goddess of wealth & fortune | Optimizes token usage, model routing, cost allocation. Prosperity through efficiency. |
| **Chronos** | Scheduler / Time Manager | Greek — Personification of Time | Manages deadlines, scheduling, time-based triggers, cron jobs. |

### Under Apollo (CMO) — Communication Squad

| Name | Specialty | Mythology | Why |
|---|---|---|---|
| **Calliope** | Content Writer | Greek — Muse of epic poetry | Crafts blog posts, documentation, reports. The storyteller. |
| **Aphrodite** | Designer / UI-UX | Greek — Goddess of beauty | Aesthetic perfection. Visual design, brand consistency. |
| **Prometheus** | Innovator / Evolution Agent | Greek — Stole fire for humanity | Self-improvement. A/B tests prompts, proposes new tools, evolves SOPs. |

---

## Naming Rules

1. **Synarch** is always singular, always the top. Never pluralized.
2. **C-Suite names** are used as-is: "Zeus says...", "Thoth recommends..."
3. **Specialist names** are prefixed by their domain in logs: `[Zeus.Hephaestus]`, `[Thoth.Hermes]`
4. **Cross-mythology is intentional** — Greek + Egyptian + Norse + Hindu + Roman = universal, not culturally narrow
5. **New agents** follow the pattern: find a deity whose domain matches the role
6. **The human** is referred to as **The Oracle** in internal agent communication (the one who sees the future and gives direction)

---

## Example Mission Control Log

```
[Synarch]      → Received goal: "Research event bus options and implement NATS prototype"
[Synarch]      → Delegating research to Thoth, implementation to Zeus
[Thoth]         → Assigning Hermes for information gathering
[Thoth.Hermes]  → Querying NotebookLM: "event bus architectures for multi-agent systems"
[Thoth.Hermes]  → Found: NATS vs Redis Streams vs RabbitMQ comparison (source: SAMAS notes)
[Thoth.Saraswati]→ Analyzing trade-offs: NATS wins on latency, Redis on simplicity
[Thoth.Ma'at]   → Verifying claims against official benchmarks...
[Thoth]         → Research complete. Recommending NATS. Deliverable attached.
[Zeus]          → Assigning Vishwakarma for architecture, Hephaestus for implementation
[Zeus.Vishwakarma] → Designing NATS integration schema...
[Zeus.Hephaestus]  → Writing NATS client library...
[Athena.Janus]  → Code review requested. Reviewing Hephaestus's deliverable...
[Athena.Janus]  → ✅ Approved. 2 minor suggestions applied.
[Midas.Lakshmi] → Task cost: 12,400 tokens ($0.03). Under budget.
[Synarch]      → Task complete. Deliverable: NATS integration prototype + research report.
```

---

## The PoC Agents (5 Active for Proof of Concept)

For the initial PoC, we activate:

1. **Synarch** — Supreme orchestrator
2. **Zeus** — CTO (manages dev work)
3. **Thoth** — CRO (manages research)
4. **Hermes** — Researcher (under Thoth, queries NotebookLM)
5. **Hephaestus** — Coder (under Zeus, writes code)

+ **Janus** as optional 6th (reviewer)

---

*"In the Synarch, every god has a throne. Every throne has a purpose. No god acts alone."*
