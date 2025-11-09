FROM python:3.11-slim
WORKDIR /app

# Install minimal build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# --- FIX ---
# Paths are now relative to the root context defined in docker-compose.yml
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- FIX ---
# Copy the 'app' folder from the 'backend' directory into the image's WORKDIR
COPY ./app /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]