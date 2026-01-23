@echo off
REM Windows PyInstaller 打包脚本
REM 用于在Windows环境下打包LinkerHand HTTP API

echo ===============================================
echo LinkerHand HTTP API Windows打包工具
echo ===============================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: 未找到Python
    echo 请确保Python已安装并在PATH中
    pause
    exit /b 1
)

REM 检查PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: 未找到PyInstaller
    echo 请运行: pip install pyinstaller pywin32
    pause
    exit /b 1
)

REM 检查LinkerHand目录
if not exist "LinkerHand" (
    echo ERROR: 未找到LinkerHand目录
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 清理旧文件
echo 清理旧的构建文件...
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "linker_hand_standalone.spec" del "linker_hand_standalone.spec" >nul 2>&1

REM 创建新的spec文件
echo 创建PyInstaller配置文件...
python create_spec.py
if %errorlevel% neq 0 (
    echo ERROR: spec文件创建失败
    pause
    exit /b 1
)

REM 运行PyInstaller
echo.
echo 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

python -m PyInstaller --clean --noconfirm linker_hand_standalone.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller打包失败
    echo 请检查上面的错误信息
    pause
    exit /b 1
)

REM 检查生成的文件
echo.
echo 检查生成的文件...

if exist "dist\LinkerHand_HTTP_Service.exe" (
    for %%A in ("dist\LinkerHand_HTTP_Service.exe") do set size=%%~zA
    set /a size_mb=size/1024/1024
    echo ✓ 主程序已生成: dist\LinkerHand_HTTP_Service.exe (!size_mb!MB)
) else (
    echo ✗ 主程序未生成
    goto :error
)

REM 创建服务文件
echo.
echo 创建服务相关文件...
python create_service_files.py
if %errorlevel% neq 0 (
    echo ERROR: 服务文件创建失败
    pause
    exit /b 1
)

echo.
echo ===============================================
echo ✅ 打包完成!
echo ===============================================
echo.
echo 生成的文件位于 dist/ 目录:
echo   - LinkerHand_HTTP_Service.exe (主程序)
echo   - LinkerHand_Service.py (服务包装器)
echo   - install.bat (安装脚本)
echo   - uninstall.bat (卸载脚本)
echo   - README.txt (说明文档)
echo.
echo 📦 部署步骤:
echo 1. 复制整个 dist/ 目录到目标Windows机器
echo 2. 以管理员身份运行 install.bat
echo 3. 等待安装完成，服务将自动启动
echo 4. 访问 http://localhost:8000 使用API
echo.
echo 📝 注意事项:
echo - 确保目标机器有管理员权限
echo - 如果有防火墙，请允许端口8000
echo - 首次运行可能需要几秒钟启动时间
echo.
pause
exit /b 0

:error
echo.
echo ❌ 打包失败
echo 请检查上面的错误信息并重试
pause
exit /b 1
