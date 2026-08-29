"""Model architecture builder and registry.

Follows Technical Interface Contract (CONTRACT.md Section 5).
"""

from typing import Callable, Dict, Optional, Union

import torch
from src.models.config import DEFAULT_ARCHITECTURE, NUM_CLASSES, get_default_device
from torch import nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    MobileNet_V2_Weights,
    ResNet18_Weights,
    efficientnet_b0,
    mobilenet_v2,
    resnet18,
)

_MODEL_BUILDERS: Dict[str, Callable] = {}


def register(name: str):
    """Decorator to register a model architecture builder function."""

    def decorator(fn: Callable):
        _MODEL_BUILDERS[name.lower()] = fn
        return fn

    return decorator


@register("resnet18")
def _build_resnet18(num_classes: int = NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


@register("mobilenet_v2")
def _build_mobilenet_v2(num_classes: int = NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    weights = MobileNet_V2_Weights.DEFAULT if pretrained else None
    model = mobilenet_v2(weights=weights)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


@register("efficientnet_b0")
def _build_efficientnet_b0(num_classes: int = NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = efficientnet_b0(weights=weights)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def get_model(
    name: str = DEFAULT_ARCHITECTURE,
    num_classes: int = NUM_CLASSES,
    device: Optional[Union[torch.device, str]] = None,
    pretrained: bool = True,
) -> nn.Module:
    """Build and initialize classification model architecture.

    Args:
        name: Architecture name ("resnet18", "mobilenet_v2", "efficientnet_b0").
        num_classes: Output class count (default 6 for TrashNet classes).
        device: Target device (CPU or CUDA). Defaults to auto-detected device.
        pretrained: Whether to load pre-trained ImageNet weights.

    Returns:
        torch.nn.Module configured with final classification layer matching num_classes.
    """
    key = name.lower()
    if key not in _MODEL_BUILDERS:
        options = list(_MODEL_BUILDERS.keys())
        raise ValueError(
            f"Unknown model architecture '{name}'. Supported options: {options}"
        )

    if device is None:
        device = get_default_device()

    model = _MODEL_BUILDERS[key](num_classes=num_classes, pretrained=pretrained)
    return model.to(device)


def list_available_models() -> list[str]:
    """Return list of all registered model architecture names."""
    return list(_MODEL_BUILDERS.keys())
