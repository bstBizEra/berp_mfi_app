#!/bin/sh
# Resumable COMPAT-001A readiness runner. No site creation and no financial tests.
set -u

ROOT=/workspace
BENCH="$ROOT/bench"
SITE=mfi-compat.localhost
EVIDENCE="$ROOT/evidence"
RECORDS="$EVIDENCE/checkpoints.jsonl"
TIMEOUT_SECONDS=${COMPAT_STEP_TIMEOUT_SECONDS:-120}
mkdir -p "$EVIDENCE"

timestamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

artifact_hashes() {
  find "$EVIDENCE" -maxdepth 1 -type f ! -name checkpoints.jsonl ! -name readiness-manifest.json -print0 |
    sort -z | xargs -0 -r sha256sum | tr '\n' ';'
}

run_step() {
  step_id=$1
  shift
  command_text="$*"
  log="$EVIDENCE/${step_id}.log"
  started=$(timestamp)
  command_hash=$(printf '%s' "$command_text" | sha256sum | awk '{print $1}')
  result=UNKNOWN
  exit_code=125
  if command -v timeout >/dev/null 2>&1; then
    timeout --signal=TERM --kill-after=10 "$TIMEOUT_SECONDS" sh -c "$command_text" >"$log" 2>&1
    exit_code=$?
    if [ "$exit_code" -eq 0 ]; then result=PASS; elif [ "$exit_code" -eq 124 ] || [ "$exit_code" -eq 125 ] || [ "$exit_code" -eq 137 ]; then result=UNKNOWN; else result=FAIL; fi
  else
    printf '%s\n' 'UNKNOWN: timeout utility unavailable' >"$log"
  fi
  finished=$(timestamp)
  hashes=$(artifact_hashes)
  STEP_ID="$step_id" STARTED="$started" FINISHED="$finished" COMMAND_HASH="$command_hash" \
    EXIT_CODE="$exit_code" RESULT="$result" ARTIFACT_HASHES="$hashes" python - <<'PY' >> "$RECORDS"
import json
import os
print(json.dumps({
    "step_id": os.environ["STEP_ID"],
    "started_at": os.environ["STARTED"],
    "finished_at": os.environ["FINISHED"],
    "command_hash": os.environ["COMMAND_HASH"],
    "exit_code": int(os.environ["EXIT_CODE"]),
    "artifact_hashes": os.environ["ARTIFACT_HASHES"].split(";") if os.environ["ARTIFACT_HASHES"] else [],
    "result": os.environ["RESULT"],
}))
PY
  printf '%s %s exit=%s\n' "$step_id" "$result" "$exit_code"
}

if ! cd "$BENCH" 2>/dev/null; then
  run_step STEP-02 'printf "%s\n" "UNKNOWN: bench directory inaccessible"; exit 125'
  exit 1
fi
run_step STEP-01 'if command -v mariadb-admin >/dev/null && command -v redis-cli >/dev/null; then printf "%s\n" "service clients present"; else printf "%s\n" "UNKNOWN: service client unavailable"; exit 125; fi'
run_step STEP-02 'test -d "sites/'"$SITE"'" && bench --site '"$SITE"' list-apps'
run_step STEP-03 'bench --site '"$SITE"' migrate'
run_step STEP-04 'bench --site '"$SITE"' doctor'
run_step STEP-05 'if command -v ss >/dev/null; then ss -lntp; else printf "%s\n" "UNKNOWN: ss unavailable"; exit 125; fi'
run_step STEP-06 'test -s "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "site=[^[:space:]]+" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "session=[^[:space:]]+" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "transaction=(BEGIN|COMMIT|ROLLBACK|NONE)" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "sql=(observed|NONE)" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "lock=(observed|NONE)" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "timestamp=[^[:space:]]+" "'"$EVIDENCE"'/instrumentation.log" && grep -Eq "correlation=[^[:space:]]+" "'"$EVIDENCE"'/instrumentation.log"'
run_step STEP-07 'sh /harness/verify-lab.sh'
printf '%s\n' 'Checkpoint records persisted; inspect all results before acceptance.'
