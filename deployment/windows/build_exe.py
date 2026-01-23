#!/usr/bin/env python3
"""
LinkerHand HTTP API Windows打包脚本
使用PyInstaller将Python应用打包成exe文件
"""

import os
import sys
import subprocess
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(SPEC))

# 定义需要包含的数据文件
datas = [
    # 包含LinkerHand包
    (os.path.join(project_root, "LinkerHand"), "LinkerHand"),
    # 包含配置文件
    (os.path.join(project_root, "LinkerHand", "config"), "LinkerHand/config"),
]

# 定义需要包含的隐藏导入
hiddenimports = [
    "LinkerHand.linker_hand_api",
    "LinkerHand.core.can",
    "LinkerHand.core.rs485",
    "LinkerHand.utils",
    "can",
    "can.interfaces.pcan",
    "minimalmodbus",
    "serial",
    "yaml",
    "fastapi",
    "uvicorn",
    "pydantic",
    "starlette",
]

a = Analysis(
    ["Demo/main_http.py"],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LinkerHand_HTTP_API",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    with open('linker_hand_http.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建了 linker_hand_http.spec 文件")

def run_pyinstaller():
    """运行PyInstaller打包"""
    print("正在打包应用...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "linker_hand_http.spec"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ 打包成功完成!")
        print("生成的文件位于: dist/LinkerHand_HTTP_API.exe")
    else:
        print("✗ 打包失败:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

def main():
    """主函数"""
    print("LinkerHand HTTP API Windows打包工具")
    print("=" * 40)

    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller未安装，请运行: pip install pyinstaller")
        sys.exit(1)

    # 创建spec文件
    create_spec_file()

    # 运行打包
    run_pyinstaller()

    print("\n打包完成！")
    print("下一步: 运行 install_service.py 来安装Windows服务")

if __name__ == "__main__":
    main()