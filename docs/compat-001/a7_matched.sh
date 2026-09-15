#!/bin/sh
# Two isolated clean builds, identical operation schedules. Preserve original lab.
set -eu
BASE=/home/berpadmin/berp-mfi-compat-r1
for label in a2 b2; do
  LAB=/home/berpadmin/berp-mfi-a7-$label
  test ! -e "$LAB"
done
for label in a2 b2; do
  LAB=/home/berpadmin/berp-mfi-a7-$label
  mkdir -p "$LAB/sources" "$LAB/harness" "$LAB/evidence"
  cp "$BASE"/sources/*.tar.gz "$LAB/sources/"
  for app in frappe erpnext lending; do
    tar -xzf "$LAB/sources/$app.tar.gz" -C "$LAB/sources"
  done
  cp "$BASE"/harness/*.sh "$LAB/harness/"
  cp "$BASE/c02_r2.py" "$LAB/"
  # Dedicated names and paths only; preparation/site scripts unchanged.
  sed "s|/home/berpadmin/berp-mfi-compat-r1|$LAB|g; s|mfi-r1-|mfi-a7-$label-|g" "$BASE/host-prepare.sh" > "$LAB/host-prepare.sh"
  sed "s|/home/berpadmin/berp-mfi-compat-r1|$LAB|g; s|mfi-r1-|mfi-a7-$label-|g" "$BASE/host-run.sh" > "$LAB/host-run.sh"
  cd "$LAB"
  date -u +%FT%TZ > evidence/campaign.started
  sh host-prepare.sh > evidence/launch-prepare.log 2>&1
  timeout 1250 sh -c 'while test ! -f evidence/prepare.exit; do sleep 3; done'
  test "$(cat evidence/prepare.exit)" = 0
  sh host-run.sh > evidence/launch-site.log 2>&1
  timeout 950 sh -c 'while test ! -f evidence/site.exit; do sleep 3; done'
  test "$(cat evidence/site.exit)" = 0
  sudo -n docker exec "mfi-a7-$label-runner" sh -c 'cd /workspace/bench; timeout 180 bench --site mfi-compat.localhost migrate > /workspace/evidence/migrate-once.log 2>&1'
  sudo -n docker exec "mfi-a7-$label-runner" sh -c 'cd /workspace/bench; bench --site mfi-compat.localhost doctor > /workspace/evidence/doctor-matched.log 2>&1'
  # No worker is started. Three snapshots; no migrations/requests between them.
  for sample in 1 2 3; do
    sudo -n docker exec "mfi-a7-$label-runner" sh -c "cd /workspace/bench/sites; /workspace/bench/env/bin/python -c 'import sys,json; sys.path.insert(0,\"/workspace\"); import c02_r2 as p; p.connect(); print(json.dumps(p.snapshot(),sort_keys=True,indent=2)); p.frappe.destroy()' > /workspace/evidence/queue-$sample.json"
    sleep 2
  done
  sudo -n docker inspect --format '{{.Name}} network={{.HostConfig.NetworkMode}} ports={{json .HostConfig.PortBindings}} image={{.Image}}' "mfi-a7-$label-db" "mfi-a7-$label-runner" > evidence/topology.txt
  date -u +%FT%TZ > evidence/campaign.finished
  sudo -n docker stop "mfi-a7-$label-runner" "mfi-a7-$label-cache" "mfi-a7-$label-queue" "mfi-a7-$label-db" > evidence/stopped.txt
  # All scenario writers stopped; do not include manifest in itself.
  find evidence -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > evidence/SHA256SUMS
done
