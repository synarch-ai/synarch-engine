# Output Template (Bar-Raiser)

Use this structure for learner-facing `final_notes.md`.

## Header

```markdown
---
title: "<Domain> Class <NN> [DD/MM/YYYY] - <Topic>"
domain: "<Domain>"
tags: [study-guide, bootcamp, <domain-tag>]
type: "tutorial-note"
status: "ready"
---
```

## Mandatory Sections

1. `# 🎓 <Domain> Class <NN> [DD/MM/YYYY] - <Topic>`
2. `## 🧠 Session Focus`
3. `## 🎯 Prerequisites`
4. `## ✅ Learning Outcomes`
5. `## 🧭 Topic Index`
6. `## 🗺️ Conceptual Roadmap` (Mermaid)
7. `## 🏗️ Systems Visualization` (Mermaid)
8. `## 🌆 Skyline Intuition Diagram` (ASCII)
9. `## 📚 Core Concepts (Intuition First)`
10. `## ➗ Mathematical Intuition` (when relevant)
11. `## 💻 Coding Walkthroughs`
12. `## 🚀 Advanced Real-World Scenario`
13. `## 🧩 HOTS (High-Order Thinking)`
14. `## ❓ FAQ`
15. `## 🛠️ Practice Roadmap`
16. `## 🔭 Next Improvements`
17. `## 🔗 Related Notes`
18. `## 🧾 Traceability`

## Concept Block Template

```markdown
### <Concept Name>
**What it is:** ...
**Why it matters:** ...
**Intuition first:** ...
**Common mistake:** ...
**Next improvement:** ...
```

## Code Example Template

```markdown
### <Example Title>
**Why this example:** ...

```<lang>
<code>
```

**What this code is doing:**
- ...
- ...
- ...
```

## Math Intuition Template

```markdown
### <Formula Name>
- Formula: `<expression>`
- Intuition: ...
- Failure mode if misunderstood: ...
```

## Traceability Note Template

```markdown
## 🧾 Traceability
> [!info] Audit Trail
> Learner-facing notes are sanitized for readability.
> Deterministic traceability remains in:
> - `.pipeline/segment_ledger.jsonl`
> - `.pipeline/coverage_matrix.json`
> - `.pipeline/validation_report.md`
> - `.pipeline/topic_inventory.json`
```

## Publish Filename Convention

Also generate a learner-facing published copy:

`<DomainFile> Class <NN> [DD-MM-YYYY] - <Topic>.md`

Where:
- `AI/ML` -> `AI-ML`
- `WebDev` -> `WebDev`
- `Web3` -> `Web3`
