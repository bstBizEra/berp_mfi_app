# BERP-MFI-RBAC-001 — LaoCapital initial configuration

> Publication copy: historical pilot example. Server/container and backup identifiers are omitted. This is not a current deployment status report or an automatic app fixture.

## Plan and scope — 2026-09-14

Configure the existing LaoCap tenant's display name and 18 core Role Profiles from
the operator's supplied design. Create `docs/laocapital-bootstrap.py` and this
record; update `docs/AGENTS.md` and `docs/SESSION-LOG.md` after verification.
Use custom atomic roles, without inherited ERPNext business roles. Back up before
the live change; dry-run, apply, and independently verify the exact site and URL.

## Historical deployment snapshot — 2026-09-14

- SSH target and container identifiers omitted from this publication.
- Internal site identifier omitted from this publication.
- Public ERP: https://laocap.bizera.la (HTTPS login returns 200).
- https://laocapital.la currently serves a separate WordPress website.
- Installed apps: Frappe, ERPNext, lao_berp. No Lending app.
- Before bootstrap: no Company, two system users, no LC roles or profiles.
- No Loan, Loan Application, Loan Disbursement, Loan Repayment, KYC,
  Credit Assessment, or AML Case DocTypes exist on this tenant.

## Catalog and activation boundaries

The executable bootstrap is an internal operational script and is not part of this documentation release.
It includes LC-001 through LC-016, LC-018 and LC-019, preserving the supplied codes.
HR (LC-017), IT Support (LC-020) and deposit profiles are not part of the supplied
18-profile core. Deposit profiles require confirmation of deposit-taking scope.

This is an **unassigned role catalog**, not an implemented microfinance permission
system. No DocPerm, Custom DocPerm, workflow, authority limit, user assignment,
company, email account, DNS record or accounting configuration is created.
Role names containing Approver confer no approval capability by themselves.
Tenant Administrator receives no System Manager or user-management permissions.

Before activation, implement and test each domain:

| Profiles | Intended authority | Required enforcement before assignment |
|---|---|---|
| Board, CEO | Governance and executive visibility | Curated reports; sensitive detail restrictions |
| Head of Credit, Credit Manager, Branch Manager | L3/L2/L1 review | Amount/product/branch limits; reject self-approval |
| Credit Analyst | Assessment | Independent reviewer; no disbursement |
| Loan Officer | Origination | Assigned portfolio and branch; no approval |
| Collection Officer | Collection activity | Assigned delinquent accounts; no balance editing |
| Cashier | Authorized receipts/disbursement | Approved loan, contract and KYC prerequisites; reversal checker |
| Accountant | Accounting preparation | Separate submit/reconcile authority |
| Finance Manager | Review and close | Independent maker/checker; period controls |
| Treasury | Funding and bank preparation | Transfer checker; no credit approval |
| Risk | Risk review | Holds/exceptions workflow; no cash authority |
| Compliance/AML | Restricted compliance review | Dedicated cases and field/file access controls |
| Internal Auditor | Audit reading | No transaction writes; separately authorized AML access |
| Customer Service | Customer inquiry | Limited fields and records |
| MIS | Reporting | Explicit report/export access and sensitive-data filtering |
| Tenant Administrator | Approved configuration | Server-side profile allowlist and privilege-escalation prevention |

Frappe permissions are additive: profile membership alone cannot enforce the
separation of duties across a user's combined roles. Validate combinations,
record scopes, server methods, linked records, reports, exports, attachments and
workflow transitions with positive and negative tests before assigning staff.
Authority limits must come from an approved business matrix, never invented LAK
values. Product, branch and portfolio controls need installed, linked data models.

## Head Office position-email design

Operator confirmed non-deposit-taking scope and Head Office only. All positions
below map to Head Office. These addresses are proposed role aliases, not created
mailboxes or active ERP users. Give each staff member a named login for audit
attribution; route position mail to that named person. Never share an ERP login.

| Profile | Proposed position email |
|---|---|
| LC-001 Board Director | board@laocapital.la |
| LC-002 CEO Managing Director | ceo@laocapital.la |
| LC-003 Head of Credit | head.credit@laocapital.la |
| LC-004 Credit Manager | credit.manager@laocapital.la |
| LC-005 Credit Analyst | credit.analyst@laocapital.la |
| LC-006 Branch Manager | ho.manager@laocapital.la |
| LC-007 Loan Officer | loan.officer@laocapital.la |
| LC-008 Collection Officer | collections@laocapital.la |
| LC-009 Cashier Teller | cashier@laocapital.la |
| LC-010 Finance Manager | finance.manager@laocapital.la |
| LC-011 Accountant | accountant@laocapital.la |
| LC-012 Treasury Officer | treasury@laocapital.la |
| LC-013 Risk Manager | risk@laocapital.la |
| LC-014 Compliance AML Officer | compliance@laocapital.la |
| LC-015 Internal Auditor | internal.audit@laocapital.la |
| LC-016 Customer Service | service@laocapital.la |
| LC-018 MIS Reporting Officer | reporting@laocapital.la |
| LC-019 Tenant Administrator | erp.admin@laocapital.la |

Multiple staff in one position should receive distinct named accounts (for example
firstname.lastname@laocapital.la), each linked to the approved profile and Head
Office. Actual names and mailbox ownership remain unconfirmed.

## Historically applied and verified — 2026-09-14

- Created 25 custom atomic roles, 18 Role Profiles and the Head Office Branch.
- Saved Website Settings app name `LaoCapital bERP`, title prefix `LaoCapital`;
  System Settings app name `LaoCapital bERP`, language `en`, timezone `Asia/Vientiane`.
- Previous website app name: `Frappe`; previous title prefix: unset. Previous
  system app name: `ERPNext`; previous language and timezone: unset.
- Database/config backup was taken before changes; backup identifiers and content are not published.
- Initial transaction rolled back because language/timezone were missing.
  Cleared only this attempt's orphan profile locks after verifying records absent;
  added rollback lock cleanup and successfully applied the complete configuration.
- Browser verified exact public URL and title `LaoCapital - Login`.
- Repeated dry-run checks every profile's exact roles, zero document permission
  grants and zero user assignments; reports zero missing roles/profiles/branch.
- Domain relationship and Company creation remain pending; no DNS changes made.

## Pending inputs at the time of the snapshot

- Whether laocapital.la remains the company website or becomes an ERP hostname.
  Do not replace the observed WordPress site without that choice.
- Registered company name; approved accounting setup. Non-deposit-taking confirmed.
- Staff email/profile/branch assignments, portfolio ownership and approval limits.
- Lending application and custom KYC/AML/workflow implementation scope.

## Recovery

Bootstrap creates only missing records and refuses conflicting existing profiles,
roles with permissions, or roles assigned to users. It is not an install hook.
The dry-run reports prior display settings for targeted restoration. To reverse
the catalog later, verify that no role is assigned or referenced before removing
only the records created by this run; do not restore a database over newer work.

Reference: [Frappe permissions](https://docs.frappe.io/erpnext/permissions).
The attachment's regulatory claims are not treated as verified legal requirements.
