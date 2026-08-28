"""Configuration parameters for data handling and preprocessing.

Follows Technical Interface Contract requirements (Section 3 & Section 4).
"""

from pathlib import Path

# Canonical waste class identifiers in exact required order
CLASS_NAMES = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash",
]

# Image Preprocessing Requirements (Contract Section 4.3)
IMAGE_SIZE = (224, 224)
COLOR_MODE = "RGB"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Default Dataset Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "src" / "data"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data"

# Dataset Splitting Defaults
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42
