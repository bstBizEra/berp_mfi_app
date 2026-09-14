# bERP Microfinance

`berp_mfi` is a planned reusable Frappe application for deposit-taking and
non-deposit-taking microfinance institutions.

**Status: architecture and planning.** This repository does not yet contain an
installable Frappe app. Financial modules, permissions and workflows are not implemented.

## Architecture

Read [BERP-MFI-ARCH-001](docs/BERP-MFI-ARCH-001.md) for module ownership, data
relationships, workflows, accounting controls, authorization and acceptance tests.

| Layer | Planned responsibilities |
|---|---|
| Shared core | Institution, license policy, customers, KYC, branches, portfolios and audit |
| Lending | Frappe Lending integration, credit assessment, approval and collections |
| Deposits | Product versions, accounts, subledger, withdrawals, holds, interest and maturity |
| Finance | ERPNext GL integration, teller operations, reconciliation and closing |
| Governance | Independent approvals, authority limits and scoped access |
| Country packs | Validated local rules, accounting mappings and regulatory reports |

Independent institutions use separate Frappe sites. Capabilities start disabled and
are activated against approved institution policy and implementation evidence.
Deposit-taking is not enabled merely by assigning a role or selecting a preset.

The proposed base dependencies are Frappe and ERPNext. Lending additionally requires
a tested Frappe Lending release. Exact supported versions remain to be validated.

## Implementation roadmap

1. Validate dependency compatibility and accounting integration in an isolated environment.
2. Build core institution policy, customer records and authorization services.
3. Implement and test the non-deposit lending workflow.
4. Implement the deposit engine and financial integrity tests.
5. Validate country packs, recovery and operational acceptance.
6. Add customer channels and payment integrations.

See the architecture's acceptance tests for concurrency, duplicate posting,
segregation of duties, tenant isolation, reconciliation and recovery requirements.

## Repository scope

Repository name: `berp_mfi_app`. Planned Python/Frappe app identifier: `berp_mfi`.
Institution-specific configuration, credentials, customer records and deployment
backups do not belong in this repository.

No installation command is provided until an installable app and a supported
dependency matrix have been implemented and verified.
