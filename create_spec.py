#!/usr/bin/env python3
"""
创建PyInstaller spec文件的Python脚本
"""

import os

def create_spec_file():
    """创建PyInstaller spec文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    linkerhand_path = os.path.join(project_root, "LinkerHand")

    if not os.path.exists(linkerhand_path):
        print(f'ERROR: LinkerHand directory not found at: {linkerhand_path}')
        return False

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

current_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(current_dir)
linkerhand_path = os.path.join(project_root, 'LinkerHand')

if not os.path.exists(linkerhand_path):
    print(f'ERROR: LinkerHand directory not found at: {{linkerhand_path}}')
    sys.exit(1)

datas = [(linkerhand_path, 'LinkerHand')]

hiddenimports = [
    'LinkerHand.linker_hand_api',
    'LinkerHand.core.can',
    'LinkerHand.core.rs485',
    'LinkerHand.utils',
    'can',
    'can.interfaces.pcan',
    'minimalmodbus',
    'serial',
    'yaml',
    'fastapi',
    'uvicorn',
    'pydantic',
    'starlette',
    'win32api',
    'win32service',
    'win32serviceutil',
    'servicemanager',
]

a = Analysis(
    ['Demo/main_http.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'PIL', 'PyQt5', 'IPython'],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LinkerHand_HTTP_Service',
    debug=False,
    console=False,
    upx=True,
)
'''

    spec_file = os.path.join(current_dir, 'linker_hand_standalone.spec')
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print('spec文件创建完成')
    return True

if __name__ == "__main__":
    create_spec_file()