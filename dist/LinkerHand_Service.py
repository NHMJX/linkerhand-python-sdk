#!/usr/bin/env python3
"""
LinkerHand HTTP API Windows服务包装器
"""

import win32serviceutil, win32service, win32event, servicemanager
import sys, os, subprocess, time, logging
from pathlib import Path

class LinkerHandService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LinkerHandHTTPAPI"
    _svc_display_name_ = "LinkerHand HTTP API Service"
    _svc_description_ = "LinkerHand机械手控制HTTP API服务 - 开机自启动"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.service_dir = Path(__file__).parent
        self.exe_path = self.service_dir / "LinkerHand_HTTP_Service.exe"

        log_path = self.service_dir / "service.log"
        logging.basicConfig(filename=str(log_path), level=logging.INFO,
                          format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def SvcStop(self):
        self.logger.info("收到停止服务请求")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        if self.process and self.process.poll() is None:
            self.logger.info("正在停止HTTP服务器...")
            try:
                self.process.terminate()
                for _ in range(10):
                    if self.process.poll() is not None: break
                    time.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
                    self.logger.info("强制终止HTTP服务器")
            except Exception as e:
                self.logger.error(f"停止进程时出错: {e}")

    def SvcDoRun(self):
        self.logger.info("启动LinkerHand HTTP API服务")

        try:
            if not self.exe_path.exists():
                raise FileNotFoundError(f"找不到可执行文件: {self.exe_path}")

            self.logger.info(f"启动HTTP服务器: {self.exe_path}")
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                cwd=str(self.service_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            while True:
                if self.process.poll() is not None:
                    exit_code = self.process.returncode
                    self.logger.error(f"HTTP服务器异常退出，退出码: {exit_code}")
                    if exit_code != 0:
                        self.logger.info("等待5秒后重启服务...")
                        time.sleep(5)
                        self.process = subprocess.Popen(
                            [str(self.exe_path)],
                            cwd=str(self.service_dir),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        break

                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if result == win32event.WAIT_OBJECT_0: break

        except Exception as e:
            self.logger.error(f"服务运行出错: {str(e)}")
            raise

        self.logger.info("LinkerHand HTTP API服务已停止")

def main():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LinkerHandService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LinkerHandService)

if __name__ == "__main__":
    main()