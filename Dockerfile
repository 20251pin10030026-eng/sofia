# 🌸 Sofia - Dockerfile para Azure Container Apps
FROM python:3.11-slim

# Metadados
LABEL maintainer="Sofia AI"
LABEL description="Sofia - Assistente Virtual com IA"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY sofia/ ./sofia/
COPY . .

# Criar diretórios necessários
RUN mkdir -p .sofia_internal logs

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/status', timeout=5)"

# Comando de inicialização
CMD ["python", "-m", "uvicorn", "sofia.api_web:app", "--host", "0.0.0.0", "--port", "8000"]
