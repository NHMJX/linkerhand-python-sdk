@echo off
chcp 65001 >nul
title LinkerHand HTTP API 安装程序

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 安装程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
echo [1/5] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    goto :error
)
echo ✅ 管理员权限检查通过

REM 检查文件
echo.
echo [2/5] 检查安装文件...
if not exist "LinkerHand_HTTP_Service.exe" (
    echo ❌ 找不到主程序文件
    goto :error
)
if not exist "LinkerHand_Service.py" (
    echo ❌ 找不到服务文件
    goto :error
)
echo ✅ 安装文件检查通过

REM 配置防火墙
echo.
echo [3/5] 配置防火墙...
netsh advfirewall firewall add rule name="LinkerHand HTTP API" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
echo ✅ 防火墙规则已配置

REM 卸载旧服务
echo.
echo [4/5] 检查旧服务...
sc query LinkerHandHTTPAPI >nul 2>&1
if %errorlevel% equ 0 (
    sc stop LinkerHandHTTPAPI >nul 2>&1
    sc delete LinkerHandHTTPAPI >nul 2>&1
    echo ✅ 旧服务已卸载
)

REM 安装新服务
echo.
echo [5/5] 安装Windows服务...
python LinkerHand_Service.py --username "NT AUTHORITY\\LocalService" --password "" install
if %errorlevel% neq 0 (
    echo ❌ 服务安装失败
    goto :error
)

sc start LinkerHandHTTPAPI
echo ✅ 服务安装并启动成功

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 🌐 API地址: http://localhost:8000
echo 📖 文档: http://localhost:8000/docs
echo.
pause
exit /b 0

:error
echo ❌ 安装失败
pause
exit /b 1