"""Model evaluation module for evaluating performance on test/validation data.

Follows Technical Interface Contract (CONTRACT.md Section 5.1 & Section 18).
"""

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import torch
from torch import nn
from tqdm import tqdm

from src.models.config import (
    CLASS_NAMES,
    DEFAULT_ARCHITECTURE,
    DEFAULT_MODEL_PATH,
    METRICS_PATH,
    NUM_CLASSES,
    TEST_DIR,
    get_default_device,
)
from src.models.dataset import get_eval_transforms, ContractImageFolder
from src.models.model import get_model


def evaluate_model(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: Union[torch.device, str],
    loss_fn: Optional[nn.Module] = None,
    class_names: List[str] = CLASS_NAMES,
) -> Dict:
    """Run full evaluation on a dataset and compute comprehensive performance metrics.

    Args:
        model: Trained PyTorch classification model.
        dataloader: DataLoader containing evaluation/test dataset.
        device: Device to run inference on.
        loss_fn: Optional loss function to compute test loss.
        class_names: List of canonical class names.

    Returns:
        Dict containing accuracy, loss, classification report metrics, and confusion matrix.
    """
    model.eval()
    device_obj = torch.device(device)
    model.to(device_obj)

    all_preds: List[int] = []
    all_targets: List[int] = []
    all_confs: List[float] = []
    total_loss = 0.0
    total_samples = 0

    if loss_fn is None:
        loss_fn = nn.CrossEntropyLoss()

    with torch.no_grad():
        for X, y in tqdm(dataloader, desc="Evaluating", leave=False):
            X, y = X.to(device_obj, non_blocking=True), y.to(device_obj, non_blocking=True)
            outputs = model(X)
            loss = loss_fn(outputs, y)

            probs = torch.softmax(outputs, dim=1)
            confs, preds = torch.max(probs, dim=1)

            batch_size = y.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(y.cpu().numpy().tolist())
            all_confs.extend(confs.cpu().numpy().tolist())

    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)

    total_samples = max(len(y_true), 1)
    overall_acc = float((y_true == y_pred).sum() / total_samples)
    avg_loss = float(total_loss / total_samples)
    avg_confidence = float(np.mean(all_confs)) if all_confs else 0.0

    # Ensure all target classes are represented in report
    labels = list(range(len(class_names)))
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    report_str = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    # Per-class metrics
    per_class = {}
    for cls_name in class_names:
        if cls_name in report_dict:
            per_class[cls_name] = {
                "precision": round(report_dict[cls_name]["precision"], 4),
                "recall": round(report_dict[cls_name]["recall"], 4),
                "f1_score": round(report_dict[cls_name]["f1-score"], 4),
                "support": int(report_dict[cls_name]["support"]),
            }

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": total_samples,
        "overall_accuracy": round(overall_acc, 4),
        "average_loss": round(avg_loss, 4),
        "average_confidence": round(avg_confidence, 4),
        "macro_avg": {
            "precision": round(report_dict["macro avg"]["precision"], 4),
            "recall": round(report_dict["macro avg"]["recall"], 4),
            "f1_score": round(report_dict["macro avg"]["f1-score"], 4),
        },
        "weighted_avg": {
            "precision": round(report_dict["weighted avg"]["precision"], 4),
            "recall": round(report_dict["weighted avg"]["recall"], 4),
            "f1_score": round(report_dict["weighted avg"]["f1-score"], 4),
        },
        "per_class": per_class,
        "confusion_matrix": cm,
        "class_names": class_names,
        "classification_report_text": report_str,
    }

    return results


def evaluate_checkpoint(
    model_path: Union[str, Path] = DEFAULT_MODEL_PATH,
    test_dir: Union[str, Path] = TEST_DIR,
    architecture: str = DEFAULT_ARCHITECTURE,
    batch_size: int = 32,
    device: Optional[Union[torch.device, str]] = None,
    output_metrics_path: Optional[Union[str, Path]] = METRICS_PATH,
) -> Dict:
    """Load model artifact from disk, run evaluation on test directory, and save metrics.

    Args:
        model_path: Path to .pth checkpoint or artifact file.
        test_dir: Directory containing test split with class subfolders.
        architecture: Fallback model architecture if not stored in checkpoint.
        batch_size: Batch size for testing.
        device: Device to run evaluation on.
        output_metrics_path: Path to save evaluation metrics JSON.

    Returns:
        Evaluation results dictionary.
    """
    model_path = Path(model_path)
    test_path = Path(test_dir)
    target_device = device or get_default_device()

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset directory not found at: {test_path}")

    # Load checkpoint
    ckpt = torch.load(model_path, map_location=str(target_device), weights_only=False)
    arch = ckpt.get("architecture", architecture)
    class_names = ckpt.get("class_names", list(CLASS_NAMES))
    num_classes = ckpt.get("num_classes", len(class_names))

    # Initialize model and load state dict
    model = get_model(name=arch, num_classes=num_classes, device=target_device, pretrained=False)
    state_dict = ckpt.get("model_state", ckpt)
    model.load_state_dict(state_dict)

    # Create test loader
    eval_tf = get_eval_transforms()
    test_dataset = ContractImageFolder(root=test_path, transform=eval_tf)
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    logging.info(f"Loaded model '{arch}' from {model_path}")
    logging.info(f"Running evaluation on {len(test_dataset)} test samples...")

    results = evaluate_model(
        model=model,
        dataloader=test_loader,
        device=target_device,
        class_names=class_names,
    )
    results["model_path"] = str(model_path)
    results["architecture"] = arch

    # Display report
    print("\n" + "=" * 65)
    print("           SMART WASTE CLASSIFICATION - MODEL EVALUATION         ")
    print("=" * 65)
    print(f"Model Architecture : {arch}")
    print(f"Overall Accuracy   : {results['overall_accuracy'] * 100:.2f}%")
    print(f"Average Loss       : {results['average_loss']:.4f}")
    print(f"Average Confidence : {results['average_confidence'] * 100:.2f}%")
    print("-" * 65)
    print("Classification Report:")
    print(results["classification_report_text"])
    print("=" * 65)

    if output_metrics_path:
        out_p = Path(output_metrics_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation metrics successfully saved to: {out_p}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Smart Waste Classification - Model Evaluation Script")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH, help="Path to saved model checkpoint")
    parser.add_argument("--test-dir", type=Path, default=TEST_DIR, help="Path to test dataset directory")
    parser.add_argument("--model", type=str, default=DEFAULT_ARCHITECTURE, help="Model architecture")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--output-json", type=Path, default=METRICS_PATH, help="Path to output metrics JSON")
    args = parser.parse_args()

    evaluate_checkpoint(
        model_path=args.model_path,
        test_dir=args.test_dir,
        architecture=args.model,
        batch_size=args.batch_size,
        output_metrics_path=args.output_json,
    )


if __name__ == "__main__":
    main()
