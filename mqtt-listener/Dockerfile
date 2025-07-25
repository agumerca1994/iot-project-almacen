FROM python:3.11-slim

# Crear carpeta de la app
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar librerías necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script
COPY app.py .

# Comando principal
CMD ["python", "app.py"]
