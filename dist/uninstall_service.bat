@echo off
chcp 65001 >nul
echo ========================================
echo 卸载 LinkerHand HTTP API 服务
echo ========================================
echo.

set TASK_NAME=LinkerHand_HTTP_API_Service

echo [1/3] 停止服务...
call "%~dp0stop_service.bat" >nul 2>&1

echo.
echo [2/3] 删除任务计划...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo 任务计划已删除
) else (
    echo 任务计划不存在或删除失败
)

echo.
echo [3/3] 删除启动文件夹中的快捷方式...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_FOLDER%\LinkerHand_Service.lnk

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo 快捷方式已删除
    ) else (
        echo 快捷方式删除失败
    )
) else (
    echo 启动文件夹中未找到快捷方式
)

echo.
echo ========================================
echo 卸载完成！
echo ========================================
echo.
echo 注意: 可执行文件和日志文件需要手动删除
echo.
pause
