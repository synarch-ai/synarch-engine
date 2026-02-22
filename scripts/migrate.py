import asyncio
import os
import sys

# Add backend to path so we can import config
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from config import get_settings
import asyncpg

async def run_migrations():
    try:
        settings = get_settings()
    except Exception as e:
        print(f"Failed to load settings: {e}")
        # Fallback for CI/Testing where config might not be importable if deps missing
        # But we are in dev environment.
        return

    print(f"Connecting to {settings.database_url}...")

    try:
        conn = await asyncpg.connect(settings.database_url)
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        sys.exit(1)

    try:
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "../backend/adapters/postgres/migrations/001_initial.sql"
        )

        if not os.path.exists(migration_path):
             print(f"Migration file not found at {migration_path}")
             sys.exit(1)

        with open(migration_path, "r") as f:
            sql = f.read()

        print("Applying migration 001_initial.sql...")
        await conn.execute(sql)
        print("Migration applied successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migrations())
