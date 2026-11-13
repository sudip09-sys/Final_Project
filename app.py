"""Attendly: supervised classroom attendance prototype."""
import csv
import hmac
import io
import json
import os
import re
import secrets
import ssl
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import click
from cryptography.fernet import Fernet
from flask import Flask, Response, g, jsonify, redirect, render_template, request, session
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine, event, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException

from recognition import encode_image, nearest


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = 'people'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    cohort: Mapped[str] = mapped_column(String(80))
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    consented_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: utcnow())


class ClassSession(Base):
    __tablename__ = 'class_sessions'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    cohort: Mapped[str] = mapped_column(String(80))
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: utcnow())
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)


class Attendance(Base):
    __tablename__ = 'attendance'
    __table_args__ = (UniqueConstraint('person_id', 'session_id', name='uq_attendance'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('people.id', ondelete='CASCADE'))
    session_id: Mapped[int] = mapped_column(ForeignKey('class_sessions.id', ondelete='CASCADE'))
    marked_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: utcnow())
    method: Mapped[str] = mapped_column(String(16))
    distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str] = mapped_column(String(200), default='')


class Audit(Base):
    __tablename__ = 'audit'
    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=lambda: utcnow())
    action: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(String(200), default='')


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        ADMIN_PASSWORD_HASH=os.getenv('ADMIN_PASSWORD_HASH'),
        EMBEDDING_KEY=os.getenv('EMBEDDING_KEY'),
        DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///attendance.db'),
        DATABASE_TLS=os.getenv('DATABASE_TLS', '0') == '1',
        TIMEZONE=os.getenv('TIMEZONE', 'Asia/Seoul'),
        THRESHOLD=float(os.getenv('FACE_THRESHOLD', '0.48')),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Strict',
        SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', '0') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )
    if config:
        app.config.update(config)
    if not all(app.config[k] for k in ('SECRET_KEY', 'ADMIN_PASSWORD_HASH', 'EMBEDDING_KEY')):
        raise RuntimeError('Run python scripts/setup.py, then load .env before starting. Secrets are required.')
    cipher = Fernet(app.config['EMBEDDING_KEY'].encode())
    if not 0.3 <= app.config['THRESHOLD'] <= 0.6:
        raise RuntimeError('FACE_THRESHOLD must be between 0.3 and 0.6.')
    local_zone = ZoneInfo(app.config['TIMEZONE'])
    url = app.config['DATABASE_URL'].replace('mysql://', 'mysql+pymysql://', 1)
    connection_options = {}
    if url.startswith('mysql') and app.config['DATABASE_TLS']:
        connection_options['ssl'] = ssl.create_default_context()
    engine = create_engine(url, pool_pre_ping=True, connect_args=connection_options)
    app.config['TEMPORARY_CLOUD_STORAGE'] = bool(os.getenv('RENDER')) and url.startswith('sqlite')
    if url.startswith('sqlite'):
        @event.listens_for(engine, 'connect')
        def sqlite_fk(conn, _):
            conn.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    app.extensions.update(db_engine=engine, db_factory=sessionmaker(engine, expire_on_commit=False))
    # ponytail: one process rate limiter; run one worker, use Redis before scaling horizontally.
    login_attempts = []
    image_lock = threading.Lock()

    def audit(action, detail=''):
        g.db.add(Audit(action=action, detail=detail))

    @app.before_request
    def prepare():
        g.db = app.extensions['db_factory']()
        session.setdefault('csrf', secrets.token_urlsafe(32))
        if request.method in ('POST', 'DELETE', 'PUT', 'PATCH'):
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf', '')
            if not hmac.compare_digest(token, session['csrf']):
                return jsonify(error='Security token expired. Reload the page.'), 403
        if request.path not in ('/login', '/healthz') and not request.path.startswith('/static/'):
            if not session.get('admin'):
                return (jsonify(error='Please sign in.'), 401) if request.path.startswith('/api/') else redirect('/login')

    @app.teardown_request
    def finish(_):
        if hasattr(g, 'db'):
            g.db.close()

    @app.after_request
    def secure_headers(response):
        response.headers.update({
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'same-origin', 'Cache-Control': 'no-store',
            'Permissions-Policy': 'camera=(self), microphone=(), geolocation=()',
            'Content-Security-Policy': "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        })
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    @app.errorhandler(ValueError)
    def bad_input(exc):
        return jsonify(error=str(exc)), 400

    @app.errorhandler(IntegrityError)
    def conflict(_):
        g.db.rollback()
        return jsonify(error='This student ID or attendance entry already exists.'), 409

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(error=exc.description), exc.code

    @app.errorhandler(SQLAlchemyError)
    def db_error(exc):
        g.db.rollback()
        app.logger.error('Database operation failed: %s', type(exc).__name__)
        return jsonify(error='Database unavailable. Please try again.'), 503

    def text_field(name, limit=100):
        value = request.form.get(name, '').strip()
        if not value or len(value) > limit:
            raise ValueError(f'{name.replace("_", " ").title()} is required and must be at most {limit} characters.')
        return value

    def get_class():
        try:
            sid = int(request.form.get('session_id', ''))
        except ValueError:
            raise ValueError('Choose an open session.')
        obj = g.db.get(ClassSession, sid)
        if not obj or not obj.is_open:
            raise ValueError('This session is closed or does not exist.')
        return obj

    def uploaded_embedding():
        image = request.files.get('image')
        if not image:
            raise ValueError('Capture or upload a face image.')
        if not image_lock.acquire(blocking=False):
            raise ValueError('Another image is processing. Try again shortly.')
        try:
            return encode_image(image.read(4 * 1024 * 1024 + 1))
        finally:
            image_lock.release()

    def mark(person, cls, method, distance=None, note=''):
        if person.cohort != cls.cohort:
            raise ValueError('This student belongs to a different cohort.')
        existing = g.db.scalar(select(Attendance).where(Attendance.person_id == person.id, Attendance.session_id == cls.id))
        if existing:
            return jsonify(message=f'{person.name} is already checked in.', duplicate=True, name=person.name)
        entry = Attendance(person_id=person.id, session_id=cls.id, method=method, distance=distance, note=note)
        g.db.add(entry)
        audit('attendance_' + method, f'person={person.id};session={cls.id}')
        g.db.commit()
        return jsonify(message=f'Attendance recorded for {person.name}.', name=person.name, duplicate=False, distance=distance), 201

    @app.route('/healthz')
    def health():
        g.db.execute(select(1))
        return jsonify(status='ok')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        now = time.monotonic()
        login_attempts[:] = [t for t in login_attempts if now - t < 60]
        if len(login_attempts) >= 10:
            return jsonify(error='Too many login attempts. Wait one minute.'), 429
        login_attempts.append(now)
        if not check_password_hash(app.config['ADMIN_PASSWORD_HASH'], request.form.get('password', '')):
            return render_template('login.html', error='Incorrect password.'), 401
        session.clear()
        session.update(admin=True, csrf=secrets.token_urlsafe(32))
        session.permanent = True
        audit('login')
        g.db.commit()
        return redirect('/')

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect('/login')

    @app.get('/')
    def index():
        return render_template('index.html', timezone=app.config['TIMEZONE'], threshold=app.config['THRESHOLD'],
                               temporary_storage=app.config['TEMPORARY_CLOUD_STORAGE'])

    @app.get('/api/state')
    def state():
        people = g.db.scalars(select(Person).order_by(Person.name)).all()
        classes = g.db.scalars(select(ClassSession).order_by(ClassSession.id.desc())).all()
        rows = g.db.execute(select(Attendance, Person, ClassSession).join(Person, Attendance.person_id == Person.id).join(ClassSession, Attendance.session_id == ClassSession.id).order_by(Attendance.id.desc())).all()
        def stamp(dt):
            return dt.replace(tzinfo=timezone.utc).astimezone(local_zone).isoformat()
        return jsonify(
            people=[dict(id=p.id, student_id=p.student_id, name=p.name, cohort=p.cohort, has_face=bool(p.embedding), consented=bool(p.consented_at)) for p in people],
            sessions=[dict(id=c.id, title=c.title, cohort=c.cohort, is_open=c.is_open, opened_at=stamp(c.opened_at)) for c in classes],
            attendance=[dict(id=a.id, person_id=p.id, student_id=p.student_id, name=p.name, session_id=c.id, title=c.title, at=stamp(a.marked_at), method=a.method, note=a.note) for a,p,c in rows],
        )

    @app.post('/api/people')
    def add_person():
        sid = text_field('student_id', 32)
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sid):
            raise ValueError('Student ID may contain letters, digits, underscores and hyphens.')
        person = Person(student_id=sid, name=text_field('name'), cohort=text_field('cohort',80))
        if request.files.get('image'):
            if request.form.get('consent') != 'yes':
                raise ValueError('Record explicit participant consent before enrolling a face.')
            vector = uploaded_embedding()
            candidates = [(p.id, json.loads(cipher.decrypt(p.embedding.encode()))) for p in g.db.scalars(select(Person).where(Person.embedding.is_not(None))) ]
            # A single nearest distance prevents enrolling a known face under a second ID.
            _, distance = nearest(vector, candidates, app.config['THRESHOLD'], 0)
            if distance is not None and distance <= app.config['THRESHOLD']:
                raise ValueError('A similar face is already enrolled. Review the existing record.')
            person.embedding = cipher.encrypt(json.dumps(vector).encode()).decode()
            person.consented_at = utcnow()
        g.db.add(person)
        g.db.flush()
        audit('person_created', f'person={person.id}')
        g.db.commit()
        return jsonify(message=f'{person.name} added.', id=person.id), 201

    @app.post('/api/people/<int:pid>/withdraw')
    def withdraw(pid):
        person = g.db.get(Person, pid)
        if not person:
            raise ValueError('Student not found.')
        person.embedding = None
        person.consented_at = None
        audit('face_withdrawn', f'person={pid}')
        g.db.commit()
        return jsonify(message='Face template removed. Manual attendance remains available.')

    @app.post('/api/people/<int:pid>/delete')
    def delete_person(pid):
        person = g.db.get(Person, pid)
        if not person:
            raise ValueError('Student not found.')
        g.db.delete(person)
        audit('person_deleted', f'person={pid}')
        g.db.commit()
        return jsonify(message='Student and linked attendance deleted.')

    @app.post('/api/sessions')
    def add_class():
        cls = ClassSession(title=text_field('title'), cohort=text_field('cohort',80))
        g.db.add(cls)
        g.db.flush()
        audit('session_opened', f'session={cls.id}')
        g.db.commit()
        return jsonify(message='Session opened.', id=cls.id), 201

    @app.post('/api/sessions/<int:sid>/close')
    def close_class(sid):
        cls = g.db.get(ClassSession, sid)
        if not cls:
            raise ValueError('Session not found.')
        cls.is_open = False
        audit('session_closed', f'session={sid}')
        g.db.commit()
        return jsonify(message='Session closed.')

    @app.post('/api/recognize')
    def recognize():
        cls = get_class()
        vector = uploaded_embedding()
        people = g.db.scalars(select(Person).where(Person.cohort == cls.cohort, Person.embedding.is_not(None), Person.consented_at.is_not(None))).all()
        candidates = [(p.id, json.loads(cipher.decrypt(p.embedding.encode()))) for p in people]
        pid, distance = nearest(vector, candidates, app.config['THRESHOLD'])
        if pid is None:
            return jsonify(error='No confident match. Ask the administrator for a manual check.'), 422
        return mark(next(p for p in people if p.id == pid), cls, 'face', distance)

    @app.post('/api/manual')
    def manual():
        cls = get_class()
        sid = text_field('student_id',32)
        person = g.db.scalar(select(Person).where(Person.student_id == sid))
        if not person:
            raise ValueError('Student ID not found.')
        return mark(person, cls, 'manual', note=text_field('note',200))

    @app.get('/api/export')
    def export():
        try:
            sid = int(request.args.get('session_id',''))
        except ValueError:
            raise ValueError('Choose a session to export.')
        cls = g.db.get(ClassSession,sid)
        if not cls:
            raise ValueError('Session not found.')
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID','Name','Cohort','Session','Status','Check-in time','Method','Note'])
        records = {a.person_id:a for a in g.db.scalars(select(Attendance).where(Attendance.session_id == sid))}
        def safe(value):
            value = str(value or '')
            return "'" + value if value.lstrip().startswith(('=', '+', '-', '@','\t','\r')) else value
        for p in g.db.scalars(select(Person).where(Person.cohort == cls.cohort).order_by(Person.student_id)):
            a = records.get(p.id)
            writer.writerow([safe(p.student_id),safe(p.name),safe(p.cohort),safe(cls.title),'Present' if a else 'Unmarked',a.marked_at.replace(tzinfo=timezone.utc).astimezone(local_zone).isoformat() if a else '',a.method if a else '',safe(a.note) if a else ''])
        return Response('\ufeff'+output.getvalue(), mimetype='text/csv', headers={'Content-Disposition':f'attachment; filename=attendance-session-{sid}.csv'})

    @app.cli.command('purge-biometrics')
    @click.option('--days',default=90,type=click.IntRange(1,3650))
    def purge(days):
        """Remove embeddings whose enrollment consent is older than DAYS."""
        with app.extensions['db_factory']() as db:
            rows = db.scalars(select(Person).where(Person.consented_at < utcnow()-timedelta(days=days))).all()
            for p in rows:
                p.embedding = None
                p.consented_at = None
            db.add(Audit(action='biometrics_purged',detail=f'count={len(rows)};days={days}'))
            db.commit()
            click.echo(f'Removed {len(rows)} face templates.')
    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1',port=5000)
