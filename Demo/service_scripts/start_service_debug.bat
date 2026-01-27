@echo off
chcp 65001 >nul
REM 调试版本 - 启动LinkerHand HTTP API服务（Conda环境专用）
REM 此版本包含详细的调试信息，帮助排查启动问题

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        LinkerHand HTTP API服务 - 调试启动模式            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM Conda环境配置（请修改为您的Conda环境名）
REM ============================================================
REM 如果留空，脚本会尝试使用已激活的环境或base环境
set "CONDA_ENV_NAME="
REM 如果上面的环境名为空，是否使用base环境
set "USE_BASE_IF_EMPTY=1"

echo [1/6] 检查脚本环境...
REM 获取脚本所在目录的父目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."
echo 脚本目录: %SCRIPT_DIR%
echo 项目目录: %PROJECT_DIR%

REM 切换到项目根目录
cd /d "%PROJECT_DIR%"
echo 当前目录: %cd%
echo.

echo [2/6] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未找到或不在PATH中
    echo    请确保Python已正确安装并添加到PATH
    goto :error
) else (
    echo ✅ Python环境正常
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo     %%i
)
echo.

echo [3/6] 检查目标文件...
if not exist "Demo\main_http.py" (
    echo ❌ 找不到 Demo\main_http.py 文件
    echo    请确保文件存在于正确位置
    goto :error
) else (
    echo ✅ 找到 Demo\main_http.py
)

REM 检查文件大小
for %%A in ("Demo\main_http.py") do echo     文件大小: %%~zA 字节
echo.

echo [4/6] 激活Conda环境...
if defined CONDA_DEFAULT_ENV (
    REM 如果已激活Conda环境，直接使用
    echo ✅ 使用已激活的Conda环境: %CONDA_DEFAULT_ENV%
) else (
    REM 尝试激活Conda环境
    set "CONDA_ACTIVATED=0"

    REM 查找conda安装路径
    set "CONDA_BASE="
    if defined CONDA_EXE (
        for %%F in ("%CONDA_EXE%") do set "CONDA_BASE=%%~dpF.."
        echo     通过CONDA_EXE找到conda: %CONDA_BASE%
    ) else (
        echo     查找conda安装路径...
        REM 尝试从注册表查找
        for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Anaconda3" /v InstallPath 2^>nul') do set "CONDA_BASE=%%B"
        if not defined CONDA_BASE (
            for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Anaconda3" /v InstallPath 2^>nul') do set "CONDA_BASE=%%B"
        )
        if not defined CONDA_BASE (
            if exist "%USERPROFILE%\Anaconda3\Scripts\conda.exe" (
                set "CONDA_BASE=%USERPROFILE%\Anaconda3"
                echo     找到Anaconda3: %CONDA_BASE%
            ) else if exist "%USERPROFILE%\Miniconda3\Scripts\conda.exe" (
                set "CONDA_BASE=%USERPROFILE%\Miniconda3"
                echo     找到Miniconda3: %CONDA_BASE%
            ) else if exist "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
                set "CONDA_BASE=C:\ProgramData\Anaconda3"
                echo     找到系统Anaconda3: %CONDA_BASE%
            )
        )
    )

    REM 如果找到conda，尝试激活环境
    if defined CONDA_BASE (
        echo     Conda基础路径: %CONDA_BASE%
        if exist "%CONDA_BASE%\Scripts\activate.bat" (
            echo     激活脚本存在，开始激活...

            REM 初始化conda（如果需要）
            call "%CONDA_BASE%\Scripts\activate.bat" >nul 2>&1
            if %errorlevel% neq 0 (
                echo ❌ Conda初始化失败
                goto :error
            )

            REM 激活指定环境或base环境
            if not "%CONDA_ENV_NAME%"=="" (
                echo     激活环境: %CONDA_ENV_NAME%
                call "%CONDA_BASE%\Scripts\activate.bat" %CONDA_ENV_NAME% >nul 2>&1
                if %errorlevel% equ 0 (
                    set "CONDA_ACTIVATED=1"
                    echo ✅ 已激活Conda环境: %CONDA_ENV_NAME%
                ) else (
                    echo ❌ 激活环境失败: %CONDA_ENV_NAME%
                )
            ) else if "%USE_BASE_IF_EMPTY%"=="1" (
                echo     激活base环境...
                call "%CONDA_BASE%\Scripts\activate.bat" base >nul 2>&1
                if %errorlevel% equ 0 (
                    set "CONDA_ACTIVATED=1"
                    echo ✅ 已激活Conda环境: base
                ) else (
                    echo ❌ 激活base环境失败
                )
            )
        ) else (
            echo ❌ 找不到conda激活脚本
        )
    ) else (
        echo ❌ 未找到conda安装路径
        echo     请确保conda已正确安装
    )

    REM 检查是否成功激活
    if not defined CONDA_DEFAULT_ENV (
        if %CONDA_ACTIVATED%==0 (
            echo.
            echo ============================================================
            echo ⚠️  警告: 无法自动激活Conda环境
            echo ============================================================
            echo.
            echo 可能的原因：
            echo 1. Conda未安装或不在PATH中
            echo 2. 环境名配置错误
            echo 3. 系统权限问题
            echo.
            echo 解决方案：
            echo 方法1: 手动激活环境后运行
            echo   conda activate 环境名
            echo   然后重新运行此脚本
            echo.
            echo 方法2: 修改脚本配置
            echo   编辑此脚本，设置CONDA_ENV_NAME变量
            echo   例如: set "CONDA_ENV_NAME=linkerhand"
            echo.
            echo 方法3: 使用系统Python（如果不需要特殊环境）
            echo   注释掉Conda激活部分，直接使用系统Python
            echo.
            goto :error
        )
    )
)
echo.

echo [5/6] 测试Python导入...
python -c "import sys; print(f'Python路径: {sys.executable}'); print(f'Python版本: {sys.version}')" 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python测试失败
    goto :error
) else (
    echo ✅ Python运行正常
)
echo.

echo [6/6] 测试main_http.py导入...
python -c "import sys; sys.path.insert(0, '.'); import Demo.main_http" 2>&1
if %errorlevel% neq 0 (
    echo ❌ main_http.py 导入测试失败
    echo     可能的原因：
    echo     - 缺少依赖包
    echo     - 导入路径错误
    echo     - 语法错误
    goto :error
) else (
    echo ✅ main_http.py 导入成功
)
echo.

echo ╔══════════════════════════════════════════════════════════╗
echo ║                   启动服务...                           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 尝试启动服务...
echo 命令: python Demo\main_http.py
echo.

REM 尝试启动服务（显示窗口，便于查看错误信息）
python Demo\main_http.py
set "START_EXIT_CODE=%errorlevel%"

echo.
echo 服务退出，退出代码: %START_EXIT_CODE%
if %START_EXIT_CODE% neq 0 (
    echo ❌ 服务启动失败
    goto :error
) else (
    echo ✅ 服务启动成功
)

goto :end

:error
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                     启动失败                            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 请根据上述错误信息进行排查
echo.
pause
exit /b 1

:end
echo.
pause
exit /b 0