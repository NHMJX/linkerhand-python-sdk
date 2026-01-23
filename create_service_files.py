#!/usr/bin/env python3
"""
创建Windows服务相关文件的Python脚本
"""

import os

def create_service_files():
    """创建服务相关文件"""

    # Windows服务包装器
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

    # 安装脚本
    install_code = '''@echo off
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

    # 卸载脚本
    uninstall_code = '''@echo off
chcp 65001 >nul
REM LinkerHand HTTP API 卸载脚本

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 卸载程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    goto :error
)

echo 正在停止并卸载LinkerHand HTTP API服务...
echo.

REM 停止服务
sc query LinkerHandHTTPAPI >nul 2>&1
if %errorlevel% equ 0 (
    echo 停止服务...
    sc stop LinkerHandHTTPAPI >nul 2>&1
    timeout /t 2 /nobreak >nul

    echo 卸载服务...
    sc delete LinkerHandHTTPAPI >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo ✅ 服务已卸载
) else (
    echo ℹ️  服务未安装
)

REM 删除防火墙规则
echo 删除防火墙规则...
netsh advfirewall firewall delete rule name="LinkerHand HTTP API" >nul 2>&1
echo ✅ 防火墙规则已清理

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 卸载完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo LinkerHand HTTP API服务已完全移除
echo.
pause
exit /b 0

:error
echo.
echo ❌ 卸载失败：需要管理员权限
echo.
pause
exit /b 1
'''

    # README文件
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
- 构建时间: Windows环境打包
- 支持的LinkerHand型号: L6, L7, L10, L20系列

---

**注意**: 请在安全的环境中使用，确保硬件连接正确。
'''

    # 确保dist目录存在
    os.makedirs('dist', exist_ok=True)

    # 写入文件
    with open('dist/LinkerHand_Service.py', 'w', encoding='utf-8') as f:
        f.write(service_code)

    with open('dist/install.bat', 'w', encoding='utf-8') as f:
        f.write(install_code)

    with open('dist/uninstall.bat', 'w', encoding='utf-8') as f:
        f.write(uninstall_code)

    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print('服务文件创建完成')

if __name__ == "__main__":
    create_service_files()