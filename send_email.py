#!/usr/bin/env python3.12
"""
订阅者管理 + 邮件发送脚本（Gmail SMTP，每天免费500封）
用法：
  python3.12 send_email.py          # 发送今日日报给所有订阅者
  python3.12 send_email.py --add email@example.com  # 添加订阅者
"""

import sys
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSCRIBERS_FILE = os.path.join(BASE_DIR, "subscribers.txt")

# Gmail SMTP 配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
FROM_EMAIL = "1099064876@qq.com"
FROM_PASSWORD = "phtnghaypycheiij"
FROM_NAME = "出海早班车"

def get_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip() and "@" in line]

def add_subscriber(email):
    subscribers = get_subscribers()
    if email in subscribers:
        print(f"  {email} 已经订阅过了")
        return
    with open(SUBSCRIBERS_FILE, "a") as f:
        f.write(f"{email}\n")
    print(f"  {email} 添加成功！当前共 {len(subscribers)+1} 位订阅者")

def send_daily_report():
    subscribers = get_subscribers()
    if not subscribers:
        print("  暂无订阅者")
        return

    # 读取数据
    data_dir = os.path.join(BASE_DIR, "data")
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')], reverse=True)
    if not files:
        print("  没有找到日报数据")
        return

    with open(os.path.join(data_dir, files[0]), "r") as f:
        data = json.load(f)

    html = build_email_html(data)

    # 连接 Gmail SMTP
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(FROM_EMAIL, FROM_PASSWORD.replace(" ", ""))

    for email in subscribers:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg["To"] = email
            msg["Subject"] = f"出海早班车 · {data['date']} · {data['headline'][:40]}..."
            msg.attach(MIMEText(html, "html", "utf-8"))
            server.sendmail(FROM_EMAIL, email, msg.as_string())
            print(f"  {email} 发送成功")
        except Exception as e:
            print(f"  {email} 发送失败: {e}")

    server.quit()
    print(f"\n发送完成: {len(subscribers)} 封邮件")

def build_email_html(data):
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
              <span style="display:inline-block;background:rgba(59,130,246,0.15);color:{color};padding:3px 12px;border-radius:12px;font-size:12px;font-weight:600;margin-bottom:12px">{card["tag"]}</span>
              <div style="font-size:36px;font-weight:800;color:{color};margin:8px 0">{card["number"]}</div>
              <h3 style="color:#e2e8f0;margin:8px 0;font-size:18px">{card["title"]}</h3>
              <p style="color:#94a3b8;font-size:14px;line-height:1.8">{card["body"]}</p>
              <p style="color:#64748b;font-size:12px;margin-top:12px"> {card["source_text"]}</p>
            </div>'''

    return f'''
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
          <p><a href="https://lingguangsz717-cloud.github.io/chuhai-daily/" style="color:#3b82f6">查看在线版</a> · <a href="https://lingguangsz717-cloud.github.io/chuhai-daily/" style="color:#ef4444">取消订阅</a></p>
        </div>
      </div>
    </body>
    </html>'''

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--add":
        add_subscriber(sys.argv[2])
    else:
        send_daily_report()
