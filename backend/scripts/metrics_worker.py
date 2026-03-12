import asyncio
import logging
import signal
from adapters.postgres.repositories import create_postgres_pool, PostgresMissionRepository
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.shutdown_event = asyncio.Event()

    def handle_shutdown(self):
        logger.info("Shutdown signal received.")
        self.shutdown_event.set()

    async def run_worker(self):
        settings = Settings()
        pool = await create_postgres_pool(settings.database_url)
        repo = PostgresMissionRepository(pool)

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.handle_shutdown)

        logger.info("Metrics worker started. Refreshing daily_mission_metrics every 5 minutes.")
        try:
            while not self.shutdown_event.is_set():
                logger.info("Refreshing materialized view...")
                try:
                    await repo.refresh_daily_metrics()
                    logger.info("Refresh successful.")
                except Exception as e:
                    logger.error(f"Failed to refresh view: {e}")

                try:
                    # Wait for 5 minutes, or until shutdown is requested
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=300)
                except asyncio.TimeoutError:
                    pass # Timeout means 5 mins elapsed without shutdown, which is normal
        finally:
            logger.info("Metrics worker shutting down.")
            await pool.close()

if __name__ == "__main__":
    worker = Worker()
    asyncio.run(worker.run_worker())
