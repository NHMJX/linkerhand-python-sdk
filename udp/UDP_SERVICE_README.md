# LinkerHand UDP控制服务

这是一个开机自启动的UDP控制服务，用于通过UDP协议远程启动指定的exe文件。

## 功能特性

- 🔄 **开机自启动**: 安装为Windows服务，开机自动启动
- 📡 **UDP控制**: 通过UDP协议监听命令，无需复杂网络配置
- ⚡ **快速启动**: 接收命令后立即启动exe文件
- 🔒 **安全隔离**: 运行在系统服务账户下
- 📝 **详细日志**: 记录所有操作和错误信息

## 文件说明

- `udp_service.py` - UDP服务器核心逻辑
- `udp_windows_service.py` - Windows服务包装器
- `install_udp_service.bat` - 服务安装脚本
- `test_udp_client.py` - 测试客户端
- `UDP_SERVICE_README.md` - 本说明文档

## 安装步骤

### 1. 准备工作

确保系统中已安装：
- Python 3.8+
- pywin32 (`pip install pywin32`)
- 目标exe文件（默认为 `linkerhand_service.exe`）

### 2. 配置（可选）

可以通过环境变量自定义配置：

```batch
# 设置exe文件路径
set LINKERHAND_EXE_PATH=C:\path\to\your\app.exe

# 设置exe参数（空格分隔）
set LINKERHAND_EXE_ARGS=robot --verbose

# 设置UDP监听端口
set UDP_PORT=9999

# 设置监听地址（默认0.0.0.0监听所有接口）
set UDP_HOST=192.168.1.100
```

### 3. 安装服务

右键点击 `install_udp_service.bat`，选择"以管理员身份运行"。

安装过程会：
- 检查系统环境
- 配置防火墙规则
- 安装并启动Windows服务
- 验证服务状态

## 使用方法

### UDP命令协议

服务监听UDP端口8888（可配置），支持以下命令：

| 命令 | 描述 | 响应示例 |
|------|------|----------|
| `START` | 启动exe文件 | `OK: exe started successfully` |
| `STATUS` | 查询服务状态 | `OK: Service running` |
| `PING` | 测试连接 | `PONG` |

### 发送UDP命令

#### Python客户端

```python
import socket

def send_udp_command(host='127.0.0.1', port=8888, command='START'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(command.encode('utf-8'), (host, port))

    # 接收响应
    data, addr = sock.recvfrom(1024)
    response = data.decode('utf-8')
    print(f"响应: {response}")

    sock.close()

# 启动exe文件
send_udp_command(command='START')
```

#### 其他语言示例

**C++ (使用winsock):**
```cpp
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    SOCKET sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

    sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_port = htons(8888);
    inet_pton(AF_INET, "127.0.0.1", &server.sin_addr);

    const char* command = "START";
    sendto(sock, command, strlen(command), 0, (sockaddr*)&server, sizeof(server));

    char buffer[1024];
    int len = recvfrom(sock, buffer, sizeof(buffer), 0, NULL, NULL);
    buffer[len] = '\0';
    std::cout << "响应: " << buffer << std::endl;

    closesocket(sock);
    WSACleanup();
    return 0;
}
```

**PowerShell:**
```powershell
$udpClient = New-Object System.Net.Sockets.UdpClient
$udpClient.Connect("127.0.0.1", 8888)

$command = [System.Text.Encoding]::UTF8.GetBytes("START")
$udpClient.Send($command, $command.Length)

$remoteEndPoint = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, 0)
$receivedBytes = $udpClient.Receive([ref]$remoteEndPoint)
$response = [System.Text.Encoding]::UTF8.GetString($receivedBytes)

Write-Host "响应: $response"

$udpClient.Close()
```

### 测试服务

运行测试客户端：

```bash
# 交互模式
python test_udp_client.py --interactive

# 单次命令
python test_udp_client.py --command START

# 默认测试
python test_udp_client.py
```

## 服务管理

### Windows服务命令

```batch
# 查看服务状态
sc query LinkerHandUDPService

# 启动服务
sc start LinkerHandUDPService

# 停止服务
sc stop LinkerHandUDPService

# 重启服务
sc stop LinkerHandUDPService && sc start LinkerHandUDPService

# 卸载服务
sc stop LinkerHandUDPService
sc delete LinkerHandUDPService
```

### 服务日志

服务运行日志保存在 `udp_service.log` 文件中，包含：
- 服务启动/停止记录
- UDP命令接收记录
- exe启动结果
- 错误信息

## 故障排除

### 常见问题

**1. 服务安装失败**
- 确保以管理员身份运行安装脚本
- 检查Python环境和pywin32安装

**2. UDP连接失败**
- 检查防火墙设置
- 确认服务正在运行
- 验证端口号配置

**3. exe启动失败**
- 检查exe文件路径和权限
- 查看服务日志中的错误信息
- 确认exe文件存在且可执行

**4. 服务无法启动**
- 查看Windows事件查看器
- 检查服务日志文件
- 验证环境变量配置

### 调试模式

临时运行UDP服务进行调试：

```bash
# 前台运行（非服务模式）
python udp_service.py --host 0.0.0.0 --port 8888 --exe linkerhand_service.exe --args robot
```

## 安全注意事项

- UDP服务监听所有网络接口，建议在安全网络环境中使用
- exe文件执行需要适当权限
- 考虑添加身份验证机制（如命令签名）
- 定期检查服务日志

## 技术规格

- **协议**: UDP/IPv4
- **端口**: 8888（可配置）
- **编码**: UTF-8
- **超时**: 5秒（客户端）
- **平台**: Windows 10/11
- **Python**: 3.8+

## 许可证

本项目遵循相应的开源许可证。