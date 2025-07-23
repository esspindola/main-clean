# Multi-stage build for optimized production image
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # PDF processing
    poppler-utils \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libtesseract-dev \
    # Additional fonts for better OCR
    fonts-liberation \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PYTHONPATH=/app:/app/yolov5
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV FLASK_ENV=production
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TORCH_HOME=/tmp/.torch
ENV OMP_NUM_THREADS=1
ENV YOLO5_VERBOSE=False

# Update PATH to include local packages
ENV PATH=/root/.local/bin:$PATH

# Create necessary directories
RUN mkdir -p /app/models /app/uploads /app/outputs /app/logs

# Copy application code
COPY . .

# Copy YOLOv5 utils and models for compatibility
COPY yolov5/utils ./yolov5/utils
COPY yolov5/models ./yolov5/models

# Verify model exists
RUN ls -la models/best.pt || echo "Model not found, will use fallback"

# Set proper permissions
RUN chmod +x /app && \
    chown -R root:root /app

# Verify Tesseract installation
RUN tesseract --version && \
    ls -la $TESSDATA_PREFIX

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "--worker-class", "sync", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "main:app"]