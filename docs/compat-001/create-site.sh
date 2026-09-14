#!/bin/sh
# Synthetic site creation only. Secrets must exist in /workspace/secrets/site.env.
set -eu
cd /workspace/bench
set -a
. /workspace/secrets/db.env
. /workspace/secrets/site.env
set +a
test -n "${MARIADB_ROOT_PASSWORD:-}"
test -n "${SITE_ADMIN_PASSWORD:-}"
bench new-site mfi-compat.localhost \
  --db-host 127.0.0.1 --no-mariadb-socket \
  --mariadb-root-password "$MARIADB_ROOT_PASSWORD" \
  --admin-password "$SITE_ADMIN_PASSWORD" \
  > /workspace/evidence/site-create.log 2>&1
bench --site mfi-compat.localhost set-config developer_mode 0
bench --site mfi-compat.localhost set-config disable_scheduler 1
bench --site mfi-compat.localhost set-config pause_scheduler 1
bench --site mfi-compat.localhost set-config redis_cache redis://127.0.0.1:6379
bench --site mfi-compat.localhost set-config redis_queue redis://127.0.0.1:6380
bench --site mfi-compat.localhost set-config redis_socketio redis://127.0.0.1:6380
bench --site mfi-compat.localhost install-app erpnext >> /workspace/evidence/site-create.log 2>&1
bench --site mfi-compat.localhost install-app lending >> /workspace/evidence/site-create.log 2>&1
bench --site mfi-compat.localhost migrate >> /workspace/evidence/site-create.log 2>&1
bench --site mfi-compat.localhost list-apps > /workspace/evidence/installed-apps.txt
echo 'Synthetic site creation and migration completed.'
