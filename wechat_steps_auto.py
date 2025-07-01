import requests
import logging
import random
import time
import os
from datetime import datetime
from wx_msg import send_wx  # 企业微信推送函数

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def get_env_or_default(key, default=None, cast_func=str):
    val = os.getenv(key)
    if val is not None and val != "":
        try:
            return cast_func(val)
        except:
            return default
    return default

def submit_wechat_steps(username, password, steps=None):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Origin': 'https://wzz.wangzouzou.com',
        'Referer': 'https://wzz.wangzouzou.com/',
    }
    url = "https://wzz.wangzouzou.com/motion/api/motion/Xiaomi"
    if steps is None:
        steps = random.randint(20000, 30000)

    data = {
        "phone": username,
        "pwd": password,
        "num": steps
    }

    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            result = r.json()
            if result.get('code') == 200:
                return True, f"🎉 微信步数提交成功，步数：{steps}", steps
            else:
                return False, f"❌ 提交失败：{result.get('data', '未知错误')}", steps
        else:
            return False, f"❌ 服务器错误，状态码：{r.status_code}", steps
    except Exception as e:
        return False, f"❌ 请求异常：{str(e)}", steps

def daily_task():
    logging.info("开始执行微信步数提交任务...")

    # 从环境变量获取配置
    username = get_env_or_default("WX_PHONE") or ""
    password = get_env_or_default("WX_PASS") or ""
    steps = get_env_or_default("WX_STEPS", None, int)

    corpid = get_env_or_default("WX_CORPID") or ""
    corpsecret = get_env_or_default("WX_SECRET") or ""
    agentid = get_env_or_default("WX_AGENTID") or ""

    if not all([username, password, corpid, corpsecret, agentid]):
        print("❌ 缺少必要的环境变量，请检查 WX_PHONE / WX_PASS / WX_CORPID / WX_SECRET / WX_AGENTID 是否设置")
        return

    # 1. 提交步数
    success, msg, _ = submit_wechat_steps(username, password, steps)

    # 2. 构造并推送消息
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[微信步数刷步通知]\n时间：{now}\n{msg}"
    print(full_msg)
    send_wx(full_msg, corpid, corpsecret, agentid)

if __name__ == "__main__":
    daily_task()
