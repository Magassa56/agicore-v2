#!/bin/bash
set -euo pipefail

# --- Configuration & Validation ---
if [ -z "${SERVICE_URL:-}" ]; then echo "::error:: Required env var SERVICE_URL is not set." && exit 1; fi
HEALTH_CHECK_PATH=${HEALTH_CHECK_PATH:-"/"}

# --- Smoke Test ---
echo "--- Running Smoke Test ---"
echo "Service URL: ${SERVICE_URL}"
echo "Health Check Path: ${HEALTH_CHECK_PATH}"

# Wait for up to 60 seconds for the service to become available
n=0
until [ $n -ge 12 ]; do
  STATUS_CODE=$(curl -s -L -o /dev/null --write-out '%{http_code}' "${SERVICE_URL}${HEALTH_CHECK_PATH}")
  if [ "${STATUS_CODE}" -ge 200 ] && [ "${STATUS_CODE}" -lt 400 ]; then
    echo "✅ Smoke test on '${HEALTH_CHECK_PATH}' passed with status ${STATUS_CODE}."
    
    if [ "${HEALTH_CHECK_PATH}" != "/" ]; then
        echo "--- Checking root path ('/') as well ---"
        ROOT_STATUS_CODE=$(curl -s -L -o /dev/null --write-out '%{http_code}' "${SERVICE_URL}/")
        if [ "${ROOT_STATUS_CODE}" -ge 200 ] && [ "${ROOT_STATUS_CODE}" -lt 400 ]; then
            echo "✅ Root path ('/') is also responsive with status ${ROOT_STATUS_CODE}."
            exit 0
        else
            echo "::error::Smoke test on root path ('/') failed with status ${ROOT_STATUS_CODE}."
            exit 1
        fi
    fi
    exit 0
  fi
  echo "Smoke test failed with status ${STATUS_CODE}. Retrying in 5 seconds..."
  n=$((n+1))
  sleep 5
done

echo "::error:: Service did not become healthy after 60 seconds."
exit 1
