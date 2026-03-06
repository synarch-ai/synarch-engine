import asyncio
import logging
from adapters.postgres.repositories import create_postgres_pool, PostgresMissionRepository
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_worker():
    settings = Settings()
    pool = await create_postgres_pool(settings.database_url)
    repo = PostgresMissionRepository(pool)

    logger.info("Metrics worker started. Refreshing daily_mission_metrics every 5 minutes.")
    try:
        while True:
            logger.info("Refreshing materialized view...")
            try:
                await repo.refresh_daily_metrics()
                logger.info("Refresh successful.")
            except Exception as e:
                logger.error(f"Failed to refresh view: {e}")

            await asyncio.sleep(300)  # 5 minutes
    except asyncio.CancelledError:
        logger.info("Metrics worker shutting down.")
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(run_worker())
