# C02-R3 Lending-to-GL topology results

Status: **PARTIAL — CLI financial-path topology observed; C02 remains incomplete.**

Run: `b47025db038041e19ff8f182009cde9c` on the private `berp-linux` R1 lab
(Frappe 16.33.1, ERPNext 16.34.2, Lending 16.5.0).

## Observed results

| Probe | Result | Durable effect |
|---|---|---|
| R3-01 Loan Repayment submit + outer rollback | PASS | Loan Repayment, PLE and GL rows returned to zero delta |
| R3-02 Loan Disbursement submit + outer rollback | PASS | Loan Disbursement and GL rows returned to zero delta |
| R3-03 successful Loan Repayment path | PASS | 1 Loan Repayment, 1 PLE and 2 GL rows committed |
| R3-04 controlled failure before outer commit | PASS | No additional durable rows after rollback |

The trace contains 1,023 events on one DB session. Each repayment path reaches
`Loan Repayment.on_submit`, `LoanController.make_gl_entries`, Payment Ledger Entry
lifecycle, and GL Entry lifecycle before the caller-owned boundary. R3-01 and
R3-02 show explicit outer rollback; R3-03 shows commit; R3-04 shows the same
Lending/GL path followed by a controlled exception and rollback.

## Scope and limits

This is a controlled CLI probe. It does not yet prove WSGI request ownership,
RQ worker ownership, `enqueue_after_commit` behavior, or a separate error-log
transaction. The probe disables the disposable lab's queue-size guard and uses
the legacy budget controller because the synthetic site's optional Department
accounting-dimension column is absent; those harness conditions are recorded in
the trace and are not financial correctness claims.

No amounts, allocation, settlement account, retry, reversal, or Model-A behavior
was tested. Financial correctness remains **NOT RUN** and C03 remains blocked.

## Disposition

C02-R3 establishes bounded CLI evidence that Lending mutations and ERPNext GL/PLE
writes occur before the caller's commit or rollback. It does not close C02. The
next required evidence is request and worker correlation plus after-commit and
error-log behavior, followed by independent C02 review.
