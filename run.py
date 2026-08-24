import os
import sys
import subprocess
import time
import threading

def start_backend():
    print("[RUNNER] Starting FastAPI Backend on http://localhost:8000 ...")
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def start_frontend():
    print("[RUNNER] Starting Vite React Frontend on http://localhost:3000 ...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, shell=True)

if __name__ == "__main__":
    print("=" * 60)
    print("      THE LENNY GROWTH ASSISTANT - LOCAL DEVELOPMENT RUNNER")
    print("=" * 60)
    
    # Check node_modules
    frontend_node_modules = os.path.join(os.path.dirname(__file__), "frontend", "node_modules")
    if not os.path.exists(frontend_node_modules):
        print("[RUNNER] Installing frontend npm dependencies...")
        subprocess.run(["npm", "install"], cwd=os.path.join(os.path.dirname(__file__), "frontend"), shell=True)

    t1 = threading.Thread(target=start_backend, daemon=True)
    t1.start()
    
    time.sleep(2)
    
    start_frontend()
