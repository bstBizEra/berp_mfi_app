# Independent review of C02 R2 evidence

Reviewer: separate agent `/root/review_r2`. Scope: read-only inspection of supplied
artifacts; no remote execution, producer verdicts, or evidence modification.

## Verdict

The generic transaction/lifecycle observation baseline is substantiated for the
five executed synthetic cases. Same-session measurements, explicit observer SQL,
origin labels, callback ordering and persistence checks substantially repair the
previous evidence defects. This is a bounded A6/C02 instrumentation renewal, not
acceptance of complete C02, the entire A6 lock-instrumentation predicate, A7, A8
handback, or COMPAT-001A. C03 remains unproven. No financial compatibility conclusion
or blocker closure follows.

## Integrity checked independently

Run: `69dcfc48ca1b46418db3c0fae4721f78`.

All local SHA-256 values were recomputed and agree with the supplied manifest:

| Artifact | SHA-256 |
| --- | --- |
| manifest.json | dbc8ffcd6b37ead1a0da90b29205e26f52c8402e872be175c8448443644c7f1f |
| events.jsonl | 4c44d64c1c6e3e58372e4d845492b26dd91ece8af0e284f5e3a687516d3c0779 |
| observer.py | db8a445bc083160818b9c6bdbb430aff681dd5642750493856073a5d7090504b |
| queue-before.json | fbbc0947bcad9a08ba95437036415b362fe4802027696aad4b0990dce3b3fbc4 |
| queue-after.json | 285b615f704f20ad27eda48a1083afd98d75edf8886b4a11674ef2285d42d7a7 |

The manifest hash agrees with the producer-side hash supplied to this reviewer.
This establishes copy integrity against that anchor, not authenticated execution
provenance. Events are contiguous 0–912. All 144 state-query results report a
measured connection ID equal to the event session ID. Observer queries are
explicitly marked `observer=true` and use the existing connection cursor.

## Actual observations

| Case | Evidence sequences | Finding |
| --- | --- | --- |
| WSGI success | 0–224; verification 235 | Guest request, session 34; lifecycle and writes followed by `commit and chain` (212–215), before/after-commit callbacks (210–217), HTTP 200; separately connected session 35 finds one row. |
| WSGI failure | 256–354; verification 361 | Guest request, session 36; `rollback and chain` (343–346), rollback callbacks, HTTP 417; session 37 finds no row. |
| CLI | 382–541; verification 546 | Administrator, session 38: START TRANSACTION, savepoint, synthetic insert/save, rollback to savepoint (515–518), full rollback then new START TRANSACTION (525–536); session 39 finds no row. |
| RQ success | 567–662; verification 667 | SimpleWorker calls Frappe execute_job; Administrator session 40 commits and chains (652–655), callbacks run, job FINISHED; session 41 finds one row. |
| RQ failure | 688–885; verification 890 | Administrator session 42 rolls back and chains (773–776), then Error Log lifecycle occurs and a second commit-and-chain follows (875–878); job FAILED; session 43 finds no synthetic row. |

The worker failure's later commit is visible and must not be erased from a topology
diagram merely because the synthetic document rolled back. Error Log lifecycle is
observed; the full identity of every SQL write is not recoverable from SQL hashes.

For chained boundaries, state remains `in_transaction=1` (e.g. 215, 346, 655,
776, 878). This is consistent with a completed transaction and chained successor;
it does not show that commit failed. CLI full rollback yields state 0 at 528 and
the explicit subsequent BEGIN yields state 1 at 533. Callback container `run`
calls and returns are captured; individual registered callback function execution
and callback effects are not exhaustively traced.

## Limits and remaining defects

1. These are in-process Werkzeug requests, a direct Python CLI scenario and RQ
   SimpleWorker, not an external HTTP server or a forked/deployed worker. They
   exercise real Frappe handlers but cannot establish all production entry paths.
2. Lazy connection creation leaves some initial SQL-entry and lifecycle events
   without session IDs; their later events identify the acquired connection.
   Treat those nulls as pre-connection observations, not measurements of a session.
   The default site label is also supplied before a live site context exists.
3. Before naming, document_hash is the hash of null, shared across unnamed
   documents. Correlation and sequential execution disambiguate these cases;
   the field is not a stable per-object identity suitable for concurrent cases.
4. SQL and boundary wrappers observe successful returns; direct driver SQL outside
   Database.sql, connection initialization and unwrapped paths remain outside
   coverage. Observer state SELECTs add latency and are sampled after application
   calls. They are identified, but zero observer effect has not been established.
5. There is no DB-side table/row lock evidence, acquisition timestamp, wait graph,
   Lending call coverage, GL coverage, submit/cancel lifecycle coverage or native
   bypass coverage. `for_update` remains intent only. Full C02 is incomplete.
6. The finally block emits observer_stop and persists events before making the
   untraced final queue snapshot. The manifest is produced last, but the bundle
   alone does not prove all remote writers stopped or a final immutable handback.
   Scenario completion at 911 supports successful execution of all five cases;
   the script can also write a manifest after failures, so manifest presence is
   never a success predicate.
7. Queue snapshots retain `origin=UNKNOWN`. Their counts are short 0→0, default
   12→12 and long 5→5. This single execution does not explain historical 13 versus
   5 or establish clean-recreation equivalence. A7 remains reopened. This review
   makes no independent acceptance claim for that historical divergence.

## Disposition

Retain this review with the exact artifact hashes. Record generic same-session
transaction/lifecycle instrumentation as demonstrated for these cases, while
keeping complete C02 and lock instrumentation incomplete. Renew A7 using semantic
recreation evidence and resolve historical provenance gaps explicitly. Final A8
requires an independently reviewed, quiescent evidence set covering all required
predicates; this review alone cannot supply it. B-BLK-01/02/03 stay open and
IMP-001 remains locked.
