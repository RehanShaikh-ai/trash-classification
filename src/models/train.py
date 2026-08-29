"""Training pipeline execution and epoch runners.

Follows Technical Interface Contract (CONTRACT.md Section 5 & 7).
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
from src.models.config import (
    DEFAULT_ARCHITECTURE,
    LATEST_CHECKPOINT_PATH,
    ModelConfig,
    get_default_device,
)
from src.models.dataset import get_dataloaders
from src.models.model import get_model
from torch import nn
from tqdm import tqdm


def train_one_epoch_amp(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    dataloader: torch.utils.data.DataLoader,
    device: Union[torch.device, str],
    loss_fn: nn.Module,
    scaler: Optional[torch.amp.GradScaler] = None,
    transform: Optional[nn.Module] = None,
) -> Tuple[float, float]:
    """Train model for one epoch using Automatic Mixed Precision (AMP) if enabled.

    Returns:
        (train_acc, train_loss)
    """
    model.train()
    running_correct = 0
    running_loss = 0.0
    total_samples = 0

    device_obj = torch.device(device)
    device_type = "cuda" if device_obj.type == "cuda" else "cpu"
    use_autocast = device_type == "cuda"

    for X, y in tqdm(dataloader, desc="Training", leave=False):
        X, y = X.to(device_obj, non_blocking=True), y.to(device_obj, non_blocking=True)

        if transform:
            X = transform(X)

        optimizer.zero_grad(set_to_none=True)

        if use_autocast:
            with torch.amp.autocast(device_type=device_type):
                y_preds = model(X)
                loss = loss_fn(y_preds, y)
        else:
            y_preds = model(X)
            loss = loss_fn(y_preds, y)

        if scaler is not None and scaler.is_enabled():
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        batch_size = y.size(0)
        running_loss += loss.item() * batch_size
        y_pred_class = torch.argmax(y_preds, dim=1)
        running_correct += (y_pred_class == y).sum().item()
        total_samples += batch_size

    train_acc = running_correct / max(total_samples, 1)
    train_loss = running_loss / max(total_samples, 1)

    return train_acc, train_loss


def test_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: Union[torch.device, str],
    loss_fn: nn.Module,
) -> Tuple[float, float]:
    """Evaluate model on evaluation/test dataset for one epoch.

    Returns:
        (test_acc, test_loss)
    """
    model.eval()
    running_loss, running_correct, total_samples = 0.0, 0, 0
    device_obj = torch.device(device)
    device_type = "cuda" if device_obj.type == "cuda" else "cpu"
    use_autocast = device_type == "cuda"

    with torch.no_grad():
        for X, y in tqdm(dataloader, desc="Testing", leave=False):
            X, y = X.to(device_obj, non_blocking=True), y.to(device_obj, non_blocking=True)

            if use_autocast:
                with torch.amp.autocast(device_type=device_type):
                    y_preds = model(X)
                    loss = loss_fn(y_preds, y)
            else:
                y_preds = model(X)
                loss = loss_fn(y_preds, y)

            y_pred_class = torch.argmax(y_preds, dim=1)
            batch_size = y.size(0)
            running_loss += loss.item() * batch_size
            running_correct += (y_pred_class == y).sum().item()
            total_samples += batch_size

    test_loss = running_loss / max(total_samples, 1)
    test_acc = running_correct / max(total_samples, 1)
    return test_acc, test_loss


def run_training(
    config: Optional[ModelConfig] = None,
    resume: bool = False,
    device: Optional[Union[torch.device, str]] = None,
) -> Dict[str, List[float]]:
    """Configure, initialize, and execute the full training workflow.

    Args:
        config: Model and training configuration instance.
        resume: Whether to resume from latest checkpoint if present.
        device: Target execution device.

    Returns:
        Dictionary of loss and accuracy history lists.
    """
    if config is None:
        config = ModelConfig()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    target_device = device or get_default_device()
    logging.info(f"Target Device: {target_device}")
    logging.info(f"Architecture: {config.model_name}")
    logging.info(
        f"Epochs: {config.num_epochs} | Batch: {config.batch_size} | LR: {config.learning_rate}"
    )

    # Build DataLoaders
    loaders = get_dataloaders(
        train_dir=config.train_dir,
        val_dir=config.val_dir,
        test_dir=config.test_dir,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        image_size=config.image_size,
    )

    train_loader = loaders["train"]
    eval_loader = loaders["validation"] or loaders["test"]

    if train_loader is None or len(train_loader) == 0:
        raise ValueError(
            f"No training data found in '{config.train_dir}'. "
            "Please ensure preprocessing has been executed first."
        )

    if eval_loader is None or len(eval_loader) == 0:
        raise ValueError(
            f"No validation/test data found in '{config.val_dir}'. "
            "Please ensure preprocessing has been executed first."
        )

    # Initialize model
    model = get_model(
        name=config.model_name,
        num_classes=config.num_classes,
        device=target_device,
        pretrained=True,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=2
    )

    loss_fn = nn.CrossEntropyLoss()

    is_cuda = torch.device(target_device).type == "cuda"
    scaler = torch.amp.GradScaler(device="cuda", enabled=config.use_amp and is_cuda)

    # Avoid circular import at module load
    from src.models.train_loop import train

    history = train(
        resume=resume,
        model=model,
        optimizer=optimizer,
        num_epochs=config.num_epochs,
        device=target_device,
        train_loader=train_loader,
        test_loader=eval_loader,
        latest_path=LATEST_CHECKPOINT_PATH,
        best_path=config.model_save_path,
        loss_fn=loss_fn,
        scaler=scaler,
        scheduler=scheduler,
        architecture=config.model_name,
        class_names=config.class_names,
    )

    return history


def main():
    parser = argparse.ArgumentParser(
        description="Smart Waste Classification - Model Training Pipeline"
    )
    parser.add_argument(
        "--model", type=str, default=DEFAULT_ARCHITECTURE, help="Model architecture"
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="DataLoader batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument(
        "--data-dir", type=Path, default=None, help="Root directory containing split datasets"
    )
    parser.add_argument("--resume", action="store_true", help="Resume from latest checkpoint")
    args = parser.parse_args()

    config = ModelConfig(
        model_name=args.model,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
    if args.data_dir:
        config.data_dir = args.data_dir
        config.train_dir = args.data_dir / "train"
        config.val_dir = args.data_dir / "validation"
        config.test_dir = args.data_dir / "test"

    run_training(config=config, resume=args.resume)


if __name__ == "__main__":
    main()
