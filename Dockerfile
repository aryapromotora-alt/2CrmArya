FROM python:3.12-slim

# Instala dependências do sistema para compilar psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia todos os arquivos necessários
COPY requirements.txt .
COPY app.py .
COPY models.py .
COPY templates/ templates/

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]