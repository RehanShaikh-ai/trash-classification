# train_loop.py

import os
import shutil
import logging

import torch

from src.models.train import train_one_epoch_amp, test_one_epoch
from src.models.train_utils import load_checkpoint, save_checkpoint


def train(
    resume: bool,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    num_epochs: int,
    device: torch.device,
    train_loader: torch.utils.data.DataLoader,
    test_loader: torch.utils.data.DataLoader,
    latest_path: str,
    best_path: str,
    loss_fn,
    scaler,
    transform=None,
    scheduler=None,
):
    """
    Main training loop for a PyTorch model with support for resuming from checkpoints
    and mixed-precision training.

    Args:
        resume (bool): Whether to resume training from the latest checkpoint.
        model (torch.nn.Module): The model to be trained.
        optimizer (torch.optim.Optimizer): Optimizer for updating model parameters.
        num_epochs (int): Total number of epochs to train.
        device (torch.device): Device to run training on (CPU/GPU).
        train_loader (torch.utils.data.DataLoader): DataLoader for training data.
        test_loader (torch.utils.data.DataLoader): DataLoader for test/validation data.
        latest_path (str): Path to save the latest checkpoint after each epoch.
        best_path (str): Path to save the best-performing model checkpoint.
        loss_fn (callable): Loss function used for training and evaluation.
        scaler (torch.amp.GradScaler): Gradient scaler for mixed-precision training.
        transform (nn.Module, optional): Optional data transform applied to inputs
            before the forward pass.

    Workflow:
        1. Optionally resumes training from the latest checkpoint if available.
        2. Initializes tracking lists for training and testing losses/accuracies.
        3. Iterates through epochs:
            - Trains the model for one epoch using mixed precision.
            - Evaluates the model on the test set.
            - Logs training and testing metrics.
            - Saves the latest checkpoint at the end of each epoch.
            - Copies it to best_path if test accuracy improved this epoch.
        4. Logs final best test accuracy after training completes.
        5. Returns a dictionary containing lists of losses and accuracies for both
           training and testing across all epochs.

    Returns:
        dict: {
            "train_loss": list of training losses per epoch,
            "train_acc": list of training accuracies per epoch,
            "test_loss": list of test losses per epoch,
            "test_acc": list of test accuracies per epoch
        }
    """

    start_epoch = 1
    best_test_acc = 0

    if resume and os.path.exists(latest_path):
        try:
            model, optimizer, start_epoch, best_test_acc = load_checkpoint(
                model, optimizer, device, latest_path, scaler=scaler , scheduler=scheduler
            )

            logging.info(
                f"Resumed from epoch {start_epoch - 1}, best acc: {best_test_acc * 100:.2f}%"
            )

        except Exception:
            logging.exception("⚠ Could not load checkpoint. Starting from scratch.")
            start_epoch = 1
            best_test_acc = 0

    else:
        logging.info("Starting training from scratch...")

    if start_epoch > num_epochs:
        logging.warning(
            f"Resumed epoch ({start_epoch}) is already >= num_epochs ({num_epochs}). "
            "Nothing to train — returning empty metric lists."
        )

    train_losses, train_accs = [], []
    test_losses, test_accs = [], []

    for epoch in range(start_epoch, num_epochs + 1):

        logging.info(f"Epoch {epoch}/{num_epochs}")

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
            model=model, dataloader=test_loader, device=device, loss_fn=loss_fn
        )

        if scheduler is not None:
            if isinstance(scheduler,torch.optim.lr_scheduler.ReduceLROnPlateau):
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
            logging.info(f"Test accuracy improved by {improvement:.2f}%!")
            best_test_acc = test_acc

        save_checkpoint(model, optimizer, epoch, latest_path, best_test_acc, scaler,scheduler=scheduler)

        if improved:
            shutil.copyfile(latest_path, best_path)
            logging.info(f"Best model updated -> {best_path}")

    logging.info(f"Training complete! Best test accuracy: {best_test_acc * 100:.2f}%")

    return {
        "train_loss": train_losses,
        "train_acc": train_accs,
        "test_loss": test_losses,
        "test_acc": test_accs,
    }