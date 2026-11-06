# Fake Job Detector — production image
# Base: python:3.11-slim (matches dev environment Python 3.11)
FROM python:3.11-slim

# ---------------------------------------------------------------------------
# System setup
# ---------------------------------------------------------------------------
# Create non-root user early so all subsequent files are owned correctly
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# ---------------------------------------------------------------------------
# Install Python dependencies
# Scikit-learn version MUST match models/current/model_metadata.json (1.9.1)
# ---------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Copy application source and model artifacts
# ---------------------------------------------------------------------------
COPY src ./src
COPY models/current ./models/current

# ---------------------------------------------------------------------------
# Runtime configuration (overridable via -e / docker-compose environment:)
# ---------------------------------------------------------------------------
ENV MODEL_DIR=/app/models/current \
    MAX_BATCH=500 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# Give the non-root user ownership of the entire workdir
RUN chown -R appuser:appuser /app

# ---------------------------------------------------------------------------
# Drop to non-root user (NFR security requirement)
# ---------------------------------------------------------------------------
USER appuser

EXPOSE 8000

# --app-dir tells uvicorn where to find the 'detector' package
CMD ["uvicorn", "detector.api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
