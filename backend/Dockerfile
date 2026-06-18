FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-runtime.txt ./requirements-runtime.txt

ARG TORCH_VERSION=2.12.1
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG PYPI_INDEX_URL=https://pypi.org/simple

RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url "${TORCH_INDEX_URL}" --extra-index-url "${PYPI_INDEX_URL}" "torch==${TORCH_VERSION}" \
    && python -m pip install --index-url "${PYPI_INDEX_URL}" -r requirements-runtime.txt

COPY backend/app ./app
COPY backend/models ./models

RUN test -f /app/models/digit_cnn_model.pt \
    && mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3).read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
