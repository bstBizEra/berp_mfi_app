# BERP-MFI-COMPAT-001 — Financial Runtime Compatibility Evidence

Status: ACTIVE / INCOMPLETE — observation bundle only; no financial gate passed.
Date: 2026-09-15. Candidate: [ARCH-001C R1](BERP-MFI-ARCH-001C.md).
Architecture contracts: [001A](BERP-MFI-ARCH-001A.md), [001B](BERP-MFI-ARCH-001B.md).

## Purpose and change-control boundary

This is a compatibility evidence unit, not application implementation. It asks whether
the pinned Frappe/ERPNext/Lending runtime can enforce 001A and 001B. It cannot amend
those contracts. Findings are classified `C-OBS` (observation), `C-MAP` (001B mapping),
`C-PIN` (candidate incompatibility), or `C-ARCH` (001A conflict). A `C-ARCH` result
returns to controlled 001A review; it never silently weakens the schema or lock order.

The lab is synthetic, site-local and isolated. It contains no production tenant,
customer, credential, balance or activated capability. No app code was built, installed,
or published. All financial tests, lock probes and fault-injection cases are NOT RUN.

## 1. Immutable inputs and measured environment

| Input | Value / result | Evidence disposition |
|---|---|---|
| Frappe source | `988e54f3c4c291e2077a83809663f123731abe76`; reported 16.33.1 | Pinned source archive; SHA-256 below |
| ERPNext source | `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; reported 16.34.2 | Pinned source archive; SHA-256 below |
| Lending source | `06fc075ae062ce38ac38a763f7f290da4ddd6fdb`; reported 16.5.0 | Pinned source archive; SHA-256 below |
| Bench image | `docker.io/frappe/bench@sha256:2132ebefed475ab4b898e0847fe00e1a8f50413dc528aafdecd188428e21b0a6` | Measured: Python 3.14.7, Node v24.21.0, Bench 5.31.0, Yarn 1.22.22, Debian 12 |
| MariaDB image | `docker.io/library/mariadb@sha256:2d2f4095530294735a857cfe22bb101e19b0849b416911c796ec4aa81b164a62` | Measured server 11.8.9; isolated pod; no financial tests |
| Redis image | `docker.io/library/redis@sha256:9702d01c1f10c3ea9f48211b4362e44f154ff02d063e6f7268eba804059f53bf` | Measured server 7.4.10; cache/queue processes intended separate |
| Source scan | Python 3.14 parser: 4,471 files, 24,083 functions, 187,984 call sites, 0 parse errors | Syntactic inventory only; not a resolved call graph |

Source archive SHA-256 values:

```text
frappe.tar.gz  217d4e48043770ac3cc44ce7001107f162ed1580cbfffca9c73bf2c83a0275d9
erpnext.tar.gz 374957165ae8d784f6ebdd30414b47077a5a5e9519d48bf61703b577f45533b0
lending.tar.gz 888e2bf910b00a2cefc4aeb220a6ab7162710a3a582a5de838252a81998acb0e
```

The full static inventory is retained in the private lab evidence directory as
`source-inventory.json` (SHA-256 `ba0b960a8dfddb67b80071c74284dac77bb037d9fc5300ba296f23927039f9e7`).
It is not committed to this repository because it is generated source metadata rather
than a reviewed, stable document. `docs/compat-001/inventory.py` can reproduce it from
the three pinned archives using Python 3.14; dynamic dispatch, hooks, SQL reachability
and runtime call order remain unresolved.

## 2. Investigation results

| Group | Required question | Current result | Class / status |
|---|---|---|---|
| C01 pins | Are exact upstream pins identified? | Yes, three commit SHAs and archive hashes recorded | C-OBS complete |
| C02 topology | What transaction and DB boundaries are actually used? | WSGI/rollback-only CLI baseline executed; trace retrieval/review pending; see [checkpoint](compat-001/C02-checkpoint.md) | C-OBS incomplete |
| C03 lock order | Can policy → exposure → reservation → account/loan locks be acquired safely? | Not proven; source inspection found early Frappe document locking before pre-save methods | C-ARCH candidate / B-BLK-01 open |
| C04 path inventory | Are Desk/REST/RPC/import/job/direct/bulk/cancel/repost paths classified? | Static candidates generated; resolved path × actor × bypass inventory not complete | C-MAP open / B-BLK-02 open |
| C05 Lending mutations | Are all financial mutation and cancellation paths mapped? | Repayment/disbursement symbols inspected; other actions remain unresolved | C-OBS incomplete |
| C06 GL paths | Are controller and lower-level GL paths covered? | Candidate controller methods observed; lower-level universal guard not proven | C-MAP open / B-BLK-02 open |
| C07 control account C | Does canonical repayment accept settlement control account C? | Not tested; no evidence of a supported matched-voucher adapter | C-ARCH candidate / B-BLK-03 open |
| C08 single commit | Can deposit debit and canonical repayment share one commit? | NOT RUN; site/service lab not completed | C-ARCH candidate / B-BLK-03 open |
| C09 fault injection | Does every failure yield zero or one complete event? | NOT RUN | B-BLK-03 open |
| C10 retry | Does a lost response/retry preserve one event? | NOT RUN | B-BLK-03 open |
| C11 reversal | Does full reversal restore both ledgers and exposure exactly once? | NOT RUN | B-BLK-03 open |
| C12 negative tests | Are every route × actor × bypass cases denied or guarded? | NOT RUN | B-BLK-02 open |
| C13 evidence | Is there an immutable reviewed evidence bundle? | Source and static manifest exist; executable financial evidence absent | Incomplete |

## 3. Source observations relevant to blockers

The inspected Frappe lifecycle checks latest state and loads the prior document with
`for_update=True` before normal pre-save methods. Its `ignore_validate` branch can skip
validation and submit/cancel guard dispatch. Lending repayment has imported and bulk
branches that return early from normal repayment processing. Disbursement and repayment
`on_submit` paths perform state/schedule/GL work after the document lifecycle has begun.
These are observations, not proof that a production path is exploitable; a complete
entry map and controlled interception decision are still required.

Primary immutable source links:

- [Frappe document lifecycle](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/model/document.py#L559)
- [Lending disbursement submit](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/lending/loan_management/doctype/loan_disbursement/loan_disbursement.py#L182)
- [Lending repayment submit](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/lending/loan_management/doctype/loan_repayment/loan_repayment.py#L183)
- [Lending repayment GL](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/lending/loan_management/doctype/loan_repayment/loan_repayment.py#L2093)
- [ERPNext Journal Entry](https://github.com/frappe/erpnext/blob/4048fb70e14d1843956fcdabb7c3cca75a1cbcdd/erpnext/accounts/doctype/journal_entry/journal_entry.py#L186)
- [ERPNext Payment Entry](https://github.com/frappe/erpnext/blob/4048fb70e14d1843956fcdabb7c3cca75a1cbcdd/erpnext/accounts/doctype/payment_entry/payment_entry.py#L203)

## 4. Lab limitations and failed setup attempts

Rootless Podman could not create a bridge because this WSL kernel lacks `/dev/net/tun`
and `ip_tables`. A no-network Podman pod was created for database/service isolation,
but it is not yet a Frappe site and therefore cannot produce financial results. The
Bench preparation container fetched dependencies and installed the pinned Frappe and
ERPNext source layers; Lending installation and site creation remain incomplete.
These infrastructure results are recorded to prevent a failed setup from being mistaken
for a financial pass.

No credentials were written to the repository. Any lab secret remains outside Git and
must be rotated or discarded with the disposable lab.

## 5. Acceptance disposition and next controlled actions

COMPAT-001 is NOT COMPLETE. B-BLK-01, B-BLK-02 and B-BLK-03 remain open, so 001B is
not accepted and 001C is not frozen. The next evidence step is to complete a working
synthetic site with private service connectivity, then instrument transaction/lock
events and run the C08–C12 matrix. If the lock or settlement contract cannot satisfy
001A, record a C-ARCH finding and return it to 001A. Do not alter 001B to make the
runtime appear compatible.

No application foundation, DocTypes, migrations, production installation, role
assignment, capability activation or financial data operation is authorized by this
report.
