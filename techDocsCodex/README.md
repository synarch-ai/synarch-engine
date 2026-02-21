# techDocsCodex

Master technical constitution directory for Synarch issue execution.

Source baseline:
- /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2, FR-1..FR-86)

## Intended workflow

1. Level 1 (create once): umbrella docs in this directory.
2. Level 2 (per issue): Ralph proposes only deltas against these docs (files touched, SQL migration(s), API/event diffs).

## Master docs (authoritative)

1. docs/02-architecture/hld/synarch-hld.md
2. docs/05-data/master-db-schema.md
3. docs/02-architecture/api-contract.md
4. docs/02-architecture/umbrella-event-catalog.md

## Governance rules

- No in-memory source of truth for mission state.
- Any PR that changes behavior must cite impacted FR(s) and these master docs.
- No breaking API/event/schema changes without explicit version bump and migration plan.
