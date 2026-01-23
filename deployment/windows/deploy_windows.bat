@echo off
REM LinkerHand HTTP API Windows一键部署批处理文件
REM 此文件简化了Python脚本的执行过程

echo LinkerHand HTTP API Windows部署工具
echo ====================================
echo.
echo 此批处理文件将运行Python部署脚本
echo 请确保:
echo   1. 已安装Python 3.8+
echo   2. 已安装所有依赖 (pip install -r requirements.txt)
echo   3. 以管理员身份运行此脚本
echo.
echo 按任意键开始部署...
pause >nul

echo.
echo 启动部署脚本...
python deploy_windows.py

echo.
echo 部署完成！
echo.
echo 按任意键退出...
pause >nul