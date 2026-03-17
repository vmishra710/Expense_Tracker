FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (for caching) \
COPY requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]