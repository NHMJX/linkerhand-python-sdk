# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 使用相对路径，避免绝对路径问题
current_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(current_dir)  # 相对于spec文件位置的上级目录

# 确保LinkerHand目录存在
linkerhand_path = os.path.join(project_root, "LinkerHand")
if not os.path.exists(linkerhand_path):
    print(f"ERROR: LinkerHand directory not found at: {linkerhand_path}")
    sys.exit(1)

datas = [
    (linkerhand_path, "LinkerHand"),
]

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
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.protocols",
    "win32api",
    "win32service",
    "win32serviceutil",
    "servicemanager",
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
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "IPython",
        "jupyter",
        "notebook",
        "ipykernel",
        "qtconsole",
        "traitlets",
        "ipython_genutils",
        "jupyter_core",
        "jupyter_client",
        "zmq",
        "tornado",
        "ipykernel_launcher",
        "jupyterlab",
        "widgetsnbextension",
        "ipywidgets",
        "nbconvert",
        "nbformat",
        "pandocfilters",
        "testpath",
        "entrypoints",
        "defusedxml",
        "mistune",
        "send2trash",
        "terminado",
        "prometheus_client",
        "webencodings",
        "html5lib",
        "bleach",
        "pandoc",
        "jupyterlab_server",
        "notebook_shim",
    ],
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
    name="LinkerHand_HTTP_Service",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None,
)