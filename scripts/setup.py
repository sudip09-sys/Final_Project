"""Interactive first-run setup. Never commit the generated .env."""
import getpass
import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

path = Path(__file__).resolve().parents[1] / '.env'
if path.exists():
    raise SystemExit('.env already exists. Preserve it: changing EMBEDDING_KEY loses access to enrolled templates.')
password = getpass.getpass('Create administrator password (at least 12 characters): ')
if len(password) < 12:
    raise SystemExit('Use at least 12 characters.')
if password != getpass.getpass('Confirm administrator password: '):
    raise SystemExit('Passwords do not match.')
values = dict(SECRET_KEY=secrets.token_urlsafe(48), ADMIN_PASSWORD_HASH=generate_password_hash(password), EMBEDDING_KEY=Fernet.generate_key().decode(), DATABASE_URL='sqlite:///attendance.db', TIMEZONE='Asia/Seoul', COOKIE_SECURE='0', FACE_THRESHOLD='0.48')
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:
    for k,v in values.items():
        f.write(f'{k}={v}\n')
print('Created private .env. Run: python scripts/run.py')
