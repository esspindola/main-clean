# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .



FROM python:3.9-slim

WORKDIR /app

# Instala librerías del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
libgl1-mesa-glx \
libglib2.0-0 \
libsm6 \
libxext6 \
libxrender-dev \
&& rm -rf /var/lib/apt/lists/*


# Expone el puerto en el que la aplicación correrá
EXPOSE 10000


# Usar la forma shell para expandir $PORT
CMD gunicorn --bind 0.0.0.0:$PORT backend:app
