# 001B — Enforcement, Upstream Integration and Test Registries

Companion to [001B](BERP-MFI-ARCH-001B.md). Status: DRAFT; no tests executed.
This document contains registries 12–14. `EN` identifiers are proposed MFI service
contracts, not existing functions. `U` identifiers identify inspected upstream
symbols or explicit pending mappings. `B-T` identifiers are executable-test designs.

## 12. Enforcement registry

Each EN row inherits this supported-path policy:

- Desk/custom API: call the authorized operation; native financial submit must
  either reach the same guard before effects or be denied without financial mutation.
- Generic REST/document RPC: identity/permission check plus the same document guard;
  no endpoint may trust a caller-supplied “already authorized” or bypass flag.
- Import: drafts may enter only where the row permits; imported financial submission
  is denied except a separately authorized maintenance contract through EN12.
- Job: scoped service identity plus originating action; no bypass merely for scheduler.
- Direct business method: either complete EN guard + transaction owner or unsupported
  and inaccessible to business users. Function existence is not support certification.
- Raw SQL, `db_set`, console and patches: governed trusted-code boundary EN12, not
  a claim that ordinary Frappe hooks intercept all database writes.

Method names below are exact proposed addresses for later implementation. Their
presence in documentation does not create callable APIs, schemas or hook registration.

| EN | Object / action | Proposed MFI boundary | Upstream mapping / transaction owner | Required guard and path differences | Tests |
|---|---|---|---|---|---|
| EN01 | E01/E07/E09–E15/E58/File read and scope validation | `berp_mfi.services.authorization.authorize` | U01 + native query/file routes pending U07; caller is read-only | Resolved site, active assignment, exact actions/fields/account or case; guessed event/result denied; all read surfaces | B-T01,B-T14 |
| EN02 | E19/E20/E21–E26 reserve, consume, release | `berp_mfi.services.exposure.transition` | MFI operation owns transaction; disbursement consumes within EN03 | K11–K14, all scopes locked, conservation, revision/quorum; direct projection writes/import denied | B-T05,B-T06,B-T07 |
| EN03 | E27–E32 submit/cancel/amend | `berp_mfi.adapters.lending.guard_mutation` | U02,U03 observed; U06 remainder pending; EN07 for funded repayment, otherwise one MFI operation | Capability, KYC, authority, reservation, date/source; early document guards plus pre-effect controller integration. Native bypass denied | B-T06,B-T07,B-T09 |
| EN04 | E52/E54 event claim and result | `berp_mfi.services.events.claim` | MFI transaction envelope, unique-claim conflict handling | K09/K23, hash/source semantics, authorized retry, HTTP mutation verb; job/import uses same identity | B-T02 |
| EN05 | E12/E35–E38/E43–E46 debit, credit, transfer, hold | `berp_mfi.services.deposits.transition` | MFI operation; candidate deposit voucher U04 pending proof | Currency/site/mandate/KYC/hold/funds; account and till locks; no direct ledger writes; draft import only | B-T08,B-T13 |
| EN06 | E39–E42 accrue/correct | `berp_mfi.services.accrual.transition` | MFI owns deposit transaction; Lending accrual owner U06 | K18–K20 stream/chain guard, non-overlap, immutable net/evidence; job has no validation exemption | B-T03,B-T04 |
| EN07 | Deposit-funded loan repayment | `berp_mfi.services.posting.repay_from_deposit` | MFI owns single transaction; U03 allocation/loan GL + U04 candidate deposit voucher | Same site/company/currency, mandate target, locked allocation, X equality and C=0. Import/bulk shortcut unsupported | B-T10,B-T13 |
| EN08 | E47/E52 full reversal | `berp_mfi.services.posting.reverse` | MFI owns reversal transaction; U03/U04 cancel behavior pending | Original-event uniqueness, independent approval, period/dependency checks; no partial v1 reversal | B-T11 |
| EN09 | E53/E56/E57/E69 evidence/delivery | `berp_mfi.services.evidence.record` | Financial evidence/outbox in posting transaction; denied-action audit separately after rollback | Redact, immutable identity, post-commit at-least-once dispatch; delivery never reposts funds | B-T15 |
| EN10 | E55/E62 reconcile/close | `berp_mfi.services.reconciliation.close` | MFI close transaction, read Lending/ERPNext canonical totals | K24/date guard, no residuals/netting/plug journals; unknown outcomes block close | B-T12 |
| EN11 | E59–E61 MFI control-account posting | `berp_mfi.services.posting.guard_control_accounts` | U04/U05 native controllers; lower GL path U08 pending | Approved E52/E53/E67 source and single voucher role; native Desk/REST/integration cannot add extra leg | B-T09,B-T10 |
| EN12 | Trusted code, migrations, special imports | Controlled maintenance registry; no public service endpoint | Exact deployment/code permissions and full call inventory pending U09 | Raw SQL/db_set/commit/bypass flags cannot be user policy escapes; approved maintenance source and reconciliation | B-T16 |
| EN13 | E02–E08/E12/E58/E64–E67 policy/assignment amendment | `berp_mfi.services.policy.activate` | MFI operation owns transaction | Independent approval; policy revision lock; no scope reset; expired delegation; conflict deny; invalidates old approval | B-T07,B-T17 |

Global lock order remains 001A §5. No EN function is permitted to invert that order.
Inter-operation calls participate in the outer transaction; they do not commit their
own “successful” legs. Exceptions roll back, and retries are bounded with stable identity.

### Path registry: required coverage per object family

| Family | Desk | REST/RPC | Import | Job | Direct method | Bypass flags / exception |
|---|---|---|---|---|---|---|
| Lending disbursement | Native submit/cancel→EN03 or deny | Same EN03 | Draft only; posting EN12 | Scoped EN03 | U02 methods guarded or inaccessible | Framework flags U01; full upstream inventory pending |
| Lending repayment/refund/repost | EN03/EN07 | Same | `is_imported` path unsupported for G5 | Scoped EN03; bulk path not presumed safe | U03 on_submit/make_gl_entries; refund/repost U06 pending | `is_imported`, `from_bulk_payment` observed; deny G5 shortcuts |
| Restructure/write-off/waiver/accrual | EN03 or deny | Same | EN12 only for financial import | Canonical jobs U06 pending | Exact modules/functions pending | No guessed “safe scheduler” exemptions |
| Journal/Payment Entry | EN11 | Same | Same control-account guard | Scoped EN11 | U04/U05 GL paths; U08 lower-level pending | `ignore_permissions` not MFI policy authority |
| MFI deposits/accruals | EN05/EN06 | Same | Draft staging only | Scoped same service | No exposed raw posting method | Context proof must be server-owned, not JSON field |
| Policy/mandate/exposure | EN02/EN13 | Same | Proposed drafts only | Expiry via same locks | Projection/ledger direct writes deny | No `migration=true` caller escape |
| Private file/report/search | EN01 | EN01 | Import attachment retrieval still EN01 | Narrow explicit principal | Native data access inventory U07 pending | Field permlevel alone insufficient |

Actual Desk URLs and REST route handlers depend on 001C pins and are pending, not
invented here. Expected canonical document route classes are established, but each
route/handler and job entry must be named in the compatibility evidence manifest.
Each B-T09 instance below enumerates actor × object × path × bypass-flag case;
an unenumerated financially capable path remains unsupported and blocks acceptance.

## 13. Upstream integration registry

Read-only source snapshots collected 2026-09-15 from `version-16` refs:

| Project | Immutable inspected commit | Meaning |
|---|---|---|
| Frappe | `988e54f3c4c291e2077a83809663f123731abe76` | Source snapshot, not accepted runtime pin |
| ERPNext | `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` | Source snapshot, not accepted runtime pin |
| Lending | `06fc075ae062ce38ac38a763f7f290da4ddd6fdb` | Source snapshot, not accepted runtime pin |

### Verified symbols and relevant observations

| U | File / methods observed | Concrete evidence | Scope of proof |
|---|---|---|---|
| U01 | `frappe/model/document.py`: `_save`, `check_if_latest`, `load_doc_before_save`, `run_before_save_methods`, `run_post_save_methods`, `_submit`, `_cancel`, `db_set` | `_save` checks latest at 588, before pre-save methods at 594; latest loads prior doc with `for_update=True` at 1432. `ignore_validate` returns before `before_submit`/`before_cancel` dispatch at 1407–1417 | Normal lifecycle ordering inspected; transitive effects and all APIs not proven |
| U02 | `lending/loan_management/doctype/loan_disbursement/loan_disbursement.py`: `validate` 108, `on_submit` 182, `on_cancel` 327, `make_gl_entries` 781 | `on_submit` mutates schedules/status/security and calls GL at 200 | No guarantee that after-submit hook can prevent earlier effects |
| U03 | `lending/loan_management/doctype/loan_repayment/loan_repayment.py`: `validate` 114, `on_submit` 183, `on_cancel` 716, `make_gl_entries` 2093 | `is_imported` updates paid amounts and returns at 184–187; `flags.from_bulk_payment` returns at 209–210 | Branches observed; no complete repayment/cancellation/commit proof |
| U04 | `erpnext/accounts/doctype/journal_entry/journal_entry.py`: `validate` 128, `submit` 186, `cancel` 195, `before_submit` 201, `on_submit` 206, `on_cancel` 296, `make_gl_entries` 1221 | Method existence/locations inspected | Voucher type/account compatibility unproven |
| U05 | `erpnext/accounts/doctype/payment_entry/payment_entry.py`: `validate` 172, `on_submit` 203, `on_cancel` 297, `make_gl_entries` 1328 | Method existence/locations inspected | Never selected as additional G5 leg |
| U06 | Other Lending action/job paths | Exact pinned functions for application, loan, refund, repost, restructure, waiver, write-off and accrual remain TBD | B-BLK-02; unsupported until inventoried/tested |
| U07 | Native read/file/report/search and REST/RPC/import dispatch | Exact handlers and leakage/bypass paths remain TBD from compatibility work | B-BLK-02; no claim of complete route coverage |
| U08 | Lower-level GL posting and cancellation entry paths | Exact global accounting guard point remains TBD | B-BLK-02/03; controller guard alone not universal |
| U09 | Raw DB calls, app patches, flags and trusted worker entry paths | Full transitive inventory, commit/DDL/external effects and permission flags remain TBD | B-BLK-01/02/03 |

Immutable evidence links:

- [U01 Document lifecycle](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/model/document.py#L559)
- [U02 disbursement](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/lending/loan_management/doctype/loan_disbursement/loan_disbursement.py#L182)
- [U03 repayment](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/lending/loan_management/doctype/loan_repayment/loan_repayment.py#L183)
- [U04 Journal Entry](https://github.com/frappe/erpnext/blob/4048fb70e14d1843956fcdabb7c3cca75a1cbcdd/erpnext/accounts/doctype/journal_entry/journal_entry.py#L186)
- [U05 Payment Entry](https://github.com/frappe/erpnext/blob/4048fb70e14d1843956fcdabb7c3cca75a1cbcdd/erpnext/accounts/doctype/payment_entry/payment_entry.py#L203)

### Blocked findings returned to the 001A review

| Blocker | Conflict/dependency | Required resolution; no invariant weakening |
|---|---|---|
| B-BLK-01 | Hook-only placement cannot establish policy→scope→account locks if framework has already locked the financial document; U01 shows early `for_update`. Validation flags also skip some lifecycle guards | Prove entry interception before early locking, or deny that native mutation path before acquiring further locks and use a verified orchestration path. Full lock graph/flag tests required; return any changed ordering proposal to 001A |
| B-BLK-02 | Exact route, direct business method, trusted-job and lower-level accounting coverage is incomplete; pre-submit alone is insufficient | Complete pinned call inventory and guard registrations, forbid unsafe bypass paths, run all path×actor negative tests. No fabricated hook registrations |
| B-BLK-03 | Single-commit G5, settlement-control account C, canonical allocation and full reversal not experimentally proven | Authorized compatibility work proves matched vouchers, callbacks/commits and fault recovery. Model A remains proposed; no automatic Model B fallback |

These blockers apply to acceptance, not to writing the remaining design sections.
Observed source ordering is not a demonstrated production vulnerability. The source
snapshots may require replacement by certified 001C pins and reinspection.

## 14. Positive and negative test registry

All tests NOT RUN. Fixtures are synthetic and carry no production thresholds.
Each EN route must have at least a successful authorized case and a denied/inconsistent
case. The registry is a specification, not a test result or test implementation.

| Test | Positive case | Negative/fault case and oracle | Existing 001A test link |
|---|---|---|---|
| B-T01 | Same-I scoped party/account read | Different I/company, guessed event, expired assignment or unentitled branch denied with no data; no source row changes | A-G4-01 |
| B-T02 | Repeat event yields same authorized result | Same key/different payload conflicts; different key/same source cannot double post; GET cannot mutate; retained identity survives retry | A-G5-02 |
| B-T03 | Adjacent stream intervals post once | Overlap, same interval/new version/new sequence, empty/reversed interval and first-row race deny duplicate base | A-G2-02/03 |
| B-T04 | Base 10→target12→target9 gives +2 then -3 | Stale revision/concurrent correction cannot duplicate delta; zero result emits no GL; erased original denied | A-G2-01/04 |
| B-T05 | Reservation fits every scope | Two 60 requests against 100 or cross-product/group bypass cannot jointly reserve; no partial scope success | A-G3-01/02 |
| B-T06 | Partial draw consumes once and becomes booked | Replay/expiry race, excess draw, second consumer or release of consumed amount denied; conservation holds | A-G3-03 |
| B-T07 | Approved limit/group/delegation amendment preserves exposure | Rule version cannot reset positions; no-match/conflict, own approval, budget recycling, stale approval or expired delegation denies | A-G3-04,A-G4-03 |
| B-T08 | Authorized hold/deposit/till transfer | Concurrent withdrawal/hold cannot overspend; source/target mismatch or second active till denied; two-leg rollback | A-G5-03 |
| B-T09 | Valid financial submission reaches the intended guard | For each object/Desk/REST/import/job/direct method, try absent authorization and observed bypass flags; no financial side effect. Include native control-account journal and DB trust-boundary review | A-G4-01/02/03 |
| B-T10 | X=100 liability/C and C/allocation post with C=0 | Crash before/after each leg/commit; imported/bulk shortcut, extra Payment Entry, nested commit, unsupported fee/overpayment denies or rolls back; response loss returns same event | A-G5-01/02 |
| B-T11 | Independent full reversal restores both ledgers once | Duplicate/partial/stale/dependency-unsafe reversal denied without partial compensation; closed period stays enforced | A-G5-04 |
| B-T12 | Reconciled source/control totals allow close | Wrong dates, residual C, hidden netting, unknown settlement or balancing plug blocks close; unexplained projection mismatch blocks increases | A-G5-05 |
| B-T13 | Explicit mandate allows same-currency loan funding | Identity match alone, wrong target, different company/currency/site, hold or changed allocation cannot fund; no material approval drift | A-G5-03 |
| B-T14 | Authorized case-specific file/field/report read | Search/export/print/download/raw report or outbox cannot leak AML/ID/account info through weaker route | A-G4-01 |
| B-T15 | Atomic success audit/outbox and deduplicated delivery | Rollback leaves no success/outbox; denial retains redacted audit; delivery retry or old lease never changes balances | A-G5-01 |
| B-T16 | Approved opening/migration with source evidence reconciles | Caller-controlled migration/bypass flag, raw DB financial writer or ungoverned worker cannot be accepted as safe; maintenance audit incomplete blocks release | A-G4-01/02 |
| B-T17 | Approved capability run-off and policy revision | Deposit-disabled preset, new activity under expired license or failed dependency denies; rule/mandate concurrent edits revalidated | A-G4-03 |
| B-T18 | Approved product/mandate version and zero-balance closure | Editing posted currency/terms/evidence, closing with residual/hold or conflicting version denied | A-G5-04 |
| B-T19 | Deadlock rolls back whole event then bounded retry succeeds once | Lock-order inversion, commit in nested call, network/human wait under locks or second independent event fails acceptance | A-G5-01 |
| B-T20 | Reviewed evidence bundle names pins, inputs and outcomes | Missing case/expected values/reviewer, empty register or document-only “pass” cannot accept a financial gate | 001A §8–9 |

Acceptance evidence must enumerate test instances, not only these 20 family labels.
Positive cases never bypass independent checks to simplify setup. No live users,
money, credentials or tenant datasets are used by this design unit.
