@echo off
chcp 65001 >nul
REM 简化版本 - 启动LinkerHand HTTP API服务（使用系统Python）

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        LinkerHand HTTP API服务 - 简化启动模式            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [1/4] 检查环境...
REM 获取脚本所在目录的父目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."
echo 项目目录: %PROJECT_DIR%

REM 切换到项目根目录
cd /d "%PROJECT_DIR%"
echo 当前目录: %cd%
echo.

echo [2/4] 检查Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未找到
    echo    请确保Python已安装并在PATH中
    goto :error
) else (
    echo ✅ Python可用
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo     %%i
)
echo.

echo [3/4] 检查文件...
if not exist "Demo\main_http.py" (
    echo ❌ 找不到 Demo\main_http.py
    goto :error
) else (
    echo ✅ 找到 main_http.py
)
echo.

echo [4/4] 启动服务...
echo 命令: python Demo\main_http.py
echo 按Ctrl+C停止服务
echo.

REM 启动服务（显示窗口，便于查看输出和错误）
python Demo\main_http.py

goto :end

:error
echo.
echo ❌ 启动失败
pause
exit /b 1

:end
echo.
echo 服务已停止
pause
exit /b 0