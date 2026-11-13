"""API contract tests use deterministic embeddings, never fabricate model accuracy."""
import io
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select
from werkzeug.security import generate_password_hash
import app as module
from recognition import nearest


@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.setattr(module,'encode_image',lambda _: [0.1]*128)
    return module.create_app(dict(TESTING=True, SECRET_KEY='test-only-key', EMBEDDING_KEY=Fernet.generate_key().decode(), ADMIN_PASSWORD_HASH=generate_password_hash('test-password'), DATABASE_URL='sqlite:///'+str(tmp_path/'test.db')))


@pytest.fixture
def client(app):
    c=app.test_client()
    c.get('/login')
    with c.session_transaction() as s: token=s['csrf']
    assert c.post('/login',data={'csrf':token,'password':'test-password'}).status_code==302
    return c


def post(c,url,data=None):
    with c.session_transaction() as s: token=s['csrf']
    return c.post(url,data=data or {},headers={'X-CSRF-Token':token})


def person(c,face=False,**kw):
    data=dict(student_id='S1',name='Test Student',cohort='CE',**kw)
    if face:data.update(image=(io.BytesIO(b'fixture'),'face.jpg'),consent='yes')
    return post(c,'/api/people',data)


def cls(c,cohort='CE'):
    return post(c,'/api/sessions',dict(title='Lab',cohort=cohort)).json['id']


def test_authentication_required(app):
    c=app.test_client()
    assert c.get('/api/state').status_code==401
    assert c.get('/').status_code==302
    assert c.get('/healthz').status_code==200


def test_csrf_blocks_mutation(client):
    assert client.post('/api/people',data={}).status_code==403


def test_manual_duplicate_close_export(client):
    assert person(client).status_code==201
    sid=cls(client)
    payload=dict(student_id='S1',session_id=sid,note='Verified ID')
    assert post(client,'/api/manual',payload).status_code==201
    assert post(client,'/api/manual',payload).json['duplicate'] is True
    assert len(client.get('/api/state').json['attendance'])==1
    csv=client.get(f'/api/export?session_id={sid}')
    assert csv.status_code==200 and 'Present' in csv.text and 'Verified ID' in csv.text
    assert post(client,f'/api/sessions/{sid}/close').status_code==200
    assert post(client,'/api/manual',payload).status_code==400


def test_face_consent_encryption_recognition_withdraw(client,app):
    no_consent=dict(student_id='S1',name='Student',cohort='CE',image=(io.BytesIO(b'x'),'x.jpg'))
    assert post(client,'/api/people',no_consent).status_code==400
    assert person(client,True).status_code==201
    with app.extensions['db_factory']() as db:
        p=db.scalar(select(module.Person))
        assert p.embedding.startswith('gAAAA') and '[0.1' not in p.embedding
    sid=cls(client)
    result=post(client,'/api/recognize',dict(session_id=sid,image=(io.BytesIO(b'x'),'x.jpg')))
    assert result.status_code==201 and result.json['distance']==pytest.approx(0)
    assert post(client,'/api/people/1/withdraw').status_code==200
    result=post(client,'/api/recognize',dict(session_id=sid,image=(io.BytesIO(b'x'),'x.jpg')))
    assert result.status_code==422
    assert len(client.get('/api/state').json['attendance'])==1


def test_cross_cohort_and_unknown_student(client):
    person(client)
    sid=cls(client,'Other')
    assert post(client,'/api/manual',dict(session_id=sid,student_id='S1',note='check')).status_code==400
    assert post(client,'/api/manual',dict(session_id=sid,student_id='missing',note='check')).status_code==400


def test_unique_student_and_cascade_delete(client):
    person(client)
    assert person(client).status_code==409
    sid=cls(client)
    post(client,'/api/manual',dict(session_id=sid,student_id='S1',note='check'))
    assert post(client,'/api/people/1/delete').status_code==200
    state=client.get('/api/state').json
    assert not state['people'] and not state['attendance']


def test_validation_and_csv_formula_protection(client):
    assert post(client,'/api/people',dict(student_id='bad id',name='x',cohort='CE')).status_code==400
    assert post(client,'/api/people',dict(student_id='SAFE',name='=SUM(A1:A5)',cohort='CE')).status_code==201
    sid=cls(client)
    assert "'=SUM(A1:A5)" in client.get(f'/api/export?session_id={sid}').text
    assert 'Unmarked' in client.get(f'/api/export?session_id={sid}').text
    assert post(client,'/api/manual',dict(session_id=sid,student_id='SAFE',note='')).status_code==400


def test_security_headers_logout(client):
    r=client.get('/')
    assert "frame-ancestors 'none'" in r.headers['Content-Security-Policy']
    assert r.headers['Cache-Control']=='no-store'
    assert post(client,'/logout').status_code==302
    assert client.get('/api/state').status_code==401


def test_login_throttle(app):
    c=app.test_client();c.get('/login')
    with c.session_transaction() as s: token=s['csrf']
    for _ in range(10):
        assert c.post('/login',data={'csrf':token,'password':'wrong'}).status_code==401
    assert c.post('/login',data={'csrf':token,'password':'wrong'}).status_code==429


def test_nearest_rejection_and_ambiguity():
    assert nearest([0]*128,[])[0] is None
    assert nearest([0]*128,[(1,[1]*128)])[0] is None
    assert nearest([0]*128,[(1,[0]*128),(2,[.001]*128)])[0] is None
    assert nearest([0]*128,[(1,[0]*128),(2,[1]*128)])[0]==1


def test_retention_command(client,app):
    person(client,True)
    with app.extensions['db_factory']() as db:
        p=db.get(module.Person,1)
        p.consented_at=module.utcnow()-module.timedelta(days=100)
        db.commit()
    result=app.test_cli_runner().invoke(args=['purge-biometrics','--days','90'])
    assert result.exit_code==0 and 'Removed 1' in result.output
    assert not client.get('/api/state').json['people'][0]['has_face']
