@echo off
chcp 65001 >nul 2>&1
REM Windows脚本测试脚本

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                 Windows脚本测试工具                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [1/3] 测试基本命令...
echo Hello World!
echo 当前时间: %TIME%
echo 当前日期: %DATE%
echo.

echo [2/3] 测试Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未找到或不在PATH中
) else (
    echo ✅ Python可用
    python --version
)
echo.

echo [3/3] 测试目录...
echo 脚本目录: %~dp0
echo 当前目录: %cd%

REM 获取项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."
echo 项目目录: %PROJECT_DIR%

REM 切换到项目根目录
cd /d "%PROJECT_DIR%" 2>nul
if %errorlevel% neq 0 (
    echo ❌ 无法切换到项目目录
) else (
    echo ✅ 成功切换到项目目录: %cd%
)
echo.

echo ╔══════════════════════════════════════════════════════════╗
echo ║                     测试完成                            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 如果你能看到这个输出，说明脚本运行正常！
echo 如果看不到输出，说明.bat文件无法执行。
echo.
pause