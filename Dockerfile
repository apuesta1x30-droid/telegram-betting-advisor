# Usamos una versión estable y ligera de Python
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de dependencias y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del bot
COPY . .

# Render usa el puerto 10000 por defecto para servicios Docker
EXPOSE 10000

# Comando para iniciar el bot
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
