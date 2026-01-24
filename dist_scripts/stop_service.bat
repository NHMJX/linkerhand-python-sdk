@echo off
chcp 65001 >nul
echo ========================================
echo 停止 LinkerHand HTTP API 服务
echo ========================================
echo.

set SERVICE_NAME=linkerhand_service.exe

echo 正在查找服务进程...
tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL

if %errorlevel% equ 0 (
    echo 找到运行中的服务进程，正在停止...
    taskkill /IM "%SERVICE_NAME%" /T /F >nul 2>&1
    
    if %errorlevel% equ 0 (
        echo 服务已停止
        timeout /t 2 >nul
        
        :: 验证是否已停止
        tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
        if %errorlevel% equ 0 (
            echo 警告: 进程可能仍在运行，尝试强制结束...
            taskkill /IM "%SERVICE_NAME%" /F >nul 2>&1
        )
    ) else (
        echo 停止服务失败，尝试强制结束...
        taskkill /IM "%SERVICE_NAME%" /F >nul 2>&1
    )
) else (
    echo 服务未运行
)

echo.
echo ========================================
echo 操作完成
echo ========================================
echo.
pause
