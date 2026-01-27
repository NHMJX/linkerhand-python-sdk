# LinkerHand UDP控制服务 - 快速开始

## 📁 文件说明

- `udp_service.py` - UDP服务核心
- `udp_windows_service.py` - Windows服务包装器
- `install_udp_service.bat` - 安装服务脚本
- `uninstall_udp_service.bat` - 卸载服务脚本
- `test_udp_client.py` - 测试客户端
- `start_udp_test.bat` - 测试启动脚本
- `UDP_SERVICE_README.md` - 详细文档

## 🚀 快速使用

### 1. 安装服务
```bash
# 以管理员身份运行
install_udp_service.bat
```

### 2. 测试服务
```bash
# 运行测试客户端
python test_udp_client.py
```

### 3. 发送UDP命令
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"START", ("127.0.0.1", 8888))
response, _ = sock.recvfrom(1024)
print(response.decode())
```

## 📋 更多信息

详细使用说明请查看 `UDP_SERVICE_README.md`