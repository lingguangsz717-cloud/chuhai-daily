#!/usr/bin/env python3.12
"""
订阅者管理 + 邮件发送脚本
用法：
  python3.12 send_email.py          # 发送今日日报给所有订阅者
  python3.12 send_email.py --add email@example.com  # 添加订阅者
"""

import sys
import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSCRIBERS_FILE = os.path.join(BASE_DIR, "subscribers.txt")
RESEND_API_KEY = "re_3yiwXcgP_BhMybmnmv8X4eADbg3GKedN3"
FROM_EMAIL = "chuhai-daily@resend.dev"
FROM_NAME = "出海早班车"

def get_subscribers():
    """读取订阅者列表"""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip() and "@" in line]

def add_subscriber(email):
    """添加一个新订阅者"""
    subscribers = get_subscribers()
    if email in subscribers:
        print(f"⚠ {email} 已经订阅过了")
        return
    with open(SUBSCRIBERS_FILE, "a") as f:
        f.write(f"{email}\n")
    print(f"✓ {email} 添加成功！当前共 {len(subscribers)+1} 位订阅者")

def send_daily_report():
    """发送今日日报给所有订阅者"""
    subscribers = get_subscribers()
    if not subscribers:
        print("⚠ 暂无订阅者")
        return
    
    # 读取最新数据
    today = datetime.now().strftime("%Y-%m-%d")
    data_file = os.path.join(BASE_DIR, "data", f"{today}.json")
    
    if not os.path.exists(data_file):
        # 尝试找最新日期的数据文件
        data_dir = os.path.join(BASE_DIR, "data")
        files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')], reverse=True)
        if not files:
            print("⚠ 没有找到日报数据")
            return
        data_file = os.path.join(data_dir, files[0])
    
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # 构建邮件HTML
    html = build_email_html(data)
    
    # 发送
    for email in subscribers:
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                    "to": email,
                    "subject": f"出海早班车 · {data['date']} · {data['headline'][:40]}",
                    "html": html
                },
                timeout=10
            )
            if resp.status_code == 200:
                print(f"✓ 已发送: {email}")
            else:
                print(f"✗ {email} 发送失败: {resp.status_code} {resp.text[:100]}")
        except Exception as e:
            print(f"✗ {email} 发送异常: {e}")
    
    print(f"\n发送完成: {len(subscribers)} 封邮件")

def build_email_html(data):
    """将JSON数据转成邮件HTML"""
    cards_html = ""
    
    region_order = ["us", "sea", "jk", "eu"]
    region_emojis = {"us": "🇺🇸", "sea": "🇲🇾🇻🇳", "jk": "🇰🇷🇯🇵", "eu": "🇪🇺"}
    region_colors = {"us": "#3b82f6", "sea": "#22c55e", "jk": "#ef4444", "eu": "#f59e0b"}
    
    for key in region_order:
        if key not in data["regions"]:
            continue
        region = data["regions"][key]
        emoji = region_emojis.get(key, "")
        color = region_colors.get(key, "#3b82f6")
        
        cards_html += f'<h2 style="color:{color};margin-top:40px;border-bottom:2px solid {color};padding-bottom:8px">{emoji} {region["name"]}</h2>'
        
        for card in region["cards"]:
            cards_html += f'''
            <div style="background:#161d2b;border-left:4px solid {color};margin:16px 0;padding:20px 24px;border-radius:0 8px 8px 0">
              <span style="display:inline-block;background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15);color:{color};padding:3px 12px;border-radius:12px;font-size:12px;font-weight:600;margin-bottom:12px">{card["tag"]}</span>
              <div style="font-size:36px;font-weight:800;color:{color};margin:8px 0">{card["number"]}</div>
              <h3 style="color:#e2e8f0;margin:8px 0;font-size:18px">{card["title"]}</h3>
              <p style="color:#94a3b8;font-size:14px;line-height:1.8">{card["body"]}</p>
              <p style="color:#64748b;font-size:12px;margin-top:12px">📊 {card["source_text"]}</p>
            </div>'''
    
    html = f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head><meta charset="UTF-8"></head>
    <body style="background:#0a0e17;color:#e2e8f0;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;padding:0;margin:0">
      <div style="max-width:680px;margin:0 auto;padding:32px 24px">
        <div style="text-align:center;padding:24px 0;border-bottom:1px solid #1e293b;margin-bottom:32px">
          <h1 style="font-size:28px;margin:0;font-weight:800">⚡ 出海早班车</h1>
          <p style="color:#64748b;font-size:13px;margin:8px 0 0">{data["date"]} · Vol.{data["vol"]}</p>
        </div>
        
        <h2 style="color:#3b82f6;font-size:22px;line-height:1.4">{data["headline"]}</h2>
        <p style="color:#94a3b8">{data["subheadline"]}</p>
        
        {cards_html}
        
        <div style="text-align:center;padding:32px 0;border-top:1px solid #1e293b;margin-top:40px;color:#64748b;font-size:12px">
          <p>出海早班车 · AI驱动的跨境市场情报 · 每个工作日8:00更新</p>
          <p><a href="https://lingguangsz717-cloud.github.io/chuhai-daily/" style="color:#3b82f6">查看在线版</a></p>
        </div>
      </div>
    </body>
    </html>'''
    
    return html

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--add":
        add_subscriber(sys.argv[2])
    else:
        send_daily_report()
