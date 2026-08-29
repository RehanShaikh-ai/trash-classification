"""Dataset splitting and directory structure generator module.
Performs stratified train/validation/test splitting for dataset structure.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from sklearn.model_selection import train_test_split

from .config import (
    CLASS_NAMES,
    COLOR_MODE,
    IMAGE_SIZE,
    PROCESSED_DATA_DIR,
    RANDOM_SEED,
    TEST_RATIO,
    TRAIN_RATIO,
    VAL_RATIO,
)
from .preprocessor import process_image


def split_class_files(
    files: List[Path],
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    random_seed: int = RANDOM_SEED,
) -> Dict[str, List[Path]]:
    """Split a list of file paths for a single class into train, validation, and test sets.

    Args:
        files: List of image file paths for a class.
        train_ratio: Proportion for training set (default 0.70).
        val_ratio: Proportion for validation set (default 0.15).
        test_ratio: Proportion for test set (default 0.15).
        random_seed: Random seed for reproducibility.

    Returns:
        Dictionary mapping split names ('train', 'validation', 'test') to lists of file paths.
    """
    total_ratio = train_ratio + val_ratio + test_ratio
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Split ratios must sum to 1.0, got {total_ratio}")

    if len(files) == 0:
        return {"train": [], "validation": [], "test": []}

    # First split off train
    train_files, temp_files = train_test_split(
        files,
        train_size=train_ratio,
        random_state=random_seed,
        shuffle=True,
    )

    # Calculate relative validation ratio for remaining files
    remaining_ratio = val_ratio + test_ratio
    val_relative_ratio = val_ratio / remaining_ratio

    if len(temp_files) > 1:
        val_files, test_files = train_test_split(
            temp_files,
            train_size=val_relative_ratio,
            random_state=random_seed,
            shuffle=True,
        )
    elif len(temp_files) == 1:
        val_files = temp_files
        test_files = []
    else:
        val_files = []
        test_files = []

    return {
        "train": train_files,
        "validation": val_files,
        "test": test_files,
    }


def build_processed_dataset(
    valid_files_by_class: Dict[str, List[Path]],
    output_dir: Path = PROCESSED_DATA_DIR,
    class_names: List[str] = CLASS_NAMES,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    random_seed: int = RANDOM_SEED,
) -> Dict:
    """Process and save dataset into structured tree: data/{train,val,test}/{class}/.

    Also outputs dataset_info.json metadata file.

    Returns:
        Summary dict containing counts and dataset metadata.
    """
    splits = ["train", "validation", "test"]

    # Ensure output directory structure exists
    for split in splits:
        for cls_name in class_names:
            (output_dir / split / cls_name).mkdir(parents=True, exist_ok=True)

    summary = {
        "contract_version": "1.0.0",
        "class_names": class_names,
        "class_to_idx": {cls_name: i for i, cls_name in enumerate(class_names)},
        "preprocessing": {
            "image_size": list(IMAGE_SIZE),
            "color_mode": COLOR_MODE,
            "format": "JPEG",
        },
        "splits": {
            "train": {cls: 0 for cls in class_names},
            "validation": {cls: 0 for cls in class_names},
            "test": {cls: 0 for cls in class_names},
        },
        "total_images": 0,
        "created_at": datetime.now().isoformat(),
    }

    for cls_name in class_names:
        files = valid_files_by_class.get(cls_name, [])
        class_splits = split_class_files(
            files,
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio,
            random_seed=random_seed,
        )

        for split_name, split_files in class_splits.items():
            for src_path in split_files:
                dest_filename = f"{src_path.stem}.jpg"
                dest_path = output_dir / split_name / cls_name / dest_filename
                process_image(src_path, dest_path, target_size=IMAGE_SIZE, color_mode=COLOR_MODE)
                summary["splits"][split_name][cls_name] += 1
                summary["total_images"] += 1

    # Save dataset_info.json metadata file
    metadata_path = output_dir / "dataset_info.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
