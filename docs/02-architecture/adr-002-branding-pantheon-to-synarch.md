# ADR-002: Branding Pivot — Pantheon AI → Synarch
*Architecture Decision Record | 2026-02-13 | Status: DECIDED*

---

## The Problem
"Pantheon AI" has critical trademark conflicts globally:

### Kill-Shot Conflicts (Direct Legal Threats)
- **Pantheon Systems (Pantheon.io)** — massive WebOps platform, strict trademark policy, Class 9 & 42
- **PantheonLab.ai** — Generative AI for digital humans (Asia-based) — exact overlap
- **pantheonai.co** — AI tools for insurance — identical name
- **Pantheon Digital Pvt Ltd (India, Delhi, 2023)** — MCA will reject similar names
- **Pantheon Ventures** — $82B AUM private equity, aggressive brand protection

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
| Pantheon | ❌ KILLED | 6+ direct conflicts documented above |

## Impact on Codebase

### What Changes
- Company/project name: Pantheon AI → **Synarch** (or Synarch AI)
- GitHub repo: will be renamed or new repo created
- Agent naming convention: The mythology stays (Zeus, Thoth, Hermes etc.) — only the company/project name changes
- The CEO agent remains **"Pantheon"** as an internal codename — the AGENT is named Pantheon, the COMPANY is Synarch

### What Stays
- All architecture (LangGraph, NATS, litellm, Qdrant, PostgreSQL)
- All agent souls (mythology-based hierarchy)
- All PRD requirements
- The "God → Pantheon → C-Suite → Specialists" hierarchy
- The NATS subject namespace can become `synarch.agent.>` or stay `pantheon.agent.>`

## Immediate Actions
1. Buy domains: synarch.ai, synarch.dev, synarch.in
2. Secure GitHub org: github.com/synarch-ai
3. MCA name reservation: "Synarch Intelligence Private Limited" or "Synarch Systems Private Limited"
4. File trademark: Class 9 (Software) + Class 42 (IT Services) via IP India
5. Codebase: rename when ready (not urgent — internal codename "pantheon" can persist during PoC)

## MOA Object Clause (drafted for CA/CS review)
See the detailed MOA language in the branding research notes — covers AI systems, multi-agent orchestration, SaaS/PaaS/IaaS delivery, and R&D consultancy.

---

*"Synarch: Where agents rule together."*
