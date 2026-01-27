#!/bin/bash
# LinkerHand HTTP API服务启动脚本（macOS版本）

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        LinkerHand HTTP API服务 - macOS启动模式            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}[1/4] 检查环境...${NC}"
echo "项目目录: $PROJECT_DIR"

# 切换到项目根目录
cd "$PROJECT_DIR"
echo "当前目录: $(pwd)"
echo

echo -e "${BLUE}[2/4] 检查Python...${NC}"
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python未找到${NC}"
    echo "   请确保Python已安装"
    echo "   可以通过以下命令安装："
    echo "   brew install python"
    exit 1
fi

# 优先使用python3，否则使用python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Python可用${NC}"
echo "   命令: $PYTHON_CMD"
$PYTHON_CMD --version
echo

echo -e "${BLUE}[3/4] 检查文件...${NC}"
if [ ! -f "Demo/main_http.py" ]; then
    echo -e "${RED}❌ 找不到 Demo/main_http.py${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 找到 main_http.py${NC}"
echo

echo -e "${BLUE}[4/4] 检查依赖...${NC}"
echo "测试导入必要的模块..."

# 测试基本导入
$PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, '.')

try:
    import fastapi
    print('✅ FastAPI 已安装')
except ImportError:
    print('❌ FastAPI 未安装')
    print('   请运行: pip install fastapi uvicorn')
    sys.exit(1)

try:
    import uvicorn
    print('✅ Uvicorn 已安装')
except ImportError:
    print('❌ Uvicorn 未安装')
    print('   请运行: pip install uvicorn')
    sys.exit(1)

try:
    import pydantic
    print('✅ Pydantic 已安装')
except ImportError:
    print('❌ Pydantic 未安装')
    print('   请运行: pip install pydantic')
    sys.exit(1)

# 测试项目导入
try:
    import LinkerHand.linker_hand_api
    print('✅ LinkerHand API 模块导入成功')
except ImportError as e:
    print('❌ LinkerHand API 模块导入失败:', str(e))
    print('   请确保LinkerHand模块在Python路径中')
    sys.exit(1)

print('✅ 所有依赖检查通过')
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 依赖检查失败${NC}"
    echo "   请检查上述错误信息并安装缺失的包"
    exit 1
fi

echo
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   启动服务...                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${GREEN}🌟 服务启动信息：${NC}"
echo "   命令: $PYTHON_CMD Demo/main_http.py"
echo "   访问地址: http://localhost:8000 (LinkerHand API)"
echo "   访问地址: http://localhost:8001 (Exe Executor API)"
echo
echo -e "${YELLOW}⚠️  按 Ctrl+C 停止服务${NC}"
echo

# 启动服务
$PYTHON_CMD Demo/main_http.py

echo
echo -e "${GREEN}✅ 服务已停止${NC}"