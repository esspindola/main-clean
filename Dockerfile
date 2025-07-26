<<<<<<< HEAD

FROM python:3.9-slim AS builder
WORKDIR /app

# Herramientas de compilación para wheels nativos
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget \
    && rm -rf /var/lib/apt/lists/*

# pip y toolchain actualizados
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Requisitos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


########################
# 2️⃣  RUNTIME STAGE
########################
FROM python:3.9-slim
WORKDIR /app

# Dependencias de sistema en tiempo de ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
        # OpenCV
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
        # PDF
        poppler-utils \
        # Tesseract OCR
        tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng libtesseract-dev \
        # Fuentes para OCR
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# Copiar las librerías Python instaladas globalmente
COPY --from=builder /usr/local /usr/local

# Variables de entorno
ENV PYTHONPATH=/app:/app/yolov5
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV FLASK_ENV=production
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TORCH_HOME=/tmp/.torch
ENV OMP_NUM_THREADS=1
ENV YOLO5_VERBOSE=False

# Directorios de trabajo
RUN mkdir -p /app/models /app/uploads /app/outputs /app/logs

# Copiar código de la aplicación
COPY . .

# Copiar utilidades YOLOv5 por compatibilidad (si procede)
COPY yolov5/utils ./yolov5/utils
COPY yolov5/models ./yolov5/models

# Verificación opcional de modelos
RUN ls -lh /app/models/best.pt || echo "Modelo YOLO no encontrado"

# Permisos
RUN chmod +x /app && chown -R root:root /app

# Verificar Tesseract
RUN tesseract --version && ls -la $TESSDATA_PREFIX

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Puerto expuesto
EXPOSE 5000

# Arrancar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "--worker-class", "sync", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "main:app"]
=======

FROM python:3.9-slim AS builder
WORKDIR /app

# Herramientas de compilación para wheels nativos
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget \
    && rm -rf /var/lib/apt/lists/*

# pip y toolchain actualizados
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Requisitos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


########################
# 2️⃣  RUNTIME STAGE
########################
FROM python:3.9-slim
WORKDIR /app

# Dependencias de sistema en tiempo de ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
        # OpenCV
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
        # PDF
        poppler-utils \
        # Tesseract OCR
        tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng libtesseract-dev \
        # Fuentes para OCR
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# Copiar las librerías Python instaladas globalmente
COPY --from=builder /usr/local /usr/local

# Variables de entorno
ENV PYTHONPATH=/app:/app/yolov5
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV FLASK_ENV=production
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TORCH_HOME=/tmp/.torch
ENV OMP_NUM_THREADS=1
ENV YOLO5_VERBOSE=False

# Directorios de trabajo
RUN mkdir -p /app/models /app/uploads /app/outputs /app/logs

# Copiar código de la aplicación
COPY . .

# Copiar utilidades YOLOv5 por compatibilidad (si procede)
COPY yolov5/utils ./yolov5/utils
COPY yolov5/models ./yolov5/models

# Verificación opcional de modelos
RUN ls -lh /app/models/best.pt || echo "Modelo YOLO no encontrado"

# Permisos
RUN chmod +x /app && chown -R root:root /app

# Verificar Tesseract
RUN tesseract --version && ls -la $TESSDATA_PREFIX

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Puerto expuesto
EXPOSE 5000

# Arrancar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "--worker-class", "sync", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "main:app"]
>>>>>>> origin/luis-develop
