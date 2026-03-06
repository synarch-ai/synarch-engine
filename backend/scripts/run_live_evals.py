import asyncio
import json
import logging
from pathlib import Path
from config import Settings
from api.dependencies import get_container
from domain.models.mission import Mission, AuthorityMode
from domain.evals.judge import EvalRunner
from api.app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_evals():
    logger.info("Starting Tier 2 Live Evals...")

    settings = Settings()
    logger.info("Loading golden dataset...")
    dataset_path = Path(__file__).parent.parent / "tests" / "datasets" / "golden_evals.json"
    with open(dataset_path) as f:
        dataset = json.load(f)

    logger.info(f"Loaded {len(dataset)} eval cases.")
    logger.info("This script is intended to run live LangGraph missions against these goals.")

if __name__ == "__main__":
    asyncio.run(run_evals())
