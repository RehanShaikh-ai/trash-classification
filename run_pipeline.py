"""Root-level shortcut runner for Smart Waste Classification pipeline."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# pyrefly: ignore [missing-import]
from src.pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
