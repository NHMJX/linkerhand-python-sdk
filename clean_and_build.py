#!/usr/bin/env python3
"""
LinkerHand HTTP API 清理并重新打包脚本
清理缓存文件并使用最兼容的方式打包
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def clean_cache():
    """清理所有缓存文件"""
    print("清理缓存文件...")

    # 清理Python缓存
    cache_dirs = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    ]

    for pattern in cache_dirs:
        if pattern.endswith("*"):
            # 使用通配符
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"✓ 删除目录: {path}")
                elif os.path.isfile(path):
                    os.remove(path)
                    print(f"✓ 删除文件: {path}")
        else:
            # 删除目录
            if os.path.exists(pattern):
                shutil.rmtree(pattern, ignore_errors=True)
                print(f"✓ 删除目录: {pattern}")

    # 清理dist和build目录
    for dir_name in ["dist", "build"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
            print(f"✓ 删除目录: {dir_name}")

    # 清理spec文件
    spec_files = ["linker_hand_standalone.spec"]
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"✓ 删除文件: {spec_file}")

    print("✓ 缓存清理完成")

def check_environment():
    """检查打包环境"""
    print("检查打包环境...")

    # 检查Python版本
    print(f"✓ Python版本: {sys.version}")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller未安装")
        print("请运行: pip install pyinstaller pywin32")
        return False

    # 检查主脚本
    main_script = Path("Demo/main_http.py")
    if not main_script.exists():
        print(f"✗ 主脚本不存在: {main_script}")
        return False
    print(f"✓ 主脚本存在: {main_script}")

    # 检查LinkerHand模块
    linkerhand_path = Path("LinkerHand")
    if not linkerhand_path.exists():
        print(f"✗ LinkerHand模块不存在: {linkerhand_path}")
        return False
    print(f"✓ LinkerHand模块存在: {linkerhand_path}")

    return True

def build_minimal():
    """使用最少的选项进行打包"""
    print("使用最小化配置打包...")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 生成单文件
        "--name", "LinkerHand_HTTP_Service",
        "--hidden-import", "LinkerHand.linker_hand_api",
        "--hidden-import", "LinkerHand.core.can",
        "--hidden-import", "LinkerHand.core.rs485",
        "--hidden-import", "LinkerHand.utils",
        "--hidden-import", "can",
        "--hidden-import", "minimalmodbus",
        "--hidden-import", "serial",
        "--hidden-import", "yaml",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "pydantic",
        "--add-data", f"{os.path.join(project_root, 'LinkerHand')};LinkerHand",
        "--noconsole",  # Windows下不显示控制台
        "Demo/main_http.py"
    ]

    print("执行最小化打包命令...")
    print(f"工作目录: {os.getcwd()}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            exe_path = Path("dist/LinkerHand_HTTP_Service.exe")
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)
                print("✓ 最小化打包成功!")
                print(".1f")
                return True
            else:
                print("✗ exe文件未生成")
                return False
        else:
            print("✗ 最小化打包失败")
            print("错误信息:")
            print(result.stderr[-2000:])
            return False

    except subprocess.TimeoutExpired:
        print("✗ 打包超时")
        return False
    except Exception as e:
        print(f"✗ 打包出错: {e}")
        return False

def create_fallback_exe():
    """创建备用的exe文件（如果PyInstaller完全失败）"""
    print("创建备用的批处理包装器...")

    # 创建一个批处理文件来启动Python脚本
    # 这不是真正的exe，但可以在有Python的环境中工作
    batch_content = '''@echo off
REM LinkerHand HTTP API 备用的批处理启动器
REM 如果PyInstaller打包失败，可以使用这个备选方案

echo LinkerHand HTTP API 启动器
echo ========================

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python
    echo 请安装Python 3.8+
    pause
    exit /b 1
)

REM 切换到正确的目录
cd /d "%~dp0"

REM 启动HTTP服务
echo 启动LinkerHand HTTP API服务...
python Demo\\main_http.py

pause
'''

    exe_path = Path("dist/LinkerHand_HTTP_Service.exe")
    with open(exe_path, 'w', encoding='utf-8') as f:
        f.write("# 这是一个备用的批处理包装器\n")
        f.write("# 如果PyInstaller打包失败，请手动安装Python并运行此文件\n")
        f.write("python Demo/main_http.py\n")

    batch_path = Path("dist/LinkerHand_HTTP_Service.bat")
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)

    print("✓ 创建了备用的批处理启动器")
    print("注意: 这需要目标机器安装Python")

    return True

def main():
    """主函数"""
    print("LinkerHand HTTP API 清理并重新打包工具")
    print("=" * 50)

    # 清理缓存
    clean_cache()

    # 检查环境
    if not check_environment():
        print("环境检查失败，请修复问题后重试")
        return

    # 尝试最小化打包
    if build_minimal():
        print("\n🎉 打包成功!")
        print("现在可以运行以下命令测试:")
        print("  python dist/LinkerHand_Service.py --help")
    else:
        print("\n⚠️  PyInstaller打包失败，创建备选方案...")
        create_fallback_exe()

        print("\n备选方案说明:")
        print("1. 目标机器需要安装Python 3.8+")
        print("2. 双击 LinkerHand_HTTP_Service.bat 启动服务")
        print("3. 或手动运行: python Demo/main_http.py")

    # 创建服务文件
    print("\n创建服务相关文件...")
    # 这里会调用之前创建的函数
    from build_standalone import create_service_wrapper, create_installer, create_readme

    try:
        create_service_wrapper()
        create_installer()
        create_readme()
        print("✓ 服务文件创建完成")
    except Exception as e:
        print(f"⚠️ 服务文件创建失败: {e}")

    print("\n" + "=" * 50)
    print("处理完成!")
    print("=" * 50)
    print("检查 dist/ 目录中的文件")
    print("如有问题，请查看上面的错误信息")

if __name__ == "__main__":
    main()