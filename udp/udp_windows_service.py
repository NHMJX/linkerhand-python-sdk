#!/usr/bin/env python3
"""
LinkerHand UDP控制服务的Windows服务包装器
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

class LinkerHandUDPService(win32serviceutil.ServiceFramework):
    """LinkerHand UDP控制服务"""

    _svc_name_ = "LinkerHandUDPService"
    _svc_display_name_ = "LinkerHand UDP Control Service"
    _svc_description_ = "LinkerHand UDP控制服务 - 监听UDP命令启动exe文件"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.udp_service = None

        # 获取服务所在目录
        self.service_dir = Path(__file__).parent

        # 设置日志
        log_path = self.service_dir / "udp_service.log"
        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def SvcStop(self):
        """停止服务"""
        self.logger.info("收到停止服务请求")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # 停止UDP服务
        if self.udp_service:
            self.logger.info("正在停止UDP服务...")
            self.udp_service.stop_server()
            self.logger.info("UDP服务已停止")

    def SvcDoRun(self):
        """运行服务"""
        self.logger.info("启动LinkerHand UDP控制服务")

        try:
            # 导入UDP服务
            from udp_service import UDPService

            # 配置UDP服务
            exe_path = os.environ.get('LINKERHAND_EXE_PATH', 'linkerhand_service.exe')
            exe_args_str = os.environ.get('LINKERHAND_EXE_ARGS', 'robot')
            exe_args = exe_args_str.split() if exe_args_str else ['robot']

            host = os.environ.get('UDP_HOST', '0.0.0.0')
            port = int(os.environ.get('UDP_PORT', '8888'))

            self.logger.info(f"配置: exe={exe_path}, args={exe_args}, listen={host}:{port}")

            # 创建并启动UDP服务
            self.udp_service = UDPService(
                host=host,
                port=port,
                exe_path=exe_path,
                exe_args=exe_args
            )

            self.udp_service.start_server()

            # 等待停止事件
            while True:
                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)  # 1秒超时
                if result == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            self.logger.error(f"服务运行出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

        self.logger.info("LinkerHand UDP控制服务已停止")

def main():
    """主函数"""
    if len(sys.argv) == 1:
        # 作为服务运行
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LinkerHandUDPService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # 处理命令行参数
        win32serviceutil.HandleCommandLine(LinkerHandUDPService)

if __name__ == '__main__':
    main()