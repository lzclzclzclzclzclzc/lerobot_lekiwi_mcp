import json
import time
import os
from fastmcp import FastMCP
import pynput

mcp = FastMCP(name="Robot_Control", host="127.0.0.1", port=12345)

ACTIONS_FILE = "actions.json"

# 初始化空的 JSON 文件
def init_actions_file():
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def save_action(key: str, duration: int, timestamp: int, desc: str):
    """将动作追加写入 JSON 文件"""
    with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
        actions = json.load(f)

    actions.append({
        "key": key,
        "duration": duration,
        "timestamp": timestamp,
        "description": desc
    })

    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=4)


# === 分开的动作函数 ===
@mcp.tool
def forward(duration: int, timestamp: int):
    """
    向前走
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("w", duration, timestamp, "向前走")
    return f"已添加动作: 向前走 {duration}ms @ {timestamp}ms"


@mcp.tool
def backward(duration: int, timestamp: int):
    """
    向后退
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("s", duration, timestamp, "向后退")
    return f"已添加动作: 向后退 {duration}ms @ {timestamp}ms"


@mcp.tool
def left(duration: int, timestamp: int):
    """向左走
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("a", duration, timestamp, "向左走")
    return f"已添加动作: 向左走 {duration}ms @ {timestamp}ms"


@mcp.tool
def right(duration: int, timestamp: int):
    """
    向右走
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("d", duration, timestamp, "向右走")
    return f"已添加动作: 向右走 {duration}ms @ {timestamp}ms"

@mcp.tool
def rotate_left(duration: int, timestamp: int):
    """
    逆时针旋转
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("z", duration, timestamp, "逆时针旋转")
    return f"已添加动作: 逆时针旋转 {duration}ms @ {timestamp}ms"

@mcp.tool
def rotate_right(duration: int, timestamp: int):
    """
    顺时针旋转
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("x", duration, timestamp, "顺时针旋转")
    return f"已添加动作: 顺时针旋转 {duration}ms @ {timestamp}ms"

@mcp.tool
def speed_down(duration: int, timestamp: int):
    """
    减速
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("f", duration, timestamp, "减速")
    return f"已添加动作: 减速 {duration}ms @ {timestamp}ms"

@mcp.tool
def speed_up(duration: int, timestamp: int):
    """
    加速
    :param duration: 持续时间，单位毫秒
    :param timestamp: 时间戳，单位毫秒
    """
    save_action("r", duration, timestamp, "加速")
    return f"已添加动作: 加速 {duration}ms @ {timestamp}ms"

@mcp.tool
def execute_actions():
    """
    写完动作后调用此函数，触发执行
    """
    run_actions()
    return "动作执行完成"

def run_actions():
    """按照 JSON 文件执行动作）"""
    with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
        actions = json.load(f)

    if not actions:
        print("没有动作可执行")
        return

    # 转换成事件
    events = []
    for action in actions:
        key = action["key"]
        duration = action["duration"]
        timestamp = action["timestamp"]
        desc = action.get("description", "")

        # 按下
        events.append({
            "action": "press",
            "key": key,
            "timestamp": timestamp,
            "description": desc
        })
        # 松开
        events.append({
            "action": "release",
            "key": key,
            "timestamp": timestamp + duration,
            "description": desc
        })

    # 按时间戳排序
    events.sort(key=lambda x: x["timestamp"])

    keyboard = pynput.keyboard.Controller()
    start_time = time.time() * 1000 

    for event in events:
        action = event["action"]
        key = event["key"]
        timestamp = event["timestamp"]
        desc = event.get("description", "")

        # 等待到时间点
        now = time.time() * 1000
        wait_time = (start_time + timestamp) - now
        if wait_time > 0:
            time.sleep(wait_time / 1000)

        # 执行动作
        if action == "press":
            keyboard.press(key)
            print(f"[{timestamp}ms] 按下 {key} ({desc})")
        elif action == "release":
            keyboard.release(key)
            print(f"[{timestamp}ms] 松开 {key} ({desc})")

    print("所有动作执行完成")
    init_actions_file()  # 执行后清空 JSON



def main():
    init_actions_file()
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
