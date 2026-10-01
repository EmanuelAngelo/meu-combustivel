"""Start the real frontend and backend in separate processes."""
import os, shutil, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
os.chdir(root)
python = root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
if not python.exists():
    subprocess.run([sys.executable, '-m', 'venv', str(root / '.venv')], check=True)
subprocess.run([str(python), '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
if not npm:
    sys.exit('Instale Node.js 22 ou superior para continuar.')
subprocess.run([npm, 'ci'], check=True)
env = {**os.environ, 'DJANGO_DEBUG': 'true', 'DJANGO_SERVE_FRONTEND': 'false'}
subprocess.run([str(python), 'backend/manage.py', 'migrate', '--noinput'], env=env, check=True)
children = []
try:
    children.append(subprocess.Popen([str(python), 'backend/manage.py', 'runserver', '127.0.0.1:8000', '--noreload'], env=env))
    children.append(subprocess.Popen([npm, 'run', 'dev'], env=env))
    print('Frontend: http://localhost:4173 | Backend: http://127.0.0.1:8000 | Ctrl+C para parar.', flush=True)
    while all(child.poll() is None for child in children):
        time.sleep(.5)
except KeyboardInterrupt:
    pass
finally:
    for child in children:
        if child.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], check=False)
            else:
                child.terminate()
    for child in children:
        child.wait()
