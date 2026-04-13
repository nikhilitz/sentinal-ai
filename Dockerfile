# Use stable Python (IMPORTANT)
FROM python:3.10-slim

# Install system dependencies (FIXES libcrypto issue)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]