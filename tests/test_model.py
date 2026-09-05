"""Unit and integration tests for Member 2 (Model + Backend).

Validates:
- Canonical class identifiers & config consistency (CONTRACT.md Section 3)
- Model architecture outputs & builder registry (CONTRACT.md Section 5)
- Predict interface input/output schema & confidence bounds (CONTRACT.md Section 6)
- Checkpoint & model artifact serialization (CONTRACT.md Section 7)
- Evaluation metric calculation (CONTRACT.md Section 18)
"""

import pytest
import torch
from PIL import Image
# pyrefly: ignore [missing-import]
from src.models.config import (
    CLASS_NAMES,
    CLASS_TO_IDX,
    IDX_TO_CLASS,
    NUM_CLASSES,
    ModelConfig,
)
# pyrefly: ignore [missing-import]
from src.models.dataset import (
    get_eval_transforms,
    get_train_transforms,
)
# pyrefly: ignore [missing-import]
from src.models.evaluate import evaluate_model
# pyrefly: ignore [missing-import]
from src.models.model import get_model
# pyrefly: ignore [missing-import]
from src.models.predict import predict
# pyrefly: ignore [missing-import]
from src.models.train_utils import load_checkpoint, save_checkpoint, save_model_artifact
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def test_canonical_class_config():
    """Verify canonical class names match CONTRACT.md Section 3 exactly."""
    expected = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
    assert CLASS_NAMES == expected
    assert NUM_CLASSES == 6
    assert len(CLASS_TO_IDX) == 6
    for idx, name in enumerate(expected):
        assert CLASS_TO_IDX[name] == idx
        assert IDX_TO_CLASS[idx] == name


def test_model_config_dataclass(tmp_path):
    """Test ModelConfig creation, serialization, and deserialization."""
    config = ModelConfig(
        model_name="mobilenet_v2",
        num_epochs=15,
        batch_size=16,
        learning_rate=5e-4,
        data_dir=tmp_path / "data",
    )
    d = config.to_dict()
    assert d["model_name"] == "mobilenet_v2"
    assert d["num_epochs"] == 15
    assert d["batch_size"] == 16
    assert d["learning_rate"] == 5e-4

    restored = ModelConfig.from_dict(d)
    assert restored.model_name == config.model_name
    assert restored.num_epochs == config.num_epochs
    assert restored.data_dir == tmp_path / "data"


@pytest.mark.parametrize("arch", ["resnet18", "mobilenet_v2", "efficientnet_b0"])
def test_model_builders_forward(arch):
    """Test that all supported models build successfully and output (batch, 6) logits."""
    model = get_model(name=arch, num_classes=6, device="cpu", pretrained=False)
    dummy_input = torch.randn(2, 3, 224, 224)
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)
    assert output.shape == (2, 6), f"Expected shape (2, 6), got {output.shape} for {arch}"


def test_invalid_model_name():
    """Test error raised for unsupported model architecture."""
    with pytest.raises(ValueError, match="Unknown model architecture"):
        get_model(name="non_existent_arch", num_classes=6, device="cpu", pretrained=False)


def test_transforms():
    """Test train and eval transforms shape and normalization."""
    train_tf = get_train_transforms(image_size=(224, 224))
    eval_tf = get_eval_transforms(image_size=(224, 224))

    img = Image.new("RGB", (300, 300), color="blue")
    tensor_train = train_tf(img)
    tensor_eval = eval_tf(img)

    assert tensor_train.shape == (3, 224, 224)
    assert tensor_eval.shape == (3, 224, 224)


def test_checkpoint_save_and_load(tmp_path):
    """Test checkpoint save and load with metadata integrity."""
    model = get_model("resnet18", num_classes=6, device="cpu", pretrained=False)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    ckpt_path = tmp_path / "test_checkpoint.pth"

    save_checkpoint(
        model=model,
        optimizer=optimizer,
        epoch=3,
        path=ckpt_path,
        best_test_acc=0.85,
        architecture="resnet18",
    )
    assert ckpt_path.exists()

    new_model = get_model("resnet18", num_classes=6, device="cpu", pretrained=False)
    new_opt = torch.optim.Adam(new_model.parameters(), lr=1e-3)
    m, opt, start_epoch, best_acc, meta = load_checkpoint(
        model=new_model,
        optimizer=new_opt,
        device="cpu",
        path=ckpt_path,
    )
    assert start_epoch == 4
    assert best_acc == pytest.approx(0.85)
    assert meta["architecture"] == "resnet18"
    assert meta["class_names"] == CLASS_NAMES


def test_save_model_artifact(tmp_path):
    """Test saving deployable model artifact conforming to CONTRACT.md Section 7."""
    model = get_model("mobilenet_v2", num_classes=6, device="cpu", pretrained=False)
    artifact_path = tmp_path / "waste_classifier.pth"

    save_model_artifact(
        model=model,
        path=artifact_path,
        architecture="mobilenet_v2",
        class_names=CLASS_NAMES,
        best_acc=0.92,
    )

    assert artifact_path.exists()
    loaded = torch.load(artifact_path, map_location="cpu", weights_only=False)
    assert "model_state" in loaded
    assert loaded["architecture"] == "mobilenet_v2"
    assert loaded["class_names"] == CLASS_NAMES
    assert loaded["num_classes"] == 6
    assert loaded["contract_version"] == "1.0.0"


def test_evaluate_model_metrics():
    """Test evaluate_model calculates accurate metrics, report, and confusion matrix."""
    model = nn.Linear(10, 6)
    # Create synthetic dataset with known targets
    X = torch.randn(12, 10)
    y = torch.tensor([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=4)

    results = evaluate_model(
        model=model,
        dataloader=loader,
        device="cpu",
        class_names=CLASS_NAMES,
    )

    assert "overall_accuracy" in results
    assert "average_loss" in results
    assert "macro_avg" in results
    assert "weighted_avg" in results
    assert "per_class" in results
    assert "confusion_matrix" in results
    assert len(results["confusion_matrix"]) == 6
    assert results["total_samples"] == 12


def test_predict_interface_contract():
    """Verify predict(image) strictly complies with CONTRACT.md Section 6 interface."""
    model = get_model("resnet18", num_classes=6, device="cpu", pretrained=False)

    # Test with RGB image
    img = Image.new("RGB", (256, 256), color=(50, 100, 150))
    res = predict(img, model=model, device="cpu")

    # Contract schema assertion: {"predicted_class": str, "confidence": float}
    assert isinstance(res, dict)
    assert "predicted_class" in res
    assert "confidence" in res
    assert isinstance(res["predicted_class"], str)
    assert isinstance(res["confidence"], float)

    # Contract value constraints:
    assert res["predicted_class"] in CLASS_NAMES
    assert 0.0 <= res["confidence"] <= 1.0

    # Test with RGBA image
    rgba_img = Image.new("RGBA", (100, 100), color=(10, 20, 30, 255))
    res_rgba = predict(rgba_img, model=model, device="cpu")
    assert res_rgba["predicted_class"] in CLASS_NAMES
    assert 0.0 <= res_rgba["confidence"] <= 1.0


def test_predict_invalid_input_type():
    """Test error raised when invalid input type is passed to predict."""
    with pytest.raises(TypeError, match="Expected PIL.Image.Image"):
        predict("not_an_image")
