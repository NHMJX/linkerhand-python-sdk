#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将LinkerHand HTTP API服务打包成可执行文件
"""

import os
import sys
import shutil
import subprocess

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理spec文件生成的缓存
    if os.path.exists('linkerhand_service.spec'):
        print("保留spec文件")

def build_exe():
    """使用PyInstaller打包"""
    print("=" * 60)
    print("开始打包 LinkerHand HTTP API 服务")
    print("=" * 60)
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: 未安装PyInstaller")
        print("请运行: pip install PyInstaller")
        return False
    
    # 清理之前的构建
    clean_build_dirs()
    
    # 执行打包
    spec_file = 'linkerhand_service.spec'
    if not os.path.exists(spec_file):
        print(f"错误: 找不到spec文件: {spec_file}")
        return False
    
    print(f"\n使用spec文件: {spec_file}")
    print("开始打包，这可能需要几分钟...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', spec_file, '--clean', '--noconfirm'],
            check=True,
            capture_output=False
        )
        
        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        
        # 复制服务管理脚本到dist文件夹
        print("\n正在复制服务管理脚本...")
        scripts_dir = 'dist_scripts'
        dist_dir = 'dist'
        
        if os.path.exists(scripts_dir):
            scripts_to_copy = [
                'start_service.bat',
                'stop_service.bat',
                'restart_service.bat',
                'uninstall_service.bat',
                'deploy.bat'
            ]
            
            for script in scripts_to_copy:
                src = os.path.join(scripts_dir, script)
                dst = os.path.join(dist_dir, script)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"  ✓ 已复制: {script}")
                else:
                    print(f"  ✗ 未找到: {script}")
        else:
            print("  警告: 未找到 dist_scripts 目录")
        
        # 创建README.txt
        readme_content = """LinkerHand HTTP API 服务 - 部署包
========================================

文件说明:
  - linkerhand_service.exe: 主程序
  - deploy.bat: 一键部署脚本（右键以管理员身份运行）
  - start_service.bat: 启动服务
  - stop_service.bat: 停止服务
  - restart_service.bat: 重启服务
  - uninstall_service.bat: 卸载服务（删除开机自启动）

快速部署:
  1. 右键点击 deploy.bat
  2. 选择"以管理员身份运行"
  3. 按照提示完成安装

服务管理:
  启动: start_service.bat
  停止: stop_service.bat
  重启: restart_service.bat
  卸载: uninstall_service.bat

验证安装:
  重启电脑后，访问 http://localhost:8000

日志说明:
  - 日志文件保存在 logs/ 目录下
  - 日志文件按日期命名: linkerhand_service_YYYYMMDD.log
  - 每个日志文件最大10MB，保留5个备份
  - 服务在后台运行，不会弹出窗口
"""
        readme_path = os.path.join(dist_dir, 'README.txt')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"  ✓ 已创建: README.txt")
        
        print(f"\n可执行文件位置: {os.path.abspath('dist/linkerhand_service.exe')}")
        print("\n部署说明:")
        print("1. 将整个 dist 文件夹复制到目标电脑")
        print("2. 在目标电脑上运行 deploy.bat（以管理员身份）")
        print("3. 服务将在用户登录后自动启动")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        return False
    except Exception as e:
        print(f"\n发生错误: {e}")
        return False

if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
