#!/usr/bin/env python3
"""
LinkerHand HTTP API Windows服务包装器
使用pywin32将FastAPI应用包装成Windows服务
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess
import time
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    filename='C:\\LinkerHand_HTTP_API\\service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LinkerHandService(win32serviceutil.ServiceFramework):
    """LinkerHand HTTP API Windows服务"""

    _svc_name_ = "LinkerHandHTTPAPI"
    _svc_display_name_ = "LinkerHand HTTP API Service"
    _svc_description_ = "LinkerHand机械手控制HTTP API服务"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.logger = logging.getLogger(__name__)

        # 获取服务所在目录
        self.service_dir = Path(__file__).parent
        self.exe_path = self.service_dir / "dist" / "LinkerHand_HTTP_API.exe"

    def SvcStop(self):
        """停止服务"""
        self.logger.info("收到停止服务请求")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # 停止子进程
        if self.process and self.process.poll() is None:
            self.logger.info("正在停止HTTP服务器...")
            self.process.terminate()

            # 等待最多10秒
            for _ in range(10):
                if self.process.poll() is not None:
                    break
                time.sleep(1)

            # 如果还没停止，强制终止
            if self.process.poll() is None:
                self.process.kill()
                self.logger.info("强制终止HTTP服务器")

    def SvcDoRun(self):
        """运行服务"""
        self.logger.info("启动LinkerHand HTTP API服务")

        try:
            # 检查exe文件是否存在
            if not self.exe_path.exists():
                raise FileNotFoundError(f"找不到可执行文件: {self.exe_path}")

            # 启动HTTP服务器
            self.logger.info(f"启动HTTP服务器: {self.exe_path}")
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                cwd=str(self.service_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # 等待停止事件
            while True:
                # 检查进程是否还在运行
                if self.process.poll() is not None:
                    self.logger.error(f"HTTP服务器异常退出，退出码: {self.process.returncode}")
                    # 读取错误输出
                    stdout, stderr = self.process.communicate()
                    if stdout:
                        self.logger.error(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                    if stderr:
                        self.logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                    break

                # 检查停止事件
                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)  # 1秒超时
                if result == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            self.logger.error(f"服务运行出错: {str(e)}")
            raise

        self.logger.info("LinkerHand HTTP API服务已停止")

def main():
    """主函数"""
    if len(sys.argv) == 1:
        # 作为服务运行
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LinkerHandService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # 处理命令行参数
        win32serviceutil.HandleCommandLine(LinkerHandService)

if __name__ == '__main__':
    main()