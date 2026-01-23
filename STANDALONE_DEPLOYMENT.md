# LinkerHand HTTP API 独立部署指南

本指南介绍如何将LinkerHand HTTP API部署为完全独立的Windows服务，目标机器无需安装Python或其他开发环境。

## 🎯 核心特性

- ✅ **零依赖部署** - 目标机器无需安装Python、pip或其他开发工具
- ✅ **开机自启动** - Windows服务，系统启动时自动运行
- ✅ **一键安装** - 双击安装脚本即可完成部署
- ✅ **自动重启** - 服务异常退出时自动重启
- ✅ **中文界面** - 友好的中文安装提示

## 📦 部署包内容

构建完成后，`dist/` 目录将包含以下文件：

```
dist/
├── LinkerHand_HTTP_Service.exe    # 主程序（已打包所有依赖）
├── LinkerHand_Service.py          # Windows服务包装器
├── install.bat                    # 一键安装脚本
├── uninstall.bat                  # 卸载脚本
└── README.txt                     # 详细说明文档
```

## 🚀 构建独立安装包

### 1. 环境准备

确保开发环境已安装必要的依赖：

```bash
# 安装Python依赖
pip install -r requirements.txt

# 验证PyInstaller安装
pyinstaller --version
```

### 2. 构建独立包

```bash
# 运行构建脚本
python build_standalone.py
```

此脚本将：
- 创建PyInstaller配置文件
- 将Python应用打包成独立的exe文件
- 生成Windows服务包装器
- 创建一键安装脚本
- 生成说明文档

### 3. 验证构建结果

```bash
# 检查生成的文件
ls -la dist/

# 验证exe文件大小（通常20-50MB）
du -sh dist/LinkerHand_HTTP_Service.exe
```

## 📋 系统要求

### 目标机器要求
- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **权限**: 管理员权限（安装时需要）
- **磁盘空间**: 至少2GB可用空间
- **硬件**: 已连接的LinkerHand设备（可选，用于实际控制）

### 开发环境要求
- Python 3.8+
- PyInstaller
- pywin32
- 所有requirements.txt中的依赖

## 🔧 部署步骤

### 方式1：本地部署

1. **复制文件**
   ```bash
   # 将整个dist目录复制到目标机器
   xcopy dist \\TARGET-PC\\C$\\LinkerHand_Service /E /I /H /Y
   ```

2. **运行安装**
   ```bash
   # 在目标机器上以管理员身份运行
   cd C:\\LinkerHand_Service
   install.bat
   ```

3. **验证安装**
   ```bash
   # 检查服务状态
   sc query LinkerHandHTTPAPI

   # 测试API
   curl http://localhost:8000/health
   ```

### 方式2：网络部署

```powershell
# PowerShell远程部署脚本
$targetComputer = "TARGET-PC"
$sourcePath = "\\\\BUILD-PC\\share\\dist"
$destPath = "C:\\LinkerHand_Service"

# 复制文件到远程机器
Copy-Item -Path $sourcePath -Destination "\\\\$targetComputer\\C$\\LinkerHand_Service" -Recurse -Force

# 在远程机器上运行安装
Invoke-Command -ComputerName $targetComputer -ScriptBlock {
    Set-Location "C:\\LinkerHand_Service"
    & ".\\install.bat"
}
```

### 方式3：批量部署

```powershell
# 批量部署到多台机器
$computers = @("PC1", "PC2", "PC3", "PC4")

foreach ($computer in $computers) {
    Write-Host "部署到 $computer..."

    # 复制文件
    Copy-Item -Path "dist" -Destination "\\\\$computer\\C$\\LinkerHand_Service" -Recurse -Force

    # 远程安装
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Set-Location "C:\\LinkerHand_Service"
        & ".\\install.bat"
    }

    Write-Host "✓ $computer 部署完成"
}
```

## 🌐 使用API

部署完成后，即可使用HTTP API控制LinkerHand：

### 基础API调用

```bash
# 查看API文档
start http://localhost:8000/docs

# 握笔动作
curl -X POST http://localhost:8000/hold_pen

# 打开手部
curl -X POST http://localhost:8000/open_hand

# 设置速度
curl -X POST http://localhost:8000/set_speed ^
  -H "Content-Type: application/json" ^
  -d "{\\"speeds\\": [60,60,60,60,60,60]}"

# 移动手指
curl -X POST http://localhost:8000/finger_move ^
  -H "Content-Type: application/json" ^
  -d "{\\"positions\\": [120,90,120,70,50,40]}"
```

### C++客户端示例

```cpp
#include <curl/curl.h>
#include <iostream>
#include <string>

int main() {
    CURL* curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8000/hold_pen");
        curl_easy_setopt(curl, CURLOPT_POST, 1L);

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            std::cerr << "请求失败: " << curl_easy_strerror(res) << std::endl;
        }

        curl_easy_cleanup(curl);
    }
    return 0;
}
```

## 📊 服务管理

### Windows服务控制

```bash
# 查看服务状态
sc query LinkerHandHTTPAPI

# 启动服务
sc start LinkerHandHTTPAPI

# 停止服务
sc stop LinkerHandHTTPAPI

# 重启服务
sc stop LinkerHandHTTPAPI & sc start LinkerHandHTTPAPI

# 查看服务配置
sc qc LinkerHandHTTPAPI
```

### 服务日志

服务运行日志保存在安装目录下的 `service.log` 文件：

```bash
# 查看最新日志
type C:\\LinkerHand_Service\\service.log | findstr /C:"INFO" | tail -10

# 实时监控日志
powershell "Get-Content 'C:\\LinkerHand_Service\\service.log' -Wait -Tail 10"
```

### 服务属性

- **服务名称**: `LinkerHandHTTPAPI`
- **显示名称**: `LinkerHand HTTP API Service`
- **描述**: `LinkerHand机械手控制HTTP API服务 - 开机自启动`
- **启动类型**: 自动
- **运行账户**: LocalService
- **恢复策略**: 自动重启

## 🔍 故障排除

### 常见问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 服务启动失败 | `sc start` 失败 | 检查service.log日志，确认端口未被占用 |
| API访问失败 | 无法连接localhost:8000 | 检查防火墙设置，确认服务正在运行 |
| 硬件连接失败 | 日志显示CAN错误 | 检查PCAN设备连接和驱动安装 |
| 权限不足 | 安装时失败 | 必须以管理员身份运行install.bat |
| 端口冲突 | 服务无法启动 | 修改端口配置或停止冲突服务 |

### 诊断脚本

```batch
@echo off
echo === LinkerHand服务诊断 ===

echo 1. 服务状态:
sc query LinkerHandHTTPAPI

echo.
echo 2. 进程状态:
tasklist /FI "IMAGENAME eq LinkerHand_HTTP_Service.exe"

echo.
echo 3. 端口状态:
netstat -ano | findstr :8000

echo.
echo 4. 防火墙规则:
netsh advfirewall firewall show rule name="LinkerHand HTTP API"

echo.
echo 5. 最新日志:
if exist "service.log" (
    powershell "Get-Content service.log -Tail 5"
) else (
    echo 日志文件不存在
)

pause
```

### 重置服务

如果服务出现问题，可以完全重置：

```batch
# 停止并删除服务
sc stop LinkerHandHTTPAPI
sc delete LinkerHandHTTPAPI

# 删除防火墙规则
netsh advfirewall firewall delete rule name="LinkerHand HTTP API"

# 清理日志文件
del service.log

# 重新安装
install.bat
```

## 🔄 更新服务

### 版本更新流程

1. **构建新版本**
   ```bash
   # 在开发机上构建新版本
   python build_standalone.py
   ```

2. **备份配置**
   ```bash
   # 备份当前的service.log（如果需要）
   copy service.log service.log.backup
   ```

3. **停止旧服务**
   ```bash
   sc stop LinkerHandHTTPAPI
   ```

4. **更新文件**
   ```bash
   # 替换exe文件和服务脚本
   copy /Y dist\\LinkerHand_HTTP_Service.exe .
   copy /Y dist\\LinkerHand_Service.py .
   ```

5. **重启服务**
   ```bash
   sc start LinkerHandHTTPAPI
   ```

### 回滚更新

如果新版本出现问题，可以快速回滚：

```batch
REM 停止服务
sc stop LinkerHandHTTPAPI

REM 恢复备份的exe文件
copy /Y LinkerHand_HTTP_Service.exe.backup LinkerHand_HTTP_Service.exe

REM 重启服务
sc start LinkerHandHTTPAPI
```

## 📈 监控和维护

### 性能监控

```powershell
# PowerShell监控脚本
while ($true) {
    $service = Get-Service -Name "LinkerHandHTTPAPI"
    $process = Get-Process -Name "LinkerHand_HTTP_Service" -ErrorAction SilentlyContinue

    Write-Host "$(Get-Date) - 服务状态: $($service.Status)"

    if ($process) {
        Write-Host "  CPU: $($process.CPU)%, 内存: $([math]::Round($process.WorkingSet64/1MB, 2))MB"
    }

    # 检查API健康状态
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "  API状态: 正常 ($($response.StatusCode))"
    } catch {
        Write-Host "  API状态: 异常"
    }

    Start-Sleep -Seconds 30
}
```

### 自动化维护

```batch
REM 每日维护脚本 (daily_maintenance.bat)
@echo off
echo [%date% %time%] 开始日常维护

REM 检查服务状态
sc query LinkerHandHTTPAPI | findstr "RUNNING" >nul
if %errorlevel% neq 0 (
    echo 服务未运行，尝试重启...
    sc start LinkerHandHTTPAPI
)

REM 检查磁盘空间
for /f "tokens=3" %%a in ('dir /-c C:\\ ^| find "bytes free"') do set free=%%a
if %free% lss 1073741824 (
    echo 警告：磁盘空间不足1GB
)

REM 清理旧日志（保留7天）
forfiles /p "C:\\LinkerHand_Service" /m "*.log.*" /d -7 /c "cmd /c del @path"

echo [%date% %time%] 维护完成
```

## 🔒 安全考虑

### 服务账户

服务默认使用 `LocalService` 账户运行，具有最小权限。如需特定权限：

```batch
# 修改服务账户
sc config LinkerHandHTTPAPI obj= ".\\用户名" password= "密码"

# 或者使用网络服务账户
sc config LinkerHandHTTPAPI obj= "NT AUTHORITY\\NetworkService"
```

### 网络安全

- 服务默认只监听本地地址 (`127.0.0.1`)
- 如需远程访问，需要修改防火墙规则
- 考虑使用HTTPS和认证机制

### 文件权限

```batch
# 设置目录权限
icacls "C:\\LinkerHand_Service" /grant "NT AUTHORITY\\LocalService:(OI)(CI)F" /T

# 设置日志文件权限
icacls "service.log" /grant "NT AUTHORITY\\LocalService:(M)"
```

## 📞 技术支持

### 自助诊断
1. 运行诊断脚本检查系统状态
2. 查看服务日志了解详细错误
3. 确认硬件连接和驱动状态
4. 测试API端点响应

### 日志分析
```bash
REM 分析错误日志
findstr /C:"ERROR" service.log | tail -10

REM 统计服务重启次数
findstr /C:"启动LinkerHand HTTP API服务" service.log | find /c "启动"
```

### 联系支持
- 📧 发送service.log日志文件
- 📝 提供系统信息和错误现象
- 🖥️ 远程协助诊断（需要授权）

---

## 📝 最佳实践

1. **定期备份** - 备份配置文件和日志
2. **监控日志** - 定期检查service.log
3. **更新维护** - 及时应用安全补丁
4. **权限控制** - 使用最小权限原则
5. **网络隔离** - 避免将API暴露到公网

通过遵循本指南，您可以安全、稳定地部署LinkerHand HTTP API服务，实现真正的开机即用！🚀