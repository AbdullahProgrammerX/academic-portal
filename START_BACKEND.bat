@echo off
cd /d C:\editorial_system\backend
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
pause
