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
    echo ✅ 打包成功！
    echo 主程序: dist\LinkerHand_HTTP_Service\LinkerHand_HTTP_Service.exe
    echo.
    echo 请运行 build_windows.bat 来创建完整的安装包
) else (
    echo.
    echo ❌ 打包失败
    echo 请检查错误信息
)

pause