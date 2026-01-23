# Windows环境打包指南

本指南专门针对在Windows环境下打包LinkerHand HTTP API为独立安装包。

## 🎯 环境准备

### 1. 安装Python和依赖

```batch
# 1. 下载并安装Python 3.8+ (如果还没有)
# 从 https://python.org 下载安装程序
# 安装时务必勾选 "Add Python to PATH"

# 2. 升级pip
python -m pip install --upgrade pip

# 3. 安装项目依赖
pip install -r requirements.txt

# 4. 验证安装
python --version
pip --version
python -c "import PyInstaller, win32api; print('依赖检查通过')"
```

### 2. 验证项目结构

确保项目文件完整：

```
linkerhand-python-sdk/
├── Demo/
│   └── main_http.py          # HTTP API主文件
├── LinkerHand/               # 核心模块
│   ├── __init__.py
│   ├── linker_hand_api.py
│   └── core/
│       ├── can/
│       └── rs485/
└── requirements.txt          # 依赖文件
```

## 🚀 打包方法

### 方法1：一键打包（推荐）

```batch
# 在项目根目录运行
build_windows.bat
```

此脚本会：
- ✅ 检查环境依赖
- ✅ 清理旧的构建文件
- ✅ 创建PyInstaller配置文件
- ✅ 运行打包过程
- ✅ 生成服务相关文件
- ✅ 创建完整的安装包

### 方法2：快速打包

如果一键脚本有问题，使用快速打包：

```batch
# 运行快速打包
quick_build.bat
```

### 方法3：手动打包

如果上述方法都不行，使用手动命令：

```batch
# 确保在项目根目录
cd C:\path\to\linkerhand-python-sdk

# 运行PyInstaller
pyinstaller --onedir ^
    --name LinkerHand_HTTP_Service ^
    --hidden-import LinkerHand.linker_hand_api ^
    --hidden-import LinkerHand.core.can ^
    --hidden-import LinkerHand.core.rs485 ^
    --hidden-import LinkerHand.utils ^
    --hidden-import can ^
    --hidden-import can.interfaces.pcan ^
    --hidden-import minimalmodbus ^
    --hidden-import serial ^
    --hidden-import yaml ^
    --hidden-import fastapi ^
    --hidden-import uvicorn ^
    --hidden-import pydantic ^
    --hidden-import starlette ^
    --hidden-import win32api ^
    --hidden-import win32service ^
    --hidden-import win32serviceutil ^
    --hidden-import servicemanager ^
    --add-data "LinkerHand;LinkerHand" ^
    --noconsole ^
    Demo/main_http.py
```

## 🔧 故障排除

### "Unable to find 'X:\path\LinkerHand'"

**原因**: PyInstaller无法找到LinkerHand目录
**解决**:
1. 确保在项目根目录运行命令
2. 检查LinkerHand目录是否存在
3. 使用绝对路径：
   ```batch
   pyinstaller --add-data "C:\full\path\to\LinkerHand;LinkerHand" ...
   ```

### "ModuleNotFoundError" 错误

**原因**: 缺少隐藏导入
**解决**: 添加相应的 `--hidden-import` 参数

### 打包文件过大

**原因**: 包含太多不必要的模块
**解决**: 添加 `--exclude-module` 参数：
```batch
pyinstaller --exclude-module tkinter --exclude-module matplotlib ...
```

### pywin32安装问题

**原因**: pywin32是Windows专用包
**解决**:
```batch
# 在Windows环境下安装
pip install pywin32

# 或者使用conda
conda install pywin32
```

## 📁 打包结果

成功打包后，`dist/` 目录将包含：

```
dist/
├── LinkerHand_HTTP_Service/          # 主程序目录
│   └── LinkerHand_HTTP_Service.exe   # 可执行文件
├── LinkerHand_Service.py             # 服务包装器
├── install.bat                       # 安装脚本
├── uninstall.bat                     # 卸载脚本
└── README.txt                        # 使用说明
```

## 🧪 测试打包结果

### 1. 测试exe文件
```batch
# 直接运行测试
dist\LinkerHand_HTTP_Service\LinkerHand_HTTP_Service.exe

# 应该看到服务启动信息
```

### 2. 测试服务安装
```batch
# 复制文件到测试目录
mkdir C:\TestLinkerHand
copy dist\* C:\TestLinkerHand\

# 进入测试目录并安装
cd C:\TestLinkerHand
install.bat
```

### 3. 验证API
```batch
# 测试API是否正常
curl http://localhost:8000/health

# 查看API文档
start http://localhost:8000/docs
```

## 📦 部署到其他机器

### 1. 准备部署包
```batch
# 压缩dist目录为部署包
powershell "Compress-Archive -Path 'dist\*' -DestinationPath 'LinkerHand_Deploy.zip'"

# 或者手动复制整个dist目录
```

### 2. 在目标机器上部署
```batch
# 1. 解压部署包到任意目录
# 2. 以管理员身份运行install.bat
# 3. 等待安装完成
# 4. 访问 http://localhost:8000 使用API
```

## ⚙️ 高级配置

### 修改服务配置

编辑 `LinkerHand_Service.py`：

```python
class LinkerHandService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LinkerHandHTTPAPI"              # 服务名称
    _svc_display_name_ = "My Custom Service"      # 显示名称
    _svc_description_ = "Custom description"      # 描述
```

### 修改端口配置

如果需要修改API端口，在打包前修改 `Demo/main_http.py`：

```python
if __name__ == "__main__":
    uvicorn.run(
        "main_http:app",
        host="0.0.0.0",
        port=8080,  # 修改端口
        reload=False,
        log_level="info"
    )
```

### 添加自定义功能

在 `Demo/main_http.py` 中添加新的API端点：

```python
@app.post("/custom_action")
async def custom_action():
    # 自定义逻辑
    return {"status": "success", "message": "Custom action completed"}
```

## 📊 性能优化

### 减小包体积

```batch
# 添加更多排除项
pyinstaller --exclude-module numpy --exclude-module matplotlib ^
    --exclude-module PyQt5 --exclude-module IPython ^
    ... 其他参数
```

### 启用UPX压缩

```batch
# 安装UPX并启用
# UPX会自动减小exe文件大小
pyinstaller --upx-dir "C:\path\to\upx" ... 其他参数
```

## 🔍 日志和调试

### 启用调试模式

```batch
# 添加--debug=all参数查看详细打包过程
pyinstaller --debug=all ... 其他参数
```

### 查看打包日志

打包过程中的详细日志会显示：
- 包含的文件和模块
- 依赖关系分析
- 潜在的问题和警告

## 📞 获取帮助

如果遇到问题：

1. **检查错误信息** - PyInstaller会提供详细的错误描述
2. **验证环境** - 确保所有依赖都正确安装
3. **查看文档** - 参考PyInstaller官方文档
4. **寻求帮助** - 提供完整的错误信息和环境描述

---

**💡 提示**: 首次打包可能需要一些时间，后续打包会快很多。如果遇到问题，建议先用最小化配置测试，然后逐步添加功能。