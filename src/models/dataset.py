"""Dataset and DataLoader utilities for model training and evaluation.

Adheres to CONTRACT.md Section 3 (Canonical Classes) and Section 4 (Data Handling Contract).
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.models.config import (
    CLASS_NAMES,
    CLASS_TO_IDX,
    IMAGE_SIZE,
    NORM_MEAN,
    NORM_STD,
    TRAIN_DIR,
    VAL_DIR,
    TEST_DIR,
)


def get_train_transforms(
    image_size: Tuple[int, int] = IMAGE_SIZE,
    mean: List[float] = NORM_MEAN,
    std: List[float] = NORM_STD,
) -> transforms.Compose:
    """Return data transformations and augmentations for training data."""
    return transforms.Compose(
        [
            transforms.Resize(image_size),
            transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )


def get_eval_transforms(
    image_size: Tuple[int, int] = IMAGE_SIZE,
    mean: List[float] = NORM_MEAN,
    std: List[float] = NORM_STD,
) -> transforms.Compose:
    """Return deterministic data transformations for validation/testing."""
    return transforms.Compose(
        [
            transforms.Resize(image_size),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )


class ContractImageFolder(datasets.ImageFolder):
    """ImageFolder wrapper enforcing canonical class ordering from CONTRACT.md."""

    def __init__(self, root: Union[str, Path], transform=None, target_transform=None):
        super().__init__(str(root), transform=transform, target_transform=target_transform)

    def find_classes(self, directory: str) -> Tuple[List[str], Dict[str, int]]:
        """Override class discovery to enforce exact canonical class indices."""
        classes = list(CLASS_NAMES)
        class_to_idx = dict(CLASS_TO_IDX)
        # Check that directories exist
        root_path = Path(directory)
        existing_dirs = {d.name for d in root_path.iterdir() if d.is_dir()}
        
        # Filter to only existing classes if subset (e.g. during minimal testing), but preserve canonical indices
        active_classes = [c for c in classes if c in existing_dirs]
        return active_classes, class_to_idx


def get_dataloaders(
    train_dir: Union[str, Path] = TRAIN_DIR,
    val_dir: Optional[Union[str, Path]] = VAL_DIR,
    test_dir: Optional[Union[str, Path]] = TEST_DIR,
    batch_size: int = 32,
    num_workers: int = 0,
    image_size: Tuple[int, int] = IMAGE_SIZE,
) -> Dict[str, Optional[DataLoader]]:
    """Build and return train, validation, and test DataLoaders.

    Args:
        train_dir: Path to training images directory (data/train).
        val_dir: Path to validation images directory (data/validation).
        test_dir: Path to test images directory (data/test).
        batch_size: Batch size for loaders.
        num_workers: DataLoader worker count.
        image_size: Target image dimensions (height, width).

    Returns:
        Dict mapping split names ('train', 'validation', 'test') to DataLoader objects.
    """
    train_tf = get_train_transforms(image_size=image_size)
    eval_tf = get_eval_transforms(image_size=image_size)

    loaders: Dict[str, Optional[DataLoader]] = {
        "train": None,
        "validation": None,
        "test": None,
    }

    train_path = Path(train_dir)
    if train_path.exists() and any(train_path.iterdir()):
        train_dataset = ContractImageFolder(root=train_path, transform=train_tf)
        loaders["train"] = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )

    if val_dir:
        val_path = Path(val_dir)
        if val_path.exists() and any(val_path.iterdir()):
            val_dataset = ContractImageFolder(root=val_path, transform=eval_tf)
            loaders["validation"] = DataLoader(
                val_dataset,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers,
                pin_memory=torch.cuda.is_available(),
            )

    if test_dir:
        test_path = Path(test_dir)
        if test_path.exists() and any(test_path.iterdir()):
            test_dataset = ContractImageFolder(root=test_path, transform=eval_tf)
            loaders["test"] = DataLoader(
                test_dataset,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers,
                pin_memory=torch.cuda.is_available(),
            )

    return loaders
