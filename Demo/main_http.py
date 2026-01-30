from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import threading
import subprocess
import socket
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LinkerHand.linker_hand_api import LinkerHandApi


_proc_lock = threading.Lock()
_current_proc: subprocess.Popen | None = None
# 配置固定的.exe程序路径和参数（请根据实际情况修改）
FIXED_EXE_PATH = r"D:\code\grape-sdk\build\Desktop_Qt_6_10_2_MSVC2022_64bit-Release\test\GrapeCli.exe"  # 请修改为实际的.exe程序路径
# FIXED_EXE_PATH = r"D:\Weixin\Weixin.exe"
FIXED_EXE_ARGS = ["robot"]  # 固定的命令行参数
UDP_HOST = "0.0.0.0"
UDP_PORT = 8001
BUFFER_SIZE = 4096

# 配置日志
def setup_logging():
    """配置日志系统"""
    # 获取可执行文件所在目录或脚本所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建日志目录
    log_dir = os.path.join(base_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件路径（按日期命名）
    log_file = os.path.join(log_dir, f'linkerhand_service_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 文件处理器（按大小轮转，最大10MB，保留5个备份）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 控制台处理器（用于开发环境，打包后不会显示）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return log_file

# 初始化日志
log_file_path = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"日志文件路径: {log_file_path}")
logger.info("LinkerHand HTTP API 服务启动中...")

# 创建FastAPI应用
app = FastAPI(
    title="LinkerHand HTTP API",
    description="LinkerHand机械手控制HTTP API服务",
    version="1.0.0"
)

# 定义请求模型
class SpeedRequest(BaseModel):
    speeds: List[int]

class TorqueRequest(BaseModel):
    torques: List[int]

class FingerMoveRequest(BaseModel):
    positions: List[int]

class ExecuteExeRequest(BaseModel):
    timeout: Optional[int] = 300  # 超时时间（秒），默认5分钟
    wait: Optional[bool] = True  # 是否等待程序执行完成，False为异步执行

# 全局变量存储手部实例
hand_instance = None

def get_hand_instance():
    """获取或创建手部实例"""
    global hand_instance
    if hand_instance is None:
        try:
            # 使用与main.py相同的配置
            hand_joint = "O6"
            hand_type = "left"
            modbus = "None"
            can = "PCAN_USBBUS1"

            hand_instance = LinkerHandApi(hand_joint=hand_joint, hand_type=hand_type, modbus=modbus, can=can)
            logger.info(f"手部API初始化成功: {hand_type} {hand_joint}")
        except Exception as e:
            logger.error(f"API初始化失败: {str(e)}", exc_info=True)
            raise
    return hand_instance

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "LinkerHand HTTP API 服务运行中",
        "version": "1.0.0",
        "endpoints": {
            "/hold_pen": "执行握笔动作",
            "/open_hand": "打开手部",
            "/close_hand": "关闭手部",
            "/set_speed": "设置速度",
            "/set_torque": "设置力矩",
            "/finger_move": "移动手指到指定位置"
        }
    }

@app.post("/hold_pen", status_code=200)
async def hold_pen():
    """执行握笔动作"""
    try:
        logger.info("收到握笔动作请求")
        hand = get_hand_instance()

        # 设置速度
        speed_values = [60] * 6
        hand.set_speed(speed_values)
        logger.info(f"设置速度: {speed_values}")

        # 设置力矩
        torque_values = [50] * 6
        hand.set_torque(torque_values)
        logger.info(f"设置力矩: {torque_values}")

        # 执行握笔动作
        positions = [120, 90, 120, 70, 50, 40]
        hand.finger_move(positions)
        logger.info(f"执行握笔动作，位置: {positions}")

        return {"status": "success", "message": "握笔动作执行成功"}

    except Exception as e:
        logger.error(f"执行握笔动作失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"执行握笔动作失败: {str(e)}")

@app.post("/open_hand", status_code=200)
async def open_hand():
    """打开手部"""
    try:
        logger.info("收到打开手部请求")
        hand = get_hand_instance()
        positions = [250, 250, 250, 250, 250, 250]
        hand.finger_move(positions)
        logger.info(f"打开手部成功，位置: {positions}")
        return {"status": "success", "message": "打开手部成功"}

    except Exception as e:
        logger.error(f"执行打开手部动作失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"执行打开手部动作失败: {str(e)}")

@app.post("/close_hand", status_code=200)
async def close_hand():
    """关闭手部"""
    try:
        logger.info("收到关闭手部请求")
        hand = get_hand_instance()
        hand.close_can()
        logger.info("关闭手部成功")
        return {"status": "success", "message": "关闭手部成功"}

    except Exception as e:
        logger.error(f"执行关闭手部动作失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"执行关闭手部动作失败: {str(e)}")

@app.post("/set_speed")
async def set_speed(request: SpeedRequest):
    """设置速度"""
    try:
        logger.info(f"收到设置速度请求: {request.speeds}")
        hand = get_hand_instance()
        hand.set_speed(request.speeds)
        logger.info(f"设置速度成功: {request.speeds}")
        return {"status": "success", "message": f"设置速度成功: {request.speeds}"}

    except Exception as e:
        logger.error(f"设置速度失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"设置速度失败: {str(e)}")

@app.post("/set_torque")
async def set_torque(request: TorqueRequest):
    """设置力矩"""
    try:
        logger.info(f"收到设置力矩请求: {request.torques}")
        hand = get_hand_instance()
        hand.set_torque(request.torques)
        logger.info(f"设置力矩成功: {request.torques}")
        return {"status": "success", "message": f"设置力矩成功: {request.torques}"}

    except Exception as e:
        logger.error(f"设置力矩失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"设置力矩失败: {str(e)}")

@app.post("/finger_move")
async def finger_move(request: FingerMoveRequest):
    """移动手指到指定位置"""
    try:
        logger.info(f"收到移动手指请求: {request.positions}")
        hand = get_hand_instance()
        hand.finger_move(request.positions)
        logger.info(f"移动手指成功: {request.positions}")
        return {"status": "success", "message": f"移动手指成功: {request.positions}"}

    except Exception as e:
        logger.error(f"移动手指失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"移动手指失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# ==================== 第二个服务：执行.exe程序的服务 ====================

# 创建第二个FastAPI应用（用于执行.exe程序）
exe_app = FastAPI(
    title="Exe Executor API",
    description="执行本地.exe程序的HTTP API服务",
    version="1.0.0"
)

@exe_app.get("/")
async def exe_root():
    """根路径，返回API信息"""
    return {
        "message": "Exe Executor API 服务运行中",
        "version": "1.0.0",
        "exe_path": FIXED_EXE_PATH,
        "exe_args": FIXED_EXE_ARGS,
        "endpoints": {
            "/execute": "执行本地.exe程序（POST，固定参数：robot）",
            "/health": "健康检查"
        }
    }

@exe_app.post("/execute")
async def execute_exe(request: ExecuteExeRequest):
    """执行本地.exe程序（使用固定路径和固定参数）"""
    try:
        logger.info(f"收到执行程序请求，固定参数: {FIXED_EXE_ARGS}")
        
        # 检查文件是否存在
        if not os.path.exists(FIXED_EXE_PATH):
            error_msg = f"程序文件不存在: {FIXED_EXE_PATH}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # 检查是否为.exe文件
        if not FIXED_EXE_PATH.lower().endswith('.exe'):
            error_msg = f"文件不是.exe格式: {FIXED_EXE_PATH}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 构建命令（使用固定参数）
        cmd = [FIXED_EXE_PATH] + FIXED_EXE_ARGS
        
        if request.wait:
            # 同步执行，等待程序完成
            logger.info(f"同步执行程序: {' '.join(cmd)}")
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                logger.info(f"程序执行完成，返回码: {result.returncode}")
                logger.info(f"标准输出: {result.stdout[:500]}")  # 只记录前500字符
                if result.stderr:
                    logger.warning(f"标准错误: {result.stderr[:500]}")
                
                return {
                    "status": "success",
                    "message": "程序执行完成",
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except subprocess.TimeoutExpired:
                error_msg = f"程序执行超时（超过{request.timeout}秒）"
                logger.error(error_msg)
                raise HTTPException(status_code=408, detail=error_msg)
        else:
            # 异步执行，不等待程序完成
            logger.info(f"异步执行程序: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            logger.info(f"程序已启动，PID: {process.pid}")
            return {
                "status": "success",
                "message": "程序已启动（异步执行）",
                "pid": process.pid
            }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"执行程序失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@exe_app.get("/health")
async def exe_health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "exe_path": FIXED_EXE_PATH,
        "exe_args": FIXED_EXE_ARGS
    }

# def run_exe_server():
#     """在独立线程中运行.exe执行服务"""
#     logger.info("=" * 60)
#     logger.info("Exe Executor API 服务启动")
#     logger.info(f"服务地址: http://0.0.0.0:8001")
#     logger.info(f"程序路径: {FIXED_EXE_PATH}")
#     logger.info(f"固定参数: {FIXED_EXE_ARGS}")
#     logger.info("=" * 60)
    
#     try:
#         uvicorn.run(
#             exe_app,
#             host="0.0.0.0",
#             port=8001,
#             reload=False,
#             log_level="info",
#             access_log=True,
#             log_config=None  # 使用我们自己的日志配置
#         )
#     except Exception as e:
#         logger.error(f"Exe Executor服务启动失败: {str(e)}", exc_info=True)
#     finally:
#         logger.info("Exe Executor API 服务已停止")

def run_exe_once_serial(sock: socket.socket, addr):
    """短任务：串行执行；运行中则拒绝；执行完回 DONE <code>"""
    global _current_proc

    # 先在锁里判断是否正在运行 + 启动进程（锁内要短）
    with _proc_lock:
        if _current_proc is not None and _current_proc.poll() is None:
            logger.warning("exe 正在运行，拒绝本次 RUN")
            sock.sendto(b"BUSY", addr)
            return

        cmd = [FIXED_EXE_PATH] + FIXED_EXE_ARGS
        # cmd = FIXED_EXE_PATH
        logger.info(f"启动 exe: {cmd}")

        _current_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    # 锁外等待结束（不影响 UDP 主循环）
    try:
        rc = _current_proc.wait()
        logger.info(f"exe 执行完成，退出码: {rc}")
        sock.sendto(f"DONE {rc}".encode("utf-8"), addr)
    except Exception as e:
        logger.error(f"等待 exe 结束时出错: {e}", exc_info=True)
        sock.sendto(b"ERROR", addr)


def run_exe_server():
    logger.info("=" * 60)
    logger.info("Exe Executor UDP 服务启动（短任务串行）")
    logger.info(f"监听地址: {UDP_HOST}:{UDP_PORT}")
    logger.info(f"程序路径: {FIXED_EXE_PATH}")
    logger.info(f"固定参数: {FIXED_EXE_ARGS}")
    logger.info("=" * 60)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((UDP_HOST, UDP_PORT))
        logger.info("UDP 服务已启动，等待指令...")

        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
            except ConnectionResetError as e:
                if getattr(e, "winerror", None) == 10054:
                    logger.warning("UDP 对端关闭 (WinError 10054)，忽略")
                    continue
                else:
                    raise

            msg = data.decode("utf-8", errors="ignore").strip().upper()

            if msg == "RUN":
                threading.Thread(
                    target=run_exe_once_serial,
                    args=(sock, addr),
                    daemon=True
                ).start()
                sock.sendto(b"ACCEPTED", addr)

            elif msg == "PING":
                sock.sendto(b"PONG", addr)
            else:
                sock.sendto(b"UNKNOWN", addr)

    except Exception as e:
        logger.error(f"UDP 服务异常: {e}", exc_info=True)
    finally:
        sock.close()
        logger.info("Exe Executor UDP 服务已停止")


if __name__ == "__main__":
    # 启动两个服务器
    # 1. LinkerHand API 服务（端口8000）
    # 2. Exe Executor 服务（端口8001）
    
    logger.info("=" * 60)
    logger.info("LinkerHand HTTP API 服务启动")
    logger.info(f"服务地址: http://0.0.0.0:8000")
    logger.info(f"日志文件: {log_file_path}")
    logger.info("=" * 60)
    
    # 在后台线程中启动第二个服务（执行.exe程序的服务）
    exe_thread = threading.Thread(target=run_exe_server, daemon=True)
    exe_thread.start()
    logger.info("Exe Executor服务已在后台线程中启动（端口8001）")
    
    try:
        # 主线程运行LinkerHand API服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True,
            log_config=None  # 使用我们自己的日志配置
        )
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("LinkerHand HTTP API 服务已停止")