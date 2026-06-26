@echo off
echo Starting TallyQuery Backend with hot-reload...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
pause
