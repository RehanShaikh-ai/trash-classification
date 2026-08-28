"""Image preprocessing module.

Handles image loading, EXIF orientation correction, RGB conversion, and resizing.
"""

from pathlib import Path
from PIL import Image, ImageOps

from .config import COLOR_MODE, IMAGE_SIZE


def process_image(
    input_path: Path,
    output_path: Path,
    target_size: tuple[int, int] = IMAGE_SIZE,
    color_mode: str = COLOR_MODE,
) -> Path:
    """Preprocess a raw image file and save to output destination.

    1. Correct EXIF orientation.
    2. Convert to RGB color space.
    3. Resize to target dimensions (224x224).
    4. Save as JPEG.

    Args:
        input_path: Source image file path.
        output_path: Destination file path.
        target_size: (width, height) tuple. Default (224, 224).
        color_mode: Color mode string. Default 'RGB'.

    Returns:
        Path to processed output file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as img:
        # Correct orientation based on EXIF tag if present
        img = ImageOps.exif_transpose(img)

        # Convert to target color space (RGB)
        if img.mode != color_mode:
            img = img.convert(color_mode)

        # Resize image using high quality Lanczos resampling
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Save processed image as JPEG
        img.save(output_path, format="JPEG", quality=95)

    return output_path
