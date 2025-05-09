@echo off
cd /d %~dp0
cd app
cd ..
call myenv\Scripts\activate
python manage.py runserver
pause 