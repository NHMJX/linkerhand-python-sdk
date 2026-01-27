@echo off
chcp 65001 >nul
REM LinkerHand UDP控制服务安装脚本

title LinkerHand UDP控制服务安装程序

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        LinkerHand UDP控制服务安装程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
echo [1/6] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    echo    请右键点击 install_udp_service.bat，选择"以管理员身份运行"
    goto :error
)
echo ✅ 管理员权限检查通过

REM 检查Python
echo.
echo [2/6] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python
    echo    请安装Python 3.8+
    goto :error
)
echo ✅ Python环境正常

REM 检查服务文件
echo.
echo [3/6] 检查服务文件...
if not exist "udp_service.py" (
    echo ❌ 找不到 udp_service.py
    goto :error
)
if not exist "udp_windows_service.py" (
    echo ❌ 找不到 udp_windows_service.py
    goto :error
)
echo ✅ 服务文件检查通过

REM 检查exe文件（如果存在）
echo.
echo [4/6] 检查exe文件...
if not exist "linkerhand_service.exe" (
    echo ⚠️  未找到 linkerhand_service.exe
    echo    服务将使用默认路径查找exe文件
    echo    可以通过环境变量 LINKERHAND_EXE_PATH 指定
) else (
    echo ✅ 找到 linkerhand_service.exe
)

REM 配置防火墙
echo.
echo [5/6] 配置防火墙...
netsh advfirewall firewall add rule name="LinkerHand UDP Service" dir=in action=allow protocol=UDP localport=8888 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  防火墙配置失败，请手动允许UDP端口8888
) else (
    echo ✅ 防火墙规则已配置
)

REM 卸载旧服务
echo.
echo [6/6] 安装Windows服务...
sc query LinkerHandUDPService >nul 2>&1
if %errorlevel% equ 0 (
    echo 发现旧服务，正在卸载...
    sc stop LinkerHandUDPService >nul 2>&1
    sc delete LinkerHandUDPService >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo ✅ 旧服务已卸载
)

REM 安装新服务
echo 正在安装UDP控制服务...
python udp_windows_service.py --username "NT AUTHORITY\\LocalService" --password "" install
if %errorlevel% neq 0 (
    echo ❌ 服务安装失败
    goto :error
)

REM 启动服务
echo 启动服务...
sc start LinkerHandUDPService
if %errorlevel% neq 0 (
    echo ⚠️  服务启动失败，请稍后手动启动
    echo    命令: sc start LinkerHandUDPService
) else (
    echo ✅ 服务启动成功
)

REM 验证安装
echo.
echo 验证安装...
timeout /t 3 /nobreak >nul
sc query LinkerHandUDPService | findstr "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✅ 服务运行正常
) else (
    echo ⚠️  服务可能未正常启动，请检查日志
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 🌟 服务信息：
echo    服务名称: LinkerHandUDPService
echo    显示名称: LinkerHand UDP Control Service
echo    UDP端口: 8888
echo    状态: 开机自启动
echo.
echo 📡 UDP控制接口：
echo    发送 "START" 到 UDP端口8888启动exe文件
echo    发送 "STATUS" 查询服务状态
echo    发送 "PING" 测试连接
echo.
echo 📝 服务管理：
echo    查看状态: sc query LinkerHandUDPService
echo    启动服务: sc start LinkerHandUDPService
echo    停止服务: sc stop LinkerHandUDPService
echo    卸载服务: sc stop LinkerHandUDPService ^& sc delete LinkerHandUDPService
echo.
echo ⚙️  配置说明：
echo    exe路径: 环境变量 LINKERHAND_EXE_PATH (默认: linkerhand_service.exe)
echo    exe参数: 环境变量 LINKERHAND_EXE_ARGS (默认: robot)
echo    UDP端口: 环境变量 UDP_PORT (默认: 8888)
echo.
echo 📋 日志位置：
echo    udp_service.log
echo.
pause
exit /b 0

:error
echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装失败                      ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 请检查上述错误信息并重试
pause
exit /b 1