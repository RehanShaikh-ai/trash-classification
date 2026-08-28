"""Configuration module for Model and Backend components (Member 2).

Follows Technical Interface Contract requirements (CONTRACT.md Section 3, 5, 6, 7).
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Tuple

import torch

# ---------------------------------------------------------------------------
# Canonical Class Identifiers (Contract Section 3 & 4.4)
# ---------------------------------------------------------------------------
CLASS_NAMES: List[str] = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash",
]

NUM_CLASSES: int = len(CLASS_NAMES)
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: name for idx, name in enumerate(CLASS_NAMES)}

# ---------------------------------------------------------------------------
# Image Preprocessing & Normalization Specs (Contract Section 4.3)
# ---------------------------------------------------------------------------
IMAGE_SIZE: Tuple[int, int] = (224, 224)
COLOR_MODE: str = "RGB"
NORM_MEAN: List[float] = [0.485, 0.456, 0.406]
NORM_STD: List[float] = [0.229, 0.224, 0.225]

# ---------------------------------------------------------------------------
# Default Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR  # Raw dataset folder if not split yet
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "validation"
TEST_DIR = DATA_DIR / "test"

MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "waste_classifier.pth"
BEST_MODEL_PATH = MODELS_DIR / "best_model.pth"
LATEST_CHECKPOINT_PATH = MODELS_DIR / "latest_checkpoint.pth"
METRICS_PATH = MODELS_DIR / "eval_metrics.json"

# Supported Model Architectures
SUPPORTED_ARCHITECTURES = ["resnet18", "mobilenet_v2", "efficientnet_b0"]
DEFAULT_ARCHITECTURE = "resnet18"


def get_default_device() -> torch.device:
    """Return CUDA device if available, otherwise CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class ModelConfig:
    """Model and training configuration dataclass."""

    model_name: str = DEFAULT_ARCHITECTURE
    num_classes: int = NUM_CLASSES
    class_names: List[str] = field(default_factory=lambda: list(CLASS_NAMES))
    image_size: Tuple[int, int] = IMAGE_SIZE
    norm_mean: List[float] = field(default_factory=lambda: list(NORM_MEAN))
    norm_std: List[float] = field(default_factory=lambda: list(NORM_STD))

    # Hyperparameters
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 10
    num_workers: int = 0
    use_amp: bool = True

    # Directories
    data_dir: Path = DATA_DIR
    train_dir: Path = TRAIN_DIR
    val_dir: Path = VAL_DIR
    test_dir: Path = TEST_DIR
    models_dir: Path = MODELS_DIR
    model_save_path: Path = DEFAULT_MODEL_PATH
    metrics_save_path: Path = METRICS_PATH

    random_seed: int = 42

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        data = asdict(self)
        for k, v in data.items():
            if isinstance(v, Path):
                data[k] = str(v)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ModelConfig":
        """Create ModelConfig instance from dictionary."""
        paths = [
            "data_dir",
            "train_dir",
            "val_dir",
            "test_dir",
            "models_dir",
            "model_save_path",
            "metrics_save_path",
        ]
        sanitized = dict(data)
        for p in paths:
            if p in sanitized and isinstance(sanitized[p], str):
                sanitized[p] = Path(sanitized[p])
        if "image_size" in sanitized and isinstance(sanitized["image_size"], list):
            sanitized["image_size"] = tuple(sanitized["image_size"])
        return cls(**sanitized)
