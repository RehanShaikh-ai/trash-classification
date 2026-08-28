"""Training loop orchestrator for model training.

Supports resuming, mixed precision, lr scheduling, and contract artifact export.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch
from src.models.config import CLASS_NAMES
from src.models.train import test_one_epoch, train_one_epoch_amp
from src.models.train_utils import load_checkpoint, save_checkpoint, save_model_artifact
from torch import nn


def train(
    resume: bool,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    num_epochs: int,
    device: Union[torch.device, str],
    train_loader: torch.utils.data.DataLoader,
    test_loader: torch.utils.data.DataLoader,
    latest_path: Union[str, Path],
    best_path: Union[str, Path],
    loss_fn: nn.Module,
    scaler: Optional[torch.amp.GradScaler] = None,
    transform: Optional[nn.Module] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    architecture: str = "resnet18",
    class_names: Optional[List[str]] = None,
) -> Dict[str, List[float]]:
    """Main training loop for a PyTorch model with checkpointing and mixed-precision.

    Args:
        resume: Whether to resume training from latest checkpoint.
        model: Model instance.
        optimizer: Optimizer.
        num_epochs: Total epochs to train.
        device: Device to train on.
        train_loader: Training DataLoader.
        test_loader: Test or validation DataLoader.
        latest_path: Path to save latest checkpoint.
        best_path: Path to save best model checkpoint.
        loss_fn: Loss function.
        scaler: GradScaler for mixed precision (optional).
        transform: Optional data transform applied before forward pass.
        scheduler: Optional learning rate scheduler.
        architecture: Model architecture name for metadata.
        class_names: Canonical class names list.

    Returns:
        dict: {"train_loss": [...], "train_acc": [...], "test_loss": [...], "test_acc": [...]}
    """
    classes = class_names or list(CLASS_NAMES)
    start_epoch = 1
    best_test_acc = 0.0

    latest_path = Path(latest_path)
    best_path = Path(best_path)

    if resume and latest_path.exists():
        try:
            model, optimizer, start_epoch, best_test_acc, _ = load_checkpoint(
                model=model,
                optimizer=optimizer,
                device=device,
                path=latest_path,
                scaler=scaler,
                scheduler=scheduler,
            )
            logging.info(
                f"Resumed from epoch {start_epoch - 1}, best acc: {best_test_acc * 100:.2f}%"
            )
        except Exception:
            logging.exception("[!] Could not load checkpoint. Starting from scratch.")
            start_epoch = 1
            best_test_acc = 0.0
    else:
        logging.info("Starting training from scratch...")

    if start_epoch > num_epochs:
        logging.warning(
            f"Resumed epoch ({start_epoch}) > num_epochs ({num_epochs}). Nothing to train."
        )

    train_losses, train_accs = [], []
    test_losses, test_accs = [], []

    for epoch in range(start_epoch, num_epochs + 1):
        logging.info(f"\n--- Epoch {epoch}/{num_epochs} ---")

        train_acc, train_loss = train_one_epoch_amp(
            model=model,
            optimizer=optimizer,
            dataloader=train_loader,
            device=device,
            loss_fn=loss_fn,
            scaler=scaler,
            transform=transform,
        )

        test_acc, test_loss = test_one_epoch(
            model=model,
            dataloader=test_loader,
            device=device,
            loss_fn=loss_fn,
        )

        if scheduler is not None:
            if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(test_loss)
            else:
                scheduler.step()

        train_losses.append(train_loss)
        train_accs.append(train_acc)
        test_losses.append(test_loss)
        test_accs.append(test_acc)

        logging.info(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc * 100:.2f}%")
        logging.info(f"Test Loss:  {test_loss:.4f} | Test Acc:  {test_acc * 100:.2f}%")

        improved = test_acc > best_test_acc
        if improved:
            improvement = (test_acc - best_test_acc) * 100
            logging.info(
                f"[+] Test accuracy improved: +{improvement:.2f}% (Best: {test_acc * 100:.2f}%)"
            )
            best_test_acc = test_acc

        save_checkpoint(
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            path=latest_path,
            best_test_acc=best_test_acc,
            scaler=scaler,
            scheduler=scheduler,
            architecture=architecture,
            class_names=classes,
        )

        if improved:
            shutil.copyfile(latest_path, best_path)
            logging.info(f"Saved best checkpoint -> {best_path}")

    logging.info(f"\nTraining complete! Best test accuracy: {best_test_acc * 100:.2f}%")

    # Always ensure best artifact is saved
    if best_path.exists():
        save_model_artifact(
            model=model,
            path=best_path,
            architecture=architecture,
            class_names=classes,
            best_acc=best_test_acc,
        )

    return {
        "train_loss": train_losses,
        "train_acc": train_accs,
        "test_loss": test_losses,
        "test_acc": test_accs,
    }
