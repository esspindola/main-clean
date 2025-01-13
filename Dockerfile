FROM python:3.11

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y poppler-utils

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expone el puerto
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
