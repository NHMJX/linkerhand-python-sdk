# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - LinkerHand HTTP API服务
用于打包成独立的可执行文件
"""

import os
import sys

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# 数据文件：包含配置文件
datas = [
    (os.path.join(project_root, 'LinkerHand', 'config'), 'LinkerHand/config'),
]

# 隐藏导入：PyInstaller可能无法自动检测到的模块
hiddenimports = [
    # FastAPI相关
    'uvicorn',
    'fastapi',
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.types',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.logging',
    'uvicorn.server',
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.middleware',
    'starlette.responses',
    'starlette.requests',
    # CAN和Modbus相关
    'pythoncan',
    'pythoncan.candle',
    'can',
    'can.interfaces',
    'can.interfaces.pcan',
    'can.interfaces.candle',
    'can.exceptions',
    'minimalmodbus',
    'pymodbus',
    'pymodbus.client',
    'pymodbus.client.sync',
    'pymodbus.client.tcp',
    'pymodbus.client.udp',
    'pymodbus.client.serial',
    'pymodbus.exceptions',
    'pyserial',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    # YAML相关
    'yaml',
    'PyYAML',
    # LinkerHand包及其子模块
    'LinkerHand',
    'LinkerHand.linker_hand_api',
    'LinkerHand.utils',
    'LinkerHand.utils.mapping',
    'LinkerHand.utils.color_msg',
    'LinkerHand.utils.load_write_yaml',
    'LinkerHand.utils.open_can',
    'LinkerHand.utils.init_linker_hand',
    'LinkerHand.core',
    'LinkerHand.core.can',
    'LinkerHand.core.can.linker_hand_g20_can',
    'LinkerHand.core.can.linker_hand_l10_can',
    'LinkerHand.core.can.linker_hand_l20_can',
    'LinkerHand.core.can.linker_hand_l21_can',
    'LinkerHand.core.can.linker_hand_l24_can',
    'LinkerHand.core.can.linker_hand_l25_can',
    'LinkerHand.core.can.linker_hand_l6_can',
    'LinkerHand.core.can.linker_hand_l7_can',
    'LinkerHand.core.can.linker_hand_o6_can',
    'LinkerHand.core.rs485',
    'LinkerHand.core.rs485.linker_hand_l10_rs485',
    'LinkerHand.core.rs485.linker_hand_l6_rs485',
    'LinkerHand.core.rs485.linker_hand_l7_rs485',
    'LinkerHand.core.rs485.linker_hand_o6_rs485',
    # 其他可能需要的模块
    'numpy',
    'enum',
    'threading',
    'struct',
    'logging',
]

a = Analysis(
    [os.path.join(project_root, 'Demo', 'main_http.py')],
    pathex=[
        project_root,
        os.path.join(project_root, 'LinkerHand'),
        os.path.join(project_root, 'Demo'),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(project_root, 'runtime_hook.py')],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='linkerhand_service',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无窗口模式，后台运行
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)
