# LinkerHand HTTP API 独立安装包

## 📦 安装包内容

此安装包包含完整的运行环境，目标机器无需安装Python或其他开发工具。

### 文件清单
- `LinkerHand_HTTP_Service.exe` - 主程序（已打包所有依赖）
- `LinkerHand_Service.py` - Windows服务包装器
- `install.bat` - 一键安装脚本
- `uninstall.bat` - 卸载脚本
- `README.txt` - 本说明文件
- `service.log` - 服务运行日志（安装后生成）

## 🚀 快速安装

1. **以管理员身份运行** `install.bat`
2. 等待安装完成
3. 访问 `http://localhost:8000` 使用API

## 📋 系统要求

- Windows 10/11 或 Windows Server 2016+
- 管理员权限
- 至少 2GB 可用磁盘空间
- 已连接的LinkerHand硬件（可选，用于实际控制）

## 🌟 功能特性

- ✅ **完全独立** - 无需安装Python或其他开发环境
- ✅ **开机自启动** - Windows服务，系统启动时自动运行
- ✅ **自动重启** - 服务异常退出时自动重启
- ✅ **防火墙配置** - 自动配置端口8000访问权限
- ✅ **中文界面** - 友好的中文安装提示

## 🔧 API使用

### 基础API
```bash
# 握笔动作
curl -X POST http://localhost:8000/hold_pen

# 打开手部
curl -X POST http://localhost:8000/open_hand

# 设置速度
curl -X POST http://localhost:8000/set_speed -H "Content-Type: application/json" -d "{\\"speeds\\": [60,60,60,60,60,60]}"

# 移动手指
curl -X POST http://localhost:8000/finger_move -H "Content-Type: application/json" -d "{\\"positions\\": [120,90,120,70,50,40]}"
```

### 完整文档
安装完成后访问：`http://localhost:8000/docs`

## 📊 服务管理

### Windows服务控制
```bash
# 查看状态
sc query LinkerHandHTTPAPI

# 启动/停止
sc start LinkerHandHTTPAPI
sc stop LinkerHandHTTPAPI

# 重启服务
sc stop LinkerHandHTTPAPI & sc start LinkerHandHTTPAPI
```

### 服务属性
- **服务名称**: `LinkerHandHTTPAPI`
- **显示名称**: `LinkerHand HTTP API Service`
- **启动类型**: 自动（开机自启动）
- **运行账户**: LocalService

## 🔍 故障排除

### 服务无法启动
1. 检查 `service.log` 日志文件
2. 确认端口8000未被占用
3. 检查硬件连接（如果使用实际硬件）

### API访问失败
1. 确认服务正在运行
2. 检查防火墙设置
3. 尝试本地访问：`http://localhost:8000/health`

### 卸载重装
```bash
# 运行卸载脚本
uninstall.bat

# 重新运行安装
install.bat
```

## 📞 技术支持

- 📖 查看API文档：`http://localhost:8000/docs`
- 📝 查看服务日志：`service.log`
- 🐛 联系技术支持团队

## 📝 版本信息

- 版本: 3.1.0
- 构建时间: 自动生成
- 支持的LinkerHand型号: L6, L7, L10, L20系列

---

**注意**: 请在安全的环境中使用，确保硬件连接正确。