import sys
import os

# Add root directory to sys.path so modules like backend.app can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app

# Expose app for Vercel serverless ASGI handler
app = app
