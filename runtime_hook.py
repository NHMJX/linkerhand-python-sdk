# -*- coding: utf-8 -*-
"""
PyInstaller运行时钩子
修复打包后的模块导入路径问题
"""

import sys
import os

# 获取可执行文件所在目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    base_path = sys._MEIPASS
    
    # 添加项目根目录到路径（最重要，必须最先添加）
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # 添加LinkerHand目录到路径
    linkerhand_path = os.path.join(base_path, 'LinkerHand')
    if os.path.exists(linkerhand_path):
        if linkerhand_path not in sys.path:
            sys.path.insert(0, linkerhand_path)
        
        # 添加utils目录（用于相对导入，如 from utils.open_can import OpenCan）
        utils_path = os.path.join(linkerhand_path, 'utils')
        if os.path.exists(utils_path):
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
        
        # 添加core目录
        core_path = os.path.join(linkerhand_path, 'core')
        if os.path.exists(core_path):
            if core_path not in sys.path:
                sys.path.insert(0, core_path)
            
            # 添加can目录（用于相对导入）
            can_path = os.path.join(core_path, 'can')
            if os.path.exists(can_path):
                if can_path not in sys.path:
                    sys.path.insert(0, can_path)
            
            # 添加rs485目录（用于相对导入）
            rs485_path = os.path.join(core_path, 'rs485')
            if os.path.exists(rs485_path):
                if rs485_path not in sys.path:
                    sys.path.insert(0, rs485_path)
    
    # 为了确保相对导入能工作，还需要将LinkerHand的父目录也加入路径
    # 这样 from utils.xxx 就能在LinkerHand目录下找到utils
    # 实际上，由于我们已经添加了LinkerHand目录，from utils.xxx应该能工作
    # 但为了保险，我们还需要确保在core/can目录下也能找到utils
    # 方法是将LinkerHand目录添加到路径，这样无论在哪里，from utils都能找到
