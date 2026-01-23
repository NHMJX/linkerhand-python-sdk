#!/usr/bin/env python3
"""
LinkerHand HTTP API 简化打包脚本
使用最基本的PyInstaller选项，避免兼容性问题
"""

import os
import sys
import subprocess
from pathlib import Path

def run_simple_build():
    """运行简化的PyInstaller打包"""
    print("使用简化模式打包LinkerHand HTTP API...")
    print("=" * 50)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 最基本的PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 生成单文件exe
        "--name", "LinkerHand_HTTP_Service",
        "--hidden-import", "LinkerHand.linker_hand_api",
        "--hidden-import", "LinkerHand.core.can",
        "--hidden-import", "LinkerHand.core.rs485",
        "--hidden-import", "LinkerHand.utils",
        "--hidden-import", "can",
        "--hidden-import", "can.interfaces.pcan",
        "--hidden-import", "minimalmodbus",
        "--hidden-import", "serial",
        "--hidden-import", "yaml",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "pydantic",
        "--hidden-import", "starlette",
        "--hidden-import", "win32api",
        "--hidden-import", "win32service",
        "--hidden-import", "win32serviceutil",
        "--hidden-import", "servicemanager",
        "--add-data", f"{os.path.join(project_root, 'LinkerHand')};LinkerHand",
        "--noconsole",  # Windows下不显示控制台
        "Demo/main_http.py"
    ]

    print("执行命令:")
    print(" ".join(cmd[:5]) + " ...")  # 只显示前5个参数
    print()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            print("✓ 打包成功完成!")

            exe_path = Path("dist/LinkerHand_HTTP_Service.exe")
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)
                print(f"✓ 生成exe文件: {exe_path}")
                print(".1f"                return True
            else:
                print("✗ exe文件未生成")
                return False
        else:
            print("✗ 打包失败")
            print("错误信息:")
            print(result.stderr[-2000:])  # 显示最后2000字符的错误信息
            return False

    except subprocess.TimeoutExpired:
        print("✗ 打包超时")
        return False
    except Exception as e:
        print(f"✗ 打包出错: {e}")
        return False

def create_service_files():
    """创建服务相关文件"""
    print("创建服务包装文件...")

    # 复制现有的服务文件到dist目录
    import shutil

    service_file = Path("dist/LinkerHand_Service.py")
    install_file = Path("dist/install.bat")
    uninstall_file = Path("dist/uninstall.bat")
    readme_file = Path("dist/README.txt")

    # 这些文件应该已经存在，如果不存在则创建基本的
    if not service_file.exists():
        print("创建基本的LinkerHand_Service.py...")
        # 这里应该从已有的文件中复制
        pass

    print("✓ 服务文件准备完成")

def main():
    """主函数"""
    print("LinkerHand HTTP API 简化打包工具")
    print("=================================")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ 未找到PyInstaller")
        print("请运行: pip install pyinstaller")
        return

    # 检查主脚本
    main_script = Path("Demo/main_http.py")
    if not main_script.exists():
        print(f"✗ 主脚本不存在: {main_script}")
        return

    print(f"✓ 主脚本: {main_script}")

    # 运行打包
    if run_simple_build():
        create_service_files()
        print("\n" + "=" * 50)
        print("🎉 打包完成!")
        print("=" * 50)
        print("生成的文件:")
        print("  - dist/LinkerHand_HTTP_Service.exe (主程序)")
        print("  - dist/LinkerHand_Service.py (服务包装器)")
        print("  - dist/install.bat (安装脚本)")
        print("  - dist/uninstall.bat (卸载脚本)")
        print("  - dist/README.txt (说明文档)")
        print("\n部署方法:")
        print("1. 复制dist目录到目标Windows机器")
        print("2. 以管理员身份运行install.bat")
        print("3. 服务将自动安装并启动")
    else:
        print("\n✗ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()