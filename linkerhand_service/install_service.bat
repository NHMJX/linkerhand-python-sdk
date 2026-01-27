@echo off
set SERVICE_NAME=LinkerHandPythonService
set NSSM=C:\nssm\nssm.exe
set BAT=C:\linkerhand-python-sdk\linkerhand_service\start_linkerhand.bat

REM 删除旧服务（如果存在）
%NSSM% stop %SERVICE_NAME% >nul 2>&1
%NSSM% remove %SERVICE_NAME% confirm >nul 2>&1

REM 创建服务
%NSSM% install %SERVICE_NAME% cmd.exe "/c \"%BAT%\""

REM 设置工作目录
%NSSM% set %SERVICE_NAME% AppDirectory C:\linkerhand-python-sdk

REM 设置为自动启动
%NSSM% set %SERVICE_NAME% Start SERVICE_AUTO_START

REM 失败自动重启
%NSSM% set %SERVICE_NAME% AppRestartDelay 5000
%NSSM% set %SERVICE_NAME% AppExit Default Restart

echo [OK] Service installed: %SERVICE_NAME%
pause
