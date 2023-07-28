#!/bin/bash
# no verbose
set -x

if [[ -z "${NEXT_API_URL}" ]]; then
  echo "The environment variable NEXT_API_URL must be set to run the container."
  exit 1
fi

echo "NEXT_API_URL=${NEXT_API_URL}" >> /app-ui/.env.local

# yarn build
# echo "Starting Nextjs"
exec "$@"