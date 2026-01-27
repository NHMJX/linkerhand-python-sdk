@echo off
chcp 65001 >nul
REM 安装开机自启动配置（Conda环境专用）
REM 此脚本用于配置Conda环境的服务开机自启动

REM 获取脚本所在目录和项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."
set "STARTUP_BAT=%SCRIPT_DIR%start_service_conda.bat"
set TASK_NAME=LinkerHand_HTTP_API_Service_Dev_Conda

echo ============================================================
echo LinkerHand HTTP API 服务 - 安装开机自启动（Conda环境）
echo ============================================================
echo.
echo 项目目录: %PROJECT_DIR%
echo 启动脚本: %STARTUP_BAT%
echo.
echo 此脚本将配置服务在用户登录时自动启动
echo 注意: 请确保 start_service_conda.bat 中已配置Conda环境名
echo.

REM 检查启动脚本是否存在
if not exist "%STARTUP_BAT%" (
    echo 错误: 找不到启动脚本 %STARTUP_BAT%
    echo 请确保此脚本位于 service_scripts 文件夹中
    pause
    exit /b 1
)

echo 找到启动脚本: %STARTUP_BAT%
echo.
echo 重要提示:
echo 1. 请先编辑 start_service_conda.bat
echo 2. 找到 "set CONDA_ENV_NAME=" 这一行
echo 3. 修改为您的Conda环境名，例如: set "CONDA_ENV_NAME=myenv"
echo 4. 保存后继续
echo.
set /p CONTINUE="已配置Conda环境名? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo.
    echo 请先配置Conda环境名，然后重新运行此脚本
    echo.
    pause
    exit /b 1
)

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 需要管理员权限来安装开机自启动
    echo 请右键点击此脚本，选择"以管理员身份运行"
    echo.
    echo 正在尝试以管理员权限重新运行...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo [1/2] 创建任务计划（开机自启动）...
echo.

REM 删除已存在的任务（如果存在）
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM 创建新任务
REM /SC ONLOGON: 用户登录时触发
REM /RL HIGHEST: 以最高权限运行
REM /DELAY 0000:30: 延迟30秒启动（等待系统完全启动）
schtasks /Create /TN "%TASK_NAME%" /TR "\"%STARTUP_BAT%\"" /SC ONLOGON /RL HIGHEST /F /DELAY 0000:30

if %errorlevel% equ 0 (
    echo 任务计划创建成功！
    echo.
    echo [2/2] 验证安装...
    schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo.
        echo ============================================================
        echo 安装成功！
        echo ============================================================
        echo.
        echo 任务名称: %TASK_NAME%
        echo 启动脚本: %STARTUP_BAT%
        echo.
        echo 服务将在用户登录后30秒自动启动
        echo 访问地址: http://localhost:8000 (LinkerHand API)
        echo 访问地址: http://localhost:8001 (Exe Executor API)
        echo.
        echo 管理命令:
        echo   启动服务: start_service_conda.bat
        echo   停止服务: stop_service.bat
        echo   卸载自启动: uninstall_autostart.bat
        echo.
        pause
        exit /b 0
    ) else (
        echo 验证失败，但任务可能已创建
        pause
        exit /b 1
    )
) else (
    echo.
    echo 任务计划创建失败，尝试使用启动文件夹方式...
    echo.
    goto :startup_folder
)

:startup_folder
echo 使用启动文件夹方式安装（不需要管理员权限）...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if not exist "%STARTUP_FOLDER%" (
    mkdir "%STARTUP_FOLDER%"
)

REM 创建快捷方式
set SHORTCUT_PATH=%STARTUP_FOLDER%\LinkerHand_Service_Dev_Conda.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortCut('%SHORTCUT_PATH%'); $s.TargetPath = '%STARTUP_BAT%'; $s.WorkingDirectory = '%PROJECT_DIR%'; $s.WindowStyle = 1; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo ============================================================
    echo 安装成功（启动文件夹方式）！
    echo ============================================================
    echo.
    echo 快捷方式位置: %SHORTCUT_PATH%
    echo 服务将在用户登录时自动启动
    echo 访问地址: http://localhost:8000 (LinkerHand API)
    echo 访问地址: http://localhost:8001 (Exe Executor API)
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
