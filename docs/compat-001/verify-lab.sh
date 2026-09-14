#!/bin/sh
# Readiness verification for the disposable COMPAT-001A lab.
# It may rerun migration on the synthetic site; it never runs financial tests.
set -eu

ROOT=/workspace
BENCH="$ROOT/bench"
SITE=mfi-compat.localhost
EVIDENCE="$ROOT/evidence"
mkdir -p "$EVIDENCE"
cd "$BENCH"

set -a
. "$ROOT/secrets/db.env"
set +a

echo "A1 source/image manifest is supplied by COMPAT-001" > "$EVIDENCE/verification-status.txt"

echo "A2 MariaDB" > "$EVIDENCE/services.log"
if command -v mariadb-admin >/dev/null 2>&1; then
  mariadb-admin --host=127.0.0.1 --user=root --password="$MARIADB_ROOT_PASSWORD" ping --silent >> "$EVIDENCE/services.log" 2>&1
else
  echo "UNKNOWN: mariadb-admin unavailable in runner image" >> "$EVIDENCE/services.log"
fi
echo "A2 Redis cache" >> "$EVIDENCE/services.log"
if command -v redis-cli >/dev/null 2>&1; then
  redis-cli -h 127.0.0.1 -p 6379 ping >> "$EVIDENCE/services.log"
else
  echo "UNKNOWN: redis-cli unavailable in runner image" >> "$EVIDENCE/services.log"
fi
echo "A2 Redis queue" >> "$EVIDENCE/services.log"
if command -v redis-cli >/dev/null 2>&1; then
  redis-cli -h 127.0.0.1 -p 6380 ping >> "$EVIDENCE/services.log"
else
  echo "UNKNOWN: redis-cli unavailable in runner image" >> "$EVIDENCE/services.log"
fi

test -d "sites/$SITE"
bench --site "$SITE" list-apps > "$EVIDENCE/installed-apps-rerun.txt"
bench --site "$SITE" migrate > "$EVIDENCE/migrate-rerun.log" 2>&1
bench --site "$SITE" doctor > "$EVIDENCE/doctor.log" 2>&1

if command -v ss >/dev/null 2>&1; then
  ss -lntp > "$EVIDENCE/listeners.txt" || true
else
  echo "UNKNOWN: ss unavailable in runner image" > "$EVIDENCE/listeners.txt"
fi

if test -s "$EVIDENCE/instrumentation.log"; then
  echo "A6 instrumentation artifact present" >> "$EVIDENCE/verification-status.txt"
else
  echo "UNKNOWN: instrumentation.log is absent" >> "$EVIDENCE/verification-status.txt"
fi

python - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path("/workspace")
evidence = root / "evidence"
files = {}
for path in sorted(evidence.glob("*.log")):
    files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
manifest = {
    "format": 1,
    "kind": "COMPAT_001A_READINESS_CHECK_NOT_FINANCIAL_ACCEPTANCE",
    "site": "mfi-compat.localhost",
    "artifacts": files,
    "financial_tests": "NOT_RUN",
    "instrumentation": "UNKNOWN unless instrumentation.log exists",
}
(evidence / "readiness-manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
PY
echo "Verification completed; inspect all artifacts before any acceptance decision."
