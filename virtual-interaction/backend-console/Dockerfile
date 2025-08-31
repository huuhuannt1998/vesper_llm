FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Install Docker CLI
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create non-root user
RUN useradd -m -u 1000 console && chown -R console:console /app

# Add user to root group for Docker socket access
RUN usermod -aG root console
# Also add to docker group for compatibility
RUN usermod -aG docker console
USER console

# Environment variables
ENV REDIS_URL=redis://redis:6379
ENV DATABASE_URL=postgresql://admin:secure_password@postgres/thermostat_testbed
ENV CLOUD_SERVER_URL=http://cloud-server:8080
ENV BACKEND_PORT=8088
ENV FRONTEND_PORT=3000

EXPOSE 3000 8088

# Start both backend and frontend
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port 8088 & cd frontend && python -m http.server 3000 --directory build"]
