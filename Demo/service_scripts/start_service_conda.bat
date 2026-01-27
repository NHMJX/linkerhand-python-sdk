@echo off
chcp 65001 >nul
REM 启动LinkerHand HTTP API服务（Conda环境专用）
REM 此脚本专门用于Conda环境，支持自动激活Conda环境

REM ============================================================
REM Conda环境配置（请修改为您的Conda环境名）
REM ============================================================
REM 如果留空，脚本会尝试使用已激活的环境或base环境
set "CONDA_ENV_NAME="
REM 如果上面的环境名为空，是否使用base环境
set "USE_BASE_IF_EMPTY=1"

REM 获取脚本所在目录的父目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."

REM 切换到项目根目录
cd /d "%PROJECT_DIR%"

REM 检测并激活Conda环境
if defined CONDA_DEFAULT_ENV (
    REM 如果已激活Conda环境，直接使用
    echo 使用已激活的Conda环境: %CONDA_DEFAULT_ENV%
) else (
    REM 尝试激活Conda环境
    set "CONDA_ACTIVATED=0"
    
    REM 查找conda安装路径
    set "CONDA_BASE="
    if defined CONDA_EXE (
        for %%F in ("%CONDA_EXE%") do set "CONDA_BASE=%%~dpF.."
    ) else (
        REM 尝试从注册表查找
        for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Anaconda3" /v InstallPath 2^>nul') do set "CONDA_BASE=%%B"
        if not defined CONDA_BASE (
            for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Anaconda3" /v InstallPath 2^>nul') do set "CONDA_BASE=%%B"
        )
        if not defined CONDA_BASE (
            if exist "%USERPROFILE%\Anaconda3\Scripts\conda.exe" (
                set "CONDA_BASE=%USERPROFILE%\Anaconda3"
            ) else if exist "%USERPROFILE%\Miniconda3\Scripts\conda.exe" (
                set "CONDA_BASE=%USERPROFILE%\Miniconda3"
            )
        )
    )
    
    REM 如果找到conda，尝试激活环境
    if defined CONDA_BASE (
        if exist "%CONDA_BASE%\Scripts\activate.bat" (
            REM 初始化conda（如果需要）
            call "%CONDA_BASE%\Scripts\activate.bat" >nul 2>&1
            
            REM 激活指定环境或base环境
            if not "%CONDA_ENV_NAME%"=="" (
                call "%CONDA_BASE%\Scripts\activate.bat" %CONDA_ENV_NAME% >nul 2>&1
                if %errorlevel% equ 0 (
                    set "CONDA_ACTIVATED=1"
                    echo 已激活Conda环境: %CONDA_ENV_NAME%
                )
            ) else if "%USE_BASE_IF_EMPTY%"=="1" (
                call "%CONDA_BASE%\Scripts\activate.bat" base >nul 2>&1
                if %errorlevel% equ 0 (
                    set "CONDA_ACTIVATED=1"
                    echo 已激活Conda环境: base
                )
            )
        )
    )
    
    REM 检查是否成功激活
    if not defined CONDA_DEFAULT_ENV (
        if %CONDA_ACTIVATED%==0 (
            echo ============================================================
            echo 警告: 无法自动激活Conda环境
            echo ============================================================
            echo.
            echo 请手动激活Conda环境，然后重新运行此脚本
            echo.
            echo 方法1: 在运行此脚本前先激活环境
            echo   conda activate 环境名
            echo.
            echo 方法2: 修改此脚本，设置CONDA_ENV_NAME变量
            echo   编辑此脚本，找到 "set CONDA_ENV_NAME=" 这一行
            echo   修改为: set "CONDA_ENV_NAME=您的环境名"
            echo.
            pause
            exit /b 1
        )
    )
)

echo ============================================================
echo 启动LinkerHand HTTP API服务
echo ============================================================
echo.
echo 项目目录: %PROJECT_DIR%
echo Conda环境: %CONDA_DEFAULT_ENV%
echo.

REM 启动服务（后台运行，不显示窗口）
start /B python Demo\main_http.py

REM 等待一下，检查服务是否启动成功
timeout /t 3 /nobreak >nul

echo 服务已启动
echo 访问地址: http://localhost:8000 (LinkerHand API)
echo 访问地址: http://localhost:8001 (Exe Executor API)
echo.
echo 提示: 服务在后台运行，关闭此窗口不会停止服务
echo 要停止服务，请运行 stop_service.bat 或使用任务管理器
echo.
