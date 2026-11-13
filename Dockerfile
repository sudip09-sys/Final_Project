FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
ENV CMAKE_BUILD_PARALLEL_LEVEL=2
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m attendance && chown -R attendance:attendance /app
USER attendance
ENV PORT=8000 PYTHONUNBUFFERED=1
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 120 'app:create_app()'"]
