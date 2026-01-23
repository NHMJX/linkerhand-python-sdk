#!/usr/bin/env python3
"""
测试打包结果的脚本
检查dist目录中的文件是否完整
"""

import os
from pathlib import Path

def test_build_result():
    """测试打包结果"""
    print("测试LinkerHand HTTP API打包结果")
    print("=" * 40)

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist目录不存在，请先运行打包脚本")
        return False

    required_files = [
        "LinkerHand_HTTP_Service.exe",
        "LinkerHand_Service.py",
        "install.bat",
        "uninstall.bat",
        "README.txt"
    ]

    missing_files = []
    for file_name in required_files:
        file_path = dist_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_name} ({size} bytes)")
        else:
            print(f"❌ {file_name} (缺失)")
            missing_files.append(file_name)

    if missing_files:
        print(f"\n❌ 缺少 {len(missing_files)} 个文件: {', '.join(missing_files)}")
        return False

    # 检查exe文件大小
    exe_path = dist_dir / "LinkerHand_HTTP_Service.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        if size_mb < 10:
            print(f"\n⚠️  exe文件较小 ({size_mb:.1f}MB)，可能是占位符文件")
            print("   建议重新运行打包脚本生成真正的exe文件")
        else:
            print(".1f"
    print("\n✅ 所有文件检查通过!")
    print("\n📦 部署说明:")
    print("1. 复制整个 dist/ 目录到目标Windows机器")
    print("2. 以管理员身份运行 install.bat")
    print("3. 等待安装完成，服务将自动启动")
    print("4. 访问 http://localhost:8000 使用API")

    return True

def show_usage():
    """显示使用说明"""
    print("\n🔧 打包脚本说明:")
    print("python build_standalone.py    # 标准打包（推荐）")
    print("python build_simple.py        # 简化打包")
    print("python clean_and_build.py     # 清理后重新打包")

    print("\n📖 故障排除:")
    print("- 如果spec文件报错，使用 build_simple.py")
    print("- 如果仍有问题，使用 clean_and_build.py")

if __name__ == "__main__":
    success = test_build_result()
    show_usage()

    if not success:
        print("\n❌ 打包结果不完整，请检查上面的错误信息")
        exit(1)
    else:
        print("\n🎉 打包结果完整，可以进行部署!")