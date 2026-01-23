#!/usr/bin/env python3
"""
LinkerHand HTTP API Windows一键部署脚本
自动完成打包、安装和启动的全过程
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

class WindowsDeployer:
    """Windows部署器"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.exe_path = self.dist_dir / "LinkerHand_HTTP_API.exe"

    def check_requirements(self):
        """检查依赖"""
        print("检查依赖...")

        required_modules = [
            'PyInstaller',
            'pywin32',
            'fastapi',
            'uvicorn',
            'pydantic'
        ]

        missing = []
        for module in required_modules:
            try:
                __import__(module.replace('-', '_'))
                print(f"  ✓ {module}")
            except ImportError:
                missing.append(module)
                print(f"  ✗ {module}")

        if missing:
            print(f"\n缺少依赖模块: {', '.join(missing)}")
            print("请运行: pip install -r requirements.txt")
            return False

        print("✓ 所有依赖已安装")
        return True

    def build_exe(self):
        """构建exe文件"""
        print("\n构建可执行文件...")

        if self.exe_path.exists():
            response = input("exe文件已存在，是否重新构建? (y/N): ")
            if response.lower() != 'y':
                print("跳过构建步骤")
                return True

        # 运行构建脚本
        result = subprocess.run([sys.executable, "build_exe.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 构建成功")
            return True
        else:
            print("✗ 构建失败:")
            print(result.stderr)
            return False

    def install_service(self):
        """安装服务"""
        print("\n安装Windows服务...")

        # 检查管理员权限
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False

        if not is_admin:
            print("⚠ 需要管理员权限来安装服务")
            print("请以管理员身份重新运行此脚本")
            return False

        # 运行安装脚本
        result = subprocess.run([sys.executable, "install_service.py", "install"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 服务安装成功")
            return True
        else:
            print("✗ 服务安装失败:")
            print(result.stderr)
            return False

    def verify_installation(self):
        """验证安装"""
        print("\n验证安装...")

        # 检查服务状态
        result = subprocess.run(["sc", "query", "LinkerHandHTTPAPI"],
                              capture_output=True, text=True)

        if "RUNNING" in result.stdout:
            print("✓ 服务正在运行")
        elif "STOPPED" in result.stdout:
            print("⚠ 服务已安装但未运行")
            # 尝试启动服务
            print("尝试启动服务...")
            subprocess.run(["sc", "start", "LinkerHandHTTPAPI"])
        else:
            print("✗ 服务未正确安装")
            return False

        # 等待服务启动
        print("等待服务启动...")
        time.sleep(3)

        # 测试API
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✓ API响应正常")
                return True
            else:
                print(f"⚠ API响应异常: {response.status_code}")
                return False
        except ImportError:
            print("⚠ 无法验证API（缺少requests模块）")
            print("请手动访问: http://localhost:8000/health")
            return True
        except Exception as e:
            print(f"⚠ API验证失败: {e}")
            print("请检查服务日志: C:\\LinkerHand_HTTP_API\\service.log")
            return False

    def show_info(self):
        """显示安装信息"""
        print("\n" + "="*50)
        print("部署完成！")
        print("="*50)
        print("服务名称: LinkerHandHTTPAPI")
        print("显示名称: LinkerHand HTTP API Service")
        print("安装目录: C:\\LinkerHand_HTTP_API")
        print("API地址: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("服务日志: C:\\LinkerHand_HTTP_API\\service.log")
        print("")
        print("常用命令:")
        print("  启动服务: sc start LinkerHandHTTPAPI")
        print("  停止服务: sc stop LinkerHandHTTPAPI")
        print("  查看状态: sc query LinkerHandHTTPAPI")
        print("  卸载服务: python install_service.py uninstall")

    def deploy(self):
        """一键部署"""
        print("LinkerHand HTTP API Windows一键部署工具")
        print("="*50)
        print("此工具将自动完成以下步骤:")
        print("1. 检查依赖")
        print("2. 构建exe文件")
        print("3. 安装Windows服务")
        print("4. 设置开机自启动")
        print("5. 验证安装")
        print("="*50)

        # 确认操作
        response = input("\n是否继续? (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return

        # 执行部署步骤
        steps = [
            ("检查依赖", self.check_requirements),
            ("构建exe", self.build_exe),
            ("安装服务", self.install_service),
            ("验证安装", self.verify_installation),
        ]

        success_count = 0
        for step_name, step_func in steps:
            try:
                if step_func():
                    success_count += 1
                else:
                    print(f"\n✗ {step_name}失败，停止部署")
                    break
            except Exception as e:
                print(f"\n✗ {step_name}出错: {e}")
                break

        if success_count == len(steps):
            self.show_info()
        else:
            print(f"\n部署未完成 ({success_count}/{len(steps)} 步骤成功)")
            print("请检查错误信息并重试")

def main():
    """主函数"""
    try:
        deployer = WindowsDeployer()
        deployer.deploy()
    except KeyboardInterrupt:
        print("\n\n部署已取消")
    except Exception as e:
        print(f"\n部署出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()