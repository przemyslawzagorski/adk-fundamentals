@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0auggie-wsl.ps1" %*
exit /b %errorlevel%
