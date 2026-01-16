"""
Configure logging to file instead of console to avoid Unicode crashes
"""
import logging
import sys
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress excessive logs
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
