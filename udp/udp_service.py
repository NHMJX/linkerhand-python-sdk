#!/usr/bin/env python3
"""
LinkerHand UDP控制服务
通过UDP协议监听命令，启动指定的exe文件

监听端口: 8888
命令格式: "START" - 启动exe文件
响应格式: "OK" 或 "ERROR: 错误信息"
"""

import socket
import subprocess
import threading
import logging
import time
import os
from pathlib import Path

class UDPService:
    """UDP控制服务"""

    def __init__(self, host='0.0.0.0', port=8888, exe_path=None, exe_args=None):
        self.host = host
        self.port = port
        self.exe_path = exe_path or "linkerhand_service.exe"
        self.exe_args = exe_args or ["robot"]
        self.running = False
        self.server_thread = None

        # 设置日志
        logging.basicConfig(
            filename='udp_service.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def start_server(self):
        """启动UDP服务器"""
        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()
        self.logger.info(f"UDP服务已启动，监听 {self.host}:{self.port}")

    def stop_server(self):
        """停止UDP服务器"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
        self.logger.info("UDP服务已停止")

    def _server_loop(self):
        """UDP服务器主循环"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((self.host, self.port))
                sock.settimeout(1.0)  # 1秒超时，用于检查停止信号

                self.logger.info(f"UDP服务器绑定到 {self.host}:{self.port}")

                while self.running:
                    try:
                        data, addr = sock.recvfrom(1024)
                        if not self.running:
                            break

                        command = data.decode('utf-8').strip().upper()
                        self.logger.info(f"收到命令 '{command}' 来自 {addr}")

                        response = self._handle_command(command)
                        sock.sendto(response.encode('utf-8'), addr)

                    except socket.timeout:
                        continue  # 超时，继续循环
                    except Exception as e:
                        self.logger.error(f"处理UDP请求时出错: {e}")
                        try:
                            sock.sendto(f"ERROR: {str(e)}".encode('utf-8'), addr)
                        except:
                            pass

        except Exception as e:
            self.logger.error(f"UDP服务器错误: {e}")

    def _handle_command(self, command):
        """处理命令"""
        try:
            if command == "START":
                return self._start_exe()
            elif command == "STATUS":
                return "OK: Service running"
            elif command == "PING":
                return "PONG"
            else:
                return f"ERROR: Unknown command '{command}'"

        except Exception as e:
            self.logger.error(f"执行命令 '{command}' 时出错: {e}")
            return f"ERROR: {str(e)}"

    def _start_exe(self):
        """启动exe文件"""
        try:
            if not os.path.exists(self.exe_path):
                return f"ERROR: exe文件不存在: {self.exe_path}"

            # 构建命令行参数
            cmd = [self.exe_path] + self.exe_args

            self.logger.info(f"启动exe: {' '.join(cmd)}")

            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # 等待一会儿检查进程是否正常启动
            time.sleep(2)

            if process.poll() is None:
                # 进程仍在运行
                self.logger.info(f"exe启动成功，PID: {process.pid}")
                return "OK: exe started successfully"
            else:
                # 进程已退出，检查退出码
                stdout, stderr = process.communicate()
                exit_code = process.returncode
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else ""
                self.logger.error(f"exe启动失败，退出码: {exit_code}, 错误: {error_msg}")
                return f"ERROR: exe exited with code {exit_code}"

        except Exception as e:
            self.logger.error(f"启动exe时出错: {e}")
            return f"ERROR: Failed to start exe: {str(e)}"

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="LinkerHand UDP控制服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听主机地址")
    parser.add_argument("--port", type=int, default=8888, help="监听端口")
    parser.add_argument("--exe", help="exe文件路径")
    parser.add_argument("--args", nargs="*", default=["robot"], help="exe参数")

    args = parser.parse_args()

    # 创建服务
    service = UDPService(
        host=args.host,
        port=args.port,
        exe_path=args.exe,
        exe_args=args.args
    )

    print(f"启动UDP控制服务，监听 {args.host}:{args.port}")
    print(f"exe路径: {service.exe_path}")
    print(f"exe参数: {service.exe_args}")
    print("按Ctrl+C停止服务")

    try:
        service.start_server()

        # 主循环
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在停止服务...")
        service.stop_server()
        print("服务已停止")

if __name__ == "__main__":
    main()