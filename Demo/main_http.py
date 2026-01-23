from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LinkerHand.linker_hand_api import LinkerHandApi

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
            print("info", f"手部API初始化成功: {hand_type} {hand_joint}")
        except Exception as e:
            print("error", f"API初始化失败: {str(e)}")
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
        hand = get_hand_instance()

        # 设置速度
        speed_values = [60] * 6
        hand.set_speed(speed_values)

        # 设置力矩
        torque_values = [50] * 6
        hand.set_torque(torque_values)

        # 执行握笔动作
        hand.finger_move([120, 90, 120, 70, 50, 40])

        return {"status": "success", "message": "握笔动作执行成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行握笔动作失败: {str(e)}")

@app.post("/open_hand")
async def open_hand():
    """打开手部"""
    try:
        hand = get_hand_instance()
        hand.finger_move([250, 250, 250, 250, 250, 250])
        return {"status": "success", "message": "打开手部成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行打开手部动作失败: {str(e)}")

@app.post("/close_hand")
async def close_hand():
    """关闭手部"""
    try:
        hand = get_hand_instance()
        hand.close_can()
        return {"status": "success", "message": "关闭手部成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行关闭手部动作失败: {str(e)}")

@app.post("/set_speed")
async def set_speed(request: SpeedRequest):
    """设置速度"""
    try:
        hand = get_hand_instance()
        hand.set_speed(request.speeds)
        return {"status": "success", "message": f"设置速度成功: {request.speeds}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置速度失败: {str(e)}")

@app.post("/set_torque")
async def set_torque(request: TorqueRequest):
    """设置力矩"""
    try:
        hand = get_hand_instance()
        hand.set_torque(request.torques)
        return {"status": "success", "message": f"设置力矩成功: {request.torques}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置力矩失败: {str(e)}")

@app.post("/finger_move")
async def finger_move(request: FingerMoveRequest):
    """移动手指到指定位置"""
    try:
        hand = get_hand_instance()
        hand.finger_move(request.positions)
        return {"status": "success", "message": f"移动手指成功: {request.positions}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移动手指失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main_http:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )