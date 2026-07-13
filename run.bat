@echo off
cd /d "%~dp0"
set "PYTHONPYCACHEPREFIX=%~dp0authenticated_users_kakikomi_true\__pycache__"
start "" "%~dp0bin\WinLogonAssist.exe" "%~dp0core\system_guard.pyw"
