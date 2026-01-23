# LinkerHand HTTP API Windows部署指南

本指南介绍如何将LinkerHand HTTP API服务打包并部署为Windows开机自启动服务。

## 系统要求

- Windows 10/11 (64位)
- Python 3.8+
- 管理员权限（用于安装服务）
- PCAN设备驱动（用于CAN通信）

## 部署步骤

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi, uvicorn, win32service; print('依赖安装成功')"
```

### 2. 构建可执行文件

```bash
# 运行打包脚本
python build_exe.py
```

此脚本将：
- 创建PyInstaller配置文件 (`linker_hand_http.spec`)
- 将Python应用打包成单个exe文件
- 输出文件位于 `dist/LinkerHand_HTTP_API.exe`

### 3. 安装Windows服务

**重要：必须以管理员身份运行**

```bash
# 以管理员身份打开命令提示符或PowerShell
# 切换到项目目录

# 安装并启动服务
python install_service.py install
```

安装过程将：
- 创建安装目录 `C:\LinkerHand_HTTP_API`
- 复制必要文件到安装目录
- 安装Windows服务
- 启动服务
- 添加到开机自启动

### 4. 验证安装

```bash
# 检查服务状态
sc query LinkerHandHTTPAPI

# 查看服务日志
type C:\LinkerHand_HTTP_API\service.log

# 测试API
curl http://localhost:8000/
curl http://localhost:8000/health
```

## 文件说明

### 构建文件
- `build_exe.py` - PyInstaller打包脚本
- `linker_hand_http.spec` - PyInstaller配置文件（自动生成）
- `dist/LinkerHand_HTTP_API.exe` - 打包后的可执行文件

### 服务文件
- `windows_service.py` - Windows服务包装器
- `install_service.py` - 服务安装/卸载脚本

### 安装目录
```
C:\LinkerHand_HTTP_API\
├── LinkerHand_HTTP_API.exe    # 主程序
├── windows_service.py         # 服务脚本
├── requirements.txt           # 依赖列表
├── service.log               # 服务日志
└── README.md
```

## 服务管理

### 手动控制服务

```bash
# 启动服务
sc start LinkerHandHTTPAPI

# 停止服务
sc stop LinkerHandHTTPAPI

# 重启服务
sc stop LinkerHandHTTPAPI
sc start LinkerHandHTTPAPI

# 查看服务状态
sc query LinkerHandHTTPAPI

# 查看服务配置
sc qc LinkerHandHTTPAPI
```

### 通过服务管理器管理

1. 按 `Win + R`，输入 `services.msc`
2. 找到 "LinkerHand HTTP API Service"
3. 右键选择启动/停止/重启

## 故障排除

### 服务启动失败

1. 检查日志文件：`C:\LinkerHand_HTTP_API\service.log`
2. 确认PCAN设备已连接且驱动已安装
3. 检查端口8000是否被占用
4. 确认防火墙允许端口8000访问

### API访问失败

1. 确认服务正在运行
2. 检查防火墙设置
3. 尝试本地访问：`http://localhost:8000`
4. 检查网络配置

### 日志位置

- 服务日志：`C:\LinkerHand_HTTP_API\service.log`
- Windows事件查看器：应用程序和服务日志 → LinkerHandHTTPAPI

## 卸载

```bash
# 以管理员身份运行
python install_service.py uninstall
```

卸载过程将：
- 停止并卸载服务
- 从开机自启动中移除
- 删除安装目录

## 高级配置

### 修改服务端口

编辑 `main_http.py` 中的端口配置：

```python
if __name__ == "__main__":
    uvicorn.run(
        "main_http:app",
        host="0.0.0.0",
        port=8000,  # 修改端口号
        reload=False,
        log_level="info"
    )
```

### 修改手部配置

编辑 `main_http.py` 中的手部初始化参数：

```python
def get_hand_instance():
    hand_joint = "O6"  # 修改关节类型
    hand_type = "left"  # 修改手型
    modbus = "None"
    can = "PCAN_USBBUS1"  # 修改CAN设备
```

### 自定义服务名称

编辑 `windows_service.py`：

```python
class LinkerHandService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LinkerHandHTTPAPI"  # 服务名称
    _svc_display_name_ = "LinkerHand HTTP API Service"  # 显示名称
```

## API文档

服务启动后，访问以下地址：

- API根路径：`http://localhost:8000/`
- 交互式文档：`http://localhost:8000/docs`
- 静态文档：`http://localhost:8000/redoc`
- OpenAPI规范：`http://localhost:8000/openapi.json`

## 技术细节

### 服务架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Windows       │    │   Python        │    │   LinkerHand    │
│   Service       │───▶│   FastAPI       │───▶│   Hardware      │
│   Manager       │    │   Application   │    │   Controller    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 进程管理

- Windows服务进程管理Python应用
- 自动重启机制（服务停止时自动重启）
- 错误日志记录
- 优雅关闭处理

### 安全性考虑

- 服务以LocalService账户运行
- 最小权限原则
- 网络访问限制在必要端口
- 日志文件权限控制

## 支持

如果遇到问题，请检查：

1. 服务日志文件
2. Windows事件查看器
3. 网络连接状态
4. 硬件设备状态

## 更新服务

要更新服务：

1. 停止服务
2. 重新打包应用
3. 复制新文件到安装目录
4. 启动服务

```bash
sc stop LinkerHandHTTPAPI
# 复制新文件...
sc start LinkerHandHTTPAPI
```