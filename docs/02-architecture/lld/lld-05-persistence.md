# LLD-05: Persistence Layer Contract

**Module:** `backend/adapters/postgres/`
**Status:** PROPOSED
**Date:** 2026-02-21
**Author:** Codex (Implementation Mode)

## 1. Overview

The persistence layer provides durable storage for Mission State, LangGraph Checkpoints, and Event Logs. It implements the contracts defined in HLD v2.0 (Persistence Plane) and DB Schema v2.0.

## 2. Components

### 2.1 Repositories

The repositories encapsulate data access logic for specific domain entities. They interact directly with the PostgreSQL database using `asyncpg` (via `databases` or raw connection pool).

**Interface:** `backend/ports/persistence.py` (Abstract Base Classes)
**Implementation:** `backend/adapters/postgres/repositories.py` (Concrete Classes)

#### MissionRepository
- **Responsibility:** Mission metadata lifecycle (create, read, update status).
- **Key Methods:**
    - `create(mission: Mission) -> Mission`
    - `get(mission_id: UUID) -> Optional[Mission]`
    - `update(mission: Mission) -> Mission`
    - `list(limit: int, offset: int) -> List[Mission]`
    - `get_by_thread_id(thread_id: str) -> Optional[Mission]`

#### TaskRepository
- **Responsibility:** Task lifecycle (create, update status, associate with mission).
- **Key Methods:**
    - `create(task: Task) -> Task`
    - `update(task: Task) -> Task`
    - `list_by_mission(mission_id: UUID) -> List[Task]`

#### ApprovalRepository
- **Responsibility:** HITL Approval requests and decisions.
- **Key Methods:**
    - `create(approval: Approval) -> Approval`
    - `update(approval: Approval) -> Approval`
    - `list_pending() -> List[Approval]`
    - `get_by_mission(mission_id: UUID) -> List[Approval]`

#### EventRepository
- **Responsibility:** Immutable log of mission events (MissionEvents table).
- **Key Methods:**
    - `create(event: MissionEvent) -> MissionEvent`
    - `list_by_mission(mission_id: UUID) -> List[MissionEvent]`

### 2.2 LangGraph Checkpointer

The checkpointer allows LangGraph to save and restore execution state.

**Interface:** `langgraph.checkpoint.base.BaseCheckpointSaver`
**Implementation:** `backend/adapters/langgraph/checkpointer.py` (Wraps `AsyncPostgresSaver` or custom implementation).

- **Responsibility:** Persist `StateGraph` snapshots keyed by `thread_id`.
- **Key Methods:**
    - `put(config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata)`
    - `get(config: RunnableConfig) -> Optional[Checkpoint]`
    - `list(config: RunnableConfig) -> Iterator[CheckpointTuple]`

## 3. Database Schema

The schema is defined in `docs/05-data/master-db-schema.md` (v2.0).

**Key Tables:**
- `missions`: Metadata, status, thread_id.
- `checkpoints`: LangGraph state blobs.
- `writes`: LangGraph side-effect tracking.

**Migration Strategy:**
- Use `backend/adapters/postgres/migrations/001_initial.sql` for setup.
- Migrations are applied manually or via script (`python scripts/migrate.py`) at startup.

## 4. Transaction Management

- **Atomicity:** Repository methods should use database transactions where critical (e.g., creating a mission and its initial tasks).
- **Isolation:** Default isolation level (Read Committed) is sufficient.
- **Consistency:** Foreign keys enforce referential integrity between Missions, Tasks, and Approvals.

## 5. Dependency Injection

The repositories and checkpointer are instantiated in `backend/container.py` and injected into the FastAPI application state / dependencies.

**Wiring:**
```python
# backend/container.py
async def create_container(settings: Settings) -> Container:
    pool = await create_pool(settings.database_url)

    return Container(
        mission_repo=PostgresMissionRepository(pool),
        task_repo=PostgresTaskRepository(pool),
        approval_repo=PostgresApprovalRepository(pool),
        event_repo=PostgresEventRepository(pool),
        checkpointer=AsyncPostgresSaver(pool)
    )
```
