# Stage 3 Guide: Enhancement + Packaging

## Inputs

1. `.pipeline/structured_notes.md`
2. `.pipeline/coverage_matrix.json`
3. `.pipeline/topic_inventory.json`

## Outputs

1. `.pipeline/enhanced_notes.md`
2. `final_notes.md`
3. `bootcamp_index.md`

## Non-Negotiable Rules

1. Do not overwrite original lecture meaning.
2. Mark added pedagogical content with `[ENHANCED: ...]`.
3. Keep deterministic traceability in `.pipeline` artifacts.
4. Preserve major timestamp anchors as `<!-- T:HH:MM:SS -->` when available.
5. Apply `references/tutorial-tech-bar-raiser.md` before finalizing.
6. Keep `[source: ...]` tags in `.pipeline/enhanced_notes.md` only.
7. Remove inline `[source: ...]` tags from learner-facing `final_notes.md`.
8. Apply class naming convention in learner-facing title/H1:
   - `<Domain> Class <NN> [DD/MM/YYYY] - <Topic>`
9. Produce learner-facing published filename:
   - `<DomainFile> Class <NN> [DD-MM-YYYY] - <Topic>.md`

## Required Enhancements

1. Topic intro blurbs
2. Tiny-concept clarifications
3. Better examples
4. Misconceptions and corrections
5. HOTS questions
6. FAQ block
7. Mermaid diagrams (preferred)
8. ASCII diagram fallback (when Mermaid is unsuitable)
9. Math-intuition blocks for math-heavy concepts
10. "Next improvement" steps per major concept
11. Emoji headings for learner-facing `final_notes.md`

## Diagram Policy

- Prefer Mermaid for process/relationship visuals.
- Use ASCII only for terminal-friendly or ultra-simple structures.
- Every diagram section should retain nearby source mapping.

## Packaging Guidance

- `.pipeline/enhanced_notes.md`: full fidelity + pedagogy layer.
- `final_notes.md`: learner-first tutorial guide (sanitized readability, emoji headings, intuition-first flow, no inline source tags).
- `<DomainFile> Class <NN> [DD-MM-YYYY] - <Topic>.md`: published learner filename copy.
- `bootcamp_index.md`: cross-lecture links and concept navigation.

Run publisher (after Stage 4 PASS):

```bash
python scripts/publish_tutorial_notes.py --root "<sessions_root>" --session-dir "<session_dir>"
```

## Stage 3 Exit Checklist

- All added content is explicitly marked `[ENHANCED]`.
- No unsupported factual additions.
- Mermaid count and enhanced-claim count are reported.
- Final notes pass bar-raiser checks:
  - tutorial structure present
  - intuition-first concept sections present
  - HOTS + FAQ + practice roadmap present
  - code walkthroughs include purpose + explanation bullets
- published class filename exists and bootcamp index links to it
