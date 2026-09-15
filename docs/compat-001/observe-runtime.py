"""Disposable C02 baseline. No financial operations; not a C03 proof."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

ROOT = Path('/workspace')
SITE = 'mfi-compat.localhost'
OUT = ROOT / 'c02-observations' / str(uuid.uuid4())
OUT.mkdir(parents=True)
os.chdir(ROOT / 'bench' / 'sites')
import frappe
from frappe.database.database import Database

events = []
origin = 'bootstrap'
correlation = str(uuid.uuid4())

def emit(kind, **fields):
    events.append(dict(sequence=len(events), timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       correlation_id=correlation, site=SITE, origin=origin, kind=kind, **fields))

def state(db):
    conn = getattr(db, '_conn', None)
    if conn is None:
        return dict(session=None, in_transaction=None, autocommit=None)
    cur = conn.cursor()
    try:
        cur.execute('SELECT CONNECTION_ID(), @@in_transaction, @@autocommit')
        session, transaction, autocommit = cur.fetchone()
        return dict(session=session, in_transaction=transaction, autocommit=autocommit)
    finally:
        cur.close()

original_sql = Database.sql

def observed_sql(db, query, *args, **kwargs):
    text = str(query)
    # Never persist values, credentials or query text.
    details = dict(sql_class=text.strip().split()[0].upper() if text.strip() else 'EMPTY',
                   query_sha256=hashlib.sha256(text.encode()).hexdigest(),
                   for_update=bool(re.search(r'\bFOR\s+UPDATE\b', text, re.I)))
    emit('sql_enter', **details, **state(db))
    try:
        result = original_sql(db, query, *args, **kwargs)
    except Exception as exc:
        emit('sql_error', exception_type=type(exc).__name__, **details, **state(db))
        raise
    emit('sql_return', **details, **state(db))
    return result

def profile(frame, event, arg):
    if event not in ('call', 'return'):
        return
    module = frame.f_globals.get('__name__', '')
    name = frame.f_code.co_name
    if module in ('frappe.app', 'frappe.model.document', 'frappe.database.database') or module.startswith(('lending.', 'erpnext.accounts.general_ledger')):
        emit('python_' + event, module=module, method=name)

Database.sql = observed_sql
sys.setprofile(profile)
try:
    origin = 'wsgi_test_client_GET_ping'
    from werkzeug.test import Client
    from werkzeug.wrappers import Response
    from frappe.app import application
    response = Client(application, Response).get('/api/method/ping', base_url='http://' + SITE)
    emit('http_result', status_code=response.status_code, actor='Guest')
    assert response.status_code == 200
    origin = 'cli_synthetic_document_rollback'
    correlation = str(uuid.uuid4())
    frappe.init(site=SITE, sites_path=str(ROOT / 'bench' / 'sites'))
    frappe.connect()
    frappe.set_user('Administrator')
    emit('context', actor='Administrator', **state(frappe.db))
    frappe.db.begin()
    frappe.db.savepoint('c02_baseline')
    doc = frappe.get_doc(dict(doctype='ToDo', description='C02 disposable observation ' + correlation))
    doc.insert()
    doc.description = 'C02 second lifecycle ' + correlation
    doc.save()
    name = doc.name
    frappe.db.rollback()
    assert not frappe.db.exists('ToDo', name)
    emit('rollback_verified', synthetic_row_absent=True, **state(frappe.db))
    frappe.db.rollback()
    emit('baseline_result', result='PASS', financial_tests='NOT_RUN', lock_proof='NOT_RUN')
finally:
    sys.setprofile(None)
    Database.sql = original_sql
    if getattr(frappe.local, 'db', None):
        frappe.db.rollback()
    frappe.destroy()
    trace = OUT / 'events.jsonl'
    trace.write_text(''.join(json.dumps(event, sort_keys=True) + '\n' for event in events))
    manifest = dict(kind='C02_PARTIAL_BASELINE_NOT_ACCEPTANCE', trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),
                    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), event_count=len(events),
                    limitations=['Observer state queries add SQL and timing overhead', 'No worker or Lending/GL path exercised',
                                 'FOR UPDATE intent is not proof of row lock acquisition', 'No C03 disposition'],
                    financial_tests='NOT_RUN')
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(str(OUT))
