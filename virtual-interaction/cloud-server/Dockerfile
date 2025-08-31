FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and fix pyngrok permissions
RUN useradd -m -u 1000 cloudserver && \
    chown -R cloudserver:cloudserver /app && \
    pip install pyngrok && \
    mkdir -p /usr/local/lib/python3.11/site-packages/pyngrok/bin && \
    chmod -R 755 /usr/local/lib/python3.11/site-packages/pyngrok && \
    chown -R cloudserver:cloudserver /usr/local/lib/python3.11/site-packages/pyngrok

USER cloudserver

# Environment variables
ENV DATABASE_URL=postgresql://admin:secure_password@postgres/thermostat_testbed
ENV REDIS_URL=redis://redis:6379
ENV API_PORT=8080

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health').raise_for_status()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
