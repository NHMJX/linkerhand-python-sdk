@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 停止LinkerHand HTTP API服务（开发环境）
REM 此脚本用于停止正在运行的Python服务

echo ============================================================
echo 停止LinkerHand HTTP API服务
echo ============================================================
echo.

REM 使用PowerShell查找并终止运行main_http.py的Python进程
echo 正在查找服务进程...

powershell -Command "$processes = Get-WmiObject Win32_Process -Filter \"name='python.exe'\" | Where-Object {$_.CommandLine -like '*main_http.py*'}; if ($processes) { $processes | ForEach-Object { Write-Host \"正在终止进程 PID: $($_.ProcessId)\"; Stop-Process -Id $_.ProcessId -Force } } else { Write-Host \"未找到运行中的服务进程\" }"

REM 等待一下
timeout /t 2 /nobreak >nul

REM 再次检查
powershell -Command "$processes = Get-WmiObject Win32_Process -Filter \"name='python.exe'\" | Where-Object {$_.CommandLine -like '*main_http.py*'}; if ($processes) { Write-Host \"警告: 可能仍有服务进程在运行\"; Write-Host \"请使用任务管理器手动终止 python.exe 进程\" } else { Write-Host \"服务已停止\" }"

echo.
echo ============================================================
echo 操作完成
echo ============================================================
echo.
echo 提示: 如果服务仍在运行，请使用任务管理器手动终止
echo 查找进程: python.exe (命令行包含 main_http.py)
echo.
pause
