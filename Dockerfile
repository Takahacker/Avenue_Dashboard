FROM python:3.10-slim

WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ .

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "api:app"]
