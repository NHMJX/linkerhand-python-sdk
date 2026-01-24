# LinkerHand HTTP API 服务 - 部署到其他电脑指南

本指南说明如何将打包后的服务部署到其他 Windows 电脑上并实现开机自启动。

## 方法一：使用部署脚本（推荐）

### 步骤 1: 准备部署包

在开发电脑上：

1. 运行打包脚本生成可执行文件：
   ```bash
   python build.py
   ```
   或双击 `quick_build.bat`

2. 打包完成后，在 `dist` 文件夹中会生成 `linkerhand_service.exe`

3. 创建部署文件夹，包含以下文件：
   ```
   部署包/
   ├── linkerhand_service.exe          # 主程序
   ├── deploy_to_other_pc.bat          # 安装脚本
   ├── uninstall_service.bat           # 卸载脚本
   └── README.txt                      # 使用说明（可选）
   ```

### 步骤 2: 复制到目标电脑

将整个部署文件夹复制到目标电脑的任意位置（建议放在 `C:\Program Files\LinkerHand\` 或用户目录下）。

### 步骤 3: 在目标电脑上安装

**方式一：使用安装脚本（推荐）**

1. 右键点击 `deploy_to_other_pc.bat`
2. 选择"以管理员身份运行"
3. 按照提示完成安装

**方式二：手动安装**

#### 使用任务计划程序（推荐，需要管理员权限）

1. 按 `Win + R`，输入 `taskschd.msc`，回车打开任务计划程序
2. 点击右侧"创建基本任务"
3. 填写任务信息：
   - 名称：`LinkerHand_HTTP_API_Service`
   - 描述：`LinkerHand机械手HTTP API服务 - 开机自启动`
4. 触发器：选择"当用户登录时"
5. 操作：选择"启动程序"
   - 程序或脚本：浏览选择 `linkerhand_service.exe` 的完整路径
   - 起始于：选择 `linkerhand_service.exe` 所在的文件夹
6. 完成设置

#### 使用启动文件夹（不需要管理员权限）

1. 按 `Win + R`，输入 `shell:startup`，回车
2. 将 `linkerhand_service.exe` 的快捷方式复制到此文件夹
3. 完成

## 方法二：使用 Python 安装脚本

如果目标电脑有 Python 环境，可以使用 Python 安装脚本：

1. 将以下文件复制到目标电脑：
   - `linkerhand_service.exe`
   - `install_autostart.py`（需要修改路径）

2. 修改 `install_autostart.py` 中的路径，或直接运行：
   ```bash
   python install_autostart.py
   ```

## 验证安装

安装完成后：

1. **重启电脑**或**注销后重新登录**
2. 等待 30 秒（如果使用任务计划程序）
3. 打开浏览器访问：`http://localhost:8000`
4. 应该能看到 API 信息页面

## 管理服务

### 使用管理脚本（推荐）

部署包中包含了以下服务管理脚本：

#### 启动服务
```bash
start_service.bat
```
或直接双击运行

#### 停止服务
```bash
stop_service.bat
```
或直接双击运行

#### 重启服务
```bash
restart_service.bat
```
或直接双击运行（先停止再启动）

#### 检查服务状态
```bash
check_service_status.bat
```
查看服务运行状态、任务计划配置和端口监听情况

### 手动管理

#### 手动启动服务

直接双击运行 `linkerhand_service.exe`

或使用任务计划程序：
```bash
schtasks /Run /TN "LinkerHand_HTTP_API_Service"
```

#### 手动停止服务

在任务管理器中结束 `linkerhand_service.exe` 进程

或使用命令行：
```bash
taskkill /IM linkerhand_service.exe /F
```

#### 查看服务状态

访问健康检查端点：
- 浏览器：`http://localhost:8000/health`
- 命令行：`curl http://localhost:8000/health`

或运行状态检查脚本：
```bash
check_service_status.bat
```

## 卸载服务

运行卸载脚本：
```bash
uninstall_service.bat
```

或手动删除：
- 任务计划程序中的任务：`LinkerHand_HTTP_API_Service`
- 启动文件夹中的快捷方式：`LinkerHand_Service.lnk`

## 常见问题

### 问题 1: 安装脚本提示需要管理员权限

**解决方案：**
- 右键点击脚本，选择"以管理员身份运行"
- 或使用启动文件夹方式（不需要管理员权限）

### 问题 2: 服务无法启动

**解决方案：**
1. 检查是否有其他程序占用 8000 端口
2. 检查 CAN 设备是否连接
3. 直接运行 `linkerhand_service.exe` 查看错误信息
4. 检查 Windows 防火墙设置

### 问题 3: 开机自启动不工作

**解决方案：**
1. 检查任务计划程序中的任务是否启用
2. 查看任务计划程序中的"历史记录"查看错误信息
3. 检查任务是否设置为"无论用户是否登录都要运行"
4. 尝试使用启动文件夹方式

### 问题 4: 在其他电脑上无法运行

**解决方案：**
1. 确保目标电脑是 Windows 系统
2. 首次运行可能需要点击"更多信息" -> "仍要运行"（Windows 安全警告）
3. 确保目标电脑有必要的系统库（Windows 10/11 通常已包含）

### 问题 5: 防火墙阻止访问

**解决方案：**
如果需要在其他电脑访问服务，需要在 Windows 防火墙中添加例外规则：

1. 打开"Windows Defender 防火墙"
2. 点击"高级设置"
3. 选择"入站规则" -> "新建规则"
4. 选择"端口" -> "TCP" -> "特定本地端口" -> 输入 `8000`
5. 选择"允许连接"
6. 完成设置

## 部署包文件清单

完整的部署包应包含：

```
LinkerHand_Service_部署包/
├── linkerhand_service.exe          # 主程序（必需）
├── deploy_to_other_pc.bat         # 安装脚本（推荐）
├── uninstall_service.bat           # 卸载脚本（推荐）
├── start_service.bat               # 启动服务脚本（推荐）
├── stop_service.bat                # 停止服务脚本（推荐）
├── restart_service.bat             # 重启服务脚本（推荐）
├── check_service_status.bat        # 状态检查脚本（推荐）
├── DEPLOYMENT_GUIDE.md            # 部署指南（可选）
└── README.txt                     # 使用说明（可选）
```

## 快速部署检查清单

- [ ] 在开发电脑上完成打包
- [ ] 创建部署文件夹
- [ ] 复制所有必需文件到部署文件夹
- [ ] 将部署文件夹复制到目标电脑
- [ ] 在目标电脑上运行安装脚本（以管理员身份）
- [ ] 重启电脑验证自启动
- [ ] 访问 http://localhost:8000 验证服务运行

## 技术支持

如有问题，请检查：
1. Windows 版本和权限
2. CAN 设备连接状态
3. 防火墙和端口设置
4. 任务计划程序中的任务状态
