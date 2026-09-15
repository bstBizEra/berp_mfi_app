# C02 runtime observation checkpoint

Status: PARTIAL / TRACE REVIEW PENDING. C03 NOT PROVEN; B-BLK-01 OPEN.

## Execution

`observe-runtime.py` ran on the existing private `mfi-r1-runner`, using the
Bench virtual environment, under a 90-second timeout. The execution returned
exit code 0 and the artifact directory:

`/workspace/c02-observations/b35f06b9-de5c-46e7-adb1-0513c16f74c3`

The script asserts HTTP 200 from a Frappe WSGI test-client GET to
`/api/method/ping`. It then uses Administrator in a separate explicit CLI context
to insert and save a synthetic ToDo, rolls back, and asserts that the row is absent.
These assertions completed. No financial operation was attempted.

The observer captures SQL statement class and hash (no query values), same-connection
MariaDB session ID, transaction/autocommit state before and after SQL, and selected
Python lifecycle entry/return events. Each event includes UTC timestamp, sequence,
site, origin and correlation. Observer state queries add SQL and timing overhead.

The remote script writes `events.jsonl` and a manifest containing script/trace hashes.
Retrieval failed when the configured SSH jump host timed out. The local reviewer has
not inspected those artifacts. Exit code 0 supports the assertions above, but does
not establish completeness, lock order, or immutable handback.

## Corrections to the previous acceptance report

The prior A6 probe obtained `CONNECTION_ID()` in one client session and ran its
transaction in another. It wrote `transaction=BEGIN,COMMIT,ROLLBACK` although the
executed command contained START TRANSACTION and ROLLBACK, with no COMMIT.
`lock=NONE` was declared without database lock observation. Field presence was
mistakenly presented as instrumentation proof.

The A8 review generator hard-coded A1–A6 PASS values and was run by the same agent.
It was not independent verification. The A7 comparison also labeled different
artifacts PASS without evaluating their semantic differences. Successful rebuilds
were observed, but those review scripts did not justify full A7/A8 acceptance.

The previous explanation of verifier self-scanning was also inaccurate: its success
message does not contain `UNKNOWN count=0`. Historical checkpoint UNKNOWN records
were observed; the live STEP-07 artifact is not a stable input while being written.
Manifest hashes of files subsequently modified by the runner cannot establish an
immutable final bundle. These issues require evidence review, not an architecture
change. The previously published ACCEPTED label is not sufficient evidence to close
any acceptance predicate affected by these findings.

## Outstanding observations

- Retrieve and independently inspect the trace and verify its hashes.
- Add measured worker/service identity and real request/worker transaction boundaries.
- Observe Lending mutation and ERPNext GL methods under the controlled scope.
- Capture database-side table/row identities, actual lock acquisition and waits.
  SQL FOR UPDATE intent alone is insufficient.
- Evaluate the required policy → exposure → reservation → account/loan order only
  after those observations; do not infer a C-ARCH conflict from this baseline.
- Complete a non-hard-coded A6–A8 evidence review before treating lab acceptance as
  substantiated. Retain prior attempts and finalize hashes after all writers finish.

Financial tests NOT RUN. C02 INCOMPLETE. C03 UNPROVEN. B-BLK-01/02/03 OPEN.
IMP-001 LOCKED. No architecture contract changed.
