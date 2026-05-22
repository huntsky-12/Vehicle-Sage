FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat for waiting on Kafka
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*


# Copy app code
COPY . .

# Default command (we will override in docker-compose)
CMD ["uvicorn", "main_new:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
RUN pip install python-jose[cryptography]