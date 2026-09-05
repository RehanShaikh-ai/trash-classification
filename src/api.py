import logging
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError
import sys
from pathlib import Path

# Add the project root to sys.path so 'src' can be resolved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# pyrefly: ignore [missing-import]
from src.models.predict import predict

app = Flask(__name__)
CORS(app)  # Allow all origins for local development

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_error_response(code: str, message: str, status_code: int):
    return jsonify({
        "error": {
            "code": code,
            "message": message
        }
    }), status_code


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    if "image" not in request.files:
        return create_error_response("IMAGE_REQUIRED", "No image was provided.", 400)

    file = request.files["image"]
    if file.filename == "":
        return create_error_response("IMAGE_REQUIRED", "No image was provided.", 400)

    # Check for supported extensions based on CONTRACT.md
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        return create_error_response("UNSUPPORTED_FILE_TYPE", "The provided file type is not supported.", 415)

    try:
        image = Image.open(file.stream)
        # Call the predict function which expects a PIL Image
        result = predict(image)
        return jsonify(result), 200

    except UnidentifiedImageError:
        return create_error_response("INVALID_IMAGE", "The uploaded file is not a valid image.", 400)
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return create_error_response("INTERNAL_ERROR", "An internal error occurred.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
