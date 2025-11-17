# Usa imagem oficial do Python 3.12 (estável)
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt .
COPY app.py .
COPY models.py .
COPY templates/ templates/
COPY runtime.txt .  # opcional, mas mantém por consistência

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 5000
EXPOSE 5000

# Comando de início
CMD ["python", "app.py"]