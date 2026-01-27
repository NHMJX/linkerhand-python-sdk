@echo off
REM ===== 设置编码，避免中文路径炸 =====
chcp 65001 >nul

REM ===== 初始化 conda =====
call "C:\miniconda\Scripts\activate.bat"

REM ===== 激活虚拟环境 =====
call conda activate hand_o6

REM ===== 切到项目目录 =====
cd /d C:\linkerhand-python-sdk\Demo

REM ===== 运行你的 Python 程序 =====
python main_http.py >> run.log 2>&1
