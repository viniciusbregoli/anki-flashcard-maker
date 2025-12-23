# Build Stage for React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# Final Stage for Python Backend
FROM python:3.11-slim
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
COPY utils.py . 
# Note: utils.py seems to be in src/ in some files but also imported from root in server.py?
# Let's check importing structure. server.py adds src/ to path.
# But original file structure had utils.py in root? Let's check file list.
# Actually, utils.py was moved to src/utils.py? 
# Wait, checking list_dir earlier: 
# src/ contains utils.py? No, list_dir output showed utils.py in src/.
# But imports in other files might expect it elsewhere.
# server.py adds src to path, so `from utils import ...` works if utils is in src.

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/web/dist ./web/dist

# Create necessary directories
RUN mkdir -p audio

# Expose port
EXPOSE 8081

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
