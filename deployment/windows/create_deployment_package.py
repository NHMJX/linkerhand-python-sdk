#!/usr/bin/env python3
"""
LinkerHand HTTP API 部署包生成器
创建包含所有必要文件的部署包，用于在其他机器上安装
"""

import os
import zipfile
import shutil
from pathlib import Path

class DeploymentPackageCreator:
    """部署包创建器"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.package_name = "LinkerHand_Deployment_Package"
        self.package_dir = self.project_root / self.package_name

    def check_requirements(self):
        """检查必要文件是否存在"""
        required_files = [
            "dist/LinkerHand_HTTP_API.exe",
            "windows_service.py",
            "install_service.py",
            "requirements.txt"
        ]

        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print("缺少必要文件，请先运行以下命令：")
            print("1. python build_exe.py  # 构建exe文件")
            print(f"缺少的文件: {', '.join(missing_files)}")
            return False

        return True

    def create_package_directory(self):
        """创建部署包目录"""
        print(f"创建部署包目录: {self.package_dir}")
        self.package_dir.mkdir(exist_ok=True)

    def copy_core_files(self):
        """复制核心文件"""
        print("复制核心文件...")

        files_to_copy = [
            ("dist/LinkerHand_HTTP_API.exe", "LinkerHand_HTTP_API.exe"),
            ("windows_service.py", "windows_service.py"),
            ("install_service.py", "install_service.py"),
            ("requirements.txt", "requirements.txt"),
            ("WINDOWS_DEPLOYMENT.md", "README.md"),
            ("REMOTE_DEPLOYMENT.md", "REMOTE_README.md")
        ]

        for src_path, dst_name in files_to_copy:
            src = self.project_root / src_path
            dst = self.package_dir / dst_name

            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ {src_path} -> {dst_name}")
            else:
                print(f"  ⚠ 跳过不存在的文件: {src_path}")

    def create_install_script(self):
        """创建安装脚本"""
        print("创建安装脚本...")

        install_script = '''@echo off
chcp 65001 >nul
REM LinkerHand HTTP API 一键安装脚本
REM 支持中文显示和自动安装

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 安装程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

set "ERROR_FLAG=0"

echo [1/6] 检查系统环境...
echo.

REM 检查操作系统版本
ver | findstr /i "10\." >nul
if %errorlevel% neq 0 (
    ver | findstr /i "6\.3" >nul
    if %errorlevel% neq 0 (
        echo ❌ 不支持的操作系统版本
        echo    需要 Windows 10 或 Windows Server 2016 及以上版本
        goto :error
    )
)
echo ✅ 操作系统版本检查通过

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    echo    请右键点击 install.bat，选择"以管理员身份运行"
    goto :error
)
echo ✅ 管理员权限检查通过

REM 检查Python
echo.
echo [2/6] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python
    echo    请从 https://python.org 下载并安装 Python 3.8+
    goto :install_python
)

python --version
echo ✅ Python已安装

REM 检查pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到pip
    echo    请重新安装Python或手动安装pip
    goto :error
)
echo ✅ Pip已安装

echo.
echo [3/6] 安装Python依赖...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    echo    请检查网络连接或手动安装依赖
    goto :error
)
echo ✅ 依赖安装完成

echo.
echo [4/6] 配置防火墙...
netsh advfirewall firewall show rule name="LinkerHand HTTP API" >nul 2>&1
if %errorlevel% neq 0 (
    netsh advfirewall firewall add rule name="LinkerHand HTTP API" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  防火墙配置失败，请手动允许端口8000
    ) else (
        echo ✅ 防火墙规则已添加
    )
) else (
    echo ✅ 防火墙规则已存在
)

echo.
echo [5/6] 安装Windows服务...
python install_service.py install
if %errorlevel% neq 0 (
    echo ❌ 服务安装失败
    goto :error
)
echo ✅ 服务安装完成

echo.
echo [6/6] 验证安装...
timeout /t 3 /nobreak >nul
sc query LinkerHandHTTPAPI | findstr "RUNNING" >nul
if %errorlevel% neq 0 (
    echo ⚠️  服务未自动启动，尝试手动启动...
    sc start LinkerHandHTTPAPI >nul 2>&1
    timeout /t 2 /nobreak >nul
)

sc query LinkerHandHTTPAPI | findstr "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✅ 服务运行正常
) else (
    echo ⚠️  服务启动可能有问题，请检查日志
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 📍 服务信息：
echo    服务名称: LinkerHandHTTPAPI
echo    显示名称: LinkerHand HTTP API Service
echo.
echo 🌐 API地址：
echo    本地访问: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
echo 📝 日志位置：
echo    C:\\LinkerHand_HTTP_API\\service.log
echo.
echo 🛠️  管理命令：
echo    启动服务: sc start LinkerHandHTTPAPI
echo    停止服务: sc stop LinkerHandHTTPAPI
echo    查看状态: sc query LinkerHandHTTPAPI
echo.
echo 💡 提示：
echo    - 服务将在系统启动时自动运行
echo    - 如有问题请查看服务日志
echo    - 卸载请运行: python install_service.py uninstall
echo.
pause
exit /b 0

:install_python
echo.
echo ╔══════════════════════════════════════════════╗
echo ║             Python安装指南                   ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 1. 打开浏览器访问: https://python.org/downloads/
echo 2. 下载最新版本的Python 3.8+ 安装程序
echo 3. 运行安装程序，务必勾选"Add Python to PATH"
echo 4. 安装完成后重新运行此安装脚本
echo.
echo 或者从微软商店安装：
echo 1. 打开Microsoft Store
echo 2. 搜索"Python"
echo 3. 安装最新版本
echo.
pause
goto :error

:error
echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 安装失败                      ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 请检查上述错误信息并重试
echo 如需帮助，请查看 README.md 或联系技术支持
echo.
pause
exit /b 1
'''

        install_script_path = self.package_dir / "install.bat"
        with open(install_script_path, 'w', encoding='utf-8') as f:
            f.write(install_script)

        print(f"  ✓ 创建安装脚本: install.bat")

    def create_uninstall_script(self):
        """创建卸载脚本"""
        print("创建卸载脚本...")

        uninstall_script = '''@echo off
chcp 65001 >nul
REM LinkerHand HTTP API 卸载脚本

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          LinkerHand HTTP API 卸载程序          ║
echo ╚══════════════════════════════════════════════╝
echo.

set "ERROR_FLAG=0"

echo [1/3] 检查管理员权限...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 需要管理员权限
    echo    请右键点击 uninstall.bat，选择"以管理员身份运行"
    goto :error
)
echo ✅ 管理员权限检查通过

echo.
echo [2/3] 卸载Windows服务...
python install_service.py uninstall
if %errorlevel% neq 0 (
    echo ❌ 服务卸载失败，可能服务不存在或已被卸载
)
echo ✅ 服务卸载完成

echo.
echo [3/3] 清理文件...
if exist "C:\\LinkerHand_HTTP_API" (
    rmdir /s /q "C:\\LinkerHand_HTTP_API"
    if %errorlevel% equ 0 (
        echo ✅ 安装目录已清理
    ) else (
        echo ⚠️  安装目录清理失败，请手动删除 C:\\LinkerHand_HTTP_API
    )
) else (
    echo ℹ️  安装目录不存在
)

echo.
echo ╔══════════════════════════════════════════════╗
echo ║                 卸载完成！                    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 已完全移除LinkerHand HTTP API服务
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

        uninstall_script_path = self.package_dir / "uninstall.bat"
        with open(uninstall_script_path, 'w', encoding='utf-8') as f:
            f.write(uninstall_script)

        print(f"  ✓ 创建卸载脚本: uninstall.bat")

    def create_portable_python_setup(self):
        """创建便携式Python设置（可选）"""
        print("创建便携式Python配置...")

        # 检查是否有便携式Python
        portable_python_url = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip"

        readme_content = f'''便携式Python设置（可选）
============================

如果目标机器没有安装Python，可以使用便携式Python：

1. 下载Python嵌入式版本：
   {portable_python_url}

2. 解压到此目录

3. 修改install.bat中的Python路径：
   将 "python" 改为 "python/python.exe"

注意：某些Python包可能不兼容嵌入式版本，建议在目标机器上安装完整Python。
'''

        portable_readme_path = self.package_dir / "PORTABLE_PYTHON_README.txt"
        with open(portable_readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"  ✓ 创建便携式Python说明: PORTABLE_PYTHON_README.txt")

    def create_deployment_readme(self):
        """创建部署说明"""
        print("创建部署说明...")

        deployment_readme = '''LinkerHand HTTP API 部署包
==========================

此部署包包含将LinkerHand HTTP API安装到Windows机器所需的所有文件。

文件清单：
├── LinkerHand_HTTP_API.exe    # 主程序（已打包）
├── windows_service.py         # Windows服务包装器
├── install_service.py         # 服务安装脚本
├── requirements.txt           # Python依赖列表
├── install.bat               # 一键安装脚本（推荐）
├── uninstall.bat             # 卸载脚本
├── README.md                 # 详细文档
└── REMOTE_README.md          # 远程部署指南

快速开始：
1. 以管理员身份运行 install.bat
2. 等待安装完成
3. 访问 http://localhost:8000 测试服务

系统要求：
- Windows 10/11 或 Windows Server 2016+
- Python 3.8+ （如果没有，将在安装过程中提示安装）
- 管理员权限

故障排除：
- 如果安装失败，请查看命令行输出的错误信息
- 常见问题请参考 README.md

技术支持：
如有问题请联系技术支持或查看项目文档。
'''

        deployment_readme_path = self.package_dir / "DEPLOYMENT_README.txt"
        with open(deployment_readme_path, 'w', encoding='utf-8') as f:
            f.write(deployment_readme)

        print(f"  ✓ 创建部署说明: DEPLOYMENT_README.txt")

    def create_zip_package(self):
        """创建ZIP压缩包"""
        print("创建ZIP压缩包...")

        zip_name = f"{self.package_name}.zip"
        zip_path = self.project_root / zip_name

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.package_dir)
                    zipf.write(file_path, arcname)
                    print(f"  ✓ 添加到压缩包: {arcname}")

        zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
        print(".1f"        print(f"  ✓ 压缩包已创建: {zip_path}")

        return zip_path

    def cleanup(self):
        """清理临时文件"""
        print("清理临时文件...")
        if self.package_dir.exists():
            shutil.rmtree(self.package_dir)
            print(f"  ✓ 删除临时目录: {self.package_dir}")

    def create_package(self):
        """创建完整部署包"""
        print("开始创建LinkerHand HTTP API部署包...")
        print("=" * 50)

        # 检查必要文件
        if not self.check_requirements():
            return None

        # 创建包目录
        self.create_package_directory()

        # 复制文件
        self.copy_core_files()

        # 创建脚本
        self.create_install_script()
        self.create_uninstall_script()

        # 创建可选配置
        self.create_portable_python_setup()
        self.create_deployment_readme()

        # 创建压缩包
        zip_path = self.create_zip_package()

        # 清理
        self.cleanup()

        print("\n" + "=" * 50)
        print("部署包创建完成！")
        print("=" * 50)
        print(f"压缩包位置: {zip_path}")
        print("\n部署说明：")
        print("1. 将ZIP包复制到目标机器")
        print("2. 解压ZIP包")
        print("3. 以管理员身份运行 install.bat")
        print("4. 等待安装完成")

        return zip_path

def main():
    """主函数"""
    creator = DeploymentPackageCreator()
    creator.create_package()

if __name__ == "__main__":
    main()