# LinkerHand HTTP API 远程部署指南

本指南介绍如何将打包好的LinkerHand HTTP API服务部署到其他Windows机器上。

## 部署方式

### 方式1：完整部署包（推荐）

#### 1. 在开发机上创建部署包

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 构建应用
python build_exe.py

# 3. 创建部署包
python create_deployment_package.py
```

#### 2. 在目标机器上部署

```bash
# 解压部署包
# 以管理员身份运行安装脚本
LinkerHand_Deployment_Package\install.bat
```

### 方式2：手动部署

#### 准备部署文件

将以下文件复制到目标机器：

```
deployment_files/
├── LinkerHand_HTTP_API.exe          # 主程序
├── windows_service.py                # 服务脚本
├── install_service.py                # 安装脚本
├── requirements.txt                  # 依赖列表
└── python-3.8.10-embed-amd64.zip     # 嵌入式Python（可选）
```

#### 在目标机器上执行

```bash
# 1. 安装Python（如果没有）
# 下载并安装Python 3.8+ 从 https://python.org

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装服务（需要管理员权限）
python install_service.py install
```

## 自动化部署脚本

### 创建部署包生成脚本

```python
# create_deployment_package.py
import os
import zipfile
from pathlib import Path

def create_deployment_package():
    """创建部署包"""
    package_name = "LinkerHand_Deployment_Package"
    package_dir = Path(package_name)

    # 创建包目录
    package_dir.mkdir(exist_ok=True)

    # 复制必要文件
    files_to_copy = [
        "dist/LinkerHand_HTTP_API.exe",
        "windows_service.py",
        "install_service.py",
        "requirements.txt",
        "WINDOWS_DEPLOYMENT.md"
    ]

    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            dst = package_dir / src.name
            if src.is_file():
                import shutil
                shutil.copy2(src, dst)
                print(f"复制: {src} -> {dst}")

    # 创建安装脚本
    create_install_script(package_dir)

    # 压缩包
    zip_name = f"{package_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(package_dir))

    print(f"部署包已创建: {zip_name}")
    return zip_name

def create_install_script(package_dir):
    """创建安装脚本"""
    install_script = '''@echo off
REM LinkerHand HTTP API 自动安装脚本

echo LinkerHand HTTP API 安装程序
echo ==============================

echo 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo 检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到pip
    pause
    exit /b 1
)

echo 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo 检查管理员权限...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 以管理员身份运行，继续安装...
) else (
    echo 错误: 需要管理员权限
    echo 请右键"以管理员身份运行"此脚本
    pause
    exit /b 1
)

echo 安装Windows服务...
python install_service.py install
if errorlevel 1 (
    echo 错误: 服务安装失败
    pause
    exit /b 1
)

echo.
echo 安装完成！
echo API地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
pause
'''

    with open(package_dir / "install.bat", 'w', encoding='utf-8') as f:
        f.write(install_script)

if __name__ == "__main__":
    create_deployment_package()
```

### 使用PowerShell远程部署

```powershell
# remote_deploy.ps1
param(
    [string]$TargetComputer,
    [string]$PackagePath,
    [string]$InstallPath = "C:\LinkerHand_HTTP_API"
)

# 复制部署包到远程机器
Copy-Item -Path $PackagePath -Destination "\\$TargetComputer\C$\Temp\" -Force

# 在远程机器上执行安装
Invoke-Command -ComputerName $TargetComputer -ScriptBlock {
    param($PackagePath, $InstallPath)

    # 解压部署包
    Expand-Archive -Path $PackagePath -DestinationPath $InstallPath -Force

    # 设置工作目录
    Set-Location $InstallPath

    # 运行安装脚本
    & ".\install.bat"

} -ArgumentList "\\$TargetComputer\C$\Temp\$($PackagePath | Split-Path -Leaf)", $InstallPath
```

## 容器化部署（可选）

### 使用Docker部署

```dockerfile
# Dockerfile.windows
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# 设置工作目录
WORKDIR /app

# 复制应用文件
COPY dist/LinkerHand_HTTP_API.exe .
COPY windows_service.py .
COPY requirements.txt .

# 安装Python
RUN powershell -Command `
    Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe' -OutFile 'python-installer.exe' ; `
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item python-installer.exe

# 安装依赖
RUN pip install -r requirements.txt

# 创建服务用户
RUN net user linkerhand /add /passwordreq:no
RUN net localgroup administrators linkerhand /add

# 设置服务
RUN sc create LinkerHandHTTPAPI binPath= "C:\app\LinkerHand_HTTP_API.exe" start= auto obj= "NT AUTHORITY\LocalService"

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["sc", "start", "LinkerHandHTTPAPI"]
```

## 企业环境部署

### 使用组策略部署

1. **创建组策略对象**
   ```
   计算机配置 → 首选项 → Windows设置 → 文件
   ```

2. **部署安装包**
   ```
   计算机配置 → 首选项 → 控制面板设置 → 计划任务
   ```

3. **配置服务**
   ```
   计算机配置 → Windows设置 → 安全设置 → 系统服务
   ```

### 使用SCCM部署

```xml
<!-- SCCM部署脚本 -->
<Configuration>
  <Package>
    <Name>LinkerHand HTTP API</Name>
    <Version>3.1.0</Version>
    <InstallCommand>install.bat</InstallCommand>
    <UninstallCommand>uninstall.bat</UninstallCommand>
  </Package>
</Configuration>
```

## 网络配置

### 防火墙配置

```batch
# firewall_config.bat
@echo off
REM 配置Windows防火墙

echo 配置防火墙规则...

REM 允许端口8000入站连接
netsh advfirewall firewall add rule name="LinkerHand HTTP API" dir=in action=allow protocol=TCP localport=8000

REM 允许服务进程
netsh advfirewall firewall add rule name="LinkerHand Service" dir=in action=allow program="C:\LinkerHand_HTTP_API\LinkerHand_HTTP_API.exe"

echo 防火墙配置完成
pause
```

### 端口配置

如果默认端口8000被占用，可以修改配置：

```python
# 在main_http.py中修改端口
if __name__ == "__main__":
    port = int(os.environ.get('LINKERHAND_PORT', 8000))
    uvicorn.run(
        "main_http:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
```

## 监控和维护

### 部署状态检查

```batch
# check_deployment.bat
@echo off
echo 检查LinkerHand HTTP API部署状态...
echo ======================================

echo 1. 检查服务状态:
sc query LinkerHandHTTPAPI
echo.

echo 2. 检查进程:
tasklist /FI "IMAGENAME eq LinkerHand_HTTP_API.exe"
echo.

echo 3. 检查端口:
netstat -ano | findstr :8000
echo.

echo 4. 检查日志:
if exist "C:\LinkerHand_HTTP_API\service.log" (
    echo 显示最近10行日志:
    powershell "Get-Content 'C:\LinkerHand_HTTP_API\service.log' -Tail 10"
) else (
    echo 日志文件不存在
)
echo.

echo 5. 测试API:
curl -s http://localhost:8000/health
if %errorlevel% equ 0 (
    echo API响应正常
) else (
    echo API无响应
)

pause
```

### 自动更新脚本

```python
# auto_update.py
import requests
import os
import subprocess
from pathlib import Path

def check_for_updates(current_version="3.1.0"):
    """检查更新"""
    try:
        # 从你的更新服务器检查版本
        response = requests.get("https://your-update-server.com/api/version")
        latest_version = response.json()["version"]

        if latest_version > current_version:
            print(f"发现新版本: {latest_version}")
            return True
    except:
        pass
    return False

def update_service():
    """更新服务"""
    print("开始更新...")

    # 停止服务
    subprocess.run(["sc", "stop", "LinkerHandHTTPAPI"])

    # 下载新版本
    # ... 下载逻辑 ...

    # 更新文件
    # ... 替换文件 ...

    # 启动服务
    subprocess.run(["sc", "start", "LinkerHandHTTPAPI"])

    print("更新完成")

if __name__ == "__main__":
    if check_for_updates():
        update_service()
```

## 故障排除

### 常见部署问题

1. **权限问题**
   ```batch
   REM 检查管理员权限
   whoami /groups | find "S-1-16-12288"
   ```

2. **端口冲突**
   ```batch
   REM 查找端口占用
   netstat -ano | findstr :8000
   ```

3. **依赖问题**
   ```batch
   REM 重新安装依赖
   pip install --force-reinstall -r requirements.txt
   ```

4. **服务注册问题**
   ```batch
   REM 清理服务注册
   sc delete LinkerHandHTTPAPI
   ```

### 远程故障排除

```powershell
# remote_troubleshoot.ps1
param([string]$ComputerName)

Invoke-Command -ComputerName $ComputerName -ScriptBlock {
    Write-Host "=== 系统信息 ==="
    Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsArchitecture

    Write-Host "`n=== 服务状态 ==="
    Get-Service -Name "LinkerHandHTTPAPI" -ErrorAction SilentlyContinue

    Write-Host "`n=== 进程状态 ==="
    Get-Process -Name "LinkerHand_HTTP_API" -ErrorAction SilentlyContinue

    Write-Host "`n=== 网络状态 ==="
    Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

    Write-Host "`n=== 磁盘空间 ==="
    Get-PSDrive C | Select-Object Used, Free, @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}
}
```

## 安全考虑

### 服务账户配置

```batch
REM 创建专用服务账户
net user linkerhandservice Password123! /add
net localgroup "Service Accounts" linkerhandservice /add

REM 配置服务使用专用账户
sc config LinkerHandHTTPAPI obj= ".\linkerhandservice" password= "Password123!"
```

### 加密配置

```python
# secure_config.py
import os
from cryptography.fernet import Fernet

def generate_key():
    """生成加密密钥"""
    return Fernet.generate_key()

def encrypt_config(config_data, key):
    """加密配置"""
    f = Fernet(key)
    return f.encrypt(config_data.encode())

def decrypt_config(encrypted_data, key):
    """解密配置"""
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
```

## 总结

选择合适的部署方式：

- **单机部署**: 使用 `deploy_windows.bat`
- **批量部署**: 使用PowerShell脚本
- **企业环境**: 使用组策略或SCCM
- **容器环境**: 使用Docker

确保目标机器满足系统要求，并有适当的权限进行安装。