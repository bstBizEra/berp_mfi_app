#!/bin/sh
# Disposable lab launch skeleton. Run only in the dedicated compatibility workspace.
# This deliberately creates a networkless pod; it publishes no ports.
set -eu

POD="mfi-compat-001a"
IMAGE_BENCH="docker.io/frappe/bench@sha256:2132ebefed475ab4b898e0847fe00e1a8f50413dc528aafdecd188428e21b0a6"
IMAGE_DB="docker.io/library/mariadb@sha256:2d2f4095530294735a857cfe22bb101e19b0849b416911c796ec4aa81b164a62"
IMAGE_REDIS="docker.io/library/redis@sha256:9702d01c1f10c3ea9f48211b4362e44f154ff02d063e6f7268eba804059f53bf"

podman pod exists "$POD" && { echo "existing pod: inspect before reuse"; exit 1; }
podman pod create --name "$POD" --network none
podman run -d --name mfi-compat-001a-db --pod "$POD" \
  --env-file /workspace/secrets/db.env "$IMAGE_DB" \
  mariadbd --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
podman run -d --name mfi-compat-001a-cache --pod "$POD" "$IMAGE_REDIS" redis-server --port 6379
podman run -d --name mfi-compat-001a-queue --pod "$POD" "$IMAGE_REDIS" redis-server --port 6380
podman run -d --name mfi-compat-001a-runner --pod "$POD" \
  -v /workspace:/workspace:rw -v /harness:/harness:ro "$IMAGE_BENCH" sleep infinity
podman exec mfi-compat-001a-runner sh /harness/prepare-lab.sh
echo "Services launched; site creation and instrumentation are separate recorded steps."
