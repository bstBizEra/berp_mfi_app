# A7 historical queue divergence review

Status: HISTORICAL EXPLANATION / A7 ACCEPTANCE NOT ESTABLISHED

Reviewer: independent read-only investigator `/root/investigate_a7`.
Review date: 2026-09-15. Scope: retained build1 archive, build2 readiness
evidence, and pinned runtime enqueue implementation on private `berp-linux`.
No migration, worker, purge, financial operation, or remote write was performed.

## Finding

The 13 versus 5 long-queue difference is accounted for by unequal readiness
execution histories. Build1 has six checkpoint rounds; build2 has two. Each
round runs migration twice. The pinned migration implementation directly
enqueues a new search-index job on each invocation.

| Observation | Build1 | Build2 |
|---|---:|---:|
| Initial site-creation migration | 1 | 1 |
| Recorded checkpoint rounds | 6 | 2 |
| Migrations from those rounds | 12 | 4 |
| Expected accumulated search-index jobs | 13 | 5 |
| Final doctor long-queue count | 13 | 5 |
| Final STEP-04 long-queue count, before verifier migration | 12 | 4 |
| Final doctor default-queue count | 12 | 12 |
| Workers online in doctor snapshots | 0 | 0 |

Arithmetic: `1 + (2 * 6) = 13`; `1 + (2 * 2) = 5`; the four additional
readiness rounds account for eight additional jobs. This is strong causal
accounting for deterministic accumulation, not direct inspection of every
historical enqueue. It does not establish a timing or isolation defect.

## Evidence provenance

Remote root: `/home/berpadmin/berp-mfi-compat-r1`.

The retained `evidence-build1.tar.gz` SHA256 matches its recorded
`evidence-build1.sha256`:
`dd5a3bbb6811ced530ec7246adfaeb7add6ee583c108621e6773910b99ac3ef6`.
Archive members below have the prefix `evidence/`. Build2 files are in the
current root's `evidence/` directory as observed during this review.

| Evidence | Location/range | Observation |
|---|---|---|
| Build1 checkpoint history | Archived `checkpoints.jsonl`, lines 1–42 | Six seven-step rounds, 01:26:39Z–01:37:13Z |
| Build2 checkpoint history | `checkpoints.jsonl`, lines 1–14 | Two seven-step rounds, 01:45:52Z–01:48:25Z |
| Final doctor | Both `doctor.log`, lines 12–15 | Long queue contains 13 versus 5 `build_index_for_all_routes` jobs |
| Pre-verifier doctor | Both `STEP-04.log`, lines 12–15 | Long queue contains 12 versus 4 of that method |
| Service observations | Both doctor logs, lines 2–5 | Scheduler disabled/paused/inactive, workers online zero |
| Default queue | Both doctor logs, lines 7–10 | Twelve `frappe.model.delete_doc.delete_dynamic_links` jobs |
| Initial migration output | Both `site-create.log`, line 2740 | One retained `Queued rebuilding of search index` message |
| Latest migration outputs | Both `STEP-03.log` and `migrate-rerun.log`, line 1372 | One retained `Queued rebuilding` message per file |

The final STEP-04-to-doctor increase is one job in each build, matching the
intervening verifier migration. Earlier per-step logs were overwritten by later
rounds; the append-only checkpoint records retain their execution outcomes but
do not retain full earlier log contents. In particular, an earlier STEP-07
failure alone does not prove where that invocation failed.

Recorded artifact SHA256 values:

| Artifact | Build1 | Build2 |
|---|---|---|
| `site-create.log` | `6117749d264535ff18f93797e77169abf8b31192febaf6e0765fc648bea2b911` | Same |
| `STEP-03.log`, `migrate-rerun.log` | `4631335350e25f34c00f2d4de235d83e98b41317880010304e07e33e9f7913bd` | Same |
| `doctor.log` | `8e22787325ebb024d1b5a5b06d15f49e22506b242af8e65fdffa1c9b4460206e` | `dedd134eedbf109bb623b14af0a3d38e6abf8d96cd42177bc83f57b02b14c730` |
| `STEP-04.log` | `5572f2e9859e7f43081d6038d84c48e1c0929a92731ae37be5c8669685386b5e` | `b9b270b934a29bb982b812a600d550a56e4d02cc6a8558e5c8f7c146e4854558` |

## Execution and source mechanism

Repository paths below are relative to `docs/compat-001/`:

- `create-site.sh:24`: initial migration.
- `run-checkpointed-readiness.sh:61–62`: STEP-03 migration followed by STEP-04 doctor.
- `run-checkpointed-readiness.sh:65`: STEP-07 invokes the verifier.
- `verify-lab.sh:55–56`: another migration followed by doctor.

Runtime paths below are relative to the lab's `bench/apps/frappe/`. These were
inspected directly in the R1 lab; the configured Frappe source pin is
`988e54f3c4c291e2077a83809663f123731abe76`.

- `frappe/migrate.py:77–82`: `skip_search_index` defaults to false.
- `frappe/migrate.py:98–112`: teardown directly calls
  `frappe.enqueue(build_index_for_all_routes, queue="long")` when indexing is not skipped.
- `frappe/utils/background_jobs.py:84,89–90`: `enqueue_after_commit=False`,
  `job_id=None`, and `deduplicate=False` defaults.
- `frappe/utils/background_jobs.py:192–209`: queue insertion occurs immediately
  unless after-commit behavior is requested.
- `frappe/utils/background_jobs.py:649–661`: an omitted job ID receives a fresh
  UUID namespaced to the site.

Therefore disabling the scheduler does not suppress this direct enqueue from
migration. Repeated migration can accumulate pending search-index jobs when no
worker consumes them. Database migration success or identical migration logs
do not establish identical queue state after different numbers of invocations.

## Limits and disposition

Build1 Redis was destroyed. Its individual job IDs, payloads, enqueue timestamps,
and continuous worker history cannot be reconstructed from these doctor logs.
The archive hash verifies consistency with the retained checksum; it does not
independently attest original collection or recover evidence that was never saved.
The inspected runtime source explains the mechanism but is not a runtime trace
of every historical enqueue.

The aggregate discrepancy is explained by unequal operation schedules, with
the limits above. A7 remains subject to renewed semantic recreation evidence:
matched operation schedules, matching observation boundaries, and queue contents
compared by site, method, and status rather than UUID or Python memory address.
This review makes no claim about subsequent fresh builds and does not accept A7
or A8. C03 and all financial/implementation gates are unaffected.
