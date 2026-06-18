#!/bin/sh
set -eu

export PORT="${PORT:-10000}"

uvicorn app.main:app --host 127.0.0.1 --port 8000 &
API_PID="$!"

envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

trap 'kill "$API_PID" 2>/dev/null || true' INT TERM

nginx -g 'daemon off;' &
NGINX_PID="$!"

wait "$NGINX_PID"
