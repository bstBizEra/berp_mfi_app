#!/bin/sh
# Synthetic compatibility lab only. No application implementation.
# Run within the measured Bench container with /workspace dedicated to this unit.
set -eu
cd /workspace
test ! -e bench || { echo 'Existing bench: inspect before resuming'; exit 1; }
mkdir -p source-repos
for item in frappe:988e54f3c4c291e2077a83809663f123731abe76 erpnext:4048fb70e14d1843956fcdabb7c3cca75a1cbcdd lending:06fc075ae062ce38ac38a763f7f290da4ddd6fdb; do
  app=${item%%:*}
  pin=${item#*:}
  cp -a "sources/$app-$pin" "source-repos/$app"
  (
    cd "source-repos/$app"
    git init -q -b compat-source
    git add .
    git -c user.name='Compatibility Lab' -c user.email='lab@example.invalid' commit -qm "Archive snapshot of $pin"
  )
done
# Local synthetic Git commits only satisfy Bench's cloning requirement.
# Upstream identity comes from pinned archive URL/hash, not these synthetic SHAs.
bench init --frappe-path /workspace/source-repos/frappe --frappe-branch compat-source \
  --skip-assets --skip-redis-config-generation --no-procfile --no-backups bench
cd bench
bench get-app --branch compat-source --skip-assets /workspace/source-repos/erpnext
bench get-app --branch compat-source --skip-assets /workspace/source-repos/lending
bench set-config -g db_host mfi-compat-db
bench set-config -g redis_cache redis://mfi-compat-cache:6379
bench set-config -g redis_queue redis://mfi-compat-queue:6379
bench set-config -g redis_socketio redis://mfi-compat-queue:6379
bench set-config -g developer_mode 0
echo 'Preparation complete. Site creation is a separate recorded step.'
