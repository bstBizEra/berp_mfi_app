# A6/C02 R2 and A7 queue investigation

Status: EVIDENCE CANDIDATE; COMPAT-001A REOPENED, C02 INCOMPLETE, C03 NOT STARTED.

## R2 generic scenarios

The lab-only observer ran on the existing pinned site, with all five persistence
assertions completed. Evidence run `69dcfc48ca1b46418db3c0fae4721f78` contains 913
events and 144 explicitly tagged same-session observer measurements. See the
[independent verdict](A8-R2-review.md) and [frozen input manifest](evidence/69dcfc48ca1b46418db3c0fae4721f78/manifest.json).

The observer wraps transaction methods and SQL, records chain/savepoint arguments,
captures before/after transaction callback containers and document lifecycle
dispatch with DocType/document hash, and labels request, CLI, worker and verification
origins. It adds state queries on the existing connection and marks them
`observer=true`. This has timing overhead and is not a zero-impact observer.

| Synthetic case | Session | Boundary | Fresh-connection row result |
|---|---|---|---|
| WSGI POST success (Guest, explicit test permission bypass) | 34 | COMMIT AND CHAIN | 1 |
| WSGI POST exception | 36 | ROLLBACK AND CHAIN | 0 |
| CLI Administrator | 38 | BEGIN, savepoint, write, rollback-to-savepoint, full rollback/new BEGIN | 0 |
| RQ SimpleWorker success | 40 | Frappe execute_job → COMMIT AND CHAIN | 1 |
| RQ SimpleWorker exception | 42 | ROLLBACK AND CHAIN → Error Log lifecycle → COMMIT AND CHAIN | 0 |

The chained transaction statements explain why `in_transaction=1` after a boundary
need not indicate a failed rollback. The failed worker commits error-recording work
after rolling back the synthetic document. These two transactions must remain
distinct in the runtime graph. No Lending or GL operation ran.

The first R2 attempt (`fb8f18c133b942e88a7455cbe1a7b739`) stopped on an uninstalled
test-module error. Its artifact directory is retained on the VM. The successful
attempt registers an ephemeral in-memory module under Frappe's namespace; it does
not install an app, edit upstream source, or publish an HTTP listener. Test requests
use Werkzeug in-process; jobs use a dedicated RQ queue and SimpleWorker without a
scheduler. This cannot certify deployed/forked worker or authorization behavior.

## Historical A7 divergence

Separate read-only investigation `/root/investigate_a7` compared both checkpoint
histories and exact pinned source. Build 1 has 42 checkpoint records (six rounds),
build 2 has 14 (two rounds). Each round migrates at STEP-03 and again at STEP-07.
Site creation also migrates once. Frappe migration teardown enqueues
`build_index_for_all_routes` on `long`, without default deduplication.

| Operation | Build 1 | Build 2 |
|---|---:|---:|
| Initial migration | 1 | 1 |
| Readiness rounds | 6 | 2 |
| Total migrations: 1 + 2 × rounds | 13 | 5 |
| Last STEP-04 long jobs (before verifier migration) | 12 | 4 |
| Last doctor long jobs | 13 | 5 |
| Default jobs | 12 | 12 |

Evidence: archived build1 bundle SHA-256
`dd5a3bbb6811ced530ec7246adfaeb7add6ee583c108621e6773910b99ac3ef6`;
checkpoint records span 01:26:39Z–01:37:13Z and 01:45:52Z–01:48:25Z respectively.
Doctor lines 12–15 identify the method and counts; both snapshots show scheduler
disabled/paused and zero workers. Matching site-create and migration log hashes
are documented in the earlier checkpoint.

Pinned Frappe `migrate.py:77–82,98–112` defaults to search-index enqueue at teardown.
`background_jobs.py:84,89–90,192–209,649–661` defaults to immediate enqueue with a
fresh UUID and no deduplication. Scheduler disablement does not suppress it.

Disposition: the aggregate divergence is explained by unequal execution histories
and deterministic accumulation, supported by counts, methods and enqueue source.
Destroyed build1 Redis prevents verification of its individual job payloads and
timestamps. Do not infer complete A7 acceptance from this causal accounting.

## Matched recreation campaign

`a7_matched.sh` specifies two fresh isolated labs with identical operation schedules:
preparation, site creation, exactly one migration rerun, doctor, three queue samples
without workers/migrations between them, container stop, then hashes after writers
stop. Original lab queues are preserved. The initial preparation attempt `a` failed
before site creation because the old harness expected extracted archives; retained
evidence records that failure. Corrected attempts use `a2` and `b2` and extract the
same pinned archives before preparation. Campaign results and independent review
must be attached before any acceptance disposition.

## Gates

Generic transaction/lifecycle instrumentation is substantiated by independent review
for the five cases only. Full C02, full A6 lock coverage, A7 and final A8 remain open
pending their required evidence. C03 is not authorized by this report. Financial
tests NOT RUN; B-BLK-01/02/03 OPEN; IMP-001 LOCKED.
