#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人消息推送工具
支持文本消息、加签验证、Markdown格式
"""

import os
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
import json
import argparse
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请执行: pip install requests")
    sys.exit(1)


def generate_signature(secret: str, timestamp: int) -> str:
    """生成钉钉机器人签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return signature


def build_webhook_url(webhook_url: str, secret: str) -> str:
    """构建带签名的完整Webhook URL"""
    timestamp = int(time.time() * 1000)
    signature = generate_signature(secret, timestamp)
    return f"{webhook_url}&timestamp={timestamp}&sign={signature}"


def send_text_message(
    webhook_url: str,
    secret: str,
    content: str,
    at_mobiles: Optional[list] = None,
    is_at_all: bool = False
) -> Dict[str, Any]:
    """发送文本消息"""
    url = build_webhook_url(webhook_url, secret)
    
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    if at_mobiles or is_at_all:
        data["at"] = {
            "atMobiles": at_mobiles or [],
            "isAtAll": is_at_all
        }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"success": True, "data": result}
        else:
            return {
                "success": False,
                "error": result.get("errmsg", "未知错误"),
                "errcode": result.get("errcode")
            }
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求失败: {str(e)}"}


def send_markdown_message(
    webhook_url: str,
    secret: str,
    title: str,
    text: str,
    at_mobiles: Optional[list] = None,
    is_at_all: bool = False
) -> Dict[str, Any]:
    """发送Markdown消息"""
    url = build_webhook_url(webhook_url, secret)
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        }
    }
    
    if at_mobiles or is_at_all:
        data["at"] = {
            "atMobiles": at_mobiles or [],
            "isAtAll": is_at_all
        }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"success": True, "data": result}
        else:
            return {
                "success": False,
                "error": result.get("errmsg", "未知错误"),
                "errcode": result.get("errcode")
            }
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"请求失败: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="钉钉机器人消息推送工具")
    
    parser.add_argument("--webhook", required=True, help="钉钉机器人Webhook地址")
    parser.add_argument("--secret", required=True, help="加签密钥")
    parser.add_argument("--type", choices=["text", "markdown"], default="text", help="消息类型")
    parser.add_argument("--content", help="消息内容（文本消息）")
    parser.add_argument("--title", help="消息标题（Markdown消息）")
    parser.add_argument("--text", help="Markdown内容")
    parser.add_argument("--at-mobiles", nargs="*", help="@的手机号列表")
    parser.add_argument("--at-all", action="store_true", help="@所有人")
    
    args = parser.parse_args()
    
    webhook_url = args.webhook
    secret = args.secret
    
    if args.type == "text":
        if not args.content:
            print("错误: 文本消息需要提供 --content 参数")
            sys.exit(1)
        
        result = send_text_message(
            webhook_url,
            secret,
            args.content,
            at_mobiles=args.at_mobiles,
            is_at_all=args.at_all
        )
    
    elif args.type == "markdown":
        if not args.title or not args.text:
            print("错误: Markdown消息需要提供 --title 和 --text 参数")
            sys.exit(1)
        
        result = send_markdown_message(
            webhook_url,
            secret,
            args.title,
            args.text,
            at_mobiles=args.at_mobiles,
            is_at_all=args.at_all
        )
    
    if result["success"]:
        print(f"✓ 消息发送成功")
        print(f"响应: {result['data']}")
    else:
        print(f"✗ 消息发送失败: {result['error']}")
        if result.get("errcode"):
            print(f"错误码: {result['errcode']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
