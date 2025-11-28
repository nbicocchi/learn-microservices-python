FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY src /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Run the app
CMD ["python", "/app/main.py"]