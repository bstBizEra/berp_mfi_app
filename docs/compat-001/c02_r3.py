"""Lab-only C02-R3 Lending-to-GL transaction topology probe.

This script uses Lending's disposable test helpers and never asserts amounts,
allocation, settlement, retry, or reversal correctness.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
import uuid
from pathlib import Path

import frappe
from frappe.model.document import Document

SITE = "mfi-compat.localhost"
RUN = uuid.uuid4().hex
OUT = Path("/workspace/c02-r3") / RUN
EVENTS: list[dict] = []
SEQ = 0
CORRELATION = ""
ORIGIN = "cli_probe"
_PATCHED = False


def emit(kind: str, **data):
    global SEQ
    row = {
        "sequence": SEQ,
        "timestamp": frappe.utils.now_datetime().isoformat(),
        "kind": kind,
        "run": RUN,
        "correlation_id": CORRELATION,
        "origin": ORIGIN,
        "site": SITE,
        "session": id(frappe.db),
    }
    row.update(data)
    EVENTS.append(row)
    SEQ += 1


def sql_class(query: str) -> str:
    text = " ".join(str(query).split()).upper()
    for name in ("COMMIT", "ROLLBACK", "SAVEPOINT", "INSERT", "UPDATE", "DELETE", "SELECT"):
        if text.startswith(name) or f" {name} " in text[:80]:
            return name
    return text.split(" ", 1)[0] if text else "EMPTY"


def patch_observer():
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    original_sql = frappe.db.sql
    original_begin = frappe.db.begin
    original_commit = frappe.db.commit
    original_rollback = frappe.db.rollback
    original_savepoint = frappe.db.savepoint
    original_run_method = Document.run_method

    def sql(query, *args, **kwargs):
        if CORRELATION and not kwargs.pop("_c02_observer", False):
            emit(
                "sql",
                sql_class=sql_class(query),
                query_hash=hashlib.sha256(str(query).encode()).hexdigest(),
                query_preview=" ".join(str(query).split())[:500],
            )
        return original_sql(query, *args, **kwargs)

    def begin(*args, **kwargs):
        emit("transaction_boundary", method="begin")
        return original_begin(*args, **kwargs)

    def commit(*args, **kwargs):
        emit("transaction_boundary", method="commit")
        return original_commit(*args, **kwargs)

    def rollback(*args, **kwargs):
        emit("transaction_boundary", method="rollback", save_point=kwargs.get("save_point"))
        return original_rollback(*args, **kwargs)

    def savepoint(name, *args, **kwargs):
        emit("transaction_boundary", method="savepoint", savepoint=name)
        return original_savepoint(name, *args, **kwargs)

    def run_method(self, method, *args, **kwargs):
        if CORRELATION and method in {
            "validate", "before_submit", "on_submit", "on_cancel", "after_insert",
            "make_gl_entries", "before_save", "on_update",
        }:
            emit("lifecycle", doctype=self.doctype, name=self.name, method=method)
        return original_run_method(self, method, *args, **kwargs)

    frappe.db.sql = sql
    frappe.db.begin = begin
    frappe.db.commit = commit
    frappe.db.rollback = rollback
    frappe.db.savepoint = savepoint
    Document.run_method = run_method

    from lending.loan_management.controllers.loan_controller import LoanController
    from erpnext.accounts.general_ledger import make_gl_entries as gl_function
    import lending.loan_management.controllers.loan_controller as loan_controller
    import erpnext.accounts.general_ledger as general_ledger

    original_lending_gl = LoanController.make_gl_entries
    original_gl = gl_function

    def lending_gl(self, *args, **kwargs):
        emit("lending_entry", doctype=self.doctype, name=self.name, method="LoanController.make_gl_entries")
        return original_lending_gl(self, *args, **kwargs)

    def gl(*args, **kwargs):
        emit("erpnext_entry", method="general_ledger.make_gl_entries")
        return original_gl(*args, **kwargs)

    LoanController.make_gl_entries = lending_gl
    loan_controller.LoanController.make_gl_entries = lending_gl
    general_ledger.make_gl_entries = gl


def count_rows():
    return {
        dt: frappe.db.count(dt)
        for dt in ("Loan", "Loan Disbursement", "Loan Repayment", "GL Entry", "Payment Ledger Entry")
    }


def setup_data():
    product = frappe.db.get_value("Loan Product", {}, "name") or "Demand Loan"
    product_company = frappe.db.get_value("Loan Product", product, "company")
    customer = frappe.db.get_value("Customer", {}, "name") or "_Test Loan Customer"
    loan = frappe.new_doc("Loan")
    loan.company = product_company
    loan.applicant_type = "Customer"
    loan.applicant = customer
    loan.loan_product = product
    loan.loan_amount = 1000
    loan.maximum_limit_amount = 1000
    loan.is_term_loan = 0
    loan.is_secured_loan = 0
    loan.posting_date = frappe.utils.nowdate()
    loan.payment_account = frappe.db.get_value("Account", {"account_type": "Bank"}, "name")
    loan.loan_account = frappe.db.get_value("Account", {"account_name": ("Loan Account")}, "name")
    loan.interest_income_account = frappe.db.get_value("Account", {"account_name": ("Interest Income Account")}, "name")
    loan.penalty_income_account = frappe.db.get_value("Account", {"account_name": ("Penalty Income Account")}, "name")
    loan.submit()
    frappe.db.commit()
    return customer, loan.name


def run_probe(label: str, operation, expect_durable: bool):
    global CORRELATION
    CORRELATION = f"{RUN}-{label}"
    before = count_rows()
    emit("probe_start", label=label, before=before)
    result = {"label": label, "before": before}
    try:
        operation()
        result["operation"] = "success"
        if expect_durable:
            frappe.db.commit()
            emit("transaction_boundary", method="commit", reason="probe_success")
        else:
            frappe.db.rollback()
            emit("transaction_boundary", method="rollback", reason="probe_outer_rollback")
    except Exception as exc:
        result["operation"] = "exception"
        result["exception"] = f"{type(exc).__name__}: {exc}"
        emit("probe_exception", label=label, error=result["exception"])
        frappe.db.rollback()
        emit("transaction_boundary", method="rollback", reason="probe_exception")
    result["after"] = count_rows()
    result["durable_delta"] = {k: result["after"][k] - before[k] for k in before}
    emit("probe_end", label=label, after=result["after"], durable_delta=result["durable_delta"])
    return result


def main():
    global CORRELATION
    OUT.mkdir(parents=True, exist_ok=True)
    frappe.init(site=SITE)
    frappe.connect()
    try:
        customer, loan_name = setup_data()
        patch_observer()
        # The disposable lab may retain a large synthetic maintenance queue
        # from ERPNext fixture bootstrap. Preserve enqueue calls in the trace,
        # but disable only the queue-size guard so it cannot block the probe.
        import frappe.utils.background_jobs as background_jobs
        background_jobs._check_queue_size = lambda queue: None
        # Keep the probe focused on transaction ownership. Disable the optional
        # budget controller because this synthetic site lacks its Department
        # accounting-dimension column; the resulting error is recorded as a
        # lab-schema precondition, not misclassified as a financial result.
        frappe.db.set_single_value("Accounts Settings", "use_legacy_budget_controller", 1)
        frappe.db.commit()
        def repayment_entry(loan, amount):
            doc = frappe.new_doc("Loan Repayment")
            doc.against_loan = loan
            doc.company = frappe.db.get_value("Loan", loan, "company")
            doc.posting_date = frappe.utils.nowdate()
            doc.value_date = frappe.utils.nowdate()
            doc.amount_paid = amount
            doc.repayment_type = "Normal Repayment"
            return doc

        def disbursement_entry(loan, amount):
            doc = frappe.new_doc("Loan Disbursement")
            doc.against_loan = loan
            doc.company = frappe.db.get_value("Loan", loan, "company")
            doc.disbursement_date = frappe.utils.nowdate()
            doc.repayment_start_date = frappe.utils.nowdate()
            doc.disbursed_amount = amount
            return doc

        # R3-01: repayment submit then explicit outer rollback.
        repayment_result = run_probe(
            "R3-01-repayment-rollback",
            lambda: repayment_entry(loan_name, 100).insert(ignore_permissions=True).submit(),
            expect_durable=False,
        )

        # R3-02: disbursement submit then explicit outer rollback.
        disbursement_result = run_probe(
            "R3-02-disbursement-rollback",
            lambda: disbursement_entry(loan_name, 1000).insert(ignore_permissions=True).submit(),
            expect_durable=False,
        )

        # R3-03: a successful repayment path with the commit owned by the probe caller.
        success_result = run_probe(
            "R3-03-repayment-commit",
            lambda: repayment_entry(loan_name, 100).insert(ignore_permissions=True).submit(),
            expect_durable=True,
        )

        # R3-04: controlled failure after the Lending/GL call is attempted.
        def failing_repayment():
            repayment_entry(loan_name, 100).insert(ignore_permissions=True).submit()
            raise RuntimeError("C02-R3 controlled failure before outer commit")

        failure_result = run_probe("R3-04-failure-before-commit", failing_repayment, expect_durable=False)
        results = {
            "run": RUN,
            "site": SITE,
            "loan": loan_name,
            "probes": [repayment_result, disbursement_result, success_result, failure_result],
            "financial_correctness": "NOT_RUN",
            "lock_observation": "NOT_RUN",
        }
        (OUT / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True))
        (OUT / "events.jsonl").write_text("\n".join(json.dumps(e, sort_keys=True) for e in EVENTS) + "\n")
        manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir()}
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        print(json.dumps({"run": RUN, "out": str(OUT), "results": results}, indent=2, sort_keys=True))
    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
