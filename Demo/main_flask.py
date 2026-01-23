from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LinkerHand.linker_hand_api import LinkerHandApi

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持，方便前端调用

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

@app.route('/')
def root():
    """根路径，返回API信息"""
    return jsonify({
        "message": "LinkerHand Flask API 服务运行中",
        "version": "1.0.0",
        "endpoints": {
            "/hold_pen": "POST - 执行握笔动作",
            "/open_hand": "POST - 打开手部",
            "/close_hand": "POST - 关闭手部",
            "/set_speed": "POST - 设置速度",
            "/set_torque": "POST - 设置力矩",
            "/finger_move": "POST - 移动手指到指定位置"
        }
    })

@app.route('/hold_pen', methods=['POST'])
def hold_pen():
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

        return jsonify({"status": "success", "message": "握笔动作执行成功"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"执行握笔动作失败: {str(e)}"}), 500

@app.route('/open_hand', methods=['POST'])
def open_hand():
    """打开手部"""
    try:
        hand = get_hand_instance()
        hand.finger_move([250, 250, 250, 250, 250, 250])
        return jsonify({"status": "success", "message": "打开手部成功"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"执行打开手部动作失败: {str(e)}"}), 500

@app.route('/close_hand', methods=['POST'])
def close_hand():
    """关闭手部"""
    try:
        hand = get_hand_instance()
        hand.close_can()
        return jsonify({"status": "success", "message": "关闭手部成功"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"执行关闭手部动作失败: {str(e)}"}), 500

@app.route('/set_speed', methods=['POST'])
def set_speed():
    """设置速度"""
    try:
        data = request.get_json()
        if not data or 'speeds' not in data:
            return jsonify({"status": "error", "message": "缺少speeds参数"}), 400

        speeds = data['speeds']
        if not isinstance(speeds, list) or len(speeds) != 6:
            return jsonify({"status": "error", "message": "speeds必须是包含6个整数的数组"}), 400

        hand = get_hand_instance()
        hand.set_speed(speeds)
        return jsonify({"status": "success", "message": f"设置速度成功: {speeds}"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"设置速度失败: {str(e)}"}), 500

@app.route('/set_torque', methods=['POST'])
def set_torque():
    """设置力矩"""
    try:
        data = request.get_json()
        if not data or 'torques' not in data:
            return jsonify({"status": "error", "message": "缺少torques参数"}), 400

        torques = data['torques']
        if not isinstance(torques, list) or len(torques) != 6:
            return jsonify({"status": "error", "message": "torques必须是包含6个整数的数组"}), 400

        hand = get_hand_instance()
        hand.set_torque(torques)
        return jsonify({"status": "success", "message": f"设置力矩成功: {torques}"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"设置力矩失败: {str(e)}"}), 500

@app.route('/finger_move', methods=['POST'])
def finger_move():
    """移动手指到指定位置"""
    try:
        data = request.get_json()
        if not data or 'positions' not in data:
            return jsonify({"status": "error", "message": "缺少positions参数"}), 400

        positions = data['positions']
        if not isinstance(positions, list) or len(positions) != 6:
            return jsonify({"status": "error", "message": "positions必须是包含6个整数的数组"}), 400

        hand = get_hand_instance()
        hand.finger_move(positions)
        return jsonify({"status": "success", "message": f"移动手指成功: {positions}"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"移动手指失败: {str(e)}"}), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    # 启动Flask服务器
    print("启动LinkerHand Flask API服务...")
    print("服务地址: http://localhost:5000")
    print("API文档: http://localhost:5000/")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )