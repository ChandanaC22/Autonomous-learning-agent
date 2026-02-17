@echo off
echo Starting Backend API...
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
pause
