@echo off
REM start_cluster_server.bat — one-click start for the p@h cluster controller
REM and viz on this Windows machine. Does:
REM   1. detect LAN IP
REM   2. verify Docker Desktop is running
REM   3. cache controller pub_key (one-time)
REM   4. start controller container in background
REM   5. start viz/serve.py in foreground (ctrl-c to stop)
REM
REM Workers connect to the printed http://<lan-ip>:7777 URL via:
REM   curl -fsSL http://<lan-ip>:7777/kit/setup-worker.sh | bash         (mac/linux)
REM   iwr   http://<lan-ip>:7777/kit/bootstrap-worker.ps1 ...            (windows)

REM Delegate to PowerShell — bash-equivalent control flow is much cleaner there.
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0tools\pah\start-cluster-server.ps1" %*
