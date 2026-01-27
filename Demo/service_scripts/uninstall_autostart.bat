@echo off
chcp 65001 >nul
REM 卸载开机自启动配置（开发环境）
REM 此脚本用于移除服务的开机自启动配置

set TASK_NAME=LinkerHand_HTTP_API_Service_Dev
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_FOLDER%\LinkerHand_Service_Dev.lnk

echo ============================================================
echo LinkerHand HTTP API 服务 - 卸载开机自启动
echo ============================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 需要管理员权限来卸载任务计划
    echo 请右键点击此脚本，选择"以管理员身份运行"
    echo.
    echo 正在尝试以管理员权限重新运行...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/2] 删除任务计划...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo 任务计划已删除
) else (
    echo 未找到任务计划（可能已删除或不存在）
)

echo.
echo [2/2] 删除启动文件夹快捷方式...
if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo 快捷方式已删除
    ) else (
        echo 删除快捷方式失败（可能需要手动删除）
    )
) else (
    echo 未找到快捷方式（可能已删除或不存在）
)

echo.
echo ============================================================
echo 卸载完成！
echo ============================================================
echo.
echo 开机自启动配置已移除
echo 服务不会在下次登录时自动启动
echo.
echo 注意: 如果服务正在运行，请手动停止
echo 运行 stop_service.bat 来停止服务
echo.
pause
