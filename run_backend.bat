@echo off
echo Starting Backend API...
pip install -r backend/requirements.txt
uvicorn backend.server:app --reload --port 8000
pause
