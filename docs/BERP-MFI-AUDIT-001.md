# BERP-MFI-AUDIT-001 — Design audit

Date: 2026-09-15. Scope: supplied 29-section proposal and published
`berp_mfi_app/docs/BERP-MFI-ARCH-001.md` at commit
`18fca1a3b77fb74159612aef402f2e865d4f0230`.
Local and remote `main` matched at inspection. No implementation exists to test.

## Verdict

Suitable as a direction for a controlled prototype; not an implementation-ready
specification or production acceptance. Retain the published architecture as the
baseline and selectively merge the attachment's credit, field-visit and teller detail.
Do not replace the baseline with the attachment: that would remove required deposit
and license-capability controls. Findings below are design defects or readiness gaps,
not demonstrated vulnerabilities in running code.

Audit plan: compare both artifacts against the requested deposit/non-deposit scope;
verify disputed upstream facts; identify failure scenarios and closure evidence;
record findings here and in project documentation. No design edits, installations,
Git publication or production changes are performed by this audit.

## Prioritized findings

### F01 — P1: Attachment omits the deposit product and transaction domain

Evidence: attachment sections 2, 3, 18, 20, 27 and 29. Navigation, ownership table,
roles and package tree cover lending; customer deposits appear only as an optional
liability account. Published architecture sections 4–8 already cover this gap.

Failure scenario: implementing the attachment as the whole product leaves a
deposit-taking MFI without customer-account balances, withdrawal mandates, holds,
interest/maturity processing or subledger reconciliation. Teller receipts and a GL
liability alone cannot establish those contracts.

Required correction: preserve the published deposit modules, license gates, account
parties, transaction state machine, deposit-specific roles and deposit release phase.
Explicitly label the attachment as a lending-domain expansion, not a replacement.
Closure: registry/ERD and test matrix cover both institution presets, including
deposit denial on the non-deposit preset and a complete deposit lifecycle.

### F02 — P1: Accrual uniqueness includes a mutable rule version

Evidence: published architecture lines 206–208 defines batch uniqueness by account,
business date, rule version and event type. Contract snapshots and controlled
adjustments are required elsewhere, but no stable economic-period uniqueness
constraint is stated independently of the rule version.

Failure scenario: interest for account A/date D is posted under V1. An approved
correction or job rerun uses V2; the specified key accepts another full accrual for
A/D instead of requiring an explicit delta or reversal/replacement. Same-version
retry tests would miss this path.

Required correction: give the original economic accrual a stable identity such as
account, accrual component and covered interval. Persist immutable calculation
version and basis separately. Corrections reference the original, supersede it
through controlled accounting and prevent overlapping base intervals. If a rate
changes within a day, define interval segmentation rather than excluding legitimate
multiple segments. Do not merely remove version without modelling intervals.
Closure: V1 → V2 rerun, overlapping periods, mid-period rate change and concurrent
correction tests yield exactly the approved net interest and reconciled GL.

### F03 — P1: Aggregate authority lacks an atomic reservation contract

Evidence: published architecture lines 238–243 defines amount/exposure limits,
aggregation windows and anti-splitting rules; lines 178–182 specifies transaction
locks but does not identify the shared borrower/group/authority exposure to lock.
Attachment section 9 relies on product/amount/risk rules and is less complete.

Failure scenario: two different applications for the same borrower each pass a
remaining exposure check before either is booked. Each transaction can be internally
atomic and still exceed the aggregate limit because they lock different records.
Similarly, two partial disbursements may reuse an authorization's remaining capacity.

Required correction: define exposure owner/key, included commitments, reservations,
expiry/release rules, currency basis and common locking/serialization boundary.
Approval or disbursement consumes capacity once using a durable unique reference;
reversals release it only according to the approved policy. Multi-currency rounding
and concurrent rule changes need deterministic handling.
Closure: parallel applications/disbursements cannot exceed borrower/group/product
limits or approved undisbursed capacity, including retries and cancelled requests.

### F04 — P1 readiness gap: Enforcement on upstream entry points is unproven

Evidence: attachment sections 10, 12, 26 and 28 promise workflow separation and a
business API. Published lines 96–101 correctly require enforcement on imports,
generic REST, jobs and direct upstream submissions; this is already a requirement,
not a missing principle. There is no release-specific interception map yet.

Failure scenario if implemented only in the new screens/API: direct submission of
a Lending disbursement or repayment bypasses MFI policy, KYC or maker/checker checks.
Frappe exposes document REST APIs, so hiding raw screens is insufficient.

Required correction: enumerate supported entry points per affected DocType/action;
map controller hooks and service checks for validate/submit/cancel/amend, imports,
jobs and upstream methods. Specify handling of technical Administrator and trusted
workers without implying that root access can be constrained by app permissions.
Closure: negative integration tests invoke each route under unauthorized roles,
changed approvals, expired KYC and disabled capabilities. No production vulnerability
is claimed here because these controls have not been implemented.

### F05 — P1 readiness gap: Deposit-to-loan posting is still an alternative, not a contract

Evidence: published lines 194–199 allows atomic execution or a reconciled clearing
workflow and explicitly blocks release pending proof. Attachment sections 13–14
and 18 do not supply transaction/idempotency contracts. The baseline already
identifies this gap, but it must be resolved before financial module implementation.

Failure scenario: deposit debit commits but Lending repayment fails; or Teller,
Payment Entry and Lending each post cash for the same receipt. A balanced GL does
not prove the customer was charged only once.

Required correction: select the exact supported voucher path for each event. Specify
transaction boundary, source identity, reversal path, clearing-account ownership,
unknown settlement states and reconciliation. Prove the selected Lending calls do
not introduce unexpected commits or non-transactional side effects.
Closure: crash/fault injection at each boundary leaves either no posting, a complete
posting, or an explicitly reserved/clearing state; recovery never doubles principal,
cash, interest or deposit movements. Freeze this contract before building teller UI.

### F06 — P2: Attachment invents dependencies and has an invalid Frappe package layout

Evidence: attachment section 1 lists `berp_core`, `berp_tenant`, `berp_lao`,
`berp_branding`, `berp_integrations` as the technical stack; section 27 places
`hooks.py`, `public/` and `templates/` outside the importable app package.
Local workspace instead contains `lao_berp` and `berp_whitelabel`; the listed
alternative apps have not been established here. This does not establish that
they do not exist elsewhere. Published sections 2 and 10 are closer to the required design.

Failure scenario: scaffolding the tree literally prevents Frappe from discovering
hooks/assets and introduces unresolved app requirements before domain work starts.
Required correction: use the generated Frappe app structure, keep `hooks.py`, assets,
templates and module/patch registration inside `berp_mfi/`, and declare only verified
dependencies. Choose one country-pack identifier (`berp_mfi_la` is the baseline;
the attachment also uses `berp_mfi_lao`). Mark future platform apps as proposals.
Closure: clean environment package build, install/migrate and hook/asset discovery
tests; exact version matrix and optional-dependency behavior documented.

### F07 — P2: Attachment asserts an unestablished path-routing contract

Evidence: attachment section 23 claims `/t/laocapital` follows an already established
tenant URL contract. Current project documentation uses hostname-based tenancy;
the published architecture does not define the proposed gateway. Section 22 also
describes data as physically separated, which overstates separate databases on a
shared runtime. The baseline explicitly acknowledges stronger isolation needs.

Failure scenario: implementers assume path-prefix proxying supplies tenant identity,
but sessions, private files, websocket connections or upstream redirects select the
wrong context. Database separation does not isolate shared workers or host admins.
Required correction: retain hostname routing as baseline. Treat a common-origin
gateway as a separate future design with authenticated membership binding, origin/
cookie/CSRF controls, canonical tenant resolution and upstream-header sanitization.
Describe current separation as site/database isolation, not dedicated physical hosts.
Closure: cross-tenant session/API/file tests for any gateway before channel rollout.
This review checks documented architecture, not current live DNS or host isolation.

### F08 — P2: Branch-only customer ownership is insufficient for deposit expansion

Evidence: attachment section 4 assigns one owning branch/officer to Customer Profile;
published lines 67–69 requires dimension validation while lines 136–137 permits
multiple account parties. Neither artifact defines the allowed cross-branch link
matrix or account-service permissions.

Failure scenario: a customer has a loan at branch A and a deposit at branch B. A strict
branch-equality implementation rejects legitimate relationships; a global customer
read grant instead exposes all account/KYC details to both branches.
Required correction: define institution-wide party identity separately from
relationship owner, account booking branch, servicing branch and staff portfolio.
Use explicit service entitlements and minimal customer lookup fields. Clarify which
links must match exactly and which may cross branch under policy; retain strict
institution/company checks.
Closure: same-customer/multiple-branch tests allow authorized servicing while denying
unrelated account balances, files and sensitive compliance cases.

## Facts checked and items not treated as defects

- The attachment's warning about Lending `develop` is correct: its inspected
  dependency metadata requires Frappe/ERPNext 17. A v16 candidate must be pinned
  and certified separately. The ERPNext support page calls end-2029 EOL for v16
  **planned**, not guaranteed, and does not certify the whole stack.
- Posting date/value date separation is documented in Lending v16. Retain it;
  still test closed periods and recalculation against pinned code.
- Reusing Customer and Lending repayment allocation is sound. Keep one canonical
  financial owner; do not replace servicing arithmetic with assessment formulas.
- Published design already includes deposit holds, decimal arithmetic, outbox,
  idempotency, run-off, private-file access, audit limitations and recovery tests.
  These must not be reported as wholly absent just because the attachment omits them.
- The attachment's proposed field visits, assessments, collections and workspaces
  are useful detail. Translate them into versioned records and scoped permissions.
- Offline mobile operations remain a later phase; no offline cash acceptance should
  be inferred from a proposed Sync button. Device revocation, replay, conflict and
  settlement rules need their own channel specification.

## Recommended correction order

1. Keep ARCH-001 as parent; classify the attachment as lending-domain detail (F01).
2. Resolve economic identities, authority reservations and accounting contracts
   together with an executable compatibility spike (F02, F03, F05).
3. Produce the DocType registry/ERD with branch relationship rules and a versioned
   upstream enforcement map (F04, F08). A registry alone does not close accounting risk.
4. Correct package/dependency names and defer path gateway work (F06, F07).
5. Implement core policies and synthetic lifecycle tests before staff activation.

No numeric architecture score is assigned. There are five P1 items (three design
issues and two acknowledged implementation-readiness gaps) and three P2 corrections.
No live financial, permission, recovery or regulatory compliance testing was performed.

## Primary sources checked

- [Lending develop metadata](https://raw.githubusercontent.com/frappe/lending/develop/pyproject.toml)
- [Lending version-16 metadata](https://raw.githubusercontent.com/frappe/lending/version-16/pyproject.toml)
- [ERPNext supported versions](https://github.com/frappe/erpnext/wiki/Supported-Versions)
- [Posting date and value date](https://docs.frappe.io/lending/loan-management/automated-accounting/posting-date-and-value-date)
- [Frappe app structure](https://docs.frappe.io/framework/user/en/basics/apps)
- [Frappe REST API](https://docs.frappe.io/framework/user/en/api/rest)

Attachment evidence references its section numbers; canonical line references are
pinned to the commit above. The proposal is now archived as [Lending proposal](reference/lending-proposal.md), published in a later documentation-only update. Audit findings remain unresolved.
