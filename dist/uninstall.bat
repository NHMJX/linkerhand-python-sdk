@echo off
chcp 65001 >nul
REM LinkerHand HTTP API 卸载脚本

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 卸载程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    goto :error
)

echo 正在停止并卸载LinkerHand HTTP API服务...
echo.

REM 停止服务
sc query LinkerHandHTTPAPI >nul 2>&1
if %errorlevel% equ 0 (
    echo 停止服务...
    sc stop LinkerHandHTTPAPI >nul 2>&1
    timeout /t 2 /nobreak >nul

    echo 卸载服务...
    sc delete LinkerHandHTTPAPI >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo ✅ 服务已卸载
) else (
    echo ℹ️  服务未安装
)

REM 删除防火墙规则
echo 删除防火墙规则...
netsh advfirewall firewall delete rule name="LinkerHand HTTP API" >nul 2>&1
echo ✅ 防火墙规则已清理

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 卸载完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo LinkerHand HTTP API服务已完全移除
echo.
pause
exit /b 0

:error
echo.
echo ❌ 卸载失败：需要管理员权限
echo.
pause
exit /b 1