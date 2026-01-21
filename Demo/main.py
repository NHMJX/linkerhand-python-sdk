from LinkerHand.linker_hand_api import LinkerHandApi


# 定义手部参数
hand_joint = "O6"  # 手部关节数量
hand_type = "left"  # 手部类型
modbus = "None"
can = "PCAN_USBBUS1"  # CAN接口名称，PCAN_USBBUS1。注：蓝色盒子为Linux下can0，WIN下位PCAN_USBBUS1。透明盒子Linux下为can0，WIN下为0

"""初始化LinkerHandApi"""
try:
    o6_hand = LinkerHandApi(hand_joint=hand_joint, hand_type=hand_type, modbus=modbus, can=can)
    print("info", f"手部API初始化成功: {hand_type} {hand_joint}")
except Exception as e:
    print("error", f"API初始化失败: {str(e)}")
    raise

def Hold_pen():
    """设置速度"""
    try:
        speed_values = [60] * 6
        o6_hand.set_speed(speed_values)
    except Exception as e:
        print("error", f"设置速度失败: {str(e)}")

    """设置力矩"""
    try:
        torque_values = [50] * 6
        o6_hand.set_torque(torque_values)
    except Exception as e:
        print("error", f"设置力矩失败: {str(e)}")

    """示例：握笔动作"""
    try:
        # 设置手部关节角度，模拟握笔动作
        o6_hand.finger_move([120, 90, 120, 70, 50, 40])  # 示例角度值
        print("info", "握笔动作执行成功")
    except Exception as e:
        print("error", f"执行握笔动作失败: {str(e)}")

def Open_hand():
    """示例：打开手部"""
    try:
        o6_hand.finger_move([250, 250, 250, 250, 250, 250])  # 打开手部
        print("info", "打开手部成功")
    except Exception as e:
        print("error", f"执行打开手部动作失败: {str(e)}")

def Close_hand():
    """示例：关闭手部"""
    try:
        o6_hand.close_can()  # 关闭CAN接口
        print("info", "关闭手部成功")
    except Exception as e:
        print("error", f"执行关闭手部动作失败: {str(e)}")

def main():
    """主函数"""
    # 通过输入命令控制手部动作
    while True:
        command = input("请输入命令 (\t h: 握住笔\t o: 打开手部\t c: 关闭手部\t q: 退出程序): ")
        if command == "h":
            Hold_pen()
        elif command == "o":
            Open_hand()
        elif command == "c":
            Close_hand()
        elif command == "q":
            print("退出程序")
            break
        else:
            print("无效命令，请重新输入")

if __name__ == "__main__":
    main()
