from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LinkerHand.linker_hand_api import LinkerHandApi

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

@app.post("/hold_pen")
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

@app.post("/open_hand")
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

@app.post("/close_hand")
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

if __name__ == "__main__":
    # 启动服务器
    # 使用app对象而不是字符串，确保打包后能正常运行
    logger.info("=" * 60)
    logger.info("LinkerHand HTTP API 服务启动")
    logger.info(f"服务地址: http://0.0.0.0:8000")
    logger.info(f"日志文件: {log_file_path}")
    logger.info("=" * 60)
    
    try:
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