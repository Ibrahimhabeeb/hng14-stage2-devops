#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${1:-frontend}"
IMAGE_NAME="${2:?image name is required}"
NEW_PORT="${3:-13000}"
HEALTH_PATH="${4:-/health}"
TIMEOUT_SECONDS="${5:-60}"
NETWORK_NAME="${6:-job_processor_network}"

OLD_CONTAINER_ID="$(docker ps -q -f "name=${SERVICE_NAME}" | head -n 1 || true)"

docker rm -f "${SERVICE_NAME}-candidate" >/dev/null 2>&1 || true

docker run -d \
  --name "${SERVICE_NAME}-candidate" \
  --network "${NETWORK_NAME}" \
  -e API_URL="http://api:8000" \
  -e FRONTEND_HOST="0.0.0.0" \
  -e FRONTEND_PORT="3000" \
  -p "${NEW_PORT}:3000" \
  "${IMAGE_NAME}" >/dev/null

deadline=$((SECONDS + TIMEOUT_SECONDS))
healthy=false
while [ "$SECONDS" -lt "$deadline" ]; do
  if curl -fsS "http://127.0.0.1:${NEW_PORT}${HEALTH_PATH}" >/dev/null 2>&1; then
    healthy=true
    break
  fi
  sleep 2
done

if [ "${healthy}" != true ]; then
  echo "Candidate service failed health check inside ${TIMEOUT_SECONDS}s; preserving old service."
  docker rm -f "${SERVICE_NAME}-candidate" >/dev/null 2>&1 || true
  exit 1
fi

if [ -n "${OLD_CONTAINER_ID}" ]; then
  docker rm -f "${OLD_CONTAINER_ID}" >/dev/null 2>&1 || true
fi

docker rename "${SERVICE_NAME}-candidate" "${SERVICE_NAME}-active"
echo "Rolling deploy completed for ${SERVICE_NAME}."
