# Build Stage for React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# Final Stage for Python Backend
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
# We use standard pip to avoid complex uv setup in simple docker deployment,
# or we can just export requirements. Let's install directly from pyproject if possible or manual.
# Simplest: install dependencies manually matching pyproject
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    openai \
    requests \
    python-dotenv \
    genanki

# Copy backend code
COPY src/ ./src/
COPY server.py .
# utils.py is inside src/, which is already copied above

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/web/dist ./web/dist

# Create necessary directories
RUN mkdir -p audio

# Expose port
EXPOSE 8081

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
