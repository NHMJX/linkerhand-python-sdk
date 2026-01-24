@echo off
chcp 65001 >nul
echo 正在打包 LinkerHand HTTP API 服务...
python build.py
if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)
echo.
echo 打包完成！可执行文件位于: dist\linkerhand_service.exe
echo.
pause
