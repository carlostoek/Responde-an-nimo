# Usa una imagen oficial de Python como base
FROM python:3.11-slim  

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app  

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*  

# Copiar archivos del proyecto al contenedor
COPY . /app  

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt  

# Exponer el puerto (si fuera necesario)
EXPOSE 8080  

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
