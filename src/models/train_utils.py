"""Model serialization and checkpointing utilities.

Adheres to Technical Interface Contract (CONTRACT.md Section 7).
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
# pyrefly: ignore [missing-import]
from src.models.config import CLASS_NAMES, COLOR_MODE, IMAGE_SIZE
from torch import nn


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    path: Union[str, Path],
    best_test_acc: float,
    scaler: Optional[torch.amp.GradScaler] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    architecture: str = "resnet18",
    class_names: Optional[List[str]] = None,
    extra_metadata: Optional[Dict] = None,
):
    """Save full training checkpoint with training state and contract metadata."""
    path = Path(path)
    os.makedirs(path.parent, exist_ok=True)

    classes = class_names or list(CLASS_NAMES)
    checkpoint = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "epoch": epoch,
        "best_test_acc": float(best_test_acc),
        "architecture": architecture,
        "class_names": classes,
        "num_classes": len(classes),
        "image_size": list(IMAGE_SIZE),
        "color_mode": COLOR_MODE,
        "contract_version": "1.0.0",
        "model_version": "0.1.0",
    }
    if scaler is not None:
        checkpoint["scaler_state"] = scaler.state_dict()
    if scheduler is not None:
        checkpoint["scheduler_state"] = scheduler.state_dict()
    if extra_metadata:
        checkpoint["extra_metadata"] = extra_metadata

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    torch.save(checkpoint, tmp_path)
    os.replace(tmp_path, path)


def load_checkpoint(
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    device: Union[torch.device, str],
    path: Union[str, Path],
    scaler: Optional[torch.amp.GradScaler] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
) -> Tuple[nn.Module, Optional[torch.optim.Optimizer], int, float, Dict]:
    """Load model state and training progress from checkpoint.

    Returns:
        (model, optimizer, start_epoch, best_test_acc, metadata_dict)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {path}")

    device_str = str(device)
    checkpoint = torch.load(path, map_location=device_str, weights_only=False)

    model.load_state_dict(checkpoint["model_state"])
    model.to(device)

    if optimizer is not None and "optimizer_state" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state"])

    if scaler is not None and "scaler_state" in checkpoint:
        scaler.load_state_dict(checkpoint["scaler_state"])

    if scheduler is not None and "scheduler_state" in checkpoint:
        scheduler.load_state_dict(checkpoint["scheduler_state"])

    start_epoch = checkpoint.get("epoch", 0) + 1
    best_test_acc = float(checkpoint.get("best_test_acc", 0.0))

    metadata = {
        "architecture": checkpoint.get("architecture", "resnet18"),
        "class_names": checkpoint.get("class_names", list(CLASS_NAMES)),
        "num_classes": checkpoint.get("num_classes", len(CLASS_NAMES)),
        "contract_version": checkpoint.get("contract_version", "1.0.0"),
        "model_version": checkpoint.get("model_version", "0.1.0"),
    }

    return model, optimizer, start_epoch, best_test_acc, metadata


def save_model_artifact(
    model: nn.Module,
    path: Union[str, Path],
    architecture: str = "resnet18",
    class_names: Optional[List[str]] = None,
    best_acc: float = 0.0,
):
    """Save finalized deployable model artifact conforming to CONTRACT.md Section 7."""
    path = Path(path)
    os.makedirs(path.parent, exist_ok=True)
    classes = class_names or list(CLASS_NAMES)

    artifact = {
        "model_state": model.state_dict(),
        "architecture": architecture,
        "class_names": classes,
        "num_classes": len(classes),
        "image_size": list(IMAGE_SIZE),
        "color_mode": COLOR_MODE,
        "contract_version": "1.0.0",
        "model_version": "0.1.0",
        "best_accuracy": float(best_acc),
    }

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    torch.save(artifact, tmp_path)
    os.replace(tmp_path, path)
