# Usa una imagen base de Python más ligera
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias necesarias del sistema para OpenCV y GStreamer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Asegúrate de usar la versión compatible de pip
RUN pip install --upgrade pip

# Instala NumPy y OpenCV en versiones compatibles
RUN pip install --no-cache-dir "numpy<2.0" "opencv-python-headless==4.5.4.60"

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
