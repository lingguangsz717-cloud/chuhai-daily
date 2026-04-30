"""
跨境日报 - 每日数据生成器
用法: python3.12 generate_daily.py [date]
      date 格式: 2026-05-01（默认今天）
      
产出: data/{date}.json
更新: index.html 自动读取最新数据（修改 DATA_FILE 变量）

工作流程:
  1. 我（AI）每天凌晨自动生成新的 JSON 数据文件
  2. 写入 data/YYYY-MM-DD.json
  3. 网页 index.html 中修改 fetch 路径指向最新文件
  4. git push 到 GitHub Pages → 自动部署
  
或者：
  1. 运行时自动生成今日数据
  2. 更新 index.html 中的 fetch 指向
"""

import json
import os
import sys
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


def generate_date(date_str: str = None):
    """生成指定日期的基础数据模板"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    today = datetime.strptime(date_str, "%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    vol_num = (today - datetime(2026, 4, 30)).days + 1  # 首期4月30日=Vol.001
    
    # ============================================================
    # 基础模板（每天运行时替换为最新数据）
    # ============================================================
    template = {
        "date": date_str,
        "vol": f"{vol_num:03d}",
        
        # ⚠️ 以下内容每天需由AI更新 ⚠️
        "headline": f"{today.month}.{today.day} 美区跨境速览：[今日头条占位]",
        "subheadline": "5个品类 × 5个信号 · 今日美区大盘异动",
        
        "summary": [
            {"value": "[%]", "label": "[品类1]", "color": "blue"},
            {"value": "[%]", "label": "[品类2]", "color": "green"},
            {"value": "[%]", "label": "[品类3]", "color": "red"},
            {"value": "[%]", "label": "[品类4]", "color": "gold"},
        ],
        
        "regions": {
            "us": {
                "name": "美区",
                "flag": "🇺🇸",
                "color": "blue",
                "cards": [
                    {
                        "tag": "[品类标签]",
                        "number": "[数据]",
                        "title": "[标题 - 用数据做钩子]",
                        "body": "[正文 - 3-5句话：数据来源 + 背后原因 + 对卖家的实际意义 + 下一步建议]",
                        "source_text": "[来源名称]",
                        "source_url": "https://..."
                    },
                    # ... 至少4条，最多5条
                ]
            },
            # ... 其他三个区域同理
        }
    }
    
    return template, date_str


def update_index(date_str: str):
    """更新 index.html 中的 fetch 路径指向新的 JSON 文件"""
    json_filename = f"data/{date_str}.json"
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    import re
    old = re.search(r"fetch\('data/[^']+\.json'\)", html)
    if old:
        html = html.replace(old.group(), f"fetch('{json_filename}')")
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ index.html 已更新 → 指向 {json_filename}")
    else:
        print(f"  ⚠ 未找到 fetch 路径，请手动更新 index.html → {json_filename}")


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    
    template, date_str = generate_date(date_str)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    filepath = os.path.join(DATA_DIR, f"{date_str}.json")
    
    # 检查是否已存在
    if os.path.exists(filepath):
        print(f"⚠ {filepath} 已存在，跳过生成")
        return
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 数据模板已生成: {filepath}")
    print(f"  日期: {date_str}")
    print(f"  ⚠ 请用AI填充模板中的占位数据后，即可使用")
    print()
    
    # 自动更新 index.html
    update_index(date_str)


if __name__ == "__main__":
    main()
