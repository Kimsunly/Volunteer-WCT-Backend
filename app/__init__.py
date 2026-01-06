"""Package initialization for app - expose `main` for Uvicorn.

This allows running `uvicorn app:main` from project root.
"""

from .main import app as main
from .main import app

__all__ = ["app", "main"]
