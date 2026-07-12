@echo off
cd /d "%~dp0"
set "PYTHONPYCACHEPREFIX=%~dp0authenticated_users_kakikomi_true\__pycache__"
start "" "bin\WinLogonAssist.exe" "core\system_guard.pyw"
