# LinkerHand 部署工具包

本目录包含将LinkerHand HTTP API服务部署到Windows系统的完整工具包。

## 📁 文件夹结构

```
deployment/
├── README.md                    # 本说明文件
└── windows/
    ├── build_exe.py            # PyInstaller打包脚本
    ├── windows_service.py      # Windows服务包装器
    ├── install_service.py      # 服务安装脚本
    ├── deploy_windows.py       # 一键部署脚本
    ├── deploy_windows.bat      # Windows一键部署批处理
    ├── create_deployment_package.py  # 部署包生成器
    ├── remote_deploy.ps1       # PowerShell远程部署脚本
    ├── create_package.bat      # 快速创建部署包批处理
    ├── WINDOWS_DEPLOYMENT.md   # Windows部署详细指南
    ├── REMOTE_DEPLOYMENT.md    # 远程部署指南
    └── DEPLOYMENT_QUICKSTART.md # 快速开始指南
```

## 🚀 快速开始

### 本地部署
```bash
cd deployment/windows
python deploy_windows.py
```

### 创建部署包
```bash
cd deployment/windows
python create_deployment_package.py
```

### 远程部署
```powershell
cd deployment/windows
.\remote_deploy.ps1 -ComputerName "TARGET-PC" -PackagePath ".\LinkerHand_Deployment_Package.zip"
```

## 📖 文档说明

- **[DEPLOYMENT_QUICKSTART.md](windows/DEPLOYMENT_QUICKSTART.md)** - 快速开始指南，包含所有部署方式的概述
- **[WINDOWS_DEPLOYMENT.md](windows/WINDOWS_DEPLOYMENT.md)** - Windows服务部署详细指南
- **[REMOTE_DEPLOYMENT.md](windows/REMOTE_DEPLOYMENT.md)** - 远程部署和企业环境指南

## 🔧 使用说明

### 系统要求
- Windows 10/11 或 Windows Server 2016+
- Python 3.8+
- 管理员权限

### 主要脚本说明

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `deploy_windows.py` | 一键本地部署 | `python deploy_windows.py` |
| `create_deployment_package.py` | 生成部署包 | `python create_deployment_package.py` |
| `remote_deploy.ps1` | 远程部署 | PowerShell脚本 |
| `install_service.py` | 服务安装/卸载 | `python install_service.py install/uninstall` |

## 🎯 部署流程

1. **准备阶段**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **构建阶段**
   ```bash
   cd deployment/windows
   python build_exe.py
   ```

3. **部署阶段**
   ```bash
   # 本地部署
   python deploy_windows.py

   # 或创建部署包
   python create_deployment_package.py
   ```

4. **验证阶段**
   - 访问 `http://localhost:8000/docs`
   - 检查服务状态：`sc query LinkerHandHTTPAPI`

## 🔄 服务管理

```bash
# 检查状态
sc query LinkerHandHTTPAPI

# 启动服务
sc start LinkerHandHTTPAPI

# 停止服务
sc stop LinkerHandHTTPAPI

# 卸载服务
python install_service.py uninstall
```

## 📞 支持

如遇到问题，请：
1. 查看详细文档
2. 检查服务日志：`C:\LinkerHand_HTTP_API\service.log`
3. 确认硬件连接和驱动安装

---

**注意：** 所有脚本都需要管理员权限运行。