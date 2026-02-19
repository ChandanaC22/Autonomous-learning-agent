import sys
import os

# Add the project root and backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from backend.main import app

# Vercel needs the app object to be exported
# FastAPI works directly with Vercel's Python runtime
