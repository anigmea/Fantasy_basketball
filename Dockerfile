# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the app with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app

# CMD ["python", "fantasy.py"]

# https://docs.cloud.google.com/build/docs/build-push-docker-image