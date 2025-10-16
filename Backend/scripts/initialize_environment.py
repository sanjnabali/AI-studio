import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directory(path: str):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {path}")

def initialize_environment():
    """Initialize the environment by creating required directories"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    # Required directories
    directories = [
        project_root / "uploads",
        project_root / "rag_storage" / "chroma_db",
    ]

    # Create directories
    for directory in directories:
        create_directory(str(directory))

    logger.info("Environment initialization completed successfully")

if __name__ == "__main__":
    try:
        initialize_environment()
    except Exception as e:
        logger.error(f"Error initializing environment: {e}")
        sys.exit(1)