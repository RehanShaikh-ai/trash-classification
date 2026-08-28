"""Dataset validation and corrupted image detection module.

Ensures raw image dataset meets CONTRACT.md requirements before processing.
"""

from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageOps

from .config import CLASS_NAMES, SUPPORTED_EXTENSIONS


def is_supported_extension(file_path: Path) -> bool:
    """Check if the file extension is supported."""
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def validate_image(file_path: Path) -> Tuple[bool, str | None]:
    """Validate that a file is an uncorrupted image and can be opened/converted.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not file_path.is_file():
        return False, "File does not exist"

    if not is_supported_extension(file_path):
        return False, f"Unsupported file extension: {file_path.suffix}"

    try:
        with Image.open(file_path) as img:
            # Verify file integrity
            img.verify()
        
        # Re-open after verify() to test conversion and loading
        with Image.open(file_path) as img:
            # Apply EXIF rotation if present to test orientation handling
            ImageOps.exif_transpose(img)
            # Test RGB conversion
            _ = img.convert("RGB")
        return True, None
    except Exception as e:
        return False, f"Corrupted image or read error: {str(e)}"


def scan_dataset(
    raw_dir: Path, class_names: List[str] = CLASS_NAMES
) -> Tuple[Dict[str, List[Path]], Dict[str, List[Tuple[Path, str]]]]:
    """Scan raw dataset directory by class, identifying valid images and corrupted/invalid files.

    Args:
        raw_dir: Directory containing raw class subfolders.
        class_names: List of expected canonical class identifiers.

    Returns:
        Tuple of (valid_files_by_class, invalid_files_by_class).
    """
    valid_files: Dict[str, List[Path]] = {cls: [] for cls in class_names}
    invalid_files: Dict[str, List[Tuple[Path, str]]] = {cls: [] for cls in class_names}

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw data directory does not exist: {raw_dir}")

    for cls_name in class_names:
        cls_dir = raw_dir / cls_name
        if not cls_dir.exists() or not cls_dir.is_dir():
            continue

        for item in sorted(cls_dir.iterdir()):
            if item.is_file():
                is_valid, err = validate_image(item)
                if is_valid:
                    valid_files[cls_name].append(item)
                else:
                    invalid_files[cls_name].append((item, err or "Unknown error"))

    return valid_files, invalid_files
