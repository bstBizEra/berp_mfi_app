# BERP-MFI-ARCH-001C — Runtime, Dependency & Packaging Contract

Status: DRAFT / CANDIDATE — not certified; reproducible application build not yet frozen.
Date: 2026-09-15. Parent: [001](BERP-MFI-ARCH-001.md).
Contracts: [001A](BERP-MFI-ARCH-001A.md), [001B](BERP-MFI-ARCH-001B.md).
Evidence: [COMPAT-001](BERP-MFI-COMPAT-001.md).

## Definition of Done

A reproducible runtime combination can be identified by immutable versions,
installed deterministically, upgraded under a defined policy, and mapped to the
exact upstream code inspected by architecture and compatibility evidence.
Freezing a candidate identifies a test subject; it does not certify financial correctness.
The application remains unimplemented. Package paths and hooks below are contracts,
not files created or registrations installed by this unit.

## 1. Candidate R1 and immutable dependency policy

| Component | R1 selection / source constraint | Disposition |
|---|---|---|
| Frappe | `988e54f3c4c291e2077a83809663f123731abe76`, reports 16.33.1 | Source pinned |
| ERPNext | `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, reports 16.34.2 | Source pinned |
| Lending | `06fc075ae062ce38ac38a763f7f290da4ddd6fdb`, reports 16.5.0 | Source pinned; financial support unproven |
| Python | Frappe requires `>=3.14,<3.15`; ERPNext `>=3.14` | Exact executable/build recorded in evidence |
| Node | Frappe package engine `>=24`; select 24.x for R1 | Exact executable/build recorded in evidence |
| MariaDB | Select 11.8 line, matching pinned framework CI | Exact image digest/server version recorded in evidence |
| Redis | Select separate cache and queue Redis 7 processes | Exact image digest/server version recorded in evidence; client version is not server requirement |
| Bench, Yarn, OS, architecture | Measured lab toolchain | Exact versions/digests required before freeze |
| PostgreSQL | Framework CI alone insufficient for Lending/financial integration | Excluded from R1 |
| `lao_berp`, `berp_mfi_la` | Optional integrations; no certified pins | Absent from R1 financial evidence |

The evidence manifest is the authoritative list of measured versions, image digests,
source archive hashes and dependency inventories. A mutable tag is allowed only to
discover an image: record and use its resolved digest thereafter. Branch names,
semver ranges and an installed package list alone do not freeze a reproducible build.
Freeze also requires transitive Python/Node dependency locks with artifact hashes,
build tooling, architecture, DB settings, locale/timezone and clean rebuild evidence.
Missing items keep R1 CANDIDATE; they must never be represented as certified defaults.

ERPNext metadata requires Frappe `>=16.21.0,<17.0.0`; Lending requires Frappe and
ERPNext `>=16.0.0,<17.0.0`. Their intersection admits these source versions but is
not proof that financial paths work. Frappe's auxiliary `tool.frappix` still names
older Python/Node choices; project Python constraints and package engines govern R1.

Immutable sources:

- [Frappe pyproject](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/pyproject.toml),
  [Node engine](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/package.json),
  [CI services](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/.github/workflows/_base-server-tests.yml).
- [ERPNext constraints](https://github.com/frappe/erpnext/blob/4048fb70e14d1843956fcdabb7c3cca75a1cbcdd/pyproject.toml),
  [Lending constraints](https://github.com/frappe/lending/blob/06fc075ae062ce38ac38a763f7f290da4ddd6fdb/pyproject.toml).

## 2. Application and dependency graph

```text
Frappe -> ERPNext -> berp_mfi (proposed core)
             \-> Lending (optional installation, required for lending capability)
berp_mfi -> berp_mfi_la (proposed Lao country pack)
ERPNext -> lao_berp (optional separate regional application)
```

Arrows mean prerequisite → dependent. Core `required_apps` is proposed as
`["erpnext"]`. Lending is deliberately absent from that mandatory list; otherwise
Frappe installs it as a prerequisite and it is no longer optional. For a lending
capability, activation must require certified Lending installed on the same site,
not merely a Python package present on the bench. Fail closed before any import or
financial mutation when that dependency is absent or mismatched.

`optional_apps` is a documentation concept here, not a claimed Frappe enforcement
hook. Capability dependencies require explicit server-side checks. No unconditional
Lending import may prevent a deposit-only core site from starting. Core/deposit-only
and core/Lending combinations need separate certificates; R1 investigates the latter.

Proposed real Frappe package shape:

```text
berp_mfi_app/
  pyproject.toml               # package name berp_mfi, flit backend, Python constraint
  README.md
  berp_mfi/
    __init__.py                # immutable release version
    hooks.py                   # dependency and lifecycle registrations
    modules.txt                # module names matching package directories
    patches.txt                # append-only ordered migration identifiers
    <module>/doctype/...
    public/...
    templates/...
```

The [pinned app generator](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/boilerplate.py)
uses flit and Bench-managed Frappe dependencies. Exact build backend is locked in
the future release build. This document does not create the package, DocTypes,
fixtures, patches or hooks. Registry EN addresses in 001B are not implemented APIs.

Hooks contract: lifecycle handlers must be idempotent, scope-aware and free of
financial activation. Financial guards need the proven COMPAT entry map; a generic
`before_submit` hook is not automatically sufficient. Fixtures may contain reviewed
neutral metadata, never users, credentials, institution licenses, balances, real
limits or activated capabilities. Migration fixtures must not overwrite local policy.

## 3. Country-pack interface

`berp_mfi_la` depends on a compatible `berp_mfi` release and supplies versioned
country-policy providers, accounting mappings and report definitions. Interface
inputs include institution, effective business date and policy version; outputs
carry provider/version/evidence and fail closed when unavailable. The core retains
economic event, authorization, accrual, reservation and transaction ownership.

`lao_berp` remains separate. An optional adapter must verify same-site installation,
version and country before use; its absence cannot disable core financial guards.
No duplicate tax/accounting source, duplicate GL hook or silent fallback rate is
permitted. Conflicting country-pack registrations block activation and require an
explicit mapping decision. This unit asserts no current Lao legal rates or approval.

## 4. Site, worker and data boundaries

One Frappe site equals one legal MFI institution and one primary ERPNext Company.
Additional legal institutions need separate sites. Branches are operating units,
not alternate tenant boundaries; 001B booking/service entitlements still apply.

- Hostname resolution uses a configured allowlist of host → site. Reject unknown
  hosts and untrusted forwarded site headers; never fall back to another tenant.
- A worker initializes the explicit site, carries original actor/service identity,
  validates company/scope and destroys site context after completion or exception.
  Queue ownership and retry identity are explicit; no process-global tenant state.
- Cache keys include site and relevant institution/policy revision; invalidation
  follows policy changes. Shared Redis infrastructure does not grant shared access.
- Public/private files remain site-scoped. Private files, reports, print, export,
  search and downloads need the same entitlements as source records. Storage paths
  and predictable URLs alone do not authorize access.
- Schedulers enumerate explicit installed-site capability policy. Disabling a
  capability blocks new business actions; documented run-off/recovery remains guarded.
- Integration credentials are per site/provider/action, held in secret storage and
  excluded from fixtures/evidence. No shared global token or actor substitution.

Lab R1 uses synthetic `mfi-compat.localhost`, no production names or datasets, no
public DNS, and no published container ports. A later HTTP test listener, if needed,
must bind loopback only. Package download egress is permitted; outbound business
integrations/mail/schedulers remain disabled unless specifically exercised synthetically.

## 5. Install, migrate, upgrade and recovery

| Operation | Required behavior | Acceptance evidence |
|---|---|---|
| Preflight | Match certificate, app graph, DB/toolchain; reject unsupported combinations | Positive supported and negative mismatched dependency cases |
| Install | Install prerequisite apps first, then future core, optional country pack; capabilities disabled | Clean site and repeated-install safety; no user/balance/license activation |
| Migrate | Maintenance mode, drain workers, backup DB/files/config, run approved patches once | Interrupted phase recovery, checksums, schema and data validation |
| Upgrade | New candidate certificate; immutable old/new release manifests; rehearse on restored synthetic fixture | Full affected financial and isolation regression, restore drill |
| Recovery | Restore coherent pre-upgrade DB/files/apps, or approved forward repair | Reconciled event/GL/exposure data and queues before reopening |
| Capability activation | Separate authorized action after compatible release and financial acceptance | Server dependency/policy checks; role assignment alone cannot activate |
| Uninstall/downgrade | Unsupported with financial history unless separate archive/recovery contract accepted | Never delete ledgers or run automatic schema downgrade |

Install and migrate are not one rollback-safe financial transaction. Pinned
[installer](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/installer.py#L379)
and [migration phases](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/migrate.py#L46)
commit work. Financial operation rules in 001A remain separate and unchanged.
Never restore DB alone against incompatible app code or leave old queued payloads
to execute under a changed schema without version validation.

## 6. Certification and unsupported combinations

Every changed source pin, dependency, database, build image or guard registration
creates a new candidate and an impact review. No floating upgrade during evidence
collection. Security fixes may expedite testing, never bypass financial acceptance.
Artifacts retain source SHA, dependency hashes, schema revision, environment manifest,
test inputs/oracles/outcomes and independent reviewer. A certificate names its scope:
deposit-only, Lending, country pack and channels cannot inherit coverage implicitly.

Unsupported in R1: PostgreSQL; Python outside 3.14; Node outside selected 24.x;
uncertified MariaDB/Redis patch or image; multiple institutions on one site; absent
Lending with lending enabled; unpinned country packs; mixed application images across
workers; direct production installs; FX; unguarded mutation entry paths. Unsupported
means activation denied, not silently best-effort support.

## 7. Governance and convergence

COMPAT findings use C-OBS (observation), C-MAP (001B mapping error), C-PIN (runtime
candidate incompatibility), or C-ARCH (001A invariant cannot be satisfied). An early
lock observation alone does not prove architectural impossibility: investigate a
supported earlier entry or deny the unsafe path first. C-ARCH requires controlled
001A review. Never weaken 001B to accommodate an unsafe runtime.

001B acceptance requires all three blockers closed, independent review of all 90
invariant rows, required B-T instances executable and green, no ambiguous/duplicate
financial owner and no financially capable unguarded entry path. Candidate FROZEN
plus COMPAT COMPLETE triggers architecture acceptance review, not automatic approval.
Only that review can unlock separately authorized IMP-001 application foundation.
