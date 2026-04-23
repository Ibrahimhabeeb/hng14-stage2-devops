FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py ./

USER appuser

HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=5 \
  CMD python -c "import os, redis; r=redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ.get('REDIS_PORT','6379')), password=os.environ.get('REDIS_PASSWORD')); r.ping()"

CMD ["python", "worker.py"]
