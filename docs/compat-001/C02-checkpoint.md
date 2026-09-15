# C02 runtime observation checkpoint

Status: PARTIAL / BASELINE TRACE RETRIEVED AND REVIEWED. C02 INCOMPLETE.
C03 NOT STARTED / UNPROVEN; B-BLK-01 OPEN.

## Retrieval and measured review (supersedes retrieval-pending notes below)

The SSH route recovered. Retrieved the original run without rerunning it and
matched remote and local SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| manifest.json | ef6ec2ac0d85bd626a3bbc7ac2bbdac1e43016e13a383d369ffe545eb2716416 |
| events.jsonl | 6ab6c0f03f883f6d8d64a510807eac9a102c3de8e0e5e04218e58c698c92a875 |
| observe-runtime.py | 951d6c8c60e03a6447505d92663528c4c0503340d033de738306610037ca4c82 |

The manifest's trace/script hashes match the retrieved trace and repository script.
The manifest hash is verified against a fresh remote calculation, not an earlier
independently anchored digest. This establishes transfer consistency, not historical
immutability. The trace contains 8,448 events.

- WSGI origin has one SQL return on session 30 (sequence 37), then 149 on session
  31. Session changes must be explained; do not claim one connection for the request.
- `sync_database` calls `rollback` at sequences 3982–3983; the SQL return at 3999
  still reports `in_transaction=1`. Without complete SQL boundary text and independent
  observation, this is not proof of an ended request transaction. HTTP 200 is at 4016.
- CLI context initially has no connection at 4019. Its 129 observed SQL returns use
  session 32. START at 4040 and SAVEPOINT at 4058 precede the document operations.
- Existing-document save enters `_save` at 7251, `check_if_latest` at 7274 and
  `load_doc_before_save` at 7275. FOR UPDATE SQL returns at 7298 before
  `run_before_save_methods` at 7324. This is lifecycle order and lock intent only.
- CLI ROLLBACK at 8350 reports transaction state 0; subsequent START at 8367 reports
  state 1. Row-absence assertion completes at 8410; a second rollback/start follows.
  No COMMIT SQL return was recorded. This does not establish coverage of every
  possible driver-level commit route.
- SQL return counts: SELECT 268, INSERT 2, UPDATE 2, START 3, ROLLBACK 3, SAVEPOINT 1.
  Raw cursor state queries added by the observer are outside that wrapper count.

Rechecked current Docker topology: DB network mode `none`, other lab containers
share its namespace, and all four have empty published-port bindings. MariaDB binds
wildcard addresses inside that isolated namespace; this is not itself public exposure.
A5 retains review of the remaining synthetic data/file/worker scope.

Semantic A7 spot-check: doctor logs both show disabled/paused/inactive scheduler and
zero workers. Default queue counts match at 12, but long queue counts differ: 13 in
the archived first build versus 5 in the current second-build log. Listener sets
match after sorting, but queue differences are not merely timestamps. Their cause
and acceptable recreation predicate remain unresolved. A7 is REOPENED.

A6 and A8 remain REOPENED. This baseline review does not certify full instrumentation,
request/worker/Lending/GL topology, or independent handback.

### Independent review

Separate read-only reviewer `/root/review_c02` inspected the retrieved files and
observer independently. It confirmed matching trace/script hashes, contiguous
sequence 0–8447, and 279 matching SQL entry/return pairs with no SQL error events.
It did not receive an independent expected manifest digest; the main agent's remote
digest comparison is documented above.

The reviewer found that Python events lack per-event session, actor, DocType identity
and `run_method` dispatch arguments. An additional insert therefore cannot be
attributed from the trace alone. Raw observer state SQL is unrecorded; final cleanup
occurs after profiling/wrapping are disabled. It concludes that A6 renewal and C02
completion are not justified and that this directory cannot renew A7/A8. This review
is independent baseline inspection, not acceptance handback.

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
