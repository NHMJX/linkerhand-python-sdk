# LinkerHand HTTP API 服务 - Conda环境使用指南

## 📁 文件说明

此文件夹包含用于管理 LinkerHand HTTP API 服务的所有脚本（Conda环境专用）。

### 脚本文件

- **`start_service_interactive.bat`** - 交互式启动服务（推荐使用，提供多种启动选项）
- **`stop_service.bat`** - 停止正在运行的服务
- **`install_autostart_conda.bat`** - 安装开机自启动配置（需要管理员权限）
- **`uninstall_autostart.bat`** - 卸载开机自启动配置（需要管理员权限）
- **`start_service_debug.bat`** - 调试启动服务（问题排查用）
- **`test_script.bat`** - 脚本测试工具（验证环境）

## 🚀 快速开始

### 首次使用

1. **测试脚本环境**
   - 双击 `test_script.bat`
   - 确认能看到彩色输出框和"Hello World!"
   - 如果看不到输出，说明脚本执行有问题

2. **启动服务**
   - 双击 `start_service_interactive.bat`
   - 选择启动模式（推荐选择1，后台启动）
   - 等待启动完成提示

3. **配置开机自启动**
   - 右键点击 `install_autostart_conda.bat`
   - 选择"以管理员身份运行"
   - 按照提示完成安装

### 日常使用

- **启动服务**：双击 `start_service_interactive.bat`（交互式选择启动模式）
- **停止服务**：双击 `stop_service.bat`
- **调试问题**：双击 `start_service_debug.bat`（遇到问题时使用）
- **测试环境**：双击 `test_script.bat`（验证脚本执行环境）

## 📋 详细步骤

### 1. 配置Conda环境

编辑 `start_service_conda.bat`，设置您的Conda环境名：

```batch
set "CONDA_ENV_NAME=您的环境名"
set "USE_BASE_IF_EMPTY=0"
```

如果不设置环境名，脚本会尝试使用base环境。

### 2. 启动服务

**方法一：后台运行（推荐）**
- 双击 `start_service_conda.bat`
- 服务在后台运行，不显示窗口

**方法二：显示窗口**
- 双击 `start_service_conda_window.bat`
- 可以看到服务运行日志

### 3. 配置开机自启动

1. 确保已配置Conda环境名（步骤1）
2. 右键点击 `install_autostart_conda.bat`
3. 选择"以管理员身份运行"
4. 按照提示完成安装

服务将在用户登录后30秒自动启动。

### 4. 停止服务

- 双击 `stop_service.bat`
- 或使用任务管理器终止 `python.exe` 进程

### 5. 卸载开机自启动

- 右键点击 `uninstall_autostart.bat`
- 选择"以管理员身份运行"

## 🔧 服务信息

- **LinkerHand API 服务**: `http://localhost:8000`
- **Exe Executor 服务**: `http://localhost:8001`
- **日志目录**: 项目根目录 `logs/` 文件夹

## ⚠️ 注意事项

1. **Conda环境配置**：必须设置 `CONDA_ENV_NAME` 环境名
2. **Conda安装**：确保Conda已正确安装
3. **环境存在**：确保指定的Conda环境存在
4. **端口占用**：确保8000和8001端口未被占用
5. **管理员权限**：安装/卸载开机自启动需要管理员权限

## 🐛 故障排除

### 快速诊断

如果遇到启动问题，建议按以下顺序尝试：

1. **测试脚本运行**：
   - 双击 `test_script.bat`
   - 确认.bat文件能在Windows上正常执行
   - 如果看不到输出，说明.bat文件执行有问题

2. **使用调试脚本**：
   - 双击 `start_service_debug.bat`
   - 查看详细的6步诊断信息
   - 根据错误信息进行修复

3. **使用简化脚本**：
   - 双击 `start_service_simple.bat`
   - 跳过Conda环境，直接使用系统Python

4. **检查环境**：
   - 确认Python已安装：`python --version`
   - 确认依赖包已安装：`pip list`

### 服务无法启动

1. **检查Conda环境配置**：
   ```cmd
   # 确认环境名正确
   conda env list
   
   # 手动激活测试
   conda activate 环境名
   python --version
   ```

2. **检查脚本配置**：
   - 确认 `start_service_conda.bat` 中 `CONDA_ENV_NAME` 已设置
   - 确认环境名拼写正确

3. **手动运行查看错误**：
   ```cmd
   cd 项目根目录
   conda activate 环境名
   python Demo\main_http.py
   ```

### 开机自启动不工作

1. **检查任务计划程序**：
   - 按 `Win + R`，输入 `taskschd.msc`
   - 查找任务 `LinkerHand_HTTP_API_Service_Dev_Conda`
   - 检查任务状态和上次运行结果

2. **检查Conda环境配置**：
   - 确认 `start_service_conda.bat` 中环境名已配置
   - 确认环境名正确

3. **查看日志**：
   - 日志保存在项目根目录的 `logs/` 文件夹中
   - 文件名格式：`linkerhand_service_YYYYMMDD.log`

### 端口被占用

如果8000或8001端口被占用：
1. 使用任务管理器终止占用端口的进程
2. 或修改 `Demo/main_http.py` 中的端口号

## 📝 详细说明文档

- **`Conda环境说明.txt`** - Conda环境详细使用说明
- **`Conda开机自启动配置说明.txt`** - 开机自启动详细配置指南

## 🔄 更新服务

如果需要更新服务代码：

1. 停止服务：运行 `stop_service.bat`
2. 更新代码文件
3. 重新启动服务：运行 `start_service_conda.bat`

开机自启动配置不需要重新安装。
