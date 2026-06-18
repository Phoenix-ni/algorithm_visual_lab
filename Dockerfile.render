FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base ca-certificates \
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
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html
COPY render/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY render/start.sh /app/start.sh

RUN test -f /app/models/digit_cnn_model.pt \
    && mkdir -p /app/data /run/nginx \
    && chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
