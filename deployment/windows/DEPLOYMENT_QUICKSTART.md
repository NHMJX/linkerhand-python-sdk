# LinkerHand HTTP API 部署快速指南

## 🎯 部署方式总览

| 方式 | 适用场景 | 复杂度 | 自动化程度 |
|------|----------|--------|------------|
| 本地一键部署 | 单机部署 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 部署包部署 | 单机/离线部署 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 远程PowerShell部署 | 多机批量部署 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 手动部署 | 自定义需求 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 🚀 快速开始

### 方式1：本地一键部署（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行一键部署脚本
python deploy_windows.py
```

**适合场景：** 在开发机上直接部署

### 方式2：部署包部署

```bash
# 1. 创建部署包
python create_deployment_package.py

# 2. 在目标机器上解压并运行
# 解压 LinkerHand_Deployment_Package.zip
# 以管理员身份运行 install.bat
```

**适合场景：** 离线环境、U盘部署、标准化部署

### 方式3：远程部署

```powershell
# PowerShell脚本部署（需要管理员权限）
.\remote_deploy.ps1 -ComputerName "TARGET-PC" -PackagePath ".\LinkerHand_Deployment_Package.zip"

# 批量部署
.\remote_deploy.ps1 -ComputerName "PC1,PC2,PC3" -PackagePath ".\LinkerHand_Deployment_Package.zip"
```

**适合场景：** IT管理员批量部署、企业环境

## 📋 系统要求

### 必须条件
- ✅ Windows 10/11 或 Windows Server 2016+
- ✅ 管理员权限
- ✅ Python 3.8+（或使用便携式Python）

### 可选条件
- 🔄 PCAN设备驱动（用于硬件控制）
- 🔄 网络访问（用于依赖安装）

## 🛠️ 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 权限不足 | 以管理员身份运行所有脚本 |
| Python未安装 | 下载安装Python 3.8+ 或使用便携版 |
| 依赖安装失败 | 检查网络连接，使用 `--user` 参数 |
| 服务启动失败 | 检查PCAN设备连接，查看服务日志 |
| 端口占用 | 修改端口配置或停止冲突服务 |

### 快速诊断

```batch
# 创建诊断脚本
echo 检查系统状态...
python -c "import sys; print('Python版本:', sys.version)"
pip list | findstr "fastapi\|uvicorn\|pywin32"
sc query LinkerHandHTTPAPI
netstat -ano | findstr :8000
```

### 服务日志位置
- **服务日志：** `C:\LinkerHand_HTTP_API\service.log`
- **Windows事件：** 事件查看器 → Windows日志 → 应用程序

## 📚 详细文档

| 文档 | 内容 |
|------|------|
| [WINDOWS_DEPLOYMENT.md](WINDOWS_DEPLOYMENT.md) | Windows服务部署详细指南 |
| [REMOTE_DEPLOYMENT.md](REMOTE_DEPLOYMENT.md) | 远程部署和企业环境指南 |
| [Demo/README_HTTP_API.md](Demo/README_HTTP_API.md) | HTTP API使用说明 |

## 🎛️ 管理命令

### 服务控制
```bash
# 状态查询
sc query LinkerHandHTTPAPI

# 启动/停止
sc start LinkerHandHTTPAPI
sc stop LinkerHandHTTPAPI

# 重启
sc stop LinkerHandHTTPAPI & sc start LinkerHandHTTPAPI
```

### 日志查看
```bash
# 查看服务日志
type C:\LinkerHand_HTTP_API\service.log

# 查看最后100行
powershell "Get-Content 'C:\LinkerHand_HTTP_API\service.log' -Tail 100"
```

### 卸载
```bash
# 卸载服务
python install_service.py uninstall

# 或使用部署包中的卸载脚本
uninstall.bat
```

## 🌐 API访问

部署完成后访问：
- **API根路径：** `http://localhost:8000/`
- **交互文档：** `http://localhost:8000/docs`
- **健康检查：** `http://localhost:8000/health`

### 常用API调用

```bash
# 握笔动作
curl -X POST http://localhost:8000/hold_pen

# 打开手部
curl -X POST http://localhost:8000/open_hand

# 设置速度
curl -X POST http://localhost:8000/set_speed -H "Content-Type: application/json" -d "{\"speeds\": [60,60,60,60,60,60]}"

# 移动手指
curl -X POST http://localhost:8000/finger_move -H "Content-Type: application/json" -d "{\"positions\": [120,90,120,70,50,40]}"
```

## 🔧 高级配置

### 修改服务配置

编辑 `windows_service.py`：
```python
class LinkerHandService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LinkerHandHTTPAPI"          # 服务名称
    _svc_display_name_ = "My Custom Service"   # 显示名称
```

### 修改API端口

创建环境变量或修改 `main_http.py`：
```python
import os
port = int(os.environ.get('LINKERHAND_PORT', 8000))
```

### 自定义安装路径

```bash
# 指定安装路径
python install_service.py install "D:\MyServices\LinkerHand"
```

## 📞 支持

### 自助诊断
1. 运行 `check_deployment.bat` 进行系统检查
2. 查看服务日志了解详细错误信息
3. 确认硬件连接和驱动安装

### 技术支持
- 📖 查看完整文档
- 🐛 检查GitHub Issues
- 💬 联系技术支持团队

---

## 📝 部署检查清单

- [ ] 确认操作系统版本 (Win10+)
- [ ] 以管理员身份运行脚本
- [ ] 确保Python 3.8+ 已安装
- [ ] 检查PCAN设备连接
- [ ] 验证防火墙设置
- [ ] 测试API访问
- [ ] 确认开机自启动

完成所有步骤后，LinkerHand HTTP API将作为Windows服务运行，并在系统启动时自动启动！🎉