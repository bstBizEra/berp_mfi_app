# A8 independent review of matched A7 campaign

Status: PASS for the bounded matched-campaign predicates; overall COMPAT-001A
handback remains incomplete.

This review was performed from the frozen evidence files and comparator source,
without using the producer's verdict as an acceptance input.

## Predicate results

| Predicate | Result | Evidence |
|---|---|---|
| Six queue snapshot hashes recompute | PASS | All three `a2` snapshots equal `c28cefb1...f7920a`; all three `b2` snapshots equal `cd4fb2f...5d7cf`. |
| Both remote evidence manifests are retained | PASS | `a2-SHA256SUMS` and `b2-SHA256SUMS` are committed and include queue/topology hashes. |
| Identical operation schedule | PASS | Both campaigns used exact-pinned preparation, site creation, one migration rerun, doctor, three snapshots, then stop. |
| Normalized semantic state equal | PASS | Independent comparator run gives equal normalized queues, registry cardinalities, and worker counts. |
| Three-snapshot stability | PASS | Each build's three raw snapshots are byte-identical; workers are zero in every sample. |
| Ignored dimensions inspected | PASS | Raw queue records differ only in `job_id` and `enqueued_at` for matching jobs; method/site/status/kwargs hash agree. |
| Isolation topology equivalent | PASS | Both topology files show the same image digests, DB `network=none`, runner network namespace sharing, and no published ports. |

## Review limits

The review substantiates the matched campaign at its defined observation boundary.
It does not prove continuous quiescence beyond the three samples, future migration
behavior, full registry payload equality, or C02 Lending/GL transaction topology.
The historical build-1 Redis payloads remain unrecoverable. These limits do not
invalidate the bounded A7 result, but they prevent treating it as financial or
lock evidence.

## Disposition

The `13 versus 5` historical queue divergence is consistent with unequal migration
schedules and the matched campaign reaches the same normalized state under equal
schedules. A7 matched recreation evidence is therefore **SUBSTANTIATED — BOUNDED**.
The A8 review of this A7 campaign is complete. Overall COMPAT-001A handback remains
open until the renewed A6/C02 bundle and this review are incorporated by the
governing evidence reviewer.

Financial tests were not run; C03 remains not started; B-BLK-01/02/03 remain open;
IMP-001 remains locked.
