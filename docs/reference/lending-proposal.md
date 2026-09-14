# Original lending-layer proposal

> Archived user-supplied proposal. Claims, examples and citations are preserved as received; they are not verified requirements or implementation authority. Read [the architecture](../BERP-MFI-ARCH-001.md) and [the audit](../BERP-MFI-AUDIT-001.md) first. This proposal does not supersede deposit/non-deposit scope.

---

Yes. I recommend **BERP MFI** as a dedicated vertical application layer on top of **bERP + ERPNext + Frappe Lending**, rather than customizing ERPNext Lending directly.

The target product becomes:

> **BERP MFI — Microfinance Management System**
> A Lao-first, multi-branch microfinance operating platform covering customer onboarding, KYC, credit origination, underwriting, approva([Frappe Docs][1])g, risk, compliance, audit and management reporting.

This fits the existing bERP architecture: ERPNext remains the core ERP, bERP provides the platform/localization/tenant layer, and business verticals are separate custom applications.

## 1. Recommended application stack

```text
┌──────────────────────────────────────────────┐
│                 BERP MFI                     │
│        Microfinance Business Layer           │
├──────────────────────────────────────────────┤
│ Credit │ KYC │ Collections │ Risk │ Teller   │
│ AML    │ Approval │ Portfolio │ Compliance   │
├──────────────────────────────────────────────┤
│              Frappe Lending                  │
│ Loan │ Schedule │ Demand │ Accrual │ Payment │
│ Security │ Restructure │ Write-off │ GL      │
├──────────────────────────────────────────────┤
│                  ERPNext                     │
│ Accounting │ Customer │ Bank │ HR │ Assets   │
│ Procurement │ Expenses │ Cost Centers        │
├──────────────────────────────────────────────┤
│                  bERP                        │
│ Tenant │ Lao │ Branding │ Identity │ API     │
├──────────────────────────────────────────────┤
│              Frappe Framework                │
│ DocType │ Workflow │ RBAC │ REST │ Scheduler │
└──────────────────────────────────────────────┘
```

I would package it technically as:

```text
frappe
├── erpnext
├── lending
├── berp_core
├── berp_tenant
├── berp_lao
├── berp_branding
├── berp_integrations
└── berp_mfi          ← NEW
```

This avoids a deep ERPNext fork, which is already the architectural direction established for bERP.

For production today, I would target the **ERPNext/Frappe v16 line**, subject to a compatibility certification against the selected Lending release. ERPNext v16 is currently supported through the end of 2029, while the current `develop` branch of Frappe Lending already declares Frappe/ERPNext 17 dependencies, so BERP MFI should pin tested versions rather than track `develop`. ([GitHub][2])

---

# 2. BERP MFI module architecture

I would expose the following application navigation instead of presenting raw ERPNext/Frappe Lending terminology.

| Workspace          | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| **MFI Home**       | Operational and executive dashboard              |
| **Customers**      | Borrower 360°, KYC, household/business profile   |
| **Origination**    | Applications and document collection             |
| **Credit**         | Assessment, scoring, underwriting and approval   |
| **Loans**          | Booking, disbursement and active loan management |
| **Teller**         | Cash disbursement, repayment and daily cash      |
| **Collections**    | Arrears, field collections and recovery          |
| **Collateral**     | Security, guarantors and collateral monitoring   |
| **Risk**           | PAR, delinquency, concentration and exceptions   |
| **Compliance**     | KYC/AML cases and regulatory controls            |
| **Finance**        | Loan accounting, GL and reconciliation           |
| **Reports**        | Portfolio, financial and regulatory reports      |
| **Administration** | Products, policies, authority and MFI settings   |

The normal operational flow becomes:

```text
CUSTOMER
   ↓
KYC
   ↓
LOAN APPLICATION
   ↓
FIELD ASSESSMENT
   ↓
CREDIT ASSESSMENT
   ↓
CREDIT DECISION
   ↓
APPROVAL
   ↓
CONTRACT
   ↓
DISBURSEMENT
   ↓
ACTIVE LOAN
   ↓
REPAYMENT
   ↓
────────────────────────────────
│ CURRENT                       │
│   ↓                           │
│ CLOSED                        │
│                               │
│ DELINQUENT                    │
│   ↓                           │
│ COLLECTION                    │
│   ↓                           │
│ RESTRUCTURE / RECOVERY        │
│   ↓                           │
│ WRITE-OFF / SETTLEMENT        │
────────────────────────────────
```

Frappe Lending already supplies the core lifecycle mechanics for Loan Product, Loan Application, Loan, repayment schedules, Loan Repayment and restructuring. ([Frappe Docs][3])

---

# 3. What BERP MFI should reuse vs build

This is a critical boundary.

| Capability                   | Source                | Strategy             |
| ---------------------------- | --------------------- | -------------------- |
| Customer                     | ERPNext               | Reuse                |
| Company                      | ERPNext               | Reuse                |
| Branch/accounting dimensions | ERPNext/bERP          | Extend               |
| Chart of Accounts            | ERPNext               | Reuse                |
| Payment Entry                | ERPNext               | Integrate            |
| Bank Account                 | ERPNext               | Reuse                |
| Cost Center                  | ERPNext               | Reuse                |
| Loan Product                 | Frappe Lending        | Extend               |
| Loan Application             | Frappe Lending        | Extend               |
| Loan                         | Frappe Lending        | Reuse                |
| Loan Disbursement            | Frappe Lending        | Reuse + control      |
| Repayment Schedule           | Frappe Lending        | Reuse                |
| Loan Repayment               | Frappe Lending        | Reuse + teller layer |
| Loan Demand                  | Frappe Lending        | Reuse                |
| Interest accrual             | Frappe Lending        | Reuse                |
| Loan Security                | Frappe Lending        | Extend               |
| Loan Restructure             | Frappe Lending        | Reuse + approval     |
| Write-off                    | Frappe Lending        | Reuse + governance   |
| MFI Customer Profile         | **BERP MFI**          | Build                |
| KYC Case                     | **BERP MFI**          | Build                |
| Household assessment         | **BERP MFI**          | Build                |
| Business assessment          | **BERP MFI**          | Build                |
| Field Visit                  | **BERP MFI**          | Build                |
| Credit Assessment            | **BERP MFI**          | Build                |
| Credit Score                 | **BERP MFI**          | Build                |
| Credit Decision              | **BERP MFI**          | Build                |
| Authority Matrix             | **BERP MFI**          | Build                |
| Approval Exception           | **BERP MFI**          | Build                |
| Collection Case              | **BERP MFI**          | Build                |
| Promise to Pay               | **BERP MFI**          | Build                |
| Recovery Action              | **BERP MFI**          | Build                |
| AML/KYC Risk Case            | **BERP MFI**          | Build                |
| Teller Session               | **BERP MFI**          | Build                |
| Cash Drawer                  | **BERP MFI**          | Build                |
| Regulatory reporting         | **BERP MFI Lao Pack** | Build                |

The key principle is:

```text
BERP MFI
does NOT replace Lending.

BERP MFI
controls, enriches and governs Lending.
```

---

# 4. Customer 360°

I would keep ERPNext `Customer` as the canonical financial party because Frappe Lending already supports customers as loan applicants. ([Frappe Docs][4])

Do not overload the standard Customer DocType with 100+ microfinance fields.

Instead:

```text
Customer
   │
   └── MFI Customer Profile
          │
          ├── Personal Profile
          ├── KYC
          ├── Household
          ├── Employment
          ├── Business
          ├── Income
          ├── Expenses
          ├── Assets
          ├── Liabilities
          ├── Existing Loans
          ├── Guarantors
          ├── Collateral
          ├── Risk Rating
          └── Documents
```

### `MFI Customer Profile`

Core fields:

| Group             | Data                                  |
| ----------------- | ------------------------------------- |
| Identity          | Customer ID, legal name, Lao name     |
| Demographic       | DOB, gender, nationality              |
| Identity Document | ID/passport/family book               |
| Address           | Province, district, village           |
| Contact           | Phone, alternate phone                |
| Occupation        | Employment/business                   |
| Household         | Members/dependants                    |
| Financial         | income, expenses, surplus             |
| Risk              | KYC risk, credit risk                 |
| Branch            | owning branch                         |
| Officer           | assigned Loan Officer                 |
| Status            | Prospect/KYC/Active/Restricted/Closed |

This gives LaoCapital something much closer to a proper borrower master than vanilla ERPNext Customer.

---

# 5. KYC architecture

Create:

```text
MFI KYC Case
```

with:

```text
Customer
KYC Type
Identity Verification
Address Verification
Occupation / Business Verification
Beneficial Owner
PEP Screening
Watchlist Screening
Risk Rating
Source of Funds
Purpose of Relationship
EDD Required
Documents
Reviewer
Review Date
Next Review Date
```

Workflow:

```text
DRAFT
  ↓
DOCUMENTS_PENDING
  ↓
UNDER_REVIEW
  ↓
─────────────────────
│ APPROVED           │
│ REJECTED           │
│ EDD_REQUIRED       │
│ COMPLIANCE_HOLD    │
─────────────────────
```

And enforce:

```text
KYC != APPROVED
        ↓
Loan cannot reach DISBURSEMENT
```

---

# 6. Credit origination

Use Frappe Lending's `Loan Application` as the formal loan request, but place BERP MFI stages around it.

```text
Opportunity / Customer
       ↓
MFI Loan Request
       ↓
Frappe Loan Application
       ↓
MFI Field Assessment
       ↓
MFI Credit Assessment
       ↓
MFI Credit Decision
       ↓
Loan Application Approved
```

Frappe Lending already supports applicant information, loan product, requested amount, repayment inputs, co-applicants, documents and collateral proposals. ([Frappe Docs][4])

BERP MFI should add the microfinance-specific underwriting layer.

---

# 7. Field Visit DocType

### `MFI Field Visit`

```text
Visit ID
Customer
Loan Application
Loan Officer
Visit Date
GPS / Location
Residence Verification
Business Verification
Employer Verification
Neighbour Reference
Business Photos
Residence Photos
Inventory Observation
Assets Observed
Income Evidence
Expense Evidence
Existing Debt
Risk Observation
Officer Recommendation
Attachments
```

Status:

```text
PLANNED
  ↓
IN_PROGRESS
  ↓
COMPLETED
  ↓
VERIFIED
```

This record should be immutable after independent verification except through amendment/change-control mechanisms.

---

# 8. Credit Assessment

This should become one of BERP MFI's most important DocTypes.

### `MFI Credit Assessment`

```text
Customer
Loan Application

Requested Amount
Requested Tenor

Monthly Revenue
Monthly Business Expense
Household Income
Household Expense
Existing Debt Payment

Disposable Income
Debt Service Capacity

DTI
FOIR
DSCR

Collateral Value
Haircut
Net Collateral Value
LTV

Credit History
Previous Loan Performance
Days Past Due History

Character Score
Capacity Score
Capital Score
Collateral Score
Conditions Score

Overall Risk Score
Risk Grade

Recommended Amount
Recommended Tenor
Recommended Interest
Recommended Instalment

Analyst
Recommendation
Assessment Date
```

The upstream project is itself moving further toward DTI/FOIR/LTV/EMI affordability inputs in Loan Application, which reinforces keeping BERP MFI's credit model compatible rather than building an entirely unrelated calculation model. ([GitHub][5])

---

# 9. Credit policy engine

Do not hard-code policy into Python such as:

```python
if amount > 100000000:
    require_manager()
```

Instead create:

```text
MFI Credit Policy
MFI Product Policy
MFI Authority Matrix
MFI Exception Rule
```

### Authority matrix

| Dimension         | Example        |
| ----------------- | -------------- |
| Product           | SME Micro Loan |
| Minimum Amount    | ₭0             |
| Maximum Amount    | ₭50M           |
| Risk Grade        | A–C            |
| Branch            | All            |
| Authority         | L1             |
| Approver Role     | Branch Manager |
| Exception Allowed | No             |

Then another rule:

```text
Amount: > ₭50M
Risk Grade: A-B

→ Credit Manager L2
```

And:

```text
Policy exception = YES

→ Head of Credit / Credit Committee
```

The actual limits above are examples only; LaoCapital should set its controlled values.

---

# 10. Approval engine

The workflow should enforce the segregation-of-duties model established for the MFI roles.

```text
Loan Officer
  MAKES
       ↓
Credit Analyst
  ASSESSES
       ↓
Credit Approver
  APPROVES
       ↓
Operations
  VERIFIES
       ↓
Cashier/Treasury
  DISBURSES
       ↓
Accounting
  RECONCILES
```

Core invariant:

```text
ORIGINATE
   ≠
ASSESS
   ≠
APPROVE
   ≠
DISBURSE
   ≠
RECONCILE
```

An application originated by User A must therefore never satisfy an approval requiring an independent User B merely because User A happens to hold both roles.

That requires **workflow-level SoD validation**, not just Frappe Role permissions.

---

# 11. Loan product architecture

Frappe Lending should remain the source of truth for financial loan product mechanics.

```text
Loan Product
├── Interest Rate
├── Frequency
├── Repayment Schedule
├── Penalty
├── Charges
├── Accounting
├── Collection Offset
└── Loan classification
```

Frappe Lending v16 supports policy configuration for repayment allocation and loan classification through company and product controls. ([Frappe Docs][6])

BERP MFI then links:

```text
MFI Product Policy
       │
       ├── Frappe Loan Product
       ├── Customer Segment
       ├── Min / Max Amount
       ├── Min / Max Tenor
       ├── Age Rules
       ├── Business Vintage
       ├── Required Documents
       ├── Guarantor Policy
       ├── Collateral Policy
       ├── Credit Score Threshold
       ├── Approval Matrix
       └── Regulatory Classification
```

This separation is important:

```text
Loan Product
= financial engine

MFI Product Policy
= business / credit governance
```

---

# 12. Loan servicing

Once approved:

```text
Approved Application
       ↓
Loan
       ↓
Contract
       ↓
Disbursement Authorization
       ↓
Loan Disbursement
       ↓
Repayment Schedule
       ↓
Loan Demand
       ↓
Interest Accrual
       ↓
Repayment
```

Frappe Lending should own the mathematical and accounting side of those records. It can already generate repayment schedules from disbursement and supports multiple repayment frequencies. ([Frappe Docs][7])

BERP MFI adds controls and user experience.

---

# 13. Teller / Cashier application

A microfinance branch needs a simplified teller workspace.

### Teller Home

```text
┌─────────────────────────────────────────────┐
│ CASHIER — VIENTIANE BRANCH                 │
├─────────────────────────────────────────────┤
│ Opening Cash     ₭ xxx                     │
│ Cash In          ₭ xxx                     │
│ Cash Out         ₭ xxx                     │
│ Expected Cash    ₭ xxx                     │
├─────────────────────────────────────────────┤
│ [ RECEIVE REPAYMENT ]                       │
│ [ DISBURSE LOAN ]                           │
│ [ OTHER RECEIPT ]                           │
│ [ CASH TRANSFER ]                           │
├─────────────────────────────────────────────┤
│ Today Transactions                          │
│ Exceptions                                  │
│ Pending Reconciliation                      │
└─────────────────────────────────────────────┘
```

Custom DocTypes:

```text
MFI Teller Session
MFI Cash Drawer
MFI Cash Transfer
MFI Teller Reconciliation
MFI Transaction Reversal Request
```

Teller does **not** own the loan ledger. Teller actions trigger controlled Frappe Lending/ERPNext transactions.

---

# 14. Repayment

User enters:

```text
Loan Number / Customer Phone
          ↓
System retrieves:
Customer
Outstanding Principal
Interest Due
Penalty
Charges
Total Due
Past Due
Next Payment
          ↓
Cash / Bank / Digital Payment
          ↓
Loan Repayment
          ↓
Receipt
```

Frappe Lending already allocates repayments through configurable collection offset sequences across principal, interest, penalties and charges. ([Frappe Docs][8])

BERP MFI should therefore **not manually reproduce payment allocation**.

---

# 15. Collection management

Build a separate collections domain.

```text
Loan
 ↓
DPD
 ↓
Collection Queue
 ↓
Collection Case
 ↓
Collector Assignment
 ↓
Call / Visit / Notice
 ↓
Promise to Pay
 ↓
Payment
```

Or:

```text
No Cure
 ↓
Restructure Review
 ↓
Recovery
 ↓
Settlement
 ↓
Write-off
```

Custom DocTypes:

| DocType                   | Purpose               |
| ------------------------- | --------------------- |
| MFI Collection Case       | Collection master     |
| MFI Collection Assignment | Collector portfolio   |
| MFI Collection Activity   | Call/visit/contact    |
| MFI Promise to Pay        | Customer commitment   |
| MFI Collection Visit      | Field collection      |
| MFI Recovery Action       | Escalation            |
| MFI Legal Recovery        | Legal process         |
| MFI Settlement Request    | Settlement governance |

Frappe Lending's servicing layer already supports restructuring, settlement-related repayment modes, write-off processing and portfolio classification; BERP MFI should govern who can initiate and approve these actions. ([Frappe Docs][9])

---

# 16. Portfolio risk

Create an MFI risk cockpit.

```text
Gross Loan Portfolio
Active Loans
Active Borrowers
Average Loan Size

PAR 1
PAR 7
PAR 30
PAR 60
PAR 90

DPD Distribution

Restructured Portfolio
Written-off Portfolio
Recovery Rate

Concentration:
    Branch
    Product
    Sector
    Geography
    Loan Officer
    Risk Grade

Disbursement Trend
Collection Trend
Vintage Performance
Roll Rate
```

Views should support:

```text
Company
→ Region
→ Branch
→ Loan Officer
→ Product
→ Customer
→ Loan
```

---

# 17. Compliance workspace

```text
Compliance
│
├── KYC Queue
├── KYC Expiring
├── High Risk Customers
├── Enhanced Due Diligence
├── AML Alerts
├── PEP Cases
├── Suspicious Activity Cases
├── Policy Exceptions
├── Compliance Holds
└── Regulatory Reports
```

Regulatory logic specific to Lao PDR should live in a distinct controlled layer:

```text
berp_mfi
      +
berp_mfi_lao
```

or:

```text
berp_mfi/
└── compliance/
    └── lao/
```

I prefer the former if bERP is intended eventually to support MFI deployments outside Laos.

That prevents:

```text
generic loan engine
=
Lao regulatory implementation
```

from becoming tightly coupled.

---

# 18. Accounting architecture

This should remain ERPNext-native.

```text
BERP MFI Transaction
       ↓
Frappe Lending
       ↓
ERPNext General Ledger
       ↓
Chart of Accounts
```

Example conceptual accounts:

```text
ASSETS
├── Loans Receivable — Principal
├── Interest Receivable
├── Penalty Receivable
└── Cash / Bank

INCOME
├── Interest Income
├── Processing Fee Income
├── Penalty Income
└── Other Lending Income

LIABILITIES
├── Customer Deposits     [only where applicable]
├── Funding Payable
└── Accrued Liabilities

EXPENSE
├── Provision Expense
├── Write-off Expense
├── Funding Cost
└── Operating Expense
```

Actual account structure should be separately designed and reconciled to LaoCapital's accounting policy and regulatory treatment.

Frappe Lending explicitly integrates its loan operations with ERPNext accounting, rather than acting as an isolated LMS. ([Frappe Docs][1])

---

# 19. Posting-date control

One particularly useful Frappe Lending v16 design is the distinction between:

```text
VALUE DATE
=
actual business transaction date

POSTING DATE
=
accounting ledger date
```

That allows a late-recorded repayment or correction to respect the underlying business date without unnecessarily reopening historical accounting periods. ([Frappe Docs][10])

BERP MFI should expose this only to authorized users and record:

```text
entered_at
entered_by
value_date
posting_date
reason_for_backdate
approved_by
source_document
```

---

# 20. Roles

The BERP MFI application should ship with the role profiles we designed:

| Domain      | Role Profiles                                                |
| ----------- | ------------------------------------------------------------ |
| Governance  | Board, CEO                                                   |
| Credit      | Head of Credit, Credit Manager, Credit Analyst, Loan Officer |
| Operations  | Branch Manager, Customer Service                             |
| Cash        | Teller/Cashier                                               |
| Collections | Collection Officer                                           |
| Finance     | Finance Manager, Accountant, Treasury                        |
| Control     | Risk, Compliance/AML, Internal Auditor                       |
| Platform    | MIS/Reporting, Tenant Administrator                          |

The app should install the role definitions, but **authority limits must be tenant configuration**, not fixture constants.

---

# 21. Branch architecture

Inside the LaoCapital tenant:

```text
Tenant
LaoCapital
│
├── Company
│   LaoCapital Microfinance
│
├── Head Office
│
├── Branch
│   ├── Vientiane
│   ├── Pakse
│   ├── Savannakhet
│   └── ...
│
├── Cost Centers
│
└── Loan Officer Portfolios
```

Remember that the bERP architecture distinguishes SaaS Tenant, Company and Branch.

So:

```text
LaoCapital
=
bERP Tenant

LaoCapital Microfinance
=
ERPNext Company

Pakse
=
Branch
```

not three separate tenants.

---

# 22. Multi-tenancy

For SaaS customers:

```text
BERP Platform
│
├── LaoCapital Tenant
│      ├── ERPNext
│      ├── Lending
│      └── BERP MFI
│
├── MFI-B Tenant
│      ├── ERPNext
│      ├── Lending
│      └── BERP MFI
│
└── MFI-C Tenant
       ├── ERPNext
       ├── Lending
       └── BERP MFI
```

The existing bERP architecture already establishes the preferred boundary:

```text
1 Tenant
=
1 Frappe Site
=
1 isolated database
```

rather than using Company as the SaaS tenant boundary.

That means LaoCapital's customer, loan and accounting data remain physically separated from another MFI tenant.

---

# 23. BERP MFI URL model

Following the existing bERP domain design:

```text
berp.bizera.la/t/laocapital
```

could expose:

```text
/t/laocapital/mfi
/t/laocapital/mfi/customers
/t/laocapital/mfi/kyc
/t/laocapital/mfi/applications
/t/laocapital/mfi/credit
/t/laocapital/mfi/loans
/t/laocapital/mfi/disbursements
/t/laocapital/mfi/teller
/t/laocapital/mfi/collections
/t/laocapital/mfi/collateral
/t/laocapital/mfi/risk
/t/laocapital/mfi/compliance
/t/laocapital/mfi/reports
/t/laocapital/mfi/settings
```

This follows the resource-oriented tenant URL contract already established for bERP.

Internally the Frappe site remains hostname/site based rather than turning Frappe itself into path-level tenancy.

---

# 24. Lao localization

BERP MFI should inherit `berp_lao` and add microfinance terminology.

```text
English                     Lao
-------------------------------------------------
Customer
Borrower
Loan
Loan Application
Principal
Interest
Interest Rate
Penalty
Instalment
Outstanding Balance
Due Date
Past Due
Collateral
Guarantor
Disbursement
Repayment
Restructure
Write-off
Collection
Credit Assessment
Risk Grade
```

The approved translation registry should drive:

```text
UI
Reports
Contracts
Receipts
Loan statements
Repayment schedules
Notifications
Print formats
```

rather than allowing each developer to invent Lao terminology independently.

---

# 25. Mobile architecture

I would plan a dedicated **BERP MFI Field App** rather than depending on a generic ERPNext mobile wrapper.

```text
BERP MFI Field App
│
├── Login
├── My Customers
├── New Customer
├── KYC
├── Loan Application
├── Field Visit
├── Assessment
├── Photo Capture
├── GPS Evidence
├── My Portfolio
├── Due Today
├── Collection Visit
├── Promise to Pay
└── Sync
```

Architecture:

```text
Mobile
  ↓
api.berp.bizera.la
  ↓
Identity / Tenant
  ↓
BERP MFI API
  ↓
BERP MFI
  ↓
Frappe Lending / ERPNext
```

The field app should ultimately be **offline-capable**, because field officers cannot assume reliable connectivity everywhere.

---

# 26. API domains

I would expose business APIs rather than the raw DocType API to external channels.

```text
/api/v1/mfi/customers
/api/v1/mfi/kyc
/api/v1/mfi/applications
/api/v1/mfi/credit-assessments
/api/v1/mfi/loans
/api/v1/mfi/disbursements
/api/v1/mfi/repayments
/api/v1/mfi/collections
/api/v1/mfi/portfolio
```

Internally, Frappe Lending is already REST/API-friendly, including loan booking and repayment-schedule generation APIs. ([Frappe Docs][11])

But BERP MFI APIs should form an **anti-corruption layer** so external mobile apps and integrations do not become permanently coupled to upstream Frappe DocType schemas.

---

# 27. Recommended repository

```text
apps/
└── berp_mfi/
    ├── berp_mfi/
    │   ├── customer/
    │   ├── kyc/
    │   ├── origination/
    │   ├── credit/
    │   ├── loan_operations/
    │   ├── teller/
    │   ├── collections/
    │   ├── collateral/
    │   ├── risk/
    │   ├── compliance/
    │   ├── accounting/
    │   ├── reporting/
    │   ├── integrations/
    │   └── setup/
    │
    ├── public/
    ├── templates/
    ├── fixtures/
    ├── patches/
    ├── tests/
    │   ├── unit/
    │   ├── workflow/
    │   ├── accounting/
    │   ├── permissions/
    │   ├── sod/
    │   ├── loan_lifecycle/
    │   └── regression/
    │
    ├── hooks.py
    └── pyproject.toml
```

Frappe's DocType model is designed precisely for building these domain-specific records without modifying ERPNext core tables. ([Frappe Docs][12])

---

# 28. Non-negotiable application invariants

For BERP MFI I would lock these as architecture requirements:

```text
01  No KYC approval → no disbursement

02  Maker cannot approve own transaction

03  Approver authority must cover amount/product/risk

04  Disbursement cannot exceed approved amount

05  Disbursement cannot precede approval

06  Teller cannot modify credit terms

07  Loan Officer cannot manipulate GL

08  Loan balances derive from financial transactions,
    never manually editable fields

09  Repayment allocation follows controlled policy

10  Submitted financial evidence is immutable

11  Backdated transactions require reason + authority

12  Write-off requires independent approval

13  Restructure preserves original contract history

14  User access is constrained by tenant + branch +
    role + portfolio + workflow + authority

15  Every privileged action creates audit evidence
```

And above all:

```text
Identity
  ↓
Tenant
  ↓
Branch
  ↓
Role
  ↓
Portfolio
  ↓
Authority
  ↓
Workflow State
  ↓
Action
  ↓
Financial Transaction
  ↓
Audit Evidence
```

That is consistent with the broader bERP security invariant already defined for Identity → Tenant Membership → Tenant Context → Authorization → ERP Site → Tenant Database → Audit Evidence.

---

# 29. BERP MFI product architecture

I would formally define the product as:

```text
                     BERP MFI
                         │
        ┌────────────────┼────────────────┐
        │                │                │
 CUSTOMER & KYC      CREDIT ENGINE    SERVICING
        │                │                │
 Customer 360        Assessment        Loan
 KYC                 Scoring           Disbursement
 Documents           Policy            Schedule
 Household           Approval          Repayment
 Business            Exception         Accrual
        │                │                │
        ├────────────────┼────────────────┤
        │                │                │
 COLLECTIONS          RISK          COMPLIANCE
        │                │                │
 DPD Queue            PAR              AML
 PTP                  NPL              KYC
 Visits               Vintage          EDD
 Recovery             Exposure         Alerts
 Restructure          Concentration    Cases
        │                │                │
        └────────────────┼────────────────┘
                         │
                  FINANCE & AUDIT
                         │
                     ERPNext GL
                         │
              ┌──────────┴──────────┐
              │                     │
          BERP PLATFORM        BERP LAO
```

## Recommended controlled build sequence

I would now establish **`BERP-MFI-ARCH-001 — BERP Microfinance Application Architecture v0.1`** as the parent architecture artifact, then execute:

| WP           | Controlled unit           | Outcome                  |
| ------------ | ------------------------- | ------------------------ |
| **MFI-001A** | Domain & bounded contexts | Domain model             |
| **MFI-001B** | DocType registry          | Data architecture        |
| **MFI-001C** | Loan lifecycle            | Canonical state machines |
| **MFI-001D** | RBAC + SoD                | Permission architecture  |
| **MFI-001E** | Credit policy & authority | Decision engine          |
| **MFI-001F** | Lending integration       | Upstream mapping         |
| **MFI-001G** | Accounting integration    | GL contracts             |
| **MFI-001H** | Collections               | DPD/recovery model       |
| **MFI-001I** | Risk & compliance         | Control model            |
| **MFI-001J** | Lao localization          | Lao MFI pack             |
| **MFI-001K** | UX/workspaces             | Screen registry          |
| **MFI-001L** | API/mobile contract       | Channel architecture     |
| **MFI-001M** | Test & evidence           | Acceptance contracts     |

The most important next step is **MFI-001B — the complete DocType Registry + ERD**, because that will force us to decide exactly which records belong to ERPNext, which belong to Frappe Lending, and which belong to `berp_mfi` before implementation starts. That prevents BERP MFI from becoming an unmaintainable set of ERPNext customizations.

[1]: https://docs.frappe.io/lending/introduction?utm_source=chatgpt.com "Introduction to Frappe Lending"
[2]: https://github.com/frappe/erpnext/wiki/Supported-Versions?utm_source=chatgpt.com "Supported Versions · frappe/erpnext Wiki · GitHub"
[3]: https://docs.frappe.io/lending/loan-product?utm_source=chatgpt.com "Loan Product"
[4]: https://docs.frappe.io/lending/loan-application?utm_source=chatgpt.com "Loan Application"
[5]: https://github.com/frappe/lending/pulls?utm_source=chatgpt.com "Pull requests · frappe/lending · GitHub"
[6]: https://docs.frappe.io/lending/loan-management/setup/company-level-setup?utm_source=chatgpt.com "Company Level Setup"
[7]: https://docs.frappe.io/lending/loan?utm_source=chatgpt.com "Loan Booking"
[8]: https://docs.frappe.io/lending/loan-repayment?utm_source=chatgpt.com "Loan Repayment"
[9]: https://docs.frappe.io/lending/loan-restructure?utm_source=chatgpt.com "Loan Restructure"
[10]: https://docs.frappe.io/lending/loan-management/automated-accounting/posting-date-and-value-date?utm_source=chatgpt.com "Posting Date and Value Date"
[11]: https://docs.frappe.io/lending/loan-management/api-documentation/transactions/loan-booking?utm_source=chatgpt.com "Loan Booking"
[12]: https://docs.frappe.io/erpnext/doctype?utm_source=chatgpt.com "DocType"
