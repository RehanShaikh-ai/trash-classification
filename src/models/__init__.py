"""Smart Waste Classification - Model and Backend Package (Member 2).

Provides model definitions, training loops, evaluation metrics, and inference interfaces
as specified in CONTRACT.md.
"""

# pyrefly: ignore [missing-import]
from src.models.config import (
    CLASS_NAMES,
    COLOR_MODE,
    IMAGE_SIZE,
    NUM_CLASSES,
    ModelConfig,
)
# pyrefly: ignore [missing-import]
from src.models.evaluate import evaluate_checkpoint, evaluate_model
# pyrefly: ignore [missing-import]
from src.models.model import get_model, list_available_models
# pyrefly: ignore [missing-import]
from src.models.predict import load_inference_model, predict
# pyrefly: ignore [missing-import]
from src.models.train import run_training
# pyrefly: ignore [missing-import]
from src.models.train_loop import train

__all__ = [
    "CLASS_NAMES",
    "NUM_CLASSES",
    "IMAGE_SIZE",
    "COLOR_MODE",
    "ModelConfig",
    "get_model",
    "list_available_models",
    "predict",
    "load_inference_model",
    "run_training",
    "train",
    "evaluate_model",
    "evaluate_checkpoint",
]
