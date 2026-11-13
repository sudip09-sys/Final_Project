"""Load generated environment without a shell-specific activation command."""
import os
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for line in (root/'.env').read_text().splitlines():
    if line and not line.startswith('#'):
        key,value=line.split('=',1)
        os.environ.setdefault(key,value)
os.chdir(root)
sys.path.insert(0,str(root))
from app import create_app
create_app().run(host='127.0.0.1',port=5000)
