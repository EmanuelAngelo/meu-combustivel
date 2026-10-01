"""Start the real Django application on localhost, with a persistent SQLite DB."""
import os, shutil, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
os.chdir(root)
venv_python=root/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not venv_python.exists(): subprocess.run([sys.executable,'-m','venv',str(root/'.venv')],check=True)
subprocess.run([str(venv_python),'-m','pip','install','-r','backend/requirements.txt'],check=True)
npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
if not npm: sys.exit('Instale Node.js 22 ou superior para continuar.')
subprocess.run([npm,'ci'],check=True)
subprocess.run([npm,'run','build:server'],check=True)
env={**os.environ,'DJANGO_DEBUG':'true'}
subprocess.run([str(venv_python),'backend/manage.py','migrate','--noinput'],env=env,check=True)
print('\nMeu Combustível: http://127.0.0.1:8000\nUse Ctrl+C para encerrar. Seu banco fica em backend/data/db.sqlite3.\n',flush=True)
subprocess.run([str(venv_python),'backend/manage.py','runserver','127.0.0.1:8000','--noreload'],env=env,check=True)
