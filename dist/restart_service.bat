@echo off
chcp 65001 >nul
echo ========================================
echo 重启 LinkerHand HTTP API 服务
echo ========================================
echo.

set SERVICE_NAME=linkerhand_service.exe
set EXE_PATH=%~dp0%SERVICE_NAME%

echo [1/2] 正在停止服务...
call "%~dp0stop_service.bat" >nul 2>&1

:: 等待服务完全停止
timeout /t 3 >nul

:: 验证服务是否已停止
tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
if %errorlevel% equ 0 (
    echo 警告: 服务可能仍在运行，尝试强制停止...
    taskkill /IM "%SERVICE_NAME%" /F >nul 2>&1
    timeout /t 2 >nul
)

echo.
echo [2/2] 正在启动服务...
if exist "%EXE_PATH%" (
    start "" "%EXE_PATH%"
    timeout /t 3 >nul
    
    :: 验证服务是否启动
    tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo 服务重启成功！
        echo ========================================
        echo.
        echo 访问地址: http://localhost:8000
        echo API文档: http://localhost:8000/docs
        echo.
        pause
        exit /b 0
    ) else (
        echo 服务启动失败，请检查日志文件查看错误信息
        pause
        exit /b 1
    )
) else (
    echo 错误: 找不到可执行文件
    pause
    exit /b 1
)
