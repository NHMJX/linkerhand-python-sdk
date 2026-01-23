#!/usr/bin/env python3
"""
LinkerHand HTTP API Windows服务安装/卸载脚本
"""

import os
import sys
import subprocess
import winreg
import shutil
from pathlib import Path

class ServiceInstaller:
    """Windows服务安装器"""

    def __init__(self):
        self.service_name = "LinkerHandHTTPAPI"
        self.display_name = "LinkerHand HTTP API Service"
        self.install_dir = Path("C:\\LinkerHand_HTTP_API")
        self.service_script = "windows_service.py"

    def check_admin_privileges(self):
        """检查管理员权限"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_install_directory(self):
        """创建安装目录"""
        print(f"创建安装目录: {self.install_dir}")
        self.install_dir.mkdir(parents=True, exist_ok=True)

    def copy_files(self):
        """复制必要文件到安装目录"""
        print("复制文件到安装目录...")

        files_to_copy = [
            "windows_service.py",
            "dist/LinkerHand_HTTP_API.exe",
            "requirements.txt",
            "README.md"
        ]

        for file_path in files_to_copy:
            src = Path(file_path)
            if src.exists():
                dst = self.install_dir / src.name
                if src.is_file():
                    shutil.copy2(src, dst)
                    print(f"  ✓ 复制: {src} -> {dst}")
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    print(f"  ✓ 复制目录: {src} -> {dst}")
            else:
                print(f"  ⚠ 跳过不存在的文件: {src}")

    def install_service(self):
        """安装Windows服务"""
        print("安装Windows服务...")

        # 切换到安装目录
        os.chdir(self.install_dir)

        # 安装服务
        cmd = [
            sys.executable, self.service_script,
            "--username", "NT AUTHORITY\\LocalService",
            "--password", "",
            "install"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✓ 服务安装成功")
            print("服务名称:", self.service_name)
            print("显示名称:", self.display_name)
        except subprocess.CalledProcessError as e:
            print("✗ 服务安装失败:")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False

        return True

    def start_service(self):
        """启动服务"""
        print("启动服务...")

        cmd = [sys.executable, self.service_script, "start"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✓ 服务启动成功")
        except subprocess.CalledProcessError as e:
            print("✗ 服务启动失败:")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False

        return True

    def stop_service(self):
        """停止服务"""
        print("停止服务...")

        try:
            cmd = [sys.executable, self.service_script, "stop"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            print("✓ 服务停止成功")
        except Exception as e:
            print(f"停止服务时出错: {e}")

    def uninstall_service(self):
        """卸载服务"""
        print("卸载Windows服务...")

        # 首先停止服务
        self.stop_service()

        try:
            cmd = [sys.executable, self.service_script, "remove"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            print("✓ 服务卸载成功")
        except Exception as e:
            print(f"卸载服务时出错: {e}")

    def add_to_startup(self):
        """添加到开机自启动（通过注册表）"""
        print("添加到开机自启动...")

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            service_exe = str(self.install_dir / "LinkerHand_HTTP_API.exe")
            winreg.SetValueEx(key, self.display_name, 0, winreg.REG_SZ, service_exe)
            winreg.CloseKey(key)

            print("✓ 已添加到开机自启动")
        except Exception as e:
            print(f"添加到开机自启动失败: {e}")

    def remove_from_startup(self):
        """从开机自启动中移除"""
        print("从开机自启动中移除...")

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            try:
                winreg.DeleteValue(key, self.display_name)
                print("✓ 已从开机自启动中移除")
            except FileNotFoundError:
                print("开机自启动中没有找到该服务")

            winreg.CloseKey(key)
        except Exception as e:
            print(f"从开机自启动移除失败: {e}")

    def install(self):
        """完整安装过程"""
        print("开始安装LinkerHand HTTP API服务...")
        print("=" * 50)

        if not self.check_admin_privileges():
            print("⚠ 警告: 当前没有管理员权限，服务安装可能失败")
            print("   建议以管理员身份运行此脚本")
            input("按Enter键继续...")

        # 创建安装目录
        self.create_install_directory()

        # 复制文件
        self.copy_files()

        # 安装服务
        if self.install_service():
            # 启动服务
            self.start_service()

            # 添加到开机自启动
            self.add_to_startup()

            print("\n" + "=" * 50)
            print("✓ 安装完成!")
            print("服务已安装并设置为开机自启动")
            print(f"安装目录: {self.install_dir}")
            print("API地址: http://localhost:8000")
            print("API文档: http://localhost:8000/docs")
        else:
            print("✗ 安装失败!")

    def uninstall(self):
        """完整卸载过程"""
        print("开始卸载LinkerHand HTTP API服务...")
        print("=" * 50)

        # 从开机自启动中移除
        self.remove_from_startup()

        # 卸载服务
        self.uninstall_service()

        # 删除安装目录
        if self.install_dir.exists():
            try:
                shutil.rmtree(self.install_dir)
                print(f"✓ 删除安装目录: {self.install_dir}")
            except Exception as e:
                print(f"删除安装目录失败: {e}")

        print("✓ 卸载完成!")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python install_service.py install    # 安装服务")
        print("  python install_service.py uninstall  # 卸载服务")
        sys.exit(1)

    command = sys.argv[1].lower()
    installer = ServiceInstaller()

    if command == "install":
        installer.install()
    elif command == "uninstall":
        installer.uninstall()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()