"""Unit tests for Member 1 Data Handling and Preprocessing component.

Validates contract compliance for:
- Canonical class identifiers (CONTRACT.md Section 3)
- Processed dataset folder hierarchy (CONTRACT.md Section 4.2)
- Image requirements (224x224, RGB) (CONTRACT.md Section 4.3)
- Class mapping and metadata output (CONTRACT.md Section 4.4)
"""

import json
from pathlib import Path
from PIL import Image
import pytest

from preprocessing.config import (
    CLASS_NAMES,
    COLOR_MODE,
    IMAGE_SIZE,
    PROCESSED_DATA_DIR,
    SUPPORTED_EXTENSIONS,
)
from preprocessing.preprocessor import process_image
from preprocessing.validator import is_supported_extension, validate_image


def test_canonical_class_identifiers():
    """Verify that class names match exact contract section 3 canonical identifiers."""
    expected_classes = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
    assert CLASS_NAMES == expected_classes, (
        f"Class names must match canonical contract names exactly. Got {CLASS_NAMES}"
    )


def test_supported_extensions():
    """Verify supported file extensions list."""
    assert ".jpg" in SUPPORTED_EXTENSIONS
    assert ".jpeg" in SUPPORTED_EXTENSIONS
    assert ".png" in SUPPORTED_EXTENSIONS


def test_validate_image_success(tmp_path):
    """Test validation on a valid generated image."""
    img_path = tmp_path / "sample.jpg"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)

    is_valid, err = validate_image(img_path)
    assert is_valid is True
    assert err is None


def test_validate_image_corrupted(tmp_path):
    """Test validation on a corrupt image file."""
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"not an image data string")

    is_valid, err = validate_image(corrupt_path)
    assert is_valid is False
    assert err is not None


def test_process_image(tmp_path):
    """Test image preprocessing: RGB conversion & resizing to 224x224."""
    src_path = tmp_path / "raw.png"
    # Create RGBA image of size 500x300
    img = Image.new("RGBA", (500, 300), color=(100, 150, 200, 255))
    img.save(src_path)

    dest_path = tmp_path / "processed.jpg"
    processed_file = process_image(src_path, dest_path, target_size=(224, 224), color_mode="RGB")

    assert processed_file.exists()
    with Image.open(processed_file) as processed_img:
        assert processed_img.size == (224, 224)
        assert processed_img.mode == "RGB"


@pytest.mark.skipif(
    not PROCESSED_DATA_DIR.exists() or not (PROCESSED_DATA_DIR / "dataset_info.json").exists(),
    reason="Processed dataset directory not built yet.",
)
def test_processed_dataset_contract_structure():
    """Test generated dataset directory tree and metadata against contract specifications."""
    splits = ["train", "validation", "test"]

    # 1. Verify directory structure
    for split in splits:
        split_dir = PROCESSED_DATA_DIR / split
        assert split_dir.exists() and split_dir.is_dir(), f"Missing split directory: {split_dir}"
        for cls_name in CLASS_NAMES:
            cls_dir = split_dir / cls_name
            assert cls_dir.exists() and cls_dir.is_dir(), f"Missing class directory: {cls_dir}"

    # 2. Verify dataset_info.json
    metadata_path = PROCESSED_DATA_DIR / "dataset_info.json"
    assert metadata_path.exists()

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["class_names"] == CLASS_NAMES
    assert meta["preprocessing"]["image_size"] == list(IMAGE_SIZE)
    assert meta["preprocessing"]["color_mode"] == COLOR_MODE

    # 3. Sample check processed image resolution and mode
    for split in splits:
        for cls_name in CLASS_NAMES:
            cls_dir = PROCESSED_DATA_DIR / split / cls_name
            images = list(cls_dir.glob("*.jpg"))
            if images:
                sample_img_path = images[0]
                with Image.open(sample_img_path) as img:
                    assert img.size == IMAGE_SIZE, f"Image size wrong: {img.size}"
                    assert img.mode == COLOR_MODE, f"Image mode wrong: {img.mode}"
