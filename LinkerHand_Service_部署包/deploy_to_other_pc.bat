@echo off
chcp 65001 >nul
echo ========================================
echo LinkerHand HTTP API 服务 - 部署安装脚本
echo ========================================
echo.
echo 此脚本用于在其他电脑上安装服务并配置开机自启动
echo.

set EXE_PATH=%~dp0linkerhand_service.exe

if not exist "%EXE_PATH%" (
    echo 错误: 找不到可执行文件 linkerhand_service.exe
    echo 请确保此脚本与 linkerhand_service.exe 在同一目录下
    echo.
    pause
    exit /b 1
)

echo 找到可执行文件: %EXE_PATH%
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 需要管理员权限来安装开机自启动
    echo 请右键点击此脚本，选择"以管理员身份运行"
    echo.
    echo 正在尝试以管理员权限重新运行...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/2] 创建任务计划（开机自启动）...
set TASK_NAME=LinkerHand_HTTP_API_Service

:: 删除已存在的任务（如果存在）
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

:: 创建新任务
schtasks /Create /TN "%TASK_NAME%" /TR "\"%EXE_PATH%\"" /SC ONLOGON /RL HIGHEST /F /DELAY 0000:30

if %errorlevel% equ 0 (
    echo 任务计划创建成功！
) else (
    echo 任务计划创建失败，尝试使用启动文件夹方式...
    goto :startup_folder
)

echo.
echo [2/2] 验证安装...
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 安装成功！
    echo ========================================
    echo.
    echo 任务名称: %TASK_NAME%
    echo 可执行文件: %EXE_PATH%
    echo.
    echo 服务将在用户登录后30秒自动启动
    echo 访问地址: http://localhost:8000
    echo.
    echo 管理命令:
    echo   启动服务: start_service.bat
    echo   停止服务: stop_service.bat
    echo   重启服务: restart_service.bat
    echo   检查状态: check_service_status.bat
    echo   查看任务: 任务计划程序
    echo   卸载服务: uninstall_service.bat
    echo.
    pause
    exit /b 0
)

:startup_folder
echo.
echo 使用启动文件夹方式安装（不需要管理员权限）...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if not exist "%STARTUP_FOLDER%" (
    mkdir "%STARTUP_FOLDER%"
)

:: 创建快捷方式
set SHORTCUT_PATH=%STARTUP_FOLDER%\LinkerHand_Service.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo ========================================
    echo 安装成功（启动文件夹方式）！
    echo ========================================
    echo.
    echo 快捷方式位置: %SHORTCUT_PATH%
    echo 服务将在用户登录时自动启动
    echo 访问地址: http://localhost:8000
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo 安装失败！请检查错误信息
    echo.
    pause
    exit /b 1
)
