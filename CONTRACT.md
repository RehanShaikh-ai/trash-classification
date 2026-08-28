# Smart Waste Classification

## Technical Interface Contract

**Contract Version:** `1.0.0`\
**Project Version:** `0.1.0`

---

# 1. Project Scope

The system classifies an uploaded waste image into one of the supported waste categories using a trained machine-learning model.

### End-to-End Pipeline

```text
Raw Dataset
    ↓
DATA HANDLING
    ↓
Processed Dataset
    ↓
MODEL TRAINING
    ↓
Trained Model
    ↓
FLASK BACKEND
    ↓
REST API
    ↓
FRONTEND
    ↓
Prediction Display
```

---

# 2. Component Ownership

| Component       | Owner    | Responsibility                        |
| --------------- | -------- | ------------------------------------- |
| Data Handling   | Member 1 | Dataset preparation and preprocessing |
| Model + Backend | Member 2 | Model training, inference, Flask API  |
| Frontend        | Member 3 | UI and API integration                |

Each member may modify the internal implementation of their component, but must preserve the interfaces defined in this contract.

---

# 3. Supported Classes

The initial model must support exactly these six classes:

```text
cardboard
glass
metal
paper
plastic
trash
```

### Class Identifier Rules

These values are the canonical class identifiers.

They must be used exactly as written.

```text
cardboard
glass
metal
paper
plastic
trash
```

Do not use alternatives such as:

```text
Cardboard
Plastic Waste
plastics
metal_waste
```

The class names form part of the system interface.

---

# 4. Data Handling Contract

## 4.1 Responsibility

The Data Handling component is responsible for:

- Dataset acquisition
- Dataset validation
- Corrupted-image detection
- Image preprocessing
- Dataset splitting
- Data augmentation
- Class consistency

---

## 4.2 Dataset Structure

The processed dataset must follow:

```text
data/
├── train/
│   ├── cardboard/
│   ├── glass/
│   ├── metal/
│   ├── paper/
│   ├── plastic/
│   └── trash/
│
├── validation/
│   ├── cardboard/
│   ├── glass/
│   ├── metal/
│   ├── paper/
│   ├── plastic/
│   └── trash/
│
└── test/
    ├── cardboard/
    ├── glass/
    ├── metal/
    ├── paper/
    ├── plastic/
    └── trash/
```

---

## 4.3 Image Requirements

Unless changed by the Model component and documented here:

```text
Color format: RGB
Image size: 224 × 224
Supported source formats:
    .jpg
    .jpeg
    .png
```

The Model component must not depend on undocumented preprocessing.

---

## 4.4 Dataset Output

The Data Handling component must provide:

```text
Processed dataset
+
Class mapping
+
Preprocessing configuration
```

The class mapping must remain consistent between training and inference.

Example:

```python
CLASS_NAMES = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash",
]
```

The exact ordering must be preserved when converting model output indices into class names.

---

# 5. Model Contract

## 5.1 Responsibility

The Model component is responsible for:

- Model architecture
- Training
- Validation
- Evaluation
- Model serialization
- Inference
- Prediction generation

---

# 6. Model Inference Interface

The Model component must expose the following function:

```python
predict(image)
```

### Input

```text
image: PIL.Image.Image
```

### Output

```python
{
    "predicted_class": str,
    "confidence": float
}
```

### Example

```python
{
    "predicted_class": "plastic",
    "confidence": 0.94
}
```

### Output Constraints

`predicted_class` must be one of:

```text
cardboard
glass
metal
paper
plastic
trash
```

`confidence` must satisfy:

```text
0.0 <= confidence <= 1.0
```

---

# 7. Model Artifact Contract

The trained model must be saved in a documented format.

Initial expected location:

```text
models/
└── waste_classifier.<FORMAT>
```

The exact model format may be selected by the Model owner, for example:

```text
.pth
.pt
```

The format must be documented before integration.

The model artifact must include or be accompanied by:

- Model architecture information
- Class mapping
- Required preprocessing
- Model version

---

# 8. Backend / Flask Contract

The Model + Backend component exposes a REST API for the Frontend.

## 8.1 Base URL

Development:

```text
http://localhost:5000
```

---

# 9. Prediction Endpoint

## Request

```http
POST /predict
```

### Content-Type

```text
multipart/form-data
```

### Request Field

| Field   | Type | Required | Description             |
| ------- | ---- | -------- | ----------------------- |
| `image` | File | Yes      | Waste image to classify |

Example:

```text
POST /predict

image = plastic_bottle.jpg
```

---

# 10. Successful Response

### HTTP Status

```text
200 OK
```

### Content-Type

```text
application/json
```

### Response

```json
{
    "predicted_class": "plastic",
    "confidence": 0.94
}
```

### Response Schema

| Field             | Type   | Required | Constraints               |
| ----------------- | ------ | -------- | ------------------------- |
| `predicted_class` | string | Yes      | Must be a supported class |
| `confidence`      | float  | Yes      | `0.0–1.0`                 |

---

# 11. Error Contract

All unsuccessful API responses must use:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message"
    }
}
```

## Defined Errors

### Missing Image

```http
400 Bad Request
```

```json
{
    "error": {
        "code": "IMAGE_REQUIRED",
        "message": "No image was provided."
    }
}
```

### Invalid Image

```http
400 Bad Request
```

```json
{
    "error": {
        "code": "INVALID_IMAGE",
        "message": "The uploaded file is not a valid image."
    }
}
```

### Unsupported File Type

```http
415 Unsupported Media Type
```

```json
{
    "error": {
        "code": "UNSUPPORTED_FILE_TYPE",
        "message": "The provided file type is not supported."
    }
}
```

### Internal Error

```http
500 Internal Server Error
```

```json
{
    "error": {
        "code": "INTERNAL_ERROR",
        "message": "An internal error occurred."
    }
}
```

---

# 12. Frozen API Identifiers

The following identifiers are part of the public interface and must be used exactly as defined.

| Type             | Identifier        |
| ---------------- | ----------------- |
| Endpoint         | `/predict`        |
| HTTP Method      | `POST`            |
| Request field    | `image`           |
| Response field   | `predicted_class` |
| Response field   | `confidence`      |
| Error root       | `error`           |
| Error identifier | `error.code`      |
| Error message    | `error.message`   |
| Model function   | `predict(image)`  |

These identifiers must not be renamed without updating this contract and coordinating with dependent components.

---

# 13. Frontend Contract

The Frontend component must:

1. Accept an image from the user.
2. Send the image to `POST /predict`.
3. Parse the documented JSON response.
4. Display the prediction.
5. Display the confidence.
6. Handle documented API errors.

---

## 13.1 Frontend Request

The Frontend must send:

```text
POST /predict
Content-Type: multipart/form-data

image=<uploaded_file>
```

---

## 13.2 Frontend Success Handling

Given:

```json
{
    "predicted_class": "plastic",
    "confidence": 0.94
}
```

The Frontend should display:

```text
Predicted Category: Plastic
Confidence: 94%
```

The Frontend must not depend on any other fields being present.

---

## 13.3 Frontend Error Handling

The Frontend must read:

```json
{
    "error": {
        "code": "...",
        "message": "..."
    }
}
```

and display an appropriate user-facing error.

The Frontend must not depend on Flask's internal error implementation.

---

# 14. Mock API Contract

The Frontend can be developed before the trained model is available.

A mock response may be:

```json
{
    "predicted_class": "plastic",
    "confidence": 0.94
}
```

The Frontend must behave exactly as it would with the real API.

This allows:

```text
Frontend development
        ≠
Model completion
```

The two components can therefore be developed independently.

---

# 15. Integration Requirements

## Data → Model

The Model component must be able to load the dataset using the structure and class names defined in Section 4.

## Model → Backend

The Backend must use the Model's `predict(image)` interface.

The Backend must convert the model result into the API response defined in Section 10.

## Backend → Frontend

The Frontend must communicate only through the API defined in Sections 9–11.

The Frontend must not import the Model implementation directly.

---

# 16. Internal vs External Interfaces

The following are considered **internal implementation details**:

```text
Model architecture
Training algorithm
Optimizer
Learning rate
Batch size
Data augmentation implementation
Flask internal functions
Frontend framework internals
```

These may change without requiring changes to dependent components.

The following are **public interfaces**:

```text
Dataset structure
Class identifiers
predict(image)
POST /predict
image
predicted_class
confidence
error.code
error.message
```

Changes to public interfaces require coordination.

---

# 17. Contract Change Procedure

If an interface must change:

```text
Proposed change
      ↓
Update CONTRACT.md
      ↓
Notify dependent owner(s)
      ↓
Update implementation
      ↓
Update tests
      ↓
Integration test
      ↓
Merge
```

No breaking interface changes should be made silently.

---

# 18. Definition of Done

## Data Handling

- [ ] Dataset obtained and documented.
- [ ] Dataset validated.
- [ ] Corrupted images handled.
- [ ] Preprocessing implemented.
- [ ] Train/validation/test split created.
- [ ] Class names match the canonical identifiers.
- [ ] Dataset structure matches this contract.
- [ ] Model owner can load the dataset successfully.

## Model / Backend

- [ ] Model trains using the defined dataset.
- [ ] Model evaluation is documented.
- [ ] Model artifact can be loaded.
- [ ] `predict(image)` is implemented.
- [ ] Prediction output follows the defined schema.
- [ ] Flask `/predict` endpoint is implemented.
- [ ] Success responses follow the defined schema.
- [ ] Errors follow the defined error schema.

## Frontend

- [ ] Image upload implemented.
- [ ] Correct API request generated.
- [ ] Successful response parsed.
- [ ] Prediction displayed.
- [ ] Confidence displayed.
- [ ] API errors handled.

## Integration

- [ ] Data → Model tested.
- [ ] Model → Backend tested.
- [ ] Backend → Frontend tested.
- [ ] Mock API tested by Frontend.
- [ ] End-to-end image classification tested.

---

# 19. Final Interface

```text
                    DATA HANDLING
                         │
                         │ Processed Dataset
                         ▼
                   MODEL TRAINING
                         │
                         │ predict(image)
                         ▼
                    FLASK BACKEND
                         │
                         │ POST /predict
                         │
                         ▼
                      FRONTEND
                         │
                         ▼
                 Prediction Display
```

### Canonical API Flow

```text
Frontend
   │
   │ POST /predict
   │ image=<file>
   ▼
Flask
   │
   │ PIL.Image
   ▼
predict(image)
   │
   │
   ▼
{
    "predicted_class": "plastic",
    "confidence": 0.94
}
   │
   ▼
Frontend
   │
   ▼
Plastic — 94%
```

**The implementation behind each interface may change. The interface itself must remain compatible with this contract.**
