#!/usr/bin/env python3
"""
LinkerHand HTTP API 独立打包脚本
生成完全独立的exe文件，无需目标机器安装Python
"""

import os
import sys
from pathlib import Path
import subprocess

def create_spec_file():
    """创建PyInstaller spec文件"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

project_root = r"''' + project_root + '''"

datas = [
    (os.path.join(project_root, "LinkerHand"), "LinkerHand"),
]

hiddenimports = [
    "LinkerHand.linker_hand_api",
    "LinkerHand.core.can",
    "LinkerHand.core.rs485",
    "LinkerHand.utils",
    "can", "can.interfaces.pcan", "minimalmodbus", "serial", "yaml",
    "fastapi", "uvicorn", "pydantic", "starlette",
    "win32api", "win32service", "win32serviceutil", "servicemanager",
]

a = Analysis(
    ["Demo/main_http.py"],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "numpy", "PIL", "PyQt5", "IPython"],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LinkerHand_HTTP_Service",
    debug=False,
    console=False,
    upx=True,
)
'''

    spec_file = Path("linker_hand_standalone.spec")
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建了 linker_hand_standalone.spec 文件")
    return spec_file

def run_pyinstaller():
    """运行PyInstaller打包"""
    print("正在打包独立exe文件...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onedir",
        "linker_hand_standalone.spec"
    ]

    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ 打包成功完成!")
        exe_path = Path("dist/LinkerHand_HTTP_Service.exe")
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ 生成exe文件大小: {exe_size:.1f}MB")
            return True
        else:
            print("✗ exe文件未找到")
            return False
    else:
        print("✗ 打包失败:")
        print(result.stderr)
        return False

def create_service_wrapper():
    """创建Windows服务包装器"""
    print("创建Windows服务包装器...")

    service_code = '''#!/usr/bin/env python3
import win32serviceutil, win32service, win32event, servicemanager
import sys, os, subprocess, time, logging
from pathlib import Path

class LinkerHandService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LinkerHandHTTPAPI"
    _svc_display_name_ = "LinkerHand HTTP API Service"
    _svc_description_ = "LinkerHand机械手控制HTTP API服务 - 开机自启动"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.service_dir = Path(__file__).parent
        self.exe_path = self.service_dir / "LinkerHand_HTTP_Service.exe"

        log_path = self.service_dir / "service.log"
        logging.basicConfig(filename=str(log_path), level=logging.INFO,
                          format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def SvcStop(self):
        self.logger.info("收到停止服务请求")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        if self.process and self.process.poll() is None:
            self.logger.info("正在停止HTTP服务器...")
            try:
                self.process.terminate()
                for _ in range(10):
                    if self.process.poll() is not None: break
                    time.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
                    self.logger.info("强制终止HTTP服务器")
            except Exception as e:
                self.logger.error(f"停止进程时出错: {e}")

    def SvcDoRun(self):
        self.logger.info("启动LinkerHand HTTP API服务")

        try:
            if not self.exe_path.exists():
                raise FileNotFoundError(f"找不到可执行文件: {self.exe_path}")

            self.logger.info(f"启动HTTP服务器: {self.exe_path}")
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                cwd=str(self.service_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            while True:
                if self.process.poll() is not None:
                    exit_code = self.process.returncode
                    self.logger.error(f"HTTP服务器异常退出，退出码: {exit_code}")
                    if exit_code != 0:
                        self.logger.info("等待5秒后重启服务...")
                        time.sleep(5)
                        self.process = subprocess.Popen(
                            [str(self.exe_path)],
                            cwd=str(self.service_dir),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        break

                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if result == win32event.WAIT_OBJECT_0: break

        except Exception as e:
            self.logger.error(f"服务运行出错: {str(e)}")
            raise

        self.logger.info("LinkerHand HTTP API服务已停止")

def main():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LinkerHandService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LinkerHandService)

if __name__ == "__main__":
    main()
'''

    service_file = Path("dist/LinkerHand_Service.py")
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_code)
    print("✓ 创建了服务包装器")
    return service_file

def create_installer():
    """创建一键安装脚本"""
    print("创建一键安装脚本...")

    installer_code = '''@echo off
chcp 65001 >nul
title LinkerHand HTTP API 安装程序

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 安装程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
echo [1/5] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    goto :error
)
echo ✅ 管理员权限检查通过

REM 检查文件
echo.
echo [2/5] 检查安装文件...
if not exist "LinkerHand_HTTP_Service.exe" (
    echo ❌ 找不到主程序文件
    goto :error
)
if not exist "LinkerHand_Service.py" (
    echo ❌ 找不到服务文件
    goto :error
)
echo ✅ 安装文件检查通过

REM 配置防火墙
echo.
echo [3/5] 配置防火墙...
netsh advfirewall firewall add rule name="LinkerHand HTTP API" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
echo ✅ 防火墙规则已配置

REM 卸载旧服务
echo.
echo [4/5] 检查旧服务...
sc query LinkerHandHTTPAPI >nul 2>&1
if %errorlevel% equ 0 (
    sc stop LinkerHandHTTPAPI >nul 2>&1
    sc delete LinkerHandHTTPAPI >nul 2>&1
    echo ✅ 旧服务已卸载
)

REM 安装新服务
echo.
echo [5/5] 安装Windows服务...
python LinkerHand_Service.py --username "NT AUTHORITY\\LocalService" --password "" install
if %errorlevel% neq 0 (
    echo ❌ 服务安装失败
    goto :error
)

sc start LinkerHandHTTPAPI
echo ✅ 服务安装并启动成功

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 🌐 API地址: http://localhost:8000
echo 📖 文档: http://localhost:8000/docs
echo.
pause
exit /b 0

:error
echo ❌ 安装失败
pause
exit /b 1
'''

    installer_file = Path("dist/install.bat")
    with open(installer_file, 'w', encoding='utf-8') as f:
        f.write(installer_code)
    print("✓ 创建了一键安装脚本")
    return installer_file

def create_readme():
    """创建说明文档"""
    print("创建说明文档...")

    readme_content = '''# LinkerHand HTTP API 独立安装包

## 📦 安装包内容

此安装包包含完整的运行环境，目标机器无需安装Python或其他开发工具。

### 文件清单
- `LinkerHand_HTTP_Service.exe` - 主程序（已打包所有依赖）
- `LinkerHand_Service.py` - Windows服务包装器
- `install.bat` - 一键安装脚本
- `uninstall.bat` - 卸载脚本
- `README.txt` - 本说明文件
- `service.log` - 服务运行日志（安装后生成）

## 🚀 快速安装

1. **以管理员身份运行** `install.bat`
2. 等待安装完成
3. 访问 `http://localhost:8000` 使用API

## 📋 系统要求

- Windows 10/11 或 Windows Server 2016+
- 管理员权限
- 至少 2GB 可用磁盘空间
- 已连接的LinkerHand硬件（可选，用于实际控制）

## 🌟 功能特性

- ✅ **完全独立** - 无需安装Python或其他开发环境
- ✅ **开机自启动** - Windows服务，系统启动时自动运行
- ✅ **自动重启** - 服务异常退出时自动重启
- ✅ **防火墙配置** - 自动配置端口8000访问权限
- ✅ **中文界面** - 友好的中文安装提示

## 🔧 API使用

### 基础API
```bash
# 握笔动作
curl -X POST http://localhost:8000/hold_pen

# 打开手部
curl -X POST http://localhost:8000/open_hand

# 设置速度
curl -X POST http://localhost:8000/set_speed -H "Content-Type: application/json" -d "{\\"speeds\\": [60,60,60,60,60,60]}"

# 移动手指
curl -X POST http://localhost:8000/finger_move -H "Content-Type: application/json" -d "{\\"positions\\": [120,90,120,70,50,40]}"
```

### 完整文档
安装完成后访问：`http://localhost:8000/docs`

## 📊 服务管理

### Windows服务控制
```bash
# 查看状态
sc query LinkerHandHTTPAPI

# 启动/停止
sc start LinkerHandHTTPAPI
sc stop LinkerHandHTTPAPI

# 重启服务
sc stop LinkerHandHTTPAPI & sc start LinkerHandHTTPAPI
```

### 服务属性
- **服务名称**: `LinkerHandHTTPAPI`
- **显示名称**: `LinkerHand HTTP API Service`
- **启动类型**: 自动（开机自启动）
- **运行账户**: LocalService

## 🔍 故障排除

### 服务无法启动
1. 检查 `service.log` 日志文件
2. 确认端口8000未被占用
3. 检查硬件连接（如果使用实际硬件）

### API访问失败
1. 确认服务正在运行
2. 检查防火墙设置
3. 尝试本地访问：`http://localhost:8000/health`

### 卸载重装
```bash
# 运行卸载脚本
uninstall.bat

# 重新运行安装
install.bat
```

## 📞 技术支持

- 📖 查看API文档：`http://localhost:8000/docs`
- 📝 查看服务日志：`service.log`
- 🐛 联系技术支持团队

## 📝 版本信息

- 版本: 3.1.0
- 构建时间: 自动生成
- 支持的LinkerHand型号: L6, L7, L10, L20系列

---

**注意**: 请在安全的环境中使用，确保硬件连接正确。
'''

    readme_file = Path("dist/README.txt")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ 创建了说明文档")
    return readme_file

def main():
    """主函数"""
    print("LinkerHand HTTP API 独立打包工具")
    print("=" * 50)
    print("此工具将创建完全独立的安装包，目标机器无需Python环境")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller未安装，请运行: pip install pyinstaller")
        sys.exit(1)

    # 创建spec文件
    spec_file = create_spec_file()

    # 运行打包
    if run_pyinstaller():
        # 创建安装包文件
        create_service_wrapper()
        create_installer()
        create_readme()

        print("\n" + "=" * 50)
        print("🎉 打包完成!")
        print("=" * 50)
        print("生成的文件位于 dist/ 目录:")
        print("  - LinkerHand_HTTP_Service.exe (主程序)")
        print("  - LinkerHand_Service.py (服务包装器)")
        print("  - install.bat (一键安装脚本)")
        print("  - README.txt (说明文档)")
        print("\n📦 部署步骤:")
        print("1. 复制整个 dist/ 目录到目标机器")
        print("2. 以管理员身份运行 install.bat")
        print("3. 等待安装完成，服务将自动启动")
        print("4. 访问 http://localhost:8000 使用API")
    else:
        print("✗ exe打包失败")
        sys.exit(1)

if __name__ == "__main__":
    main()