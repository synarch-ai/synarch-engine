# ADR-002: Branding Pivot — Synarch AI → Synarch

**Developer:** PraxLannister
*Architecture Decision Record | 2026-02-13 | Status: DECIDED*

---

## The Problem
"Synarch AI" has critical trademark conflicts globally:

### Kill-Shot Conflicts (Direct Legal Threats)
- **Synarch Systems (Synarch.io)** — massive WebOps platform, strict trademark policy, Class 9 & 42
- **SynarchLab.ai** — Generative AI for digital humans (Asia-based) — exact overlap
- **synarchai.co** — AI tools for insurance — identical name
- **Synarch Digital Pvt Ltd (India, Delhi, 2023)** — MCA will reject similar names
- **Synarch Ventures** — $82B AUM private equity, aggressive brand protection

### Research Sources
- Perplexity AI: comprehensive global search across trademark databases
- Gemini 3 Pro: detailed legal analysis with MCA/ROC/IP India specifics
- Cross-referenced: USPTO, EUIPO, WIPO Global Brand Database, IP India

## Decision: **SYNARCH**

**Etymology:** syn (together) + arch (rule/govern) = "ruling together"

### Why Synarch Wins
- ✅ **Zero trademark conflicts** in Class 9 (Software) or Class 42 (SaaS/IT) globally
- ✅ **Etymologically perfect** — literally means "orchestrated governance" = multi-agent orchestration
- ✅ **Brandable** — sounds like enterprise infrastructure, not a Greek restaurant
- ✅ **Clean domains available** — synarch.ai, synarch.dev, synarch.in
- ✅ **GitHub available** — github.com/synarch-ai
- ✅ **The "shadow governance" vibe** actually fits agentic AI infrastructure

### Why Others Were Killed
| Name | Status | Reason |
|---|---|---|
| Conclave | ❌ DEAD | Conclave Info System + Conclave Technologies Pvt Ltd (India) exist |
| Tesseract | ❌ RADIOACTIVE | Disney/Marvel + Google's Tesseract OCR engine |
| Praetor | ❌ BLOCKED | Wolters Kluwer has "Praetor AI" for legal tech |
| Archon | ❌ HIGH RISK | Archon Systems exists |
| Synarch | ❌ KILLED | 6+ direct conflicts documented above |

## Impact on Codebase

### What Changes
- Company/project name: Synarch AI → **Synarch** (or Synarch AI)
- GitHub repo: will be renamed or new repo created
- Agent naming convention: The mythology stays (Zeus, Thoth, Hermes etc.) — only the company/project name changes
- The CEO agent remains **"Synarch"** as an internal codename — the AGENT is named Synarch, the COMPANY is Synarch

### What Stays
- All architecture (LangGraph, NATS, litellm, Qdrant, PostgreSQL)
- All agent souls (mythology-based hierarchy)
- All PRD requirements
- The "God → Synarch → C-Suite → Specialists" hierarchy
- The NATS subject namespace can become `synarch.agent.>` or stay `synarch.agent.>`

## Immediate Actions
1. Buy domains: synarch.ai, synarch.dev, synarch.in
2. Secure GitHub org: github.com/synarch-ai
3. MCA name reservation: "Synarch Intelligence Private Limited" or "Synarch Systems Private Limited"
4. File trademark: Class 9 (Software) + Class 42 (IT Services) via IP India
5. Codebase: rename when ready (not urgent — internal codename "synarch" can persist during PoC)

## The "Synarchy of Gods" Model (Antigravity Recommendation — ADOPTED)

| Layer | Name | Rationale |
|---|---|---|
| **Company** | Synarch | Legal entity, trademark, domains |
| **Product** | Synarch Engine | The multi-agent orchestration platform |
| **CEO Agent** | Synarch (renamed from Synarch) | The orchestrator node matches the brand |
| **C-Suite Agents** | Zeus, Thoth, Athena, Odin, Midas, Apollo | Mythology stays — gods inside the machine |
| **Specialist Agents** | Hermes, Hephaestus, Janus, etc. | Mythology stays |
| **User** | God | Unchanged |

**Key Insight (Antigravity):** *"Synarch is the System. The gods are its council."*

### Operation Rename Scope (for next session)
1. `SynarchAgent` class → `SynarchAgent`
2. `src/agents/synarch.py` → `src/agents/synarch.py`
3. `docs/agents/synarch/soul.md` → update name to "Synarch" (keep mythology vibe)
4. NATS subjects: `synarch.agent.>` → `synarch.agent.>`
5. Docker service names: add `synarch-` prefix
6. `package.json` name field
7. Documentation sweep: Synarch → Synarch where referring to company/product

### What Does NOT Change
- Zeus, Thoth, Hermes, Hephaestus, Janus — all keep their names
- God — stays as God
- The hierarchy — unchanged
- All architecture decisions — unchanged

## MOA Object Clause (drafted for CA/CS review)
See the detailed MOA language in the branding research notes — covers AI systems, multi-agent orchestration, SaaS/PaaS/IaaS delivery, and R&D consultancy.

---

*"Synarch: Where agents rule together."*
