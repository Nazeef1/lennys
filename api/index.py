import sys
import os
import traceback

# Ensure root directory and current directory are in sys.path for Vercel lambdas
file_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(file_dir)
cwd = os.getcwd()

for p in [root_dir, cwd, file_dir]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.main import app as _app
    app = _app
    handler = _app
except Exception as e:
    print(f"[VERCEL IMPORT ERROR] Failed to import backend.app.main: {e}")
    traceback.print_exc()
    raise e

