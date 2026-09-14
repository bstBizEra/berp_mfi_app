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

EXPECTED_FRAPPE_SHA=217d4e48043770ac3cc44ce7001107f162ed1580cbfffca9c73bf2c83a0275d9
EXPECTED_ERPNEXT_SHA=374957165ae8d784f6ebdd30414b47077a5a5e9519d48bf61703b577f45533b0
EXPECTED_LENDING_SHA=888e2bf910b00a2cefc4aeb220a6ab7162710a3a582a5de838252a81998acb0e

set -a
. "$ROOT/secrets/db.env"
set +a

echo "A1 source/image manifest is supplied by COMPAT-001" > "$EVIDENCE/verification-status.txt"
for item in "frappe.tar.gz:$EXPECTED_FRAPPE_SHA" "erpnext.tar.gz:$EXPECTED_ERPNEXT_SHA" "lending.tar.gz:$EXPECTED_LENDING_SHA"; do
  archive=${item%%:*}
  expected=${item#*:}
  actual=$(sha256sum "$ROOT/sources/$archive" | awk '{print $1}')
  test "$actual" = "$expected"
done
printf 'source_archives=verified\n' >> "$EVIDENCE/verification-status.txt"

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
grep -Eq '^frappe[[:space:]]+16\.33\.1([[:space:]]|$)' "$EVIDENCE/installed-apps-rerun.txt"
grep -Eq '^erpnext[[:space:]]+16\.34\.2([[:space:]]|$)' "$EVIDENCE/installed-apps-rerun.txt"
grep -Eq '^lending[[:space:]]+16\.5\.0([[:space:]]|$)' "$EVIDENCE/installed-apps-rerun.txt"
printf 'installed_apps=frappe@16.33.1,erpnext@16.34.2,lending@16.5.0\n' >> "$EVIDENCE/verification-status.txt"
bench --site "$SITE" migrate > "$EVIDENCE/migrate-rerun.log" 2>&1
bench --site "$SITE" doctor > "$EVIDENCE/doctor.log" 2>&1

if command -v ss >/dev/null 2>&1; then
  ss -lntp > "$EVIDENCE/listeners.txt" || true
else
  echo "UNKNOWN: ss unavailable in runner image" > "$EVIDENCE/listeners.txt"
fi

if test -s "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'site=[^[:space:]]+' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'session=[^[:space:]]+' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'transaction=(BEGIN|COMMIT|ROLLBACK|NONE)' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'sql=(observed|NONE)' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'lock=(observed|NONE)' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'timestamp=[^[:space:]]+' "$EVIDENCE/instrumentation.log" \
  && grep -Eq 'correlation=[^[:space:]]+' "$EVIDENCE/instrumentation.log"; then
  echo "A6 instrumentation probe=verified" >> "$EVIDENCE/verification-status.txt"
else
  echo "UNKNOWN: structured instrumentation probe is absent or incomplete" >> "$EVIDENCE/verification-status.txt"
fi

python - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path("/workspace")
evidence = root / "evidence"
files = {}
for path in sorted(evidence.iterdir()):
    if path.name in {"readiness-manifest.json"} or not path.is_file():
        continue
    files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
unknown = 0
for path in sorted(evidence.iterdir()):
    if path.is_file() and path.name != "readiness-manifest.json":
        unknown += path.read_text(errors="replace").count("UNKNOWN")
manifest = {
    "format": 1,
    "kind": "COMPAT_001A_READINESS_CHECK_NOT_FINANCIAL_ACCEPTANCE",
    "site": "mfi-compat.localhost",
    "artifacts": files,
    "financial_tests": "NOT_RUN",
    "instrumentation": "verified only when structured probe fields are present",
    "unknown_count": unknown,
}
(evidence / "readiness-manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
if unknown:
    raise SystemExit(f"COMPAT-001A not ready: UNKNOWN count={unknown}")
PY
echo "Verification completed; inspect all artifacts before any acceptance decision."
