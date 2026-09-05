FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by opencv-python and other scientific libraries
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and source code
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set Python path to ensure module imports work correctly
ENV PYTHONPATH=/app

# Command to run the application
CMD ["flask", "--app", "src/api.py", "run", "--host=0.0.0.0", "--port=5000"]
