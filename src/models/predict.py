"""Inference interface for Smart Waste Classification.

Adheres strictly to CONTRACT.md Section 6 (Model Inference Interface):
predict(image: PIL.Image.Image) -> {"predicted_class": str, "confidence": float}
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
from PIL import Image, ImageOps
import torch
from torch import nn

from src.models.config import (
    CLASS_NAMES,
    DEFAULT_ARCHITECTURE,
    DEFAULT_MODEL_PATH,
    IDX_TO_CLASS,
    IMAGE_SIZE,
    NORM_MEAN,
    NORM_STD,
    get_default_device,
)
from src.models.dataset import get_eval_transforms
from src.models.model import get_model

# Global cached model singleton for efficient inference
_CACHED_MODEL: Optional[nn.Module] = None
_CACHED_DEVICE: Optional[torch.device] = None
_CACHED_CLASS_NAMES: List[str] = list(CLASS_NAMES)


def load_inference_model(
    model_path: Optional[Union[str, Path]] = None,
    architecture: str = DEFAULT_ARCHITECTURE,
    device: Optional[Union[torch.device, str]] = None,
) -> nn.Module:
    """Load and cache model for inference.

    Args:
        model_path: Path to model weights / artifact (.pth).
        architecture: Architecture to use if artifact does not specify.
        device: Device to load model onto.

    Returns:
        Loaded PyTorch model in eval mode.
    """
    global _CACHED_MODEL, _CACHED_DEVICE, _CACHED_CLASS_NAMES

    target_device = torch.device(device) if device else get_default_device()

    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    if not path.exists():
        # Fallback to initialized model if artifact not yet saved on disk
        model = get_model(name=architecture, num_classes=len(CLASS_NAMES), device=target_device, pretrained=True)
        model.eval()
        _CACHED_MODEL = model
        _CACHED_DEVICE = target_device
        _CACHED_CLASS_NAMES = list(CLASS_NAMES)
        return _CACHED_MODEL

    ckpt = torch.load(path, map_location=str(target_device), weights_only=False)

    if isinstance(ckpt, dict) and "model_state" in ckpt:
        arch = ckpt.get("architecture", architecture)
        _CACHED_CLASS_NAMES = ckpt.get("class_names", list(CLASS_NAMES))
        num_classes = ckpt.get("num_classes", len(_CACHED_CLASS_NAMES))
        model = get_model(name=arch, num_classes=num_classes, device=target_device, pretrained=False)
        model.load_state_dict(ckpt["model_state"])
    elif isinstance(ckpt, dict):
        model = get_model(name=architecture, num_classes=len(CLASS_NAMES), device=target_device, pretrained=False)
        model.load_state_dict(ckpt)
    else:
        model = ckpt

    model.to(target_device)
    model.eval()
    _CACHED_MODEL = model
    _CACHED_DEVICE = target_device
    return _CACHED_MODEL


def predict(
    image: Image.Image,
    model: Optional[nn.Module] = None,
    model_path: Optional[Union[str, Path]] = None,
    device: Optional[Union[torch.device, str]] = None,
) -> Dict[str, Union[str, float]]:
    """Predict waste class and confidence for a single PIL image.

    Follows CONTRACT.md Section 6:
        Input: image (PIL.Image.Image)
        Output: {"predicted_class": str, "confidence": float}

    Args:
        image: PIL Image instance to classify.
        model: Optional pre-loaded model. If None, uses cached or loaded model.
        model_path: Path to model checkpoint if not using default.
        device: Device to execute prediction on.

    Returns:
        Dict with "predicted_class" (canonical class string) and "confidence" (float in [0.0, 1.0]).
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL.Image.Image instance, got {type(image)}")

    # Ensure model is ready
    if model is None:
        global _CACHED_MODEL
        if _CACHED_MODEL is None or model_path is not None:
            model = load_inference_model(model_path=model_path, device=device)
        else:
            model = _CACHED_MODEL

    dev = _CACHED_DEVICE or (device if device else get_default_device())

    # Preprocessing: EXIF orientation, RGB conversion, eval transform (Contract Section 4.3 & 6)
    img = ImageOps.exif_transpose(image)
    if img.mode != "RGB":
        img = img.convert("RGB")

    transform = get_eval_transforms(image_size=IMAGE_SIZE, mean=NORM_MEAN, std=NORM_STD)
    tensor = transform(img).unsqueeze(0).to(dev)

    model.eval()
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze(0)
        confidence, pred_idx = torch.max(probabilities, dim=0)

    predicted_idx = int(pred_idx.item())
    conf_value = float(confidence.item())

    # Ensure confidence is in range [0.0, 1.0]
    conf_value = max(0.0, min(1.0, conf_value))

    # Lookup canonical class name
    if 0 <= predicted_idx < len(_CACHED_CLASS_NAMES):
        predicted_class = _CACHED_CLASS_NAMES[predicted_idx]
    else:
        predicted_class = IDX_TO_CLASS.get(predicted_idx, "trash")

    return {
        "predicted_class": predicted_class,
        "confidence": round(conf_value, 4),
    }
