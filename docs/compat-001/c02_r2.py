"""Lab-only transaction observer and synthetic cases. No financial functionality."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import uuid

import frappe
from frappe.database.database import Database
from frappe.model.document import Document

SITE = 'mfi-compat.localhost'
ROOT = Path('/workspace')
EVENTS = []
ORIGIN = 'setup'
CASE = 'setup'
RUN = uuid.uuid4().hex
ORIGINALS = []

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()

def identity(db=None):
    db = db or getattr(frappe.local, 'db', None)
    conn = getattr(db, '_conn', None)
    session = conn.thread_id() if conn is not None else None
    return dict(site=getattr(frappe.local, 'site', SITE), actor=getattr(getattr(frappe.local, 'session', None), 'user', None),
                session=session, db_object=id(db) if db else None)

def emit(kind, db=None, **fields):
    EVENTS.append(dict(sequence=len(EVENTS), monotonic_ns=time.monotonic_ns(),
                       timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       run=RUN, correlation_id=CASE, origin=ORIGIN, kind=kind, **identity(db), **fields))

def state(db):
    conn = getattr(db, '_conn', None)
    if conn is None:
        return
    # Explicitly identified observer SQL; never infer it belongs to the application.
    emit('sql_enter', db, observer=True, sql='SELECT CONNECTION_ID(), @@in_transaction, @@autocommit')
    cur = conn.cursor()
    try:
        cur.execute('SELECT CONNECTION_ID(), @@in_transaction, @@autocommit')
        sid, tx, auto = cur.fetchone()
        emit('sql_return', db, observer=True, measured_session=sid, in_transaction=tx, autocommit=auto)
    finally:
        cur.close()

def patch(cls, name, wrapper):
    old = getattr(cls, name)
    ORIGINALS.append((cls, name, old))
    setattr(cls, name, wrapper(old))

def sql_wrapper(old):
    def wrapped(db, query, *args, **kwargs):
        text = str(query).strip()
        operation = text.split()[0].upper() if text else 'EMPTY'
        detail = dict(observer=False, sql_class=operation, query_hash=digest(text),
                      boundary_sql=text if operation in ('START', 'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'RELEASE') else None,
                      for_update=bool(re.search(r'\bFOR\s+UPDATE\b', text, re.I)))
        emit('sql_enter', db, **detail)
        try:
            result = old(db, query, *args, **kwargs)
        except Exception as exc:
            emit('sql_error', db, exception=type(exc).__name__, **detail)
            raise
        emit('sql_return', db, **detail)
        state(db)
        return result
    return wrapped

def boundary_wrapper(name):
    def wrap(old):
        def wrapped(db, *args, **kwargs):
            emit('boundary_enter', db, method=name, chain=kwargs.get('chain', False),
                 savepoint=kwargs.get('save_point', args[0] if name in ('savepoint','release_savepoint') and args else None))
            try:
                result = old(db, *args, **kwargs)
            except Exception as exc:
                emit('boundary_error', db, method=name, exception=type(exc).__name__)
                raise
            emit('boundary_return', db, method=name)
            state(db)
            return result
        return wrapped
    return wrap

def lifecycle_wrapper(old):
    def wrapped(doc, method, *args, **kwargs):
        detail = dict(method=method, doctype=doc.doctype, document_hash=digest(doc.name))
        emit('lifecycle_enter', **detail)
        try:
            result = old(doc, method, *args, **kwargs)
        except Exception as exc:
            emit('lifecycle_error', exception=type(exc).__name__, **detail)
            raise
        emit('lifecycle_return', **detail)
        return result
    return wrapped

def profile(frame, event, arg):
    if event not in ('call','return'):
        return
    module, method = frame.f_globals.get('__name__',''), frame.f_code.co_name
    if module == 'frappe.app' and method in ('application','sync_database','init_request','run_after_response_callbacks'):
        emit('python_' + event, module=module, method=method)
    if module == 'frappe.utils.background_jobs' and method == 'execute_job':
        emit('python_' + event, module=module, method=method, job_name=frame.f_locals.get('job_name'))
    obj = frame.f_locals.get('self')
    db = getattr(frappe.local,'db',None)
    if method == 'run' and db:
        for name in ('before_commit','after_commit','before_rollback','after_rollback'):
            if obj is getattr(db,name,None):
                emit('callback_' + event, db, callback=name)

def connect():
    frappe.init(site=SITE, sites_path=str(ROOT/'bench'/'sites'))
    frappe.connect()
    frappe.set_user('Administrator')

def snapshot():
    from frappe.utils.background_jobs import get_redis_conn, get_queue
    from rq import Worker
    redis = get_redis_conn()
    result = dict(workers=[w.name for w in Worker.all(connection=redis)], queues={})
    for name in ('short','default','long'):
        queue = get_queue(name)
        jobs=[]
        for job in queue.jobs:
            kw = job.kwargs
            method=kw.get('method')
            if callable(method):
                method=method.__module__ + '.' + method.__qualname__
            jobs.append(dict(job_id=job.id, method=method, site=kw.get('site'), event=kw.get('event'),
                             job_name=kw.get('job_name'), kwargs_hash=digest(kw.get('kwargs')),
                             enqueued_at=str(job.enqueued_at), status=str(job.get_status(refresh=True)),
                             origin='UNKNOWN'))
        registries={}
        for label in ('started','finished','failed','deferred','scheduled','canceled'):
            registry=getattr(queue,label+'_job_registry',None)
            registries[label]=[x.decode() for x in redis.zrange(registry.key,0,-1)] if registry else []
        result['queues'][name]=dict(jobs=jobs, registries=registries)
    result['rq_keys'] = sorted(k.decode() for k in redis.scan_iter(match='rq:*'))
    return result

@frappe.whitelist(allow_guest=True, methods=['POST'])
def synthetic(case, fail=False):
    emit('synthetic_enter', test_permission_bypass=True)
    doc=frappe.get_doc(dict(doctype='ToDo',description='C02-R2:' + case))
    doc.insert(ignore_permissions=True)
    doc.description += ':saved'
    doc.save(ignore_permissions=True)
    emit('synthetic_written', doctype=doc.doctype, document_hash=digest(doc.name))
    if fail in (True, 'true', '1'):
        raise frappe.ValidationError('C02-R2 controlled rollback')
    return 'synthetic-complete'

def verify(case, expected):
    connect()
    found=frappe.get_all('ToDo', filters={'description':['like','C02-R2:' + case + '%']}, pluck='name')
    emit('persistence_check', found=len(found), expected=expected)
    assert len(found)==expected
    frappe.db.rollback()
    frappe.destroy()

def main():
    global ORIGIN, CASE
    os.chdir(ROOT/'bench'/'sites')
    out=ROOT/'c02-r2'/RUN
    out.mkdir(parents=True)
    connect()
    (out/'queue-before.json').write_text(json.dumps(snapshot(), indent=2))
    frappe.destroy()
    patch(Database,'sql',sql_wrapper)
    for method in ('begin','commit','rollback','savepoint','release_savepoint'):
        patch(Database,method,boundary_wrapper(method))
    patch(Document,'run_method',lifecycle_wrapper)
    sys.setprofile(profile)
    try:
        from werkzeug.test import Client
        from werkzeug.wrappers import Response
        from frappe.app import application
        for fail in (False,True):
            CASE=RUN + '-web-' + str(fail)
            ORIGIN='web_test_client'
            response=Client(application,Response).post('/api/method/frappe.c02_probe.synthetic',base_url='http://'+SITE,
                json={'case':CASE,'fail':fail})
            emit('http_result',status=response.status_code)
            response.close()
            assert response.status_code == (417 if fail else 200)
            ORIGIN='verification'
            verify(CASE,0 if fail else 1)
        CASE=RUN+'-cli'
        ORIGIN='cli'
        connect()
        frappe.db.begin()
        frappe.db.savepoint('c02_r2')
        synthetic(CASE)
        frappe.db.rollback(save_point='c02_r2')
        frappe.db.rollback()
        frappe.destroy()
        ORIGIN='verification'
        verify(CASE,0)
        from frappe.utils.background_jobs import get_redis_conn, execute_job
        from rq import Queue, SimpleWorker
        for fail in (False,True):
            connect()
            redis=get_redis_conn()
            CASE=RUN+'-worker-'+str(fail)
            queue=Queue('c02-r2-'+RUN,connection=redis)
            job=queue.enqueue_call(execute_job,kwargs=dict(site=SITE,method=synthetic,event=None,job_name=CASE,
                kwargs={'case':CASE,'fail':fail},user='Administrator',is_async=True),job_id=CASE)
            frappe.destroy()
            ORIGIN='rq_simpleworker'
            emit('worker_start',job_id=job.id,queue=queue.name)
            SimpleWorker([queue],connection=redis).work(burst=True,with_scheduler=False,logging_level='CRITICAL')
            emit('worker_end',job_id=job.id,status=str(job.get_status(refresh=True)))
            ORIGIN='verification'
            verify(CASE,0 if fail else 1)
        emit('scenarios_completed')
    finally:
        ORIGIN='cleanup'
        if getattr(frappe.local,'db',None):
            frappe.db.rollback()
        frappe.destroy()
        emit('observer_stop')
        sys.setprofile(None)
        for cls,name,old in reversed(ORIGINALS):
            setattr(cls,name,old)
        (out/'events.jsonl').write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in EVENTS))
        connect()
        (out/'queue-after.json').write_text(json.dumps(snapshot(),indent=2))
        frappe.destroy()
        (out/'observer.py').write_bytes(Path(__file__).read_bytes())
        manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print('ARTIFACT_DIRECTORY='+str(out))

if __name__=='__main__':
    sys.modules['c02_r2']=sys.modules[__name__]
    # Ephemeral test module only: no Frappe source file or installed app is changed.
    sys.modules['frappe.c02_probe']=sys.modules[__name__]
    synthetic.__module__='frappe.c02_probe'
    main()
