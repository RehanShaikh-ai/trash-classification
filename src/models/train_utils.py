import os
import torch
from torch import nn
from typing import Union, Optional


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    path,
    best_test_acc,
    scaler: Optional[torch.amp.GradScaler] = None,
    scheduler=None,
):
    checkpoint = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "epoch": epoch,
        "best_test_acc": best_test_acc,
    }
    if scaler is not None:
        checkpoint["scaler_state"] = scaler.state_dict()
    if scheduler is not None:
        checkpoint["scheduler_state"] = scheduler.state_dict()

    os.makedirs(os.path.dirname(path),exist_ok=True)
    tmp_path = f"{path}.tmp"
    torch.save(checkpoint, tmp_path)
    os.replace(tmp_path, path)


def load_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: Union[torch.device, str],
    path,
    scaler: Optional[torch.amp.GradScaler] = None,
    scheduler=None,
):
    checkpoint = torch.load(path, map_location=device, weights_only=False)

    model.load_state_dict(checkpoint["model_state"])
    model.to(device) 
    optimizer.load_state_dict(checkpoint["optimizer_state"])

    if scaler is not None and "scaler_state" in checkpoint:
        scaler.load_state_dict(checkpoint["scaler_state"])
    if scheduler is not None and "scheduler_state" in checkpoint:
        scheduler.load_state_dict(checkpoint["scheduler_state"])

    start_epoch = checkpoint.get("epoch", 0) + 1
    best_test_acc = checkpoint.get("best_test_acc", 0)

    return model, optimizer, start_epoch, best_test_acc