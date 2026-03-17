#!/usr/bin/env python3
"""
钉钉消息发送脚本 - GitHub Actions 版本
用于向钉钉群发送文本消息
支持加签验证
"""

import os
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


def generate_sign(secret: str, timestamp: int) -> str:
    """
    生成钉钉机器人签名

    参数:
        secret: 机器人密钥（SEC开头）
        timestamp: 时间戳（毫秒）

    返回:
        签名后的字符串
    """
    # 拼接字符串：timestamp + \n + secret
    string_to_sign = f"{timestamp}\n{secret}"

    # 使用 HMAC-SHA256 加密
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # Base64 编码
    sign = base64.b64encode(hmac_code).decode('utf-8')

    # URL 编码
    sign = urllib.parse.quote(sign)

    return sign


def send_dingtalk_message(webhook_url: str, message: str, secret: str = None):
    """
    发送文本消息到钉钉群

    参数:
        webhook_url: 钉钉机器人Webhook URL
        message: 要发送的消息内容
        secret: 机器人密钥（可选，用于加签验证）

    返回:
        返回发送结果字典
    """
    headers = {
        'Content-Type': 'application/json'
    }

    # 如果提供了密钥，添加签名参数
    if secret:
        timestamp = int(time.time() * 1000)
        sign = generate_sign(secret, timestamp)

        # 在 URL 中添加 timestamp 和 sign 参数
        if '?' in webhook_url:
            webhook_url += f"&timestamp={timestamp}&sign={sign}"
        else:
            webhook_url += f"?timestamp={timestamp}&sign={sign}"

    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }

    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=data,
            timeout=10
        )

        result = response.json()

        if result.get('errcode') != 0:
            print(f"❌ 发送失败: {result.get('errmsg')} (错误码: {result.get('errcode')})")
            return False
        else:
            print("✅ 消息发送成功！")
            return True

    except Exception as e:
        print(f"❌ 发送失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 从环境变量读取配置
    webhook_url = os.getenv("DINGTALK_WEBHOOK_URL")
    secret = os.getenv("DINGTALK_SECRET")

    if not webhook_url or not secret:
        print("❌ 错误: 缺少必需的环境变量 DINGTALK_WEBHOOK_URL 或 DINGTALK_SECRET")
        exit(1)

    # 消息内容
    message = (
        "🏃 健身打卡提醒！\n\n"
        "现在是晚上8点30分，该去锻炼了！\n\n"
        "今日运动目标：[请根据实际情况填写]\n\n"
        "记得记录你的运动数据哦~ 💪"
    )

    # 发送消息
    success = send_dingtalk_message(webhook_url, message, secret)

    if not success:
        exit(1)
