@echo off
cd /d %~dp0
set PYTHONPATH=%~dp0src;%~dp0
"C:\Users\hateco\AppData\Local\Programs\Python\Python315\python.exe" run_gui.py
pause
