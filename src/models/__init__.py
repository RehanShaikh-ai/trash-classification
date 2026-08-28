"""Smart Waste Classification - Model and Backend Package (Member 2).

Provides model definitions, training loops, evaluation metrics, and inference interfaces
as specified in CONTRACT.md.
"""

from src.models.config import (
    CLASS_NAMES,
    NUM_CLASSES,
    IMAGE_SIZE,
    COLOR_MODE,
    ModelConfig,
)
from src.models.model import get_model, list_available_models
from src.models.predict import predict, load_inference_model
from src.models.train import run_training
from src.models.train_loop import train
from src.models.evaluate import evaluate_model, evaluate_checkpoint

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
