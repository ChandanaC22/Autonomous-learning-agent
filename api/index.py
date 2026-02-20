import sys
import os

# Add the project root to sys.path so all modules resolve correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.main import app
