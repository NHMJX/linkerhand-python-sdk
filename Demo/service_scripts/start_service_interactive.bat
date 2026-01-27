@echo off
chcp 65001 >nul 2>&1
REM 交互式启动LinkerHand HTTP API服务
REM 让用户选择启动模式

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        LinkerHand HTTP API服务 - 交互式启动模式          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 请选择启动模式：
echo.
echo [1] 后台启动（推荐）- 服务在后台运行，不显示窗口
echo [2] 前台启动 - 显示服务运行窗口，可以看到日志
echo [3] 调试启动 - 详细诊断模式，显示所有检查过程
echo [4] 简化启动 - 使用系统Python，跳过Conda环境
echo [5] 取消启动
echo.
set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" goto background
if "%choice%"=="2" goto foreground
if "%choice%"=="3" goto debug
if "%choice%"=="4" goto simple
if "%choice%"=="5" goto cancel

echo ❌ 无效选择，请重新运行脚本
pause
exit /b 1

:background
echo.
echo 🔄 选择：后台启动模式
echo 📝 调用: start_service_conda.bat
echo.
call "%~dp0start_service_conda.bat"
goto end

:foreground
echo.
echo 🔄 选择：前台启动模式
echo 📝 调用: start_service_conda_window.bat
echo.
call "%~dp0start_service_conda_window.bat"
goto end

:debug
echo.
echo 🔄 选择：调试启动模式
echo 📝 调用: start_service_debug.bat
echo.
call "%~dp0start_service_debug.bat"
goto end

:simple
echo.
echo 🔄 选择：简化启动模式
echo 📝 调用: start_service_simple.bat
echo.
call "%~dp0start_service_simple.bat"
goto end

:cancel
echo.
echo ❌ 已取消启动
pause
exit /b 0

:end
echo.
echo ✅ 启动流程完成
pause