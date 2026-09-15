#!/bin/sh
# Host adapter; the frozen COMPAT-001A scripts are mounted read-only.
set -eu
LAB=/home/berpadmin/berp-mfi-compat-r1
BENCH_IMAGE=frappe/bench@sha256:2132ebefed475ab4b898e0847fe00e1a8f50413dc528aafdecd188428e21b0a6
DB_IMAGE=mariadb@sha256:2d2f4095530294735a857cfe22bb101e19b0849b416911c796ec4aa81b164a62
REDIS_IMAGE=redis@sha256:9702d01c1f10c3ea9f48211b4362e44f154ff02d063e6f7268eba804059f53bf
cd "$LAB"
test "$(cat evidence/prepare.exit)" = 0
test ! -d bench/sites/mfi-compat.localhost
mkdir -p secrets
chmod 700 secrets
umask 077
python3 - <<'PY'
import pathlib, secrets
for file, key in [("db.env", "MARIADB_ROOT_PASSWORD"), ("site.env", "SITE_ADMIN_PASSWORD")]:
    with (pathlib.Path("secrets") / file).open("x") as stream:
        stream.write(key + "=" + secrets.token_urlsafe(32) + "\n")
PY
sudo -n docker run -d --name mfi-r1-db --network none --memory=384m --memory-swap=384m --cpus=1 \
  --env-file "$LAB/secrets/db.env" "$DB_IMAGE" \
  --innodb-buffer-pool-size=64M --max-connections=30 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
sudo -n docker run -d --name mfi-r1-cache --network container:mfi-r1-db --memory=64m --memory-swap=64m \
  "$REDIS_IMAGE" redis-server --port 6379 --bind 127.0.0.1
sudo -n docker run -d --name mfi-r1-queue --network container:mfi-r1-db --memory=64m --memory-swap=64m \
  "$REDIS_IMAGE" redis-server --port 6380 --bind 127.0.0.1
sudo -n docker run -d --name mfi-r1-runner --network container:mfi-r1-db --memory=640m --memory-swap=640m --cpus=1 \
  -v "$LAB:/workspace" -v "$LAB/harness:/harness:ro" "$BENCH_IMAGE" sleep infinity
timeout 90 sh -c 'until sudo -n docker exec mfi-r1-db healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; do sleep 2; done'
sudo -n docker exec -d mfi-r1-runner sh -c 'date -u +%FT%TZ > /workspace/evidence/site.started; timeout --kill-after=15 900 sh /harness/create-site.sh > /workspace/evidence/site-wrapper.log 2>&1; rc=$?; printf "%s\n" "$rc" > /workspace/evidence/site.exit; date -u +%FT%TZ > /workspace/evidence/site.finished; exit "$rc"'
printf 'Site creation dispatched; observe evidence/site.exit and site-create.log.\n'
