FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create data directory
RUN mkdir -p data/raw

# Set python path to include src
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["python", "src/ingestion/ingest_traffic.py"]
