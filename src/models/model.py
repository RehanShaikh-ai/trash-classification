import torch
from torch import nn
from torchvision.models import (resnet18,ResNet18_Weights,mobilenet_v2,MobileNet_V2_Weights,efficientnet_b0,EfficientNet_B0_Weights,)
from typing import Union

_MODEL_BUILDERS = {}

def register(name):
    def decorator(fn):
        _MODEL_BUILDERS[name] = fn
        return fn
    return decorator

@register("resnet18")
def _build_resnet18(num_classes:int):
    model = resnet18(weights=ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features,num_classes)
    return model

@register("mobilenet_v2")
def _build_mobilenet_v2(num_classes:int):
    model = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features,num_classes)
    return model

@register("efficientnet_b0")
def _build_efficientnet_b0(num_classes: int):
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model

def get_model(name:str,num_classes:int,device:Union[torch.device,str])-> nn.Module:
    """
    name: "resnet18" | "mobilenet_v2" | "efficientnet_b0"
    num_classes: pull this from config.py (NUM_CLASSES = 6 for TrashNet) — do not
    hardcode it per call-site, that's exactly the drift config.py exists to prevent.
    """
    if name not in _MODEL_BUILDERS:
        raise ValueError(f"Unknown model '{name}'. Options: {list(_MODEL_BUILDERS)}")
    return _MODEL_BUILDERS[name](num_classes).to(device)
