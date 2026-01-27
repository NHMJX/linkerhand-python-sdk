@echo off
chcp 65001 >nul
REM LinkerHand UDP控制服务卸载脚本

title LinkerHand UDP控制服务卸载程序

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        LinkerHand UDP控制服务卸载程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
echo [1/4] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    echo    请右键点击 uninstall_udp_service.bat，选择"以管理员身份运行"
    goto :error
)
echo ✅ 管理员权限检查通过

REM 检查服务是否存在
echo.
echo [2/4] 检查服务状态...
sc query LinkerHandUDPService >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  服务不存在，可能已被卸载
    goto :cleanup
)
echo ✅ 找到服务，正在停止...

REM 停止服务
echo.
echo [3/4] 停止服务...
sc stop LinkerHandUDPService >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  服务停止失败，可能已在停止状态
) else (
    echo ✅ 服务已停止
)

REM 删除服务
echo.
echo [4/4] 删除服务...
sc delete LinkerHandUDPService >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 服务删除失败
    echo    请稍后重试或手动删除
    goto :error
) else (
    echo ✅ 服务已删除
)

:cleanup
REM 清理防火墙规则
echo.
echo [清理] 清理防火墙规则...
netsh advfirewall firewall delete rule name="LinkerHand UDP Service" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  防火墙规则清理失败，请手动删除
) else (
    echo ✅ 防火墙规则已清理
)

REM 询问是否删除日志文件
echo.
set /p delete_logs="是否删除日志文件? (y/N): "
if /i "%delete_logs%"=="y" (
    if exist "udp_service.log" (
        del "udp_service.log"
        echo ✅ 日志文件已删除
    ) else (
        echo ⚠️  日志文件不存在
    )
) else (
    echo ⏭️  保留日志文件
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 卸载完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 🗑️  已清理：
echo    - LinkerHandUDPService (Windows服务)
echo    - 防火墙规则
if /i "%delete_logs%"=="y" echo    - udp_service.log
echo.
echo 📝 注意：
echo    exe文件和Python脚本文件未被删除，如需完全清理请手动删除
echo.
pause
exit /b 0

:error
echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 卸载失败                      ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 请检查上述错误信息并重试
pause
exit /b 1