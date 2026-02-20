"""
server.py - Render deployment entry point for the FastAPI backend.
Uses lazy import to avoid triggering ML dependency chain during scanner phase.
"""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
