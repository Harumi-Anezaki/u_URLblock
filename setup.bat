@echo off
echo 環境のセットアップを開始します...
powershell -ExecutionPolicy Bypass -File "%~dp0build_portable.ps1"
echo セットアップが完了しました！
pause
