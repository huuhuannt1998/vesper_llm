FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 environment && chown -R environment:environment /app
USER environment

# Environment variables
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV API_PORT=8001

EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health').raise_for_status()"

CMD ["python", "main.py"]
