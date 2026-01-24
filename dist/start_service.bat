@echo off
chcp 65001 >nul
echo ========================================
echo 启动 LinkerHand HTTP API 服务
echo ========================================
echo.

set SERVICE_NAME=linkerhand_service.exe
set EXE_PATH=%~dp0%SERVICE_NAME%

if not exist "%EXE_PATH%" (
    echo 错误: 找不到可执行文件 %EXE_PATH%
    pause
    exit /b 1
)

:: 检查服务是否已在运行
tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
if %errorlevel% equ 0 (
    echo 服务已在运行中！
    echo.
    echo 如需重启服务，请运行 restart_service.bat
    echo.
    pause
    exit /b 0
)

echo 启动服务（后台模式）...
start "" "%EXE_PATH%"
timeout /t 2 >nul

:: 验证服务是否启动
tasklist /FI "IMAGENAME eq %SERVICE_NAME%" 2>NUL | find /I /N "%SERVICE_NAME%">NUL
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 服务启动成功！
    echo ========================================
    echo.
    echo 访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    echo.
) else (
    echo 服务启动失败，请检查日志文件查看错误信息
    echo 日志文件位置: %~dp0logs\
)

echo.
pause
