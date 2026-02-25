@echo off
echo Starting Backend API...
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
pause
