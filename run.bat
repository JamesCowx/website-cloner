@echo off
cd /d "%~dp0"
pip install -r requirements.txt >nul 2>&1
python cloner.py
pause
