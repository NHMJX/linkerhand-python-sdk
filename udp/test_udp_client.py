#!/usr/bin/env python3
"""
LinkerHand UDP控制服务测试客户端
用于测试UDP服务是否正常工作
"""

import socket
import time
import sys
import argparse

class UDPClient:
    """UDP测试客户端"""

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)  # 5秒超时

    def send_command(self, command):
        """发送命令并接收响应"""
        try:
            # 发送命令
            self.sock.sendto(command.encode('utf-8'), (self.host, self.port))

            # 接收响应
            data, addr = self.sock.recvfrom(1024)
            response = data.decode('utf-8')

            return True, response

        except socket.timeout:
            return False, "超时：服务无响应"
        except Exception as e:
            return False, f"错误：{str(e)}"

    def close(self):
        """关闭连接"""
        self.sock.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LinkerHand UDP控制服务测试客户端")
    parser.add_argument("--host", default="127.0.0.1", help="服务主机地址")
    parser.add_argument("--port", type=int, default=8888, help="服务端口")
    parser.add_argument("--command", help="要发送的命令 (START/STATUS/PING)")
    parser.add_argument("--interactive", action="store_true", help="进入交互模式")

    args = parser.parse_args()

    client = UDPClient(args.host, args.port)

    try:
        if args.interactive:
            # 交互模式
            print(f"连接到UDP服务: {args.host}:{args.port}")
            print("可用命令: START, STATUS, PING, QUIT")
            print("-" * 50)

            while True:
                try:
                    command = input("命令> ").strip().upper()
                    if command in ['QUIT', 'EXIT', 'Q']:
                        break

                    if command not in ['START', 'STATUS', 'PING']:
                        print("无效命令，可用: START, STATUS, PING")
                        continue

                    print(f"发送: {command}")
                    success, response = client.send_command(command)
                    if success:
                        print(f"响应: {response}")
                    else:
                        print(f"错误: {response}")

                except KeyboardInterrupt:
                    print("\n退出...")
                    break
                except EOFError:
                    break

        elif args.command:
            # 单次命令模式
            command = args.command.upper()
            if command not in ['START', 'STATUS', 'PING']:
                print("无效命令，可用: START, STATUS, PING")
                return 1

            print(f"发送命令: {command} 到 {args.host}:{args.port}")
            success, response = client.send_command(command)
            if success:
                print(f"响应: {response}")
                return 0
            else:
                print(f"错误: {response}")
                return 1

        else:
            # 默认测试模式
            print("LinkerHand UDP控制服务测试")
            print(f"目标: {args.host}:{args.port}")
            print("-" * 50)

            # 测试连接
            print("1. 测试连接 (PING)...")
            success, response = client.send_command("PING")
            if success and response == "PONG":
                print("   ✅ 连接正常")
            else:
                print(f"   ❌ 连接失败: {response}")
                return 1

            # 测试状态
            print("2. 查询服务状态...")
            success, response = client.send_command("STATUS")
            if success:
                print(f"   ✅ 状态: {response}")
            else:
                print(f"   ❌ 状态查询失败: {response}")
                return 1

            # 询问是否启动exe
            print("3. 启动exe文件测试...")
            try:
                choice = input("   是否启动exe文件? (y/N): ").strip().lower()
                if choice == 'y' or choice == 'yes':
                    success, response = client.send_command("START")
                    if success:
                        print(f"   ✅ {response}")
                    else:
                        print(f"   ❌ {response}")
                        return 1
                else:
                    print("   ⏭️  跳过启动测试")
            except KeyboardInterrupt:
                print("   ⏭️  跳过启动测试")

            print("-" * 50)
            print("✅ 所有测试通过！")
            return 0

    except Exception as e:
        print(f"测试出错: {e}")
        return 1
    finally:
        client.close()

if __name__ == "__main__":
    exit(main())