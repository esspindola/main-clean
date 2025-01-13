# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY . /app

# Instala las dependencias del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
