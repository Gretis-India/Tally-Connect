FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY tally_connect /app/tally_connect

EXPOSE 9100

ENV PYTHONUNBUFFERED=1
ENV TALLY_CONNECT_CONFIG=/app/tally_connect/config.json

CMD ["python", "tally_connect/run_connect.py"]
