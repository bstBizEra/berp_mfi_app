# BERP-MFI-COMPAT-001A — Executable Lab Enablement & Instrumentation

Status: ACCEPTED — lab readiness only; no financial blocker closed.
Date: 2026-09-15. Parent evidence unit: [COMPAT-001](BERP-MFI-COMPAT-001.md).
Runtime candidate: [ARCH-001C R1](BERP-MFI-ARCH-001C.md).

## Purpose and hard boundary

This controlled unit establishes a disposable, isolated Frappe/ERPNext/Lending site
for evidence collection. It does not implement BERP MFI behavior, create MFI DocTypes,
add financial hooks, enable capabilities, assign roles, run production migrations or
close B-BLK-01, B-BLK-02 or B-BLK-03. Any runtime result is returned to COMPAT-001 as
evidence and is classified before it can affect 001B or 001A.

The lab must use the exact R1 source pins and measured images from 001C/COMPAT-001.
Mutable tags are discovery inputs only; the launch manifest uses immutable digests.
No public ports, DNS, external integrations, mail, customer data or production secrets
are permitted. Disposable synthetic credentials are generated outside Git and removed
with the lab.

## Acceptance contract

```text
COMPAT-001A ACCEPTED only when

exact R1 source pins installed
AND MariaDB reachable privately
AND Redis cache/queue reachable privately
AND synthetic Frappe site created
AND ERPNext installed
AND Lending installed
AND site migration succeeds
AND scheduler/business integrations disabled
AND no production data/credentials present
AND transaction + SQL/lock instrumentation works
AND environment can be recreated from evidence
```

Acceptance is a lab-readiness result. It does not imply that any financial path is
safe, atomic, guarded or compatible. All C02–C13 tests remain governed by COMPAT-001.

## Isolation model

The preferred topology is one rootful Podman pod with `--network none`, so database,
Redis cache, Redis queue and the Bench runner share only private loopback. This avoids
the current WSL kernel's missing `/dev/net/tun` and `ip_tables` bridge support. If a
future environment uses a private bridge instead, it must retain no published ports,
deny outbound business integrations, record the network configuration and prove site
and file isolation. Rootless bridge failure is infrastructure evidence, not a runtime
finding.

The runner receives only the disposable lab directory and read-only harness scripts.
The site name is synthetic (`mfi-compat.localhost`); company, user, account and loan
fixtures are synthetic and minimal. Scheduler events, email, payment gateways,
webhooks and external service credentials remain disabled. Workers are started only
for controlled probes and carry an explicit site context.

## Reproducible steps

1. Verify the R1 source archive hashes and image digests against COMPAT-001.
2. Create a fresh rootful Podman pod with no network and four containers: MariaDB,
   Redis cache, Redis queue and Bench runner. Record container IDs, image digests,
   command lines, environment policy and UTC timestamps.
3. Run `docs/compat-001/prepare-lab.sh` inside the runner. It creates a Bench from
   the synthetic Git commits made from the immutable source archives; those local
   commits satisfy Bench's clone interface and never replace the upstream SHAs.
4. Create the synthetic site with a disposable generated administrator/database
   secret supplied through `/workspace/secrets/db.env` and `/workspace/secrets/site.env`.
   Install ERPNext and Lending, set private
   Redis endpoints, disable scheduler and integrations, then migrate.
5. Verify `bench --site mfi-compat.localhost doctor`, installed-app metadata,
   database/Redis reachability, site file permissions and no external listeners.
6. Install read-only instrumentation: SQL query/transaction logging, database lock
   observation and request/worker correlation. Instrumentation must not alter
   transaction ownership, commit behavior or financial data.
7. Export a redacted manifest containing versions, hashes, topology, site settings,
   instrumentation checks and commands. Never export secrets or customer/financial data.

Every step is idempotence-tested on a disposable copy. A failed step leaves the lab
NOT ACCEPTED; it is repaired or recreated, never marked successful by documentation.

The readiness command is `docs/compat-001/verify-lab.sh`. Missing client utilities,
traces or listener evidence are recorded as `UNKNOWN`; the command never converts an
absent observation into a pass and its manifest explicitly remains non-financial.

For bounded execution, use `docs/compat-001/run-checkpointed-readiness.sh`. It does
not create a site; it runs service, site, migration-rerun, doctor, isolation,
instrumentation and verifier steps independently with a timeout. Each step persists
timestamps, command hash, exit code, artifact hashes and `PASS`/`FAIL`/`UNKNOWN` in
`evidence/checkpoints.jsonl`. An inaccessible process is represented as `UNKNOWN`.

## Instrumentation contract

The first probes are observational:

- database connection/session IDs, explicit `BEGIN`/`COMMIT`/`ROLLBACK`, savepoints
  and implicit-commit warnings;
- SQL statement class, table/object, timestamp, transaction/session ID and lock wait;
- row-lock acquisition order for policy, exposure, reservation, account and loan rows;
- Frappe lifecycle entry/exit, site, actor, request/job identity and exception result;
- enqueue/dequeue, retry, worker site context and post-commit outbox dispatch;
- route source and bypass flags for every synthetic request.

Values, credentials, document bodies and personal fields are redacted. Logs are
append-only, hashed and correlated to the manifest. Instrumentation cannot issue
financial writes, commits, DDL, network calls or approval waits while observing.
No probe is allowed to claim a lock order until the underlying DB/session evidence is
present. A missing trace is `UNKNOWN`, never inferred success.

## Readiness evidence register

| Evidence | Required artifact | Status |
|---|---|---|
| A1 pins | source/image hashes and installed versions | PASS — exact R1 inputs and versions |
| A2 services | private MariaDB/Redis health and version output | PASS |
| A3 site | fresh synthetic site and installed-app manifest | PASS |
| A4 migration | clean migration and rerun result | PASS |
| A5 isolation | no public listeners, synthetic-only data, file/worker scope | PASS |
| A6 instrumentation | redacted transaction/SQL/lock/lifecycle trace | PASS — structured harmless probe |
| A7 recreation | clean rebuild from scripts and manifest | PASS — second clean build |
| A8 handback | COMPAT-001 evidence bundle with hashes/reviewer | PASS — persisted review |

The verifier requires installed versions `frappe 16.33.1`, `erpnext 16.34.2` and
`lending 16.5.0`, verifies the three source archive hashes, and hashes every regular
file in the evidence directory except the manifest being generated. A6 requires a
structured probe containing site, session, transaction, SQL, lock, timestamp and
correlation fields. Any `UNKNOWN` in required evidence causes the verifier to fail;
it cannot be treated as acceptance evidence.

## 8. Execution result

On the private `berp-linux` VM, the frozen checkpoint runner passed STEP-01 through
STEP-07 with `unknown_count=0`. Both the initial site and a clean destroy/recreate
run installed `frappe 16.33.1`, `erpnext 16.34.2` and `lending 16.5.0`; migration
and safe rerun passed; MariaDB and Redis remained private; and the structured probe
recorded site, session, transaction, SQL, lock, timestamp and correlation fields.
The A7 comparison is persisted as `evidence/recreation-compare.txt`, and the A8
review is persisted as `evidence/a8-handback-review.txt`. No financial test ran.

## Failure and handback rules

If a dependency cannot install, classify `C-PIN` only after confirming the exact pin,
environment and reproducible command. If a transaction or lock observation conflicts
with 001B, classify it first as observation or mapping evidence. If it proves an 001A
invariant cannot be satisfied, create a `C-ARCH` finding and return to 001A review.
Do not patch upstream, add an MFI hook, weaken a lock order, or call a financial test
green to make the lab pass.

The acceptance contract is complete for lab readiness. Hand back only the immutable
manifest, redacted logs, topology and recreation commands. COMPAT-001 now resumes C02
transaction topology, then C03 lock-order feasibility, before any financial prototype
or Model A test. B-BLK-01, B-BLK-02 and B-BLK-03 remain open and IMP-001 remains locked.
