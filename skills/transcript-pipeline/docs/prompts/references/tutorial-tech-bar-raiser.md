# Tutorial Tech Bar-Raiser (Mandatory)

Apply this during Stage 3 before writing `final_notes.md`.

## Output Quality Goal

Produce a **teaching guide**, not a compressed summary.

The learner should get:
1. intuition,
2. formal understanding,
3. practical implementation path,
4. next-step progression.

## Mandatory Structure

1. `# 🎓 <Domain> Class <NN> [DD/MM/YYYY] - <Topic>`
2. `## 🧠 Session Focus`
3. `## 🎯 Prerequisites`
4. `## ✅ Learning Outcomes`
5. `## 🧭 Topic Index`
6. `## 🗺️ Conceptual Roadmap` (Mermaid)
7. `## 🏗️ Systems Visualization` (Mermaid)
8. `## 🌆 Skyline Intuition Diagram` (ASCII)
9. `## 📚 Core Concepts (Intuition First)`
10. `## ➗ Mathematical Intuition` (where relevant)
11. `## 💻 Coding Walkthroughs`
12. `## 🚀 Advanced Real-World Scenario`
13. `## 🧩 HOTS (High-Order Thinking)`
14. `## ❓ FAQ`
15. `## 🛠️ Practice Roadmap`
16. `## 🔭 Next Improvements`
17. `## 🔗 Related Notes`
18. `## 🧾 Traceability`

## Naming Policy (Mandatory)

1. `final_notes.md` must have frontmatter `title` matching the H1 title format.
2. Also create a learner-facing published tutorial filename:
   - `<DomainFile> Class <NN> [DD-MM-YYYY] - <Topic>.md`
3. Domains:
   - `AI/ML` -> `AI-ML` (filename)
   - `WebDev` -> `WebDev`
   - `Web3` -> `Web3`

## Sanitization Policy (Mandatory)

1. Remove inline `[source: <segment_id>]` tags from learner-facing `final_notes.md`.
2. Keep source-traceability in `.pipeline/coverage_matrix.json` and `.pipeline/segment_ledger.jsonl`.
3. Keep optional source-rich content in `.pipeline/enhanced_notes.md` only.

## Concept Policy

Each concept must include:
1. what it is,
2. why it matters,
3. intuition first,
4. common mistake,
5. next improvement.

## Math Policy

If the concept is math-heavy:
1. include formula,
2. explain symbols,
3. explain intuition behind formula behavior.

If not math-heavy:
1. skip forced formulas,
2. use causal/operational explanation.

## Examples Policy

Include:
1. beginner runnable example,
2. real-world application example,
3. advanced extension,
4. bullet explanation of code behavior.

## Diagram Policy

Minimum:
1. Mermaid diagrams >= 2
2. ASCII skyline diagram >= 1

## Exit Gate

Do not finalize Stage 3 unless:
1. all mandatory sections exist,
2. HOTS + FAQ + practice roadmap exist,
3. code walkthroughs are explanatory (not just snippets),
4. guide reads as tutorial, not bullet summary,
5. learner-facing `final_notes.md` has no inline `[source: ...]` tags,
6. class naming convention is applied.
