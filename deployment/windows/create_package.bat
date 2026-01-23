@echo off
chcp 65001 >nul
REM LinkerHand HTTP API 部署包创建脚本

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        LinkerHand HTTP API 部署包创建器        ║
echo ╚══════════════════════════════════════════════╝
echo.

echo [1/2] 检查必要文件...
python -c "import sys; sys.exit(0)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    goto :error
)

if not exist "dist\LinkerHand_HTTP_API.exe" (
    echo ❌ 找不到主程序文件，请先运行: python build_exe.py
    goto :error
)

if not exist "windows_service.py" (
    echo ❌ 找不到服务文件
    goto :error
)

if not exist "install_service.py" (
    echo ❌ 找不到安装脚本
    goto :error
)

echo ✅ 必要文件检查通过

echo.
echo [2/2] 生成部署包...
python create_deployment_package.py
if %errorlevel% neq 0 (
    echo ❌ 部署包生成失败
    goto :error
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║               部署包创建完成！                ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 📦 生成的文件：
echo    LinkerHand_Deployment_Package.zip
echo.
echo 🚀 部署方式：
echo.
echo    方式1：本地部署
echo    1. 解压 LinkerHand_Deployment_Package.zip
echo    2. 以管理员身份运行 install.bat
echo.
echo    方式2：远程部署
echo    1. 复制ZIP包到目标机器
echo    2. 运行 PowerShell 脚本：
echo       .\remote_deploy.ps1 -ComputerName "TARGET-PC" -PackagePath ".\LinkerHand_Deployment_Package.zip"
echo.
echo 📖 详细说明请查看：
echo    WINDOWS_DEPLOYMENT.md
echo    REMOTE_DEPLOYMENT.md
echo.
pause
exit /b 0

:error
echo.
echo ❌ 部署包创建失败
echo 请检查上述错误信息
echo.
pause
exit /b 1