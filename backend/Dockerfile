FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# Descargar script para esperar la DB
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Comando de arranque que espera la DB y lanza Uvicorn
CMD ["/wait-for-it.sh", "db:5432", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
