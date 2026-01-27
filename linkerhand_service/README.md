# LinkerHand Windows 服务部署指南

本目录包含将 LinkerHand HTTP API 服务安装为 Windows 系统服务的脚本和工具。

## 功能说明

LinkerHand 服务将 `Demo/main_http.py` 作为 Windows 系统服务运行，实现开机自启动和后台运行。

## 前置要求

1. **NSSM (Non-Sucking Service Manager)**
   - 需要安装 NSSM 到 `C:\nssm\`
   - 下载地址：https://nssm.cc/download
   - 将 `nssm.exe` 放置到 `C:\nssm\nssm.exe`

2. **Conda 环境**
   - 需要安装 Miniconda 或 Anaconda
   - Conda 路径：`C:\miniconda\Scripts\activate.bat`
   - 需要创建名为 `hand_o6` 的 conda 虚拟环境

3. **项目路径**
   - 项目根目录：`C:\linkerhand-python-sdk`
   - 确保路径正确，或修改脚本中的路径配置

## 文件说明

- `install_service.bat` - 安装 Windows 服务
- `start_service.bat` - 启动服务
- `stop_service.bat` - 停止服务
- `restart_service.bat` - 重启服务
- `start_linkerhand.bat` - 服务实际执行的启动脚本

## 使用步骤

### 1. 安装服务

**以管理员身份运行** `install_service.bat`：

```batch
右键点击 install_service.bat -> 以管理员身份运行
```

安装脚本会：
- 删除旧服务（如果存在）
- 创建新的 Windows 服务 `LinkerHandPythonService`
- 设置服务为自动启动
- 配置服务失败后自动重启（延迟 5 秒）

### 2. 启动服务

方式一：使用批处理文件
```batch
start_service.bat
```

方式二：使用 Windows 服务管理器
1. 按 `Win + R`，输入 `services.msc`
2. 找到 `LinkerHandPythonService`
3. 右键 -> 启动

方式三：使用命令行（管理员权限）
```batch
sc start LinkerHandPythonService
```

### 3. 停止服务

方式一：使用批处理文件
```batch
stop_service.bat
```

方式二：使用 Windows 服务管理器
1. 打开服务管理器
2. 找到 `LinkerHandPythonService`
3. 右键 -> 停止

### 4. 重启服务

```batch
restart_service.bat
```

## 服务配置

服务名称：`LinkerHandPythonService`

服务配置：
- **启动类型**：自动（系统启动时自动运行）
- **工作目录**：`C:\linkerhand-python-sdk`
- **执行脚本**：`C:\linkerhand-python-sdk\linkerhand_service\start_linkerhand.bat`
- **失败重启**：自动重启（延迟 5 秒）

## 日志文件

服务运行日志保存在：
- 控制台输出：`C:\linkerhand-python-sdk\Demo\run.log`
- 应用日志：`C:\linkerhand-python-sdk\logs\linkerhand_service_YYYYMMDD.log`

## 自定义配置

如果需要修改路径或配置，请编辑以下文件：

### 修改项目路径

编辑 `install_service.bat`：
```batch
set BAT=C:\linkerhand-python-sdk\linkerhand_service\start_linkerhand.bat
%NSSM% set %SERVICE_NAME% AppDirectory C:\linkerhand-python-sdk
```

### 修改 Conda 环境

编辑 `start_linkerhand.bat`：
```batch
call "C:\miniconda\Scripts\activate.bat"
call conda activate hand_o6
```

### 修改 NSSM 路径

编辑所有 `.bat` 文件中的 NSSM 路径：
```batch
set NSSM=C:\nssm\nssm.exe
```

## 卸载服务

如果需要卸载服务，可以：

方式一：使用 NSSM（推荐）
```batch
C:\nssm\nssm.exe stop LinkerHandPythonService
C:\nssm\nssm.exe remove LinkerHandPythonService confirm
```

方式二：使用 sc 命令（管理员权限）
```batch
sc stop LinkerHandPythonService
sc delete LinkerHandPythonService
```

## 故障排查

### 服务无法启动

1. 检查 NSSM 是否正确安装
2. 检查 Conda 环境是否存在
3. 检查项目路径是否正确
4. 查看日志文件：`C:\linkerhand-python-sdk\Demo\run.log`

### 服务启动后立即停止

1. 检查 Python 依赖是否安装完整
2. 检查 `main_http.py` 是否有语法错误
3. 检查端口是否被占用
4. 查看应用日志：`C:\linkerhand-python-sdk\logs\`

### 查看服务状态

使用 NSSM：
```batch
C:\nssm\nssm.exe status LinkerHandPythonService
```

使用 sc 命令：
```batch
sc query LinkerHandPythonService
```

## 注意事项

1. **管理员权限**：安装和卸载服务需要管理员权限
2. **路径配置**：确保所有路径配置正确，特别是包含中文的路径
3. **环境变量**：服务运行在系统账户下，可能无法访问用户特定的环境变量
4. **端口占用**：确保 HTTP API 使用的端口未被其他程序占用
5. **日志轮转**：日志文件会自动轮转，避免占用过多磁盘空间

## 技术支持

如遇到问题，请检查：
- 日志文件输出
- Windows 事件查看器（Event Viewer）
- NSSM 服务状态

更多信息请参考项目主 README：`../README.md`
