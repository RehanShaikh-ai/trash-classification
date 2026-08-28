# train.py

import torch
from torch import nn
from tqdm import tqdm
from typing import Optional ,Union

def train_one_epoch_amp(
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        dataloader: torch.utils.data.DataLoader,
        device: Union[torch.device,str],
        loss_fn,
        scaler: torch.amp.GradScaler,
        transform:Optional[nn.Module]= None,
):
    """
    Train the model for one epoch using Automatic Mixed Precision (AMP) for speed and efficiency.
    
    Args:
        model (nn.Module): The neural network model to train.
        optimizer (torch.optim.Optimizer): Optimizer used for gradient updates.
        dataloader (torch.utils.data.DataLoader): DataLoader for training data.
        device (torch.device or str): Device to train on ("cuda" or "cpu").
        loss_fn: Loss function.
        scaler (torch.amp.GradScaler): GradScaler for AMP.
        transform (nn.Module, optional): Optional data transformation applied on X.
    
    Returns:
        train_acc (float): Training accuracy for the epoch.
        train_loss (float): Average training loss for the epoch.
    """

    model.train()
    running_correct = 0
    running_loss = 0.0
    total_samples = 0

    device_type = "cuda" if torch.device(device).type == "cuda" else "cpu"

    for X , y in tqdm(dataloader,desc="Training"):

        X , y = X.to(device,non_blocking=True) , y.to(device,non_blocking=True)

        if transform:
            X = transform(X)

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast(device_type=device_type):
            y_preds = model(X)
            loss = loss_fn(y_preds,y)
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        batch_size = y.size(0)
        running_loss += loss.item() * batch_size
        y_pred_class = torch.argmax(y_preds,dim=1)
        running_correct += (y_pred_class==y).sum().item()
        total_samples += batch_size

    train_acc = running_correct / total_samples
    train_loss = running_loss / total_samples

    return train_acc , train_loss

def test_one_epoch(
        model: nn.Module,
        dataloader: torch.utils.data.DataLoader,
        device: Union[torch.device, str],
        loss_fn,
):
    """
    Runs one testing epoch and returns accuracy and loss.

    Args:
        model (nn.Module): Trained PyTorch model.
        dataloader (DataLoader): DataLoader for test/validation data.
        device (torch.device or str): Device to run evaluation on.
        loss_fn (nn.Module): Loss function.

    Returns:
        Tuple[float, float]: (accuracy, average_loss)
    """

    model.eval()
    running_loss, running_correct, total_samples = 0.0, 0, 0
    device_type = "cuda" if torch.device(device).type == "cuda" else "cpu"

    with torch.no_grad():
        for X, y in tqdm(dataloader, desc="Testing"):
            X, y = X.to(device, non_blocking=True), y.to(device, non_blocking=True)

            with torch.amp.autocast(device_type=device_type):
                y_preds = model(X)
                loss = loss_fn(y_preds, y)

            y_pred_class = torch.argmax(y_preds, dim=1)
            batch_size = y.size(0)
            running_loss += loss.item() * batch_size
            running_correct += (y_pred_class == y).sum().item()
            total_samples += batch_size

    test_loss = running_loss / total_samples
    test_acc = running_correct / total_samples
    return test_acc, test_loss 
       