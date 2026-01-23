@echo off
REM 快速PyInstaller打包命令
REM 如果其他脚本有问题，请使用此脚本

echo 开始快速打包...
echo.

pyinstaller --onedir ^
    --name LinkerHand_HTTP_Service ^
    --hidden-import LinkerHand.linker_hand_api ^
    --hidden-import LinkerHand.core.can ^
    --hidden-import LinkerHand.core.rs485 ^
    --hidden-import LinkerHand.utils ^
    --hidden-import can ^
    --hidden-import can.interfaces.pcan ^
    --hidden-import minimalmodbus ^
    --hidden-import serial ^
    --hidden-import yaml ^
    --hidden-import fastapi ^
    --hidden-import uvicorn ^
    --hidden-import pydantic ^
    --hidden-import starlette ^
    --hidden-import win32api ^
    --hidden-import win32service ^
    --hidden-import win32serviceutil ^
    --hidden-import servicemanager ^
    --add-data "LinkerHand;LinkerHand" ^
    --noconsole ^
    Demo/main_http.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ PyInstaller打包成功！

    REM 调整目录结构 - 将exe文件复制到dist根目录
    if exist "dist\LinkerHand_HTTP_Service\LinkerHand_HTTP_Service.exe" (
        echo 调整目录结构...
        copy "dist\LinkerHand_HTTP_Service\LinkerHand_HTTP_Service.exe" "dist\LinkerHand_HTTP_Service.exe" >nul
        echo ✅ exe文件已复制到正确位置
    )

    REM 创建服务文件
    echo.
    echo 创建服务相关文件...
    python create_service_files.py

    echo.
    echo ✅ 快速打包和文件创建完成！
    echo.
    echo 📦 生成的文件位于 dist/ 目录:
    echo   - LinkerHand_HTTP_Service.exe (主程序)
    echo   - LinkerHand_Service.py (服务包装器)
    echo   - install.bat (安装脚本)
    echo   - uninstall.bat (卸载脚本)
    echo   - README.txt (说明文档)
    echo.
    echo 🚀 部署步骤:
    echo 1. 复制整个 dist/ 目录到目标Windows机器
    echo 2. 以管理员身份运行 install.bat
    echo 3. 等待安装完成，服务将自动启动
    echo 4. 访问 http://localhost:8000 使用API

) else (
    echo.
    echo ❌ 打包失败
    echo 请检查上面的错误信息
)

pause