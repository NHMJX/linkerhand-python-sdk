@echo off
chcp 65001 >nul
REM LinkerHand UDP控制服务测试启动脚本

title LinkerHand UDP控制服务测试

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        LinkerHand UDP控制服务测试模式          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查Python
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python
    goto :error
)
echo ✅ Python环境正常

REM 检查服务文件
echo.
echo [2/3] 检查服务文件...
if not exist "udp_service.py" (
    echo ❌ 找不到 udp_service.py
    goto :error
)
echo ✅ 服务文件检查通过

REM 配置参数
echo.
echo [3/3] 配置服务参数...
set UDP_HOST=0.0.0.0
set UDP_PORT=8888
set LINKERHAND_EXE_PATH=linkerhand_service.exe
set LINKERHAND_EXE_ARGS=robot

echo 监听地址: %UDP_HOST%:%UDP_PORT%
echo exe路径: %LINKERHAND_EXE_PATH%
echo exe参数: %LINKERHAND_EXE_ARGS%

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 启动服务                      ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 🌟 UDP控制服务已启动！
echo 📡 监听端口: %UDP_PORT%
echo ⚡ 发送 "START" 命令到UDP端口 %UDP_PORT% 可启动exe文件
echo 🔄 发送 "STATUS" 可查询服务状态
echo 📶 发送 "PING" 可测试连接
echo.
echo 🛑 按Ctrl+C停止服务
echo.
echo 💡 提示：可同时运行 test_udp_client.py 进行测试
echo.

REM 启动服务
python udp_service.py --host %UDP_HOST% --port %UDP_PORT% --exe "%LINKERHAND_EXE_PATH%" --args %LINKERHAND_EXE_ARGS%

echo.
echo 服务已停止
pause
exit /b 0

:error
echo.
echo ❌ 启动失败，请检查上述错误信息
pause
exit /b 1