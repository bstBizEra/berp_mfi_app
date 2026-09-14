# BERP-MFI-ARCH-001A — Financial Integrity & Enforcement Contracts

Status: DRAFT FOR REVIEW — specification only, not accepted or implemented.
Date: 2026-09-15. Parent: [BERP-MFI-ARCH-001](BERP-MFI-ARCH-001.md).
Findings: F02–F05 in [BERP-MFI-AUDIT-001](BERP-MFI-AUDIT-001.md).

## 1. Authority, scope and gates

This child refines financial identities, concurrency, enforcement and repayment
posting. It does not replace the deposit/non-deposit parent. Its proposed correction
to the parent's rule-version accrual key requires review; publication is not acceptance.
The original audit remains historical and its findings remain open.

| Gate | Required contract | Current state |
|---|---|---|
| G1 | Deposit and lending remain first-class capabilities | Parent retained; no implementation evidence |
| G2 / F02 | Stable economic accrual and controlled correction | Specified below; untested |
| G3 / F03 | Atomic exposure reservation and authority consumption | Specified below; untested |
| G4 / F04 | Enforcement on every supported mutation path | Required coverage defined; exact upstream map pending |
| G5 / F05 | One deposit-funded repayment across subledgers and GL | Model A proposed for v1; executable proof pending |

Only documentation is authorized by this unit. No application scaffolding, schema,
fixtures, real accounts or live transactions are created. An isolated executable
compatibility investigation requires a separately authorized work unit; its results
must be available before an implementation baseline is accepted. This separates
investigation evidence from production app scaffolding and avoids pretending that
paper review proves upstream transaction behavior.

`001B` will produce the canonical data model/enforcement registry; `001C` the runtime
and packaging contract. Both are planned, not delivered or accepted here. Their
schema/runtime decisions may refine this draft but cannot weaken its invariants.

## 2. Definitions and common event envelope

One institution operates inside an already resolved Frappe site. Company, account,
party, branch and currency links are validated server-side. No route or customer
input selects a different site. Hostname/gateway provisioning is outside this app.

Every mutation carries:

| Field | Contract |
|---|---|
| business_event_id | Server-issued durable identity, unique within site/institution |
| source namespace + source_transaction_id | Durable business source; unique for the action, even if transport key changes |
| idempotency_key + request_hash | Unique per institution/principal namespace/operation; same key and different payload is rejected |
| actor + originating_actor | Authenticated executor and initiating human/service; immutable attribution |
| institution/company/account references | Validated resolved records, not trusted claims |
| expected_revision + approval reference | Binds the action to material terms, policy and approved revision |
| amount/currency/value_date/posting_date | Decimal, explicit precision; date policy and period restrictions checked |
| policy/calculation versions | Immutable decision evidence, never a new economic identity |
| operation state + result references | Durable outcome, voucher/subledger IDs, reversal and recovery links |

Canonical hashing normalizes currency, decimal scale, dates and material fields.
Idempotency records persist for the business event's retention life. A new transport
key cannot circumvent the stable source identity. All reads of an existing result
still require authorization; guessed event IDs must not disclose another account.
Financial POST operations never execute as GET requests.

Denied actions create redacted security evidence independently of rolled-back
financial writes. Successful financial audit/outbox records commit with the event.
Do not write secrets or full KYC payloads to either log.

## 3. G2 — Economic accrual identity

An original accrual recognizes one component on one account for one economic
half-open interval `[start, end)` in an identified time/calendar basis. Components
distinguish principal interest, penalty, fees and other approved accrual categories.
The interval basis must distinguish daily, sub-day or contractual periods explicitly.

### Identity and segmentation

Base identity: institution + account + component + interval_start + interval_end.
Account currency is immutable. A segment sequence is ordering metadata within an
approved partition, NOT an additional uniqueness escape hatch. Rule, rate, job,
calculation and policy versions are evidence attributes, not base identity fields.

Exact uniqueness is necessary but insufficient: overlapping active base intervals
for the same account/component are forbidden. Serialize through a stable accrual
stream lock keyed by institution/account/component. Under that lock, check all
overlaps before insertion. The lock row itself is created using a unique key with
race-safe retry; absence of an existing accrual row must not mean absence of a lock.
Detailed storage/index choice belongs to 001B; an ordinary composite unique index
alone cannot enforce non-overlap.

An approved partition defines rate-change boundaries. Adjacent segments are allowed;
overlapping segments are not. After posting, a new partition cannot produce another
base accrual over already covered time. Recalculate over the original covered
interval and issue an adjustment; retain the new computational segments as evidence.

### Calculation and correction

Persist basis snapshot, rate/day-count/calendar, calculation version, policy version,
unrounded result, rounding method, posted amount and voucher references. The net
recognized amount is base plus all posted linked adjustments, never a mutable field.

For a correction, lock the accrual stream and original chain. Recalculate the target
for the covered interval; delta = approved target minus current recognized net.
Store expected chain revision and unique correction request identity. If the chain
changed, reject/recompute and reauthorize material changes; do not apply a stale delta.
Zero delta records the reviewed result without an unnecessary financial posting.
Post only the delta through a linked adjustment voucher, retaining original evidence.
Cancellation/reversal uses the same serialized correction chain, not deletion.

Example using abstract currency units: base 10, corrected target 12 → adjustment +2.
Retry the same correction → no new posting. Later target 9 → adjustment -3. Net 9.
Two corrections starting from net 10 cannot both add +2 after one has committed.

Lending remains owner of loan accrual mechanics. This identity contract directly
governs MFI-owned deposit accruals; the Lending adapter must map equivalent source/
correction evidence without creating a second loan accrual ledger. If the pinned
release cannot satisfy the invariant, affected functionality stays disabled.

## 4. G3 — Exposure positions, reservations and authority

Logical records: MFI Exposure Position, MFI Exposure Reservation, MFI Authority
Consumption. These are contract names, not finalized DocType schemas.

### Limit scopes

Evaluate ALL applicable limits: borrower across products, connected borrower group,
product, branch, institution, and delegated approval/disbursement budget. A key with
every dimension populated can accidentally split a global borrower limit by product.
Use explicit scope type + scope owner + optional scope dimension + currency basis +
aggregation window. Resolve a set of applicable scope keys per decision.

Rule identity/version is decision evidence. Changing a rule must not reset the
existing exposure position; map new rules onto stable economic scope keys. Overlap,
no-match and conflicting policy rules deny new commitments until resolved. Group
membership changes require locked remapping/revalidation, not erasing old obligations.

Each rule defines included principal, commitments, guarantees, fees or other exposure;
undrawn approved commitments are counted as reservations. Avoid counting a consumed
reservation and its newly booked principal twice. All obligations count once per
applicable scope even if they have multiple memberships/links. Distinct scopes may
each legitimately count the obligation for their own independent limit check.

### Reserve and consume

1. Resolve active policy/assignment revision and all applicable scope owners.
2. Claim the stable request identity, then acquire policy/scope locks in global order.
3. Re-read policy revision, existing exposure, active reservations and request terms.
4. For every scope check booked exposure + open reservations + requested delta ≤ limit.
5. Validate maker/checker, quorum, product/currency and effective delegation.
6. Atomically save approval, reservation allocations for every scope and audit event.

Reservation fields: source revision, approval, original amount, outstanding reserved
amount, consumed amount, released amount, currency basis/rate snapshot, expiry,
scope allocations, status and immutable event history. Conservation:
original amount = outstanding reserved + consumed + released, with explicit signed
adjustment events for any authorized change; never overwrite history to make it fit.

Disbursement locks the reservation AND the same applicable exposure scopes, plus
the loan/disbursement capacity. It revalidates approval and policy, consumes only
remaining capacity, replaces reservation exposure with booked exposure, and posts
the canonical financial event in the same transaction. A partial draw cannot exceed
either remaining authorization or remaining reservation. Replay consumes nothing.

Before financial implementation, define the exact exposure-event basis per product.
This draft does not invent a credit ceiling or assume all limits are revolving.
Single-currency is the initial acceptance scope. FX exposure remains disabled until
conversion source, conservative rounding, revaluation and existing-reservation
treatment are independently specified and tested.

### Release and lifecycle

Expired/cancelled approvals release only unconsumed capacity under the same locks.
Consumed capacity is not released by reservation expiry. A posted repayment may
reduce booked exposure according to the rule; a cumulative approval budget does
not automatically replenish. Reversal adjusts only capacity actually restored by
the financial reversal. Every release has its own stable reference and cannot recur.

Expiry worker and disbursement race under the same locks: exactly one valid outcome
wins. Unknown external outcomes retain reservations until conclusively reconciled.
Limit reductions can place existing exposure over limit; preserve obligations,
prevent increases and initiate review rather than deleting balances. Concurrent
policy changes require a revision check protected by the policy lock protocol.

## 5. Locking and transaction discipline

Required global ordering for all financial writers: policy revision guards → stable
exposure scope keys → reservation/authority records → financial accounts/loans →
accrual streams/event chains. Within each class use sorted stable IDs. Claim unique
event identity first; an event retry reads/waits for that outcome, never starts a
second independent financial action. Re-resolve scope membership after policy locks.

All writers, including hold creation/release, approval expiry, rate corrections and
scheduled accruals, must participate in the applicable lock protocol. If upstream
Lending acquires conflicting locks, the compatibility work must choose a proven
common order; this draft does not certify that upstream currently follows it.
Deadlocks roll back the entire transaction and receive bounded idempotent retries.
No network call or human approval wait occurs while financial DB locks are held.

Local transactions may not issue nested commits, DDL or external irreversible
effects. Financial outbox dispatch is post-commit, with at-least-once delivery and
consumer deduplication. A lost HTTP response is an unknown client outcome, not a
reason to generate a new event. Resume/query the same durable identity.

## 6. G4 — Required enforcement registry

Every supported route converges on the same authorization service and a document/
posting guard. A custom API alone is not the boundary. The following is REQUIRED
coverage, not a claim that exact hooks have been verified in a selected release.

| Object/action | Policy and atomic guard | Routes that must be covered |
|---|---|---|
| Application/approval/limit amendment | Revision, KYC policy, authority, SoD, scope reservation | Desk, REST, imports, business methods |
| Loan Disbursement submit/cancel | Capability, contract/KYC, capacity, reservation consumption or reversal | Direct DocType submit, adapter, bulk jobs |
| Loan Repayment/refund/repost | Funding mandate, source identity, allocation ownership, dates and reversal linkage | Direct submission, adapter, scheduler, integration |
| Restructure/write-off/waiver | Independent approval, exception limits, original-contract links | Upstream methods, documents, jobs |
| Deposit debit/credit/transfer | Capability, mandate, holds, funds, economic identity | All financial services; generic direct writes denied |
| Accrual/fee generation/correction | Stream lock, no overlap, policy snapshot, authorized adjustment | Scheduler, retry, imports, manual correction |
| GL/Payment/Journal operations touching MFI control accounts | Approved source voucher, event ownership, no duplicate leg | ERPNext native entry points as well as MFI services |
| Policy/role/entitlement changes | Independent approval, assignment allowlist, revision invalidation | Configuration UI, REST, migration paths |

Map `validate` for early feedback; perform authoritative rechecks before irreversible
effects at submit/cancel services and the lowest supported document guard. `on_submit`
must not be the only check if effects occur earlier. Amendment creates a fresh
revision requiring authorization; there is no assumption of a universal `amend`
hook. Account balances and ledger entries reject ordinary edit/delete endpoints.

001B must list for each pinned DocType: exact module/function, event ordering,
supported interception point, flags/permission bypasses, transaction owner, tests
and unsupported entry paths. Hooks can be bypassed by direct database writes;
`db_set`, raw SQL, patches and background code require a governed trusted-code
boundary and inventory. Arbitrary server scripts/console access is not a business
user capability. Migration mode is a separately controlled maintenance procedure,
not a request-controlled bypass flag.

Trusted jobs use scoped service identity and immutable initiating context; neither
background execution nor `ignore_permissions` exempts policy checks. Framework/root
administrators remain an infrastructure trust boundary with break-glass evidence.
Read/list/report/export/file permissions belong in 001B and must not be mistaken
for write-policy enforcement. KYC identity visibility does not grant account access.

## 7. G5 — Deposit-funded repayment, proposed v1 contract

**Select Model A for the proposed v1 implementation contract. Activation is blocked
until atomicity is proven for pinned dependencies.** Model B is not a second enabled
runtime mode or automatic fallback. If A fails the compatibility proof, revise this
document with a separately reviewed clearing contract before implementing the feature.

Scope: same institution/site/company and same account/loan currency; no external
payment rail. A valid account mandate must authorize payment to this loan/borrower;
shared customer identity alone is insufficient. Cross-currency and cross-site
repayment are disabled. Third-party funding requires an explicit approved mandate.

### Owner and voucher contract

| Balance/event | Sole owner |
|---|---|
| Customer deposit movement | MFI deposit subledger |
| Loan principal, interest, fee allocation | Canonical Lending repayment |
| Authoritative financial statements | ERPNext GL |
| End-to-end business event and correlation | MFI financial orchestrator |

Define a matched internal settlement-control account C. The deposit leg produces
an MFI-supported voucher: Dr customer deposit liability X, Cr C X. The canonical
Lending repayment debits C X and credits its own allocated loan/interest/fee
accounts totaling X. Net C for this event is zero at the same commit. There is no
extra Payment Entry or cash/bank movement for this internal transfer.

These are accounting requirements, not verified upstream APIs. The compatibility
proof must establish that the chosen Lending repayment can use the approved C
account with correct validation, account types, dimensions and cancellation behavior.
Do not insert raw GL rows to force the proposed entries or duplicate Lending's GL.
Unsupported overpayment, fee deductions or tax behavior rejects the event rather
than silently changing X; require an explicit extension for those cases.

### One atomic operation

1. Resolve/claim event and stable source identity; compare payload/revision.
2. Lock applicable policy, exposure, reservation, deposit and loan records in the
   verified global order. Recheck mandates, holds, KYC action policy, dates and funds.
3. Compute the canonical repayment allocation using current locked loan state;
   persist the allocation result/basis. Material changes require fresh authorization.
4. Write the deposit transaction and its liability/C voucher; execute one canonical
   Lending repayment with the same amount and source reference.
5. Update applicable exposure positions without double-counting reservations.
6. Verify deposit movement = loan repayment tendered amount = X; verify both voucher
   legs balance and C nets to zero for this event, currency and company.
7. Persist posting batch, voucher links, successful audit, outbox and POSTED outcome.
8. Commit once. Send receipt/integration notifications from the committed outbox.

No intermediate financial state is externally committed. Durable request tracking
may have RECEIVED/REJECTED states, but POSTED means all accounting has committed.
Request rejection may be recorded after rollback in a separate non-financial
transaction. A PROCESSING marker or worker lease is never evidence of a debit.

### Crash and retry outcomes

| Crash point | Required persisted financial outcome | Recovery |
|---|---|---|
| Before locks or validation | No financial movements | Retry same identity or return rejection |
| After deposit leg, before Lending completion | Entire transaction rolled back | Re-run same identity after lock release |
| After Lending leg, before final validation/commit | Entire transaction rolled back | No standalone repayment survives |
| Commit succeeds, response is lost | All movements and POSTED event exist | Return original outcome; never post again |
| Commit outcome temporarily unknown | Unknown to caller; do not infer rollback | Query durable identity after DB recovery |
| Outbox delivery fails | Financial result remains POSTED | Retry delivery; consumer deduplicates |
| Process restarts with an old lease | No conclusion from lease alone | Resolve committed event and DB state first |

### Reversal

Lock the original event, affected balances and reversal identity. Original event
must be POSTED and not already fully reversed. Require independent authorization
and current date/period policy. Proposed v1 supports full reversal only.
Canonical Lending reversal/cancellation generates its own compensating accounting;
MFI generates the matched deposit adjustment and exposure change once. C must again
net to zero. Retain the original and link reversal batch/vouchers.

Subsequent accruals, payments, period closing or contract changes may make simple
reversal unsafe. In that case refuse the simple reversal and require an approved
dependency-aware correction plan; do not delete/rewrite history or partially commit.
An upstream cancellation that cannot meet the contract blocks this feature until
a tested correction path is specified.

## 8. Reconciliation and evidence

At event level verify source uniqueness, one canonical repayment, deposit debit X,
allocation sum X, balanced voucher set, and zero settlement-control residual.
For example X=100 with principal 80 and interest 20 yields deposit debit 100 and
loan tender 100, not 200; C credit/debit cancel without moving cash.

At close, reconcile by institution/company/currency/accounting date: deposit
subledger totals to mapped liability controls, loan source totals to mapped Lending
GL controls, and every internal settlement batch to zero. Timing bases and accrual
payables are reconciled separately; no netting across customers conceals differences.
Unexplained mismatches block close and raise a case, not an automatic balancing
journal. Approved migration/opening events require the same traceability.

Each evidence bundle includes code SHAs, schema version, case ID, synthetic inputs,
concurrency schedule/fault point, expected/actual source and GL balances, event IDs,
logs with sensitive fields removed, and reviewer outcome. No empty test register,
documentation review or working login is a passing financial gate.

## 9. Acceptance register and dependencies

All rows are NOT RUN. Amounts below are synthetic test units, not institution limits.

| ID | Scenario | Required result |
|---|---|---|
| A-G2-01 | Base 10, V2 target 12, repeated request | One +2 adjustment; net 12 |
| A-G2-02 | Same interval with different segment sequence/version | No second base accrual |
| A-G2-03 | Adjacent vs overlapping subintervals | Adjacent allowed; overlap rejected under concurrent writers |
| A-G2-04 | Concurrent correction targets 12 and 9 | Stale chain rechecked; final net matches authorized serial outcome |
| A-G3-01 | Capacity 100; two concurrent requests of 60 | At most one reserves 60 |
| A-G3-02 | Different products, same borrower-wide cap | Shared cap still enforced |
| A-G3-03 | Partial disbursement retry and simultaneous expiry | Capacity consumed/released once; no overdraw |
| A-G3-04 | Rule/version/group membership changes | No reset or escape of existing exposure |
| A-G4-01 | Direct REST/Desk/import/job submit without authorization | Every supported route denied |
| A-G4-02 | Native journal to MFI control account without valid event | Denied under business credentials |
| A-G4-03 | Amendment, extra role, expired delegation/KYC | Current policy evaluated; no stale approval bypass |
| A-G5-01 | X=100 repayment, crash at each tabled point | All-or-none accounting; zero event residual |
| A-G5-02 | Same key/different body; new key/same source | Conflict or original result; never duplicate |
| A-G5-03 | Parallel withdrawal/hold and repayment | No use of unavailable funds |
| A-G5-04 | Full reversal, repeated reversal, later dependent event | One valid compensation or controlled refusal |
| A-G5-05 | Close with unexplained deposit/loan/control mismatch | Close blocked; no balancing plug |

Acceptance requires 001A design review, exact 001B enforcement/schema mapping and
001C dependency/runtime pins, then authorized synthetic evidence for the gates.
Financial/accounting reviewer and application/security reviewer must be distinct
from the implementer for acceptance; reviewer identities and dates are currently
unassigned. F02–F05 remain OPEN, with draft remediation specified only.

001B must resolve party identity vs booking/servicing branch, account mandates,
sensitive KYC entitlements, state machines, indexes and supported upstream paths.
001C must confirm the actual Frappe layout, optional Lending activation, country-pack
interface and site boundary. No speculative platform app is a required dependency.
The example hostname in the supplied proposal is not a site rename instruction.

## 10. Sources and limitations

- [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks): potential
  extension mechanisms; availability is not proof of universal interception.
- [Lending version-16 repayment source](https://github.com/frappe/lending/blob/version-16/lending/loan_management/doctype/loan_repayment/loan_repayment.py): candidate
  source for the later call/commit/GL inventory; branch is not a certified release pin.
- [Parent architecture](BERP-MFI-ARCH-001.md) and [audit](BERP-MFI-AUDIT-001.md):
  scope, findings and ownership requirements.

Upstream documentation/source was consulted for orientation only. No complete call
graph, transaction proof or runtime test was performed. Database API documentation
fetch timed out during preparation; no unsupported API guarantee is inferred.
