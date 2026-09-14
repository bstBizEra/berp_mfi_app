# BERP MFI documentation

All documents describe design, proposed behavior or dated pilot evidence.
The repository does not yet contain an installable microfinance application.

| Document | Status and purpose |
|---|---|
| [Architecture](BERP-MFI-ARCH-001.md) | Parent design for deposit-taking and non-deposit-taking institutions |
| [Financial Integrity & Enforcement Contracts — 001A](BERP-MFI-ARCH-001A.md) | Draft child for F02–F05; gates untested and unaccepted |
| [Canonical Data Model & Enforcement Registry — 001B](BERP-MFI-ARCH-001B.md) | Draft entity, ownership, key, state and permission model; acceptance blocked |
| [001B enforcement and upstream evidence](BERP-MFI-ARCH-001B-enforcement.md) | Proposed boundaries, source observations, three blockers and 20 unrun test families |
| [001B invariant traceability](BERP-MFI-ARCH-001B-traceability.md) | 90 draft invariant mappings; completeness requires independent review |
| [Design audit](BERP-MFI-AUDIT-001.md) | Eight open findings; read before implementation |
| [Role profiles and Head Office email design](BERP-MFI-RBAC-001.md) | Historical LaoCapital pilot example, with operational identifiers omitted |
| [Original role-profile proposal](reference/role-profile-proposal.md) | Archived input; not an approved permission implementation |
| [Original lending-layer proposal](reference/lending-proposal.md) | Archived input audited against the broader architecture |

The audit identifies corrections and readiness gaps; publication does not resolve
them. In particular, the lending proposal must not replace the parent's deposit
scope, and the financial transaction contracts require further specification.

Controlled sequence: parent → 001A financial/enforcement contracts → draft 001B
data model/enforcement registry → planned 001C runtime/packaging contract → accepted
implementation baseline. No app scaffolding is authorized by these draft documents.

Reference proposals retain their original wording and citation defects for
traceability. Example limits, company names, branches and email aliases do not
create production configuration or represent verified legal requirements.

This collection includes the MFI-specific design documents and supplied proposals.
General bERP manuals, internal session logs, credentials, backups and executable
tenant bootstrap scripts remain outside this repository.
