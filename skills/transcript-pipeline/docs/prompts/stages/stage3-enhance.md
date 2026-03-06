# Stage 3 Prompt: Enhance + Package

```text
You are Stage 3 of the transcript pipeline.

Goal:
Enhance structured notes pedagogically while preserving source fidelity, then package learner outputs.

Inputs I will provide:
1) .pipeline/structured_notes.md
2) .pipeline/coverage_matrix.json
3) .pipeline/topic_inventory.json
4) run mode: tool-enabled or tool-restricted
5) tutorial quality bar:
   docs/prompts/references/tutorial-tech-bar-raiser.md

Required behavior:
1) Preserve original teaching points.
2) Mark all added pedagogical content with:
   [ENHANCED: ...]
3) Keep source tags [source: <segment_id>] in `.pipeline/enhanced_notes.md` only.
4) In `final_notes.md`, remove inline `[source: ...]` tags for readability and keep traceability only via `.pipeline/` artifacts.
5) Add enhancements:
   - concise intros per topic
   - intuition builders
   - misconceptions
   - better examples
   - HOTS questions
   - FAQs
   - Mermaid diagrams (primary)
   - ASCII diagrams (optional fallback)
   - emoji heading style for learner-facing final guide
   - math intuition where relevant
   - beginner + advanced coding walkthroughs with explanation bullets
6) Preserve timestamp anchors at major transitions:
   <!-- T:HH:MM:SS -->
7) Apply class-title convention in `final_notes.md` frontmatter + H1:
   <Domain> Class <NN> [DD/MM/YYYY] - <Topic>
8) Create/refresh learner-friendly published file name (in addition to `final_notes.md`):
   <DomainFile> Class <NN> [DD-MM-YYYY] - <Topic>.md

Required outputs:
1) .pipeline/enhanced_notes.md
2) final_notes.md
3) bootcamp_index.md

Rules:
1) No unsupported factual claims.
2) No overwrite of original meaning.
3) Keep final_notes.md learner-friendly while retaining traceability in `.pipeline/`.
4) final_notes.md must satisfy the Tutorial Tech Bar-Raiser structure and exit gate.

Mode handling:
- tool-enabled: write files
- tool-restricted: output as fenced blocks

Checkpoint (must print at end):
Stage 3 Complete:
- [ ] enhanced_notes.md
- [ ] final_notes.md
- [ ] bootcamp_index.md
- [ ] enhanced_claim_count = N
- [ ] mermaid_diagram_count = N

Do not continue to Stage 4. Stop after Stage 3 outputs + checkpoint.
```
