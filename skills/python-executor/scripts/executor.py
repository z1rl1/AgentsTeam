#!/usr/bin/env python3
"""Safe Python executor. Usage: python3 executor.py "<code_or_filepath>"""
import sys, os, subprocess, tempfile, time
from pathlib import Path

BLOCKED = ['subprocess','os.system','os.popen','os.exec','os.spawn','__import__',
           'importlib','ctypes','socket','shutil.rmtree','os.remove','os.unlink']
BLOCKED_PATHS = ['/etc/','/sys/','/proc/','/dev/']

def is_safe(code):
    for p in BLOCKED:
        if p in code: return False, f'Blocked: {p}'
    import re
    for m in re.finditer(r"open\s*\(\s*['\"]([^'\"]+)['\"]", code):
        for bp in BLOCKED_PATHS:
            if m.group(1).startswith(bp): return False, f'Blocked path: {m.group(1)}'
    return True, None

def run_code(code, timeout=30):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code); tmp = f.name
    try:
        t0 = time.time()
        r = subprocess.run([sys.executable, tmp], capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr, r.returncode, time.time()-t0
    except subprocess.TimeoutExpired:
        return '', f'TIMEOUT ({timeout}s)', -1, timeout
    finally:
        try: os.unlink(tmp)
        except OSError: pass

def main():
    if len(sys.argv) < 2: print('Usage: executor.py "<code_or_filepath>"'); sys.exit(1)
    arg = ' '.join(sys.argv[1:])
    p = Path(arg)
    if p.suffix == '.py' and p.exists():
        code = p.read_text(encoding='utf-8')
        print(f'Running file: {p}')
    else:
        code = arg
        print('Running inline code')
    ok, reason = is_safe(code)
    if not ok: print(f'BLOCKED: {reason}'); sys.exit(2)
    stdout, stderr, rc, elapsed = run_code(code)
    if stdout: print('STDOUT:\n' + stdout)
    if stderr: print('STDERR:\n' + stderr)
    print(f'Exit: {rc}  Time: {elapsed:.2f}s')
    sys.exit(rc if rc >= 0 else 1)

if __name__ == '__main__': main()
