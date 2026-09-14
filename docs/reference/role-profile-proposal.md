# Original role-profile proposal

> Archived user-supplied proposal. Claims, examples and citations are preserved as received; they are not verified requirements or implementation authority. Read [the architecture](../BERP-MFI-ARCH-001.md) and [the audit](../BERP-MFI-AUDIT-001.md) first. This proposal does not supersede deposit/non-deposit scope.

---

Yes. For **LaoCapital.la as a microfinance institution running on bERP/ERPNext**, I recommend designing access around the **credit lifecycle and segregation of duties**, rather than simply copying ERPNext’s default roles.

The Bank of the Lao PDR distinguishes deposit-taking MFIs, non-deposit-taking MFIs, and microfinance projects, so LaoCapital’s exact regulatory role set should ultimately be calibrated to its license type. ([Bolivia Government][1]) Current Lao financial-sector requirements also make AML/CFT and financial-consumer-protection controls material to the design. ([Bolivia Government][2])

## 1. Recommended LaoCapital role architecture

I would use **atomic system roles + business Role Profiles**.

```text
User
  ↓
Role Profile = Job Function
  ↓
Atomic Roles = Individual Capabilities
  ↓
Company / Branch / Portfolio restrictions
  ↓
Workflow authority
  ↓
Transaction limits
```

This fits ERPNext well because Frappe supports role-based permissions, per-user restrictions, field permission levels, and Role Profiles grouping multiple roles. ([Frappe Docs][3])

### Recommended business Role Profiles

| Code   | Role Profile             | Primary Responsibility                       |
| ------ | ------------------------ | -------------------------------------------- |
| LC-001 | Board / Director         | Governance, high-level oversight             |
| LC-002 | CEO / Managing Director  | Executive authority                          |
| LC-003 | Head of Credit           | Credit policy and portfolio                  |
| LC-004 | Credit Manager           | Loan review and approval                     |
| LC-005 | Credit Analyst           | Credit assessment                            |
| LC-006 | Branch Manager           | Branch operation + bounded approval          |
| LC-007 | Loan Officer             | Customer acquisition and loan origination    |
| LC-008 | Collection Officer       | Repayment and delinquency management         |
| LC-009 | Cashier / Teller         | Cash receipt and disbursement                |
| LC-010 | Finance Manager          | Accounting and financial control             |
| LC-011 | Accountant               | GL/AP/AR/reconciliation                      |
| LC-012 | Treasury Officer         | Bank/cash/funding management                 |
| LC-013 | Risk Manager             | Portfolio and operational risk               |
| LC-014 | Compliance / AML Officer | KYC, AML/CFT, regulatory compliance          |
| LC-015 | Internal Auditor         | Independent audit                            |
| LC-016 | Customer Service         | Customer service and account inquiry         |
| LC-017 | HR Manager               | HR/payroll administration                    |
| LC-018 | MIS / Reporting Officer  | Management and regulatory reporting          |
| LC-019 | Tenant Administrator     | LaoCapital bERP administration               |
| LC-020 | IT Support               | Technical support without business authority |

I would add another profile only if LaoCapital is a **deposit-taking MFI**:

| Code   | Role Profile       | Responsibility              |
| ------ | ------------------ | --------------------------- |
| LC-021 | Deposit Officer    | Savings/deposit accounts    |
| LC-022 | Deposit Supervisor | Deposit operations approval |

---

# 2. Credit lifecycle and authority

The central workflow should be:

```text
Customer / Lead
      ↓
KYC
      ↓
Loan Application
      ↓
Credit Assessment
      ↓
Credit Recommendation
      ↓
Approval
      ↓
Loan Contract
      ↓
Disbursement
      ↓
Active Loan
      ↓
Repayment
      ↓
─────────────────────────
│ Normal      Delinquent │
│    ↓             ↓     │
│ Closed     Collections │
│                  ↓     │
│          Restructure   │
│          / Recovery    │
│          / Write-off   │
─────────────────────────
```

The same user should **not control the complete chain**.

The fundamental control is:

```text
ORIGINATE ≠ ASSESS ≠ APPROVE ≠ DISBURSE ≠ RECONCILE
```

That should become a LaoCapital/bERP security invariant.

---

# 3. Loan Officer

### `LC Loan Officer`

The Loan Officer is the **maker**, not the approver.

Can:

```text
Create Customer
Create Prospect / Lead
Collect KYC
Create Loan Application
Upload customer documents
Capture household/business data
Capture income / expense
Capture collateral
Request credit bureau check
Conduct field visit
Create assessment notes
Recommend loan
View own customer portfolio
View own repayment portfolio
```

Cannot:

```text
Approve own loan
Change approved interest rate
Override product rules
Disburse loan
Post GL
Write off loan
Delete submitted loan
Change repayment history
Approve restructuring
```

Recommended record scope:

```text
Branch = assigned branch
Loan Officer = current user
Portfolio = assigned portfolio
```

---

# 4. Credit Analyst

### `LC Credit Analyst`

Can independently review:

```text
KYC
Customer profile
Loan request
Income / expense
Debt service capacity
Credit history
Collateral
Guarantor
Risk score
Field verification
Supporting documents
```

Can produce:

```text
Credit Assessment
Risk Grade
Recommended Amount
Recommended Tenor
Recommended Pricing
Conditions Precedent
Recommendation:
    APPROVE
    DECLINE
    RETURN
```

Cannot:

```text
Disburse
Receive cash
Alter accounting
Approve outside delegated authority
```

This separation between Loan Officer and Credit Analyst becomes particularly valuable as LaoCapital scales.

---

# 5. Credit approval roles

Do **not** create one generic `Loan Approver`.

Use authority levels.

```text
LC Credit Approver L1
LC Credit Approver L2
LC Credit Approver L3
LC Credit Committee
LC Executive Credit Approver
```

For example:

```text
Loan Officer
    ↓ Recommend

Credit Analyst
    ↓ Assess

L1 — Branch Approval
    ↓

L2 — Credit Manager
    ↓

L3 — Head of Credit
    ↓

Credit Committee / CEO
```

But approval should be determined by an **Authority Matrix**, not merely the role name.

Example:

| Condition           | Required Authority                                |
| ------------------- | ------------------------------------------------- |
| Standard small loan | L1                                                |
| Higher exposure     | L2                                                |
| Large exposure      | L3                                                |
| Policy exception    | Credit Committee                                  |
| Related party       | Special governance route                          |
| Restructure         | Credit + Risk                                     |
| Write-off           | Credit + Finance + authorized executive/committee |

The actual LAK limits should live in configuration:

```text
Credit Authority Matrix

Product
Branch
Risk Grade
Min Amount
Max Amount
Approver Level
Exception Rule
Effective Date
```

not hard-coded into permissions.

---

# 6. Branch Manager

A Branch Manager should manage a branch, but **not become a superuser**.

Can:

```text
Branch dashboard
Branch portfolio
Branch staff
Customer escalations
Operational approvals
Loan approval within delegated limit
Collection performance
Branch expense approval within limit
Cash position view
```

Cannot:

```text
Change approved accounting entries
Change system permissions
Approve above delegated credit limit
Approve own originated transaction
Perform unrestricted write-off
Change audit records
```

Scope:

```text
Company = LaoCapital
Branch = Assigned Branch
```

ERPNext's User Permissions are useful here because users can be restricted using linked values such as a branch or other organizational dimension. ([Frappe Docs][4])

---

# 7. Cashier / Teller

This role needs very strong separation.

Can:

```text
Receive repayment
Receive fees
Disburse approved loans
Issue receipt
Cash transfer
Cash opening
Cash closing
Cash denomination
Daily cash report
```

Cannot:

```text
Create loan
Assess credit
Approve loan
Change loan amount
Change interest
Modify repayment schedule
Write off
Approve reversal
```

A disbursement should require:

```text
APPROVED Loan
      +
Executed Contract
      +
KYC Complete
      +
Conditions Satisfied
      ↓
PAYMENT AUTHORIZATION
      ↓
Cashier
      ↓
DISBURSED
```

The Cashier must never turn an unapproved application into cash.

---

# 8. Collection Officer

### `LC Collection Officer`

Can see:

```text
Assigned accounts
Outstanding balance
Due instalments
Days Past Due
Arrears
Promise-to-pay
Customer contact
Collection history
Collateral information needed for recovery
```

Can create:

```text
Collection Visit
Collection Call
Promise to Pay
Recovery Action
Delinquency Note
Restructure Request
Legal Escalation Request
```

Cannot:

```text
Erase arrears
Change principal
Change interest already posted
Backdate repayments
Approve restructuring
Approve write-off
```

Collections should preferably use a separate portfolio authority from origination.

---

# 9. Finance & Accounting roles

I would split finance into three profiles.

### Accountant

```text
Journal Entries
GL
AP
AR
Accruals
Fixed Assets
Expense posting
Reconciliation preparation
Financial reports
```

### Finance Manager

```text
Approve journal entries
Period close
Financial statements
Accounting controls
Provision review
Expense approvals
Reconciliation approval
```

### Treasury Officer

```text
Bank Accounts
Liquidity
Funding
Transfers
Cash position
Bank reconciliation preparation
Funding repayment
```

A Loan Officer or Branch Manager should never get unrestricted GL authority.

---

# 10. Risk Manager

Risk should be independent of loan origination.

Access:

```text
Entire loan portfolio — READ
Portfolio concentration
PAR
NPL / delinquency
Risk grades
Exceptions
Collateral
Restructuring
Write-offs
Branch risk
Product risk
Vintage analysis
Credit concentration
```

Authority:

```text
Flag risk
Place review hold
Escalate exception
Review restructuring
Review policy exception
```

But generally:

```text
Risk ≠ transaction maker
Risk ≠ cashier
```

---

# 11. Compliance / AML Officer

This should be a first-class bERP role, not part of accounting.

```text
LC Compliance Officer
LC AML Officer
```

For a smaller MFI these can initially be one Role Profile.

Access:

```text
Customer KYC
Beneficial owner
ID documents
Customer risk rating
PEP status
AML alerts
Suspicious transaction cases
Sanctions screening results
High-risk customers
Transaction patterns
Compliance exceptions
Regulatory reporting
```

Authority should include:

```text
KYC REVIEW
KYC REJECT
EDD REQUIRED
COMPLIANCE HOLD
AML ESCALATION
CASE CLOSE
```

without granting ordinary accounting or loan-disbursement authority.

The current Bank of Lao PDR legislation catalogue includes the amended 2024 AML/CFT law, which is one reason I would make this a dedicated security domain. ([Bolivia Government][2])

---

# 12. Internal Auditor

The auditor should have **broad read access and almost zero operational write access**.

```text
READ:
Customers
Loans
Credit assessments
Approvals
Payments
Cash
Accounting
User activity
Workflow history
Configuration changes
Exceptions
AML cases where authorized
Audit evidence

WRITE:
Audit Finding
Audit Working Paper
Audit Recommendation
Audit Follow-up
```

Should **not** be permitted to:

```text
Approve loans
Post transactions
Collect cash
Edit customer balances
Edit GL
Change original evidence
```

Think:

```text
AUDITOR
= See almost everything
+ Change almost nothing
```

---

# 13. Board / Director

Board users should not need normal ERP operational access.

Provide an **Executive Governance Workspace**:

```text
Portfolio Outstanding
Number of Active Borrowers
Disbursement
Collections
PAR 1
PAR 30
PAR 60
PAR 90
NPL
Write-off
Provision
Portfolio Yield
Cost of Funds
Liquidity
Branch Performance
Product Performance
Risk Concentration
Compliance Exceptions
P&L
Balance Sheet
Cash Flow
Capital / Equity
```

Mostly:

```text
READ + REPORT
```

with workflow authority only where LaoCapital's governance policy explicitly requires Board action.

---

# 14. CEO / Managing Director

CEO should have wide visibility but still not use unrestricted `Administrator`.

```text
Executive Dashboard
Company-wide portfolio
Finance reports
Risk
Compliance
Branches
HR summary
Credit authority where policy permits
Major expenditure approvals
Strategic reports
```

But:

```text
CEO ≠ System Administrator
```

This is an important distinction.

---

# 15. bERP Tenant Administrator

For LaoCapital I would create:

### `LC Tenant Administrator`

Can:

```text
Manage users
Assign approved Role Profiles
Branch configuration
Workspace configuration
Notifications
Print formats
Approved system configuration
Integration configuration
```

Cannot by default:

```text
Approve loans
Post payments
Post accounting
Disburse cash
Write off loans
Change audit evidence
```

And reserve the Frappe `Administrator` account for controlled technical administration/emergency use.

This follows the bERP security model in which identity, tenant context, authorization, isolated tenant data, and audit evidence remain distinct controls.

---

# 16. Recommended permission dimensions

Do not rely on Role alone.

I recommend that every authorization resolve:

```text
USER
 ↓
TENANT
 ↓
COMPANY
 ↓
BRANCH
 ↓
ROLE
 ↓
PORTFOLIO
 ↓
PRODUCT
 ↓
TRANSACTION
 ↓
WORKFLOW STATE
 ↓
AUTHORITY LIMIT
 ↓
ACTION
```

For example:

```text
User: Somchai

Tenant:
laocapital

Role Profile:
Loan Officer

Branch:
Vientiane Capital

Portfolio:
LO-VTE-003

Products:
Micro SME
Consumer

Maximum Approval:
0

Loan Access:
Assigned customers only
```

versus:

```text
User: Branch Manager

Tenant:
laocapital

Branch:
Pakse

Role:
Branch Manager
Credit Approver L1

Approval Limit:
configured by authority matrix

Customer Access:
Pakse Branch

Accounting:
Read only

Cash:
Summary only
```

---

# 17. Sensitive field security

Use field-level permission for highly sensitive information.

Frappe supports different permission levels for fields within the same document. ([Frappe Docs][5])

For example:

```text
Customer
├── General Profile          Perm Level 0
├── KYC Information          Perm Level 1
├── AML Risk                 Perm Level 2
├── Credit Bureau Result     Perm Level 2
└── Sensitive Compliance     Perm Level 3
```

And:

```text
Loan
├── Normal Loan Data         Level 0
├── Credit Assessment        Level 1
├── Approval Information     Level 2
├── Exception Override       Level 3
└── Write-off Information    Level 3
```

---

# 18. Recommended V1 role hierarchy

I would lock the first LaoCapital configuration at **18 operational Role Profiles**:

```text
LAOCAPITAL
│
├── GOVERNANCE
│   ├── Board / Director
│   └── CEO / Managing Director
│
├── CREDIT
│   ├── Head of Credit
│   ├── Credit Manager
│   ├── Credit Analyst
│   └── Loan Officer
│
├── BRANCH OPERATIONS
│   ├── Branch Manager
│   ├── Customer Service
│   ├── Cashier / Teller
│   └── Collection Officer
│
├── FINANCE
│   ├── Finance Manager
│   ├── Accountant
│   └── Treasury Officer
│
├── CONTROL
│   ├── Risk Manager
│   ├── Compliance / AML Officer
│   └── Internal Auditor
│
└── PLATFORM
    ├── MIS / Reporting
    └── Tenant Administrator
```

Then add **Deposit Operations** only if LaoCapital is licensed for deposit taking.

---

## The control model I recommend locking

For LaoCapital, the core access-control invariant should be:

```text
Customer Acquisition
        ↓
Loan Officer
        ↓
Credit Assessment
        ↓
Independent Credit Review
        ↓
Delegated Approval
        ↓
Contract
        ↓
Independent Disbursement
        ↓
Accounting
        ↓
Independent Reconciliation
        ↓
Risk / Compliance
        ↓
Independent Audit
```

And technically:

```text
Identity
  → LaoCapital Tenant
  → Role Profile
  → Branch / Portfolio Scope
  → Workflow Authority
  → Transaction Limit
  → Action
  → Audit Evidence
```

This is considerably safer than creating broad roles such as `Loan User`, `Loan Manager`, and `Administrator`.

For **bERP**, I would make this the basis of a dedicated **`BERP-MFI-RBAC-001 — Microfinance Role, Authority & Segregation-of-Duties Matrix`**, because the next important step is not merely listing roles—it is mapping these 18 profiles against **Customer, KYC, Loan Application, Credit Assessment, Loan Approval, Contract, Disbursement, Repayment, Collection, Restructure, Write-off, GL, Cash, AML Case, Reports and System Settings** with `Read / Create / Write / Submit / Approve / Cancel / Export / Scope / Approval Limit`. That would be implementation-ready for ERPNext.

[1]: https://www.bol.gov.la/en/fileupload/20-01-2020_1579502727.pdf?utm_source=chatgpt.com "1. **Financial Institution** means the commercial banks, Microfinance Institutions, Saving and Credit Union, Pawnshops, Leasing Company and other Financial Institutions which are under the supervision of the Bank of the Lao PDR as defined in relevant laws and regulations;"
[2]: https://bol.gov.la/en/law?utm_source=chatgpt.com "Bank of the Lao P.D.R"
[3]: https://docs.frappe.io/erpnext/permissions?utm_source=chatgpt.com "Role Based Permissions"
[4]: https://docs.frappe.io/erpnext/user-permissions?utm_source=chatgpt.com "User Permissions"
[5]: https://docs.frappe.io/erpnext/perm-levels?utm_source=chatgpt.com "Perm Levels"
