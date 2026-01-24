@echo off
chcp 65001 >nul
echo ========================================
echo 检查 LinkerHand HTTP API 服务状态
echo ========================================
echo.

set SERVICE_NAME=linkerhand_service.exe
set TASK_NAME=LinkerHand_HTTP_API_Service

:: 检查进程是否运行
echo [1/2] 检查进程状态...
tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
if %errorlevel% equ 0 (
    echo 状态: 运行中
    echo.
    echo 进程信息:
    tasklist /FI "IMAGENAME eq %SERVICE_NAME%" /FO TABLE
) else (
    echo 状态: 未运行
)

echo.
echo [2/2] 检查任务计划状态...
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo 任务计划: 已配置
    echo.
    echo 任务详情:
    schtasks /Query /TN "%TASK_NAME%" /FO LIST /V | findstr /C:"状态" /C:"下次运行时间" /C:"任务路径"
) else (
    echo 任务计划: 未配置
)

echo.
echo [3/3] 检查服务端口...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo HTTP端口(8000): 已监听
    echo.
    echo 端口连接信息:
    netstat -an | findstr ":8000"
) else (
    echo HTTP端口(8000): 未监听
)

echo.
echo ========================================
echo 状态检查完成
echo ========================================
echo.
echo 管理命令:
echo   启动服务: start_service.bat
echo   停止服务: stop_service.bat
echo   重启服务: restart_service.bat
echo.
pause
