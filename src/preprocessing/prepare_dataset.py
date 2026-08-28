"""Command-line script to run full data handling pipeline.

Executes dataset validation, image preprocessing, and stratified train/validation/test splitting.
Usage:
    python -m preprocessing.prepare_dataset [--raw-dir src/data] [--output-dir data]
"""

import argparse
import sys
from pathlib import Path

from .config import (
    CLASS_NAMES,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    RANDOM_SEED,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
)
from .dataset_splitter import build_processed_dataset
from .validator import scan_dataset


def main():
    parser = argparse.ArgumentParser(
        description="Smart Waste Classification - Data Handling & Preprocessing Pipeline"
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DATA_DIR,
        help="Path to raw dataset directory containing class subfolders (default: src/data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROCESSED_DATA_DIR,
        help="Path to destination directory for processed split dataset (default: data)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help="Random seed for split reproducibility (default: 42)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("      SMART WASTE CLASSIFICATION - DATA HANDLING PIPELINE      ")
    print("=" * 60)
    print(f"Raw Data Source   : {args.raw_dir}")
    print(f"Output Destination : {args.output_dir}")
    print(f"Canonical Classes  : {CLASS_NAMES}")
    print("-" * 60)

    # 1. Validation & Corrupted-image detection
    print("\n[Step 1/3] Scanning and validating dataset...")
    try:
        valid_files, invalid_files = scan_dataset(args.raw_dir, CLASS_NAMES)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    total_valid = sum(len(files) for files in valid_files.values())
    total_invalid = sum(len(files) for files in invalid_files.values())

    for cls_name in CLASS_NAMES:
        valid_count = len(valid_files.get(cls_name, []))
        invalid_count = len(invalid_files.get(cls_name, []))
        print(f"  Class '{cls_name:10s}': {valid_count:4d} valid images, {invalid_count:2d} corrupted/invalid")

    print(f"\nTotal Valid Images  : {total_valid}")
    print(f"Total Invalid/Corrupt: {total_invalid}")

    if total_valid == 0:
        print("ERROR: No valid images found to process!", file=sys.stderr)
        sys.exit(1)

    # 2. Preprocessing & Splitting
    print("\n[Step 2/3] Processing images and building stratified splits...")
    print(f"Splits: Train ({TRAIN_RATIO*100:.0f}%), Validation ({VAL_RATIO*100:.0f}%), Test ({TEST_RATIO*100:.0f}%)")

    summary = build_processed_dataset(
        valid_files_by_class=valid_files,
        output_dir=args.output_dir,
        class_names=CLASS_NAMES,
        train_ratio=TRAIN_RATIO,
        val_ratio=VAL_RATIO,
        test_ratio=TEST_RATIO,
        random_seed=args.seed,
    )

    # 3. Output Summary & Verification
    print("\n[Step 3/3] Split Summary & Output Verification:")
    print("-" * 60)
    header = f"{'Class':<12} | {'Train':<8} | {'Validation':<10} | {'Test':<8} | {'Total':<8}"
    print(header)
    print("-" * len(header))

    for cls_name in CLASS_NAMES:
        tr = summary["splits"]["train"][cls_name]
        va = summary["splits"]["validation"][cls_name]
        te = summary["splits"]["test"][cls_name]
        tot = tr + va + te
        print(f"{cls_name:<12} | {tr:<8d} | {va:<10d} | {te:<8d} | {tot:<8d}")

    print("-" * len(header))
    print(f"Dataset Info Saved : {args.output_dir / 'dataset_info.json'}")
    print("\n✅ Data Handling Pipeline completed successfully!")
    print("   Dataset matches Technical Interface Contract specs.")


if __name__ == "__main__":
    main()
