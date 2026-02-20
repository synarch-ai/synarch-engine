# Synarch Engine — Workspace Rules (NON-NEGOTIABLE)

## SKILL ENFORCEMENT (MANDATORY)

**Before ANY work, you MUST load the relevant skill(s). No exceptions.**

### Skill Selection Matrix

| Task Type | Required Skill(s) | Load Before |
|---|---|---|
| Backend code (Python) | `backend-pe`, `clean-code` | Writing any .py file |
| Architecture decisions | `architecture`, `sequential-thinking` | Making any design choice |
| New feature/component | `brainstorming` | Writing ANY creative code |
| Bug fixing | `systematic-debugging` | Proposing any fix |
| Code review | `code-review-checklist` | Reviewing any code |
| Database work | `database-design`, `backend-pe` | Schema or query changes |
| Frontend code | `frontend-pe` or `ultrathink-frontend` | Writing any .tsx/.css |
| UI/UX design | `ui-ux-pro-max`, `frontend-design` | Design decisions |
| API design | `api-patterns` | Endpoint design |
| Testing | `testing-patterns`, `tdd-workflow` | Writing tests |
| Diagrams | `mermaid-diagrams` | Creating any diagram |
| Security | `security-best-practices` | Security-related code |
| Deployment | `deployment-procedures` | Deploy config changes |
| Documentation | `documentation-templates` | Writing docs |
| Complex reasoning | `sequential-thinking` | Multi-step analysis |
| Planning | `plan-writing`, `writing-plans` | Task decomposition |

### VIOLATION = REJECTION
If Codex or any reviewer finds code written without the relevant skill loaded, the work is considered **sloppy** and must be redone.

---

## PRE-COMMIT WORKFLOW (MANDATORY)

Every time before committing, execute this exact sequence:

1. `git add .`
2. `npx ai-review quick` → generates `AI_REVIEW.md`
3. Review `AI_REVIEW.md` using `code-review-checklist` skill
4. Check ALL files for cross-file consistency (ports, paths, names, contracts)
5. Fix any issues found
6. Present changes to God for approval
7. Only commit after explicit "go" from God

**NEVER commit without God's approval.**
**NEVER skip the ai-review step.**

---

## CROSS-FILE CONSISTENCY CHECKS (MANDATORY)

Before every commit, verify:
- [ ] All port numbers match across: `config.py`, `.env.example`, `docker-compose.yml`, `moveforward_final.md`
- [ ] All abstract port interfaces have implementations for every method
- [ ] All lifecycle methods (setup/close) are called in container bootstrap/shutdown
- [ ] No `hasattr` hacks — use typed port contracts
- [ ] No broken symlinks or references to non-existent files
- [ ] Runbook commands actually work on the current system

---

## PROJECT CONTEXT

- **Project:** Synarch Engine — Autonomous Multi-Agent Orchestration Engine
- **Architecture:** Modular Monolith, Hexagonal (Ports & Adapters) — ADR-005
- **PRD:** `docs/01-requirements/prd-1.0-final.md` (FR-1 to FR-44)
- **Master Plan:** `moveforward_final.md` (Phase 0-5)
- **Memory Bank:** `memory-bank/` (read at session start)
- **Three Planes:** Control (LangGraph) | Observation (NATS) | Persistence (PostgreSQL)
- **Design System:** V3 Cyber-Sovereign Industrialism (LOCKED)

---

## KEY RULES

1. **No commits without God's explicit "go"**
2. **Load skills before ANY work**
3. **Run ai-review before ANY commit**
4. **Check cross-file consistency before ANY commit**
5. **Update memory-bank after every significant change**
6. **Use conventional commits** (✨ feat, 🐛 fix, 📝 docs, ✅ test, 🔧 chore)
7. **Domain layer imports NOTHING from adapters or api**
8. **NATS is observation plane — NEVER control plane**
9. **litellm for ALL model calls — never raw SDK**
10. **Every FR change must trace to PRD and traceability matrix**
