"""Smart Waste Classification - End-to-End Pipeline Runner.

Orchestrates full workflow:
1. Data Validation & Preprocessing (Member 1)
2. Model Initialization & Training (Member 2)
3. Model Evaluation & Performance Reporting (Member 2)
4. Contract-Compliant Inference Smoke Test (CONTRACT.md Section 6)

Usage:
    python src/pipeline.py [--epochs 5] [--batch-size 32] [--model resnet18] [--force-preprocess]
"""

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from PIL import Image

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.config import (
    CLASS_NAMES,
    DEFAULT_ARCHITECTURE,
    DEFAULT_MODEL_PATH,
    METRICS_PATH,
    ModelConfig,
    get_default_device,
)
from src.models.evaluate import evaluate_checkpoint
from src.models.predict import predict
from src.models.train import run_training
from src.preprocessing.config import (
    RANDOM_SEED,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
)
from src.preprocessing.dataset_splitter import build_processed_dataset
from src.preprocessing.validator import scan_dataset


def check_processed_data_ready(data_dir: Path) -> bool:
    """Check if train, validation, and test split directories already exist and contain images."""
    splits = ["train", "validation", "test"]
    for split in splits:
        split_dir = data_dir / split
        if not split_dir.exists() or not split_dir.is_dir():
            return False
        # Check if at least one class directory has files
        has_files = any(
            (split_dir / cls).exists() and any((split_dir / cls).glob("*.jpg"))
            for cls in CLASS_NAMES
        )
        if not has_files:
            return False
    return True


def find_raw_data_dir(project_root: Path, custom_raw_dir: Path = None) -> Path:
    """Locate the directory containing raw class folders."""
    if custom_raw_dir and custom_raw_dir.exists():
        return custom_raw_dir

    candidates = [
        project_root / "data",
        project_root / "src" / "data",
        project_root / "dataset",
        project_root / "raw_data",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            # Check if it contains class subfolders
            has_class_dirs = sum(1 for cls in CLASS_NAMES if (c / cls).exists()) >= 3
            if has_class_dirs:
                return c
    return project_root / "data"


def run_pipeline(
    raw_dir: Path = None,
    data_dir: Path = None,
    model_name: str = DEFAULT_ARCHITECTURE,
    num_epochs: int = 5,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    force_preprocess: bool = False,
    device: str = None,
) -> dict:
    """Execute end-to-end data preprocessing, model training, evaluation, and smoke test."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    root = PROJECT_ROOT
    dest_data_dir = data_dir or (root / "data")
    models_dir = root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("      SMART WASTE CLASSIFICATION - UNIFIED PIPELINE RUNNER      ")
    print("=" * 70)
    print(f"Timestamp        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model Name       : {model_name}")
    print(f"Epochs           : {num_epochs}")
    print(f"Batch Size       : {batch_size}")
    print(f"Learning Rate    : {learning_rate}")
    print(f"Canonical Classes: {CLASS_NAMES}")
    print("-" * 70)

    # -----------------------------------------------------------------------
    # Step 1: Preprocessing & Dataset Preparation (Member 1)
    # -----------------------------------------------------------------------
    print("\n>>> [STEP 1/4] DATA HANDLING & PREPROCESSING...")
    already_processed = check_processed_data_ready(dest_data_dir)

    if already_processed and not force_preprocess:
        print("[OK] Processed train/validation/test splits already exist. Skipping preprocessing.")
    else:
        source_raw = find_raw_data_dir(root, raw_dir)
        print(f"Scanning raw dataset from: {source_raw}")
        valid_files, invalid_files = scan_dataset(source_raw, CLASS_NAMES)

        total_valid = sum(len(f) for f in valid_files.values())
        print(f"Found {total_valid} valid images across {len(CLASS_NAMES)} classes.")

        if total_valid == 0:
            raise RuntimeError(f"No valid images found in {source_raw} to process!")

        print("Building stratified splits into data/train, data/validation, data/test...")
        summary = build_processed_dataset(
            valid_files_by_class=valid_files,
            output_dir=dest_data_dir,
            class_names=CLASS_NAMES,
            train_ratio=TRAIN_RATIO,
            val_ratio=VAL_RATIO,
            test_ratio=TEST_RATIO,
            random_seed=RANDOM_SEED,
        )
        print("[OK] Preprocessing completed successfully.")

    # -----------------------------------------------------------------------
    # Step 2: Model Training (Member 2)
    # -----------------------------------------------------------------------
    print("\n>>> [STEP 2/4] MODEL TRAINING...")
    config = ModelConfig(
        model_name=model_name,
        num_epochs=num_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        data_dir=dest_data_dir,
        train_dir=dest_data_dir / "train",
        val_dir=dest_data_dir / "validation",
        test_dir=dest_data_dir / "test",
        models_dir=models_dir,
        model_save_path=DEFAULT_MODEL_PATH,
        metrics_save_path=METRICS_PATH,
    )

    training_history = run_training(config=config, device=device)
    print("[OK] Model training completed and artifact saved to models/waste_classifier.pth.")

    # -----------------------------------------------------------------------
    # Step 3: Model Evaluation (Member 2)
    # -----------------------------------------------------------------------
    print("\n>>> [STEP 3/4] MODEL EVALUATION...")
    eval_results = evaluate_checkpoint(
        model_path=DEFAULT_MODEL_PATH,
        test_dir=dest_data_dir / "test",
        architecture=model_name,
        batch_size=batch_size,
        device=device,
        output_metrics_path=METRICS_PATH,
    )
    print("[OK] Model evaluation completed and metrics saved to models/eval_metrics.json.")

    # -----------------------------------------------------------------------
    # Step 4: Contract-Compliant Inference Smoke Test
    # -----------------------------------------------------------------------
    print("\n>>> [STEP 4/4] INFERENCE CONTRACT VERIFICATION (CONTRACT.md Section 6)...")
    test_split_dir = dest_data_dir / "test"
    sample_images = list(test_split_dir.glob("*/*.jpg"))
    if not sample_images:
        sample_images = list(test_split_dir.glob("*/*.png"))

    if sample_images:
        sample_img_path = sample_images[0]
        actual_class = sample_img_path.parent.name
        with Image.open(sample_img_path) as img:
            prediction = predict(img, model_path=DEFAULT_MODEL_PATH)

        print(f"Sample Image Path : {sample_img_path}")
        print(f"Actual Class      : {actual_class}")
        print(f"Predicted Output  : {prediction}")

        assert "predicted_class" in prediction, "predict() output missing 'predicted_class'"
        assert "confidence" in prediction, "predict() output missing 'confidence'"
        assert prediction["predicted_class"] in CLASS_NAMES, f"Invalid class: {prediction['predicted_class']}"
        assert 0.0 <= prediction["confidence"] <= 1.0, f"Invalid confidence: {prediction['confidence']}"
        print("[OK] Interface Contract Verification PASSED!")
    else:
        print("[!] No sample test image found for smoke test.")

    print("\n" + "=" * 70)
    print("[SUCCESS] END-TO-END PIPELINE FINISHED SUCCESSFULLY!")
    print("=" * 70)

    return {
        "training_history": training_history,
        "eval_results": eval_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Smart Waste Classification - End-to-End Pipeline")
    parser.add_argument("--model", type=str, default=DEFAULT_ARCHITECTURE, help="Model architecture")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="DataLoader batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--raw-dir", type=Path, default=None, help="Path to raw dataset directory")
    parser.add_argument("--data-dir", type=Path, default=None, help="Path to destination processed data directory")
    parser.add_argument("--force-preprocess", action="store_true", help="Force re-running preprocessing")
    parser.add_argument("--device", type=str, default=None, help="Device to use (cpu, cuda)")
    args = parser.parse_args()

    run_pipeline(
        raw_dir=args.raw_dir,
        data_dir=args.data_dir,
        model_name=args.model,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        force_preprocess=args.force_preprocess,
        device=args.device,
    )


if __name__ == "__main__":
    main()
