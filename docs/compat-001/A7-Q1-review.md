# A7-Q1 matched queue investigation

Status: CANDIDATE EVIDENCE; A7 REOPENED; A8 REVIEW PENDING.

## Matched campaign result

Two fresh labs (`a2` and `b2`) ran the same operation schedule: preparation from
the exact source archives, site creation, one migration rerun, doctor, three queue
snapshots with workers stopped and no migration/request between snapshots, then
container stop. The original lab and failed `a` preparation were preserved.

The local semantic comparator reports:

```text
builds_semantically_equal: true
a2 samples_semantically_equal: true; raw_samples_equal: true
b2 samples_semantically_equal: true; raw_samples_equal: true
a2 default jobs: 12; b2 default jobs: 12
a2 long method groups: 1; b2 long method groups: 1
a2 long multiplicity: 2; b2 long multiplicity: 2
workers: 0 in both builds
registry counts: equal in all sampled queues
```

The six queue files were retrieved and remote/local SHA-256 values match:

```text
a2 queue-1/2/3: c28cefb1efd5ba36c81d103f28595fd11ee0112dc6cc442e541970439f7920a5
b2 queue-1/2/3: cd4fb2f666ac8b5123211feb12f6a2bd76e059807d6ef93bad5c07e3dfe5d7cf
```

The comparator ignores job UUIDs, enqueue timestamps, Redis key inventory and
worker names; it compares method, site, event, job name, kwargs hash, status,
multiplicity, worker count and registry cardinality. The ignored fields remain
available in the raw files for provenance.

Stopped-build topology manifests were also retrieved and hash-bound. Both builds
use the same DB and runner image digests; the DB has `network=none`, the runner
shares the DB network namespace, and both report `ports={}`. This substantiates
the campaign isolation shape while retaining the full remote manifests for review.

## Relation to historical 13 versus 5

The prior divergence is explained by unequal schedules: build 1 had six checkpoint
rounds and build 2 had two; each round ran migration twice, and initial site creation
ran once. Pinned Frappe migration enqueues one non-deduplicated long queue search-index
job per migration, giving `1 + 2×6 = 13` and `1 + 2×2 = 5`. The matched campaign
uses one migration rerun per build and therefore reaches the same normalized state.

This supports deterministic accumulation and removes timing as the explanation for
the observed aggregate difference. It does not recover destroyed build-1 Redis job
payloads or timestamps, and it does not prove all future upgrade procedures produce
the same state. Three snapshots are evidence of a stable point, not continuous
quiescence. The campaign's own output is not independent review.

## Disposition

Treat this as A7 candidate evidence only. Retain A7 reopened until an independent,
read-only reviewer recomputes all six queue hashes and both manifests, checks the
schedule and evaluates the comparator predicates without producer verdicts.
A8 remains pending. A6 generic R2 evidence is bounded and independently reviewed;
full C02 and C03 remain incomplete/unproven. Financial tests NOT RUN;
B-BLK-01/02/03 OPEN; IMP-001 LOCKED.
