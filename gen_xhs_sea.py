#!/usr/bin/env python3.12
"""Generate 4 newspaper-style images for 小红书 (4:3 ratio, 1600x1200)"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

W, H = 1600, 1200
font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
OUT = '/mnt/c/Users/Lenovo/Desktop/跨境日报/xhs_output'
os.makedirs(OUT, exist_ok=True)

BG = '#FDFCF8'
TEXT = '#1A1A1A'; TEXT2 = '#3D3D3D'; TEXT3 = '#6B6B6B'
ACCENT = '#C41E3A'; BLUE = '#1A5276'; GREEN = '#1B5E20'; GOLD = '#8B6914'
BORDER = '#D4D0C8'; BORDER_LT = '#E8E4DC'

def f(size):
    return ImageFont.truetype(font_path, size)

def draw_wrapped(draw, text, x, y, max_w, font, color=TEXT, lh=None):
    if lh is None: lh = int(font.size * 1.6)
    lines = []
    for para in text.split('\n'):
        if not para: lines.append(''); continue
        b = draw.textbbox((0,0), para, font=font)
        cw = (b[2]-b[0]) / max(len(para), 1)
        cpl = max(int(max_w / cw), 10)
        lines.extend(textwrap.fill(para, width=cpl).split('\n'))
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        y += lh
    return y

def hline(draw, y, color=BORDER, w=1520, x=40):
    draw.line([(x, y), (x+w, y)], fill=color, width=1)

def card(draw, x, y, w, tag, num, title, desc, source, tc=ACCENT):
    ftag = f(12); fnum = f(40); ftitle = f(22); fdesc = f(16); fsrc = f(13)
    draw.text((x, y), tag.upper(), fill=tc, font=ftag); y += 22
    draw.text((x, y), num, fill=tc, font=fnum)
    nw = draw.textbbox((0,0), num, font=fnum)[2] + 14
    tlines = textwrap.fill(title, width=max(int(w/14), 12))
    draw.text((x+nw, y+8), tlines, fill=TEXT, font=ftitle)
    tb = draw.multiline_textbbox((x+nw, y+8), tlines, font=ftitle)
    y = max(y+50, tb[3]+8)
    y = draw_wrapped(draw, desc, x, y, w, fdesc, TEXT2, 26)
    y += 8; draw.text((x, y), source, fill=TEXT3, font=fsrc)
    return y + 30

# ===== IMG 1: MASTHEAD + LEAD =====
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,6], fill=TEXT)
cx = W//2
d.text((cx,30), 'SOUTHEAST ASIA SPECIAL EDITION', fill=TEXT3, font=f(14), anchor='mt')
d.text((cx,60), '出海早班车 · 东南亚', fill=TEXT, font=f(64), anchor='mt')
d.text((cx,130), '聚焦东南亚六国 · 独立客观 · 数据驱动', fill=TEXT3, font=f(16), anchor='mt')
d.text((cx,165), '2026年5月2日 星期五 | AI情报编辑部 | 印尼·泰国·越南·马来·菲律宾·新加坡', fill=TEXT3, font=f(13), anchor='mt')
hline(d, 185)

y = 210
d.text((60,y), '头版头条 · 合规变革', fill=ACCENT, font=f(14)); y+=30
lt = 'TikTok Shop东南亚推出账号健康分（AHR）\n7月全面取代违规分体系'
d.multiline_text((60,y), lt, fill=TEXT, font=f(36))
y += d.multiline_textbbox((60,y), lt, font=f(36))[3] - y + 20

lb = ('TikTok Shop东南亚跨境站点正式推出全新店铺合规评估体系——账号健康分（AHR）。'
      '5月起开放预览，7月起全面取代现有违规分体系。新体系通过更透明的计分规则，'
      '使商家能实时了解店铺合规状态。对于东南亚六国跨境卖家，这三个月是适配窗口期——'
      'AHR低于阈值将触发流量降权、限制大促甚至关店。')
y = draw_wrapped(d, lb, 60, y, 700, f(20), TEXT2, 32)

# Right sidebar - signal cards
sx, sy = 820, 240
d.text((sx, sy), '东南亚关键信号', fill=TEXT, font=f(26)); sy+=45
for label, val, clr in [
    ('AHR合规', '7月起全面生效', ACCENT),
    ('泰国增值税', '+3%提案引争议', ACCENT),
    ('越南配件', '搜索量周涨89%', BLUE),
    ('TikTok SEA', '年GMV达$456亿', GREEN),
    ('美妆ROAS', '标杆案例达4.73', GOLD),
]:
    d.rectangle([sx,sy,sx+400,sy+48], fill=BORDER_LT, outline=BORDER)
    d.text((sx+15,sy+12), label, fill=clr, font=f(18))
    d.text((sx+220,sy+12), val, fill=TEXT2, font=f(18)); sy+=58

sy+=20
d.rectangle([sx,sy,sx+400,sy+100], fill='#F5F2EB', outline=BORDER)
d.multiline_text((sx+20,sy+15),
    '"东南亚TikTok Shop GMV\n是美区的整整三倍。\n这里是全球社交电商的绝对中心。"',
    fill=TEXT2, font=f(19)); sy+=115
d.text((sx,sy), '综合：Momentum Works · Sensor Tower · TT123', fill=TEXT3, font=f(12))

y = max(y, sy+30); hline(d, y+10); y+=30
d.text((60,y), '数据来源：TikTok Shop卖家中心 | Momentum Works | Sensor Tower | 雨果跨境 | TT123', fill=TEXT3, font=f(14))
img.save(f'{OUT}/sea_01_headline.png')
print("✓ Image 1: Masthead + Lead")

# ===== IMG 2: POLICY & COMPLIANCE =====
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,50], fill=TEXT)
d.text((cx,25), '出海早班车 · 政策与合规', fill=BG, font=f(22), anchor='mm')

y = 80
y = card(d, 60, y, 700, '税收政策 · 泰国', '+3%',
    '泰国拟将本土店增值税从7%上调至10%',
    '泰国财政部提案拟将本土企业增值税率上调3个百分点。对跨境卖家而言，本土店税负增加意味着价格优势被削弱，跨境卖家性价比竞争力相对提升。但需警惕消费者购买力短期承压。',
    '泰国财政部提案 · 雨果跨境 · 东南亚电商观察')
y+=10; hline(d, y, BORDER_LT, 700, 60); y+=20
y = card(d, 60, y, 700, '合规升级 · 印尼', 'BPOM',
    '印尼BPOM化妆品认证执法升级',
    '印尼食品药品监管局加大跨境电商化妆品合规执法力度，多个Shopee/TikTok Shop店铺因缺少BPOM认证被强制下架。印尼是东南亚最大美妆市场（年规模$80亿+），跨境卖家必须先完成BPOM备案。',
    'BPOM官方公告 · Shopee印尼站 · 跨境卖家社群', BLUE)
y+=10; hline(d, y, BORDER_LT, 700, 60); y+=20
y = card(d, 60, y, 700, '支付基建 · 东盟', 'QR',
    '东盟六国统一QR支付码试运行',
    '东盟六国央行联合推动统一QR支付码系统4月启动试运行。全面落地后跨境卖家不再需对接6套本地支付体系，跨境收款成本预计下降40%以上。东南亚数字经济里程碑事件。',
    '东盟央行联合公告 · 东南亚支付白皮书', '#1B5E20')

# Right sidebar
sx, sy = 820, 80
d.rectangle([sx,sy,W-40,H-40], fill='#F5F2EB', outline=BORDER)
d.text((sx+20,sy+15), '⚡ 快速信号', fill=ACCENT, font=f(28)); sy+=55
for title, desc in [
    ('AHR倒计时', 'TikTok Shop东南亚7月全面启用AHR\n5-6月为适配窗口期'),
    ('泰国税改', '增值税7%→10%\n本土店成本上升，跨境性价比提升'),
    ('印尼BPOM', '美妆执法升级\n无证产品面临下架风险'),
    ('QR支付', '六国统一码试运行\n收款成本下降40%'),
    ('Shopee物流', '印尼站运费降8%-15%\n菲律宾站推优选卖家计划'),
]:
    d.rectangle([sx+15,sy,sx+385,sy+54], fill=BG, outline=BORDER_LT)
    d.text((sx+25,sy+6), title, fill=ACCENT, font=f(18))
    d.multiline_text((sx+25,sy+28), desc, fill=TEXT2, font=f(14)); sy+=66

d.rectangle([0,H-50,W,H], fill=TEXT)
d.text((cx,H-25), '出海早班车 · 东南亚特刊 | 2026.05.02 | 多元来源交叉验证', fill=BG, font=f(14), anchor='mm')
img.save(f'{OUT}/sea_02_policy.png')
print("✓ Image 2: Policy & Compliance")

# ===== IMG 3: PRODUCTS & GROWTH =====
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,50], fill=TEXT)
d.text((cx,25), '出海早班车 · 选品情报与增长密码', fill=BG, font=f(22), anchor='mm')

y = 80
cw = 720
for tag, num, title, desc, src in [
    ('选品信号 · 越南', '89%↑', 'Type-C转接头周搜索量飙升',
     '越南站一周搜索量涨89%，竞争不足50家。三星OPPO换机潮拉动配件需求。1688源头价¥1.2-2.8元，终端¥10-16元，毛利55%-70%。选PD快充版做差异化。',
     'TikTok越南热门趋势 · 1688深圳产业带'),
    ('选品信号 · 马来', '3×', '穆斯林时尚品类年增3倍',
     'Modest Fashion年GMV增300%：头巾、长袍、祈祷毯。1688义乌/广州供应链集群已成熟，头巾批发¥3-8元，终端¥15-40元。需注意Halal认证和本地化设计。',
     'TikTok Shop马来站 · 1688义乌产业带'),
    ('选品信号 · 电子', '$12.9', 'TWS蓝牙耳机印尼爆单',
     '一款$12.9的TWS耳机周销5万件：ENC降噪+30h续航+IPX5防水。1688源头¥25-38元/副，终端$9.9-19.9。电子产品需关注各国SIRIM/SNI认证。',
     'TikTok Shop印尼站 · 1688深圳'),
]:
    y = card(d, 60, y, cw, tag, num, title, desc, src, GREEN)

# Right: ROAS + GMV
sx, sy = 820, 80
d.rectangle([sx,sy,W-40,sy+280], fill='#F5F2EB', outline=BLUE)
d.text((sx+20,sy+15), '广告标杆拆解', fill=BLUE, font=f(16))
d.text((sx+20,sy+40), 'ROAS 4.73', fill=BLUE, font=f(48))
d.text((sx+140,sy+55), '东南亚美妆低成本投放', fill=TEXT, font=f(22))
d.multiline_text((sx+20,sy+120),
    '某中国美妆品牌通过"短视频种草+直播收割"\n'
    '在TikTok Shop印尼和越南站实现ROAS 4.73\n\n'
    '核心打法：\n'
    '① 本土KOC矩阵100+素人日常分发\n'
    '② 爆款单品集中投放，非全店推广\n'
    '③ "小样试用→正装复购"转化漏斗',
    fill=TEXT2, font=f(16))
sy+=300

d.rectangle([sx,sy,W-40,sy+200], fill='#F5F2EB', outline=GREEN)
d.text((sx+20,sy+15), 'TikTok电商核心数据', fill=GREEN, font=f(16))
d.text((sx+20,sy+45), '$456亿', fill=GREEN, font=f(52))
d.text((sx+190,sy+60), '东南亚年GMV\n=美国市场×3倍', fill=TEXT, font=f(22))
d.multiline_text((sx+20,sy+115),
    'TikTok Shop全球GMV $643亿(同比+94%)\n'
    '东南亚贡献71% → 增速达翻倍级别\n'
    'Shopee SEA $780亿 → TikTok已逼近60%',
    fill=TEXT2, font=f(15))

d.rectangle([0,H-50,W,H], fill=TEXT)
d.text((cx,H-25), '数据来源：Momentum Works · Sensor Tower · TikTok · 1688 · Shopee', fill=BG, font=f(14), anchor='mm')
img.save(f'{OUT}/sea_03_products.png')
print("✓ Image 3: Products & Growth")

# ===== IMG 4: PLATFORMS & DATA =====
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,50], fill=TEXT)
d.text((cx,25), '出海早班车 · 平台动态与趋势研判', fill=BG, font=f(22), anchor='mm')

y = 80
y = card(d, 60, y, 700, '平台动态 · Shopee', 'SLS',
    'Shopee印尼站跨境运费普降8%-15%',
    'Shopee官方物流SLS宣布5月起下调印尼站费率。$5-$20客单价日用品和配件直接受益。菲律宾站同步推"跨境优选卖家"激励计划，达标享额外流量倾斜。',
    'Shopee卖家中心公告 · 雨果跨境')
y+=10; hline(d, y, BORDER_LT, 700, 60); y+=20
y = card(d, 60, y, 700, '物流 · 菲律宾', '72h',
    '菲律宾海外仓72小时达覆盖率提升至85%',
    '多家物流商海外仓覆盖马尼拉、宿务、达沃。跨境物流体验逼近本土卖家。"海外仓备货+TikTok直播"成菲律宾站标准打法。',
    '物流商公告 · 跨境物流白皮书', GREEN)
y+=10; hline(d, y, BORDER_LT, 700, 60); y+=20
y = card(d, 60, y, 700, '选品 · 家居', 'Home',
    '东南亚"租房经济"催生折叠家具搜索量月增67%',
    '东南亚年轻租房人群比例60%-80%。折叠书桌、便携衣柜、门后收纳架在Shopee和TikTok搜索量月增67%。1688折叠书桌¥35-60元，终端$15-25。适合海外仓。',
    'Shopee数据 · 1688 · 雨果跨境', GOLD)

# Right: Country data table
sx, sy = 820, 80
d.rectangle([sx,sy,W-40,H-40], fill='#F5F2EB', outline=BORDER)
d.text((sx+20,sy+15), '📊 六国电商速览', fill=TEXT, font=f(24)); sy+=55
col_x = [sx+15, sx+100, sx+170, sx+225, sx+325]
for i, h in enumerate(['国家','人口','渗透','平台','热门品类']):
    d.text((col_x[i], sy), h, fill=TEXT3, font=f(13)); sy+=24
hline(d, sy, BORDER, 370, sx+15); sy+=8
for c in [
    ('🇮🇩 印尼','2.81亿','32%','Shopee','美妆·穆斯林·3C'),
    ('🇹🇭 泰国','7180万','48%','Shopee/Lazada','美妆·家居·食品'),
    ('🇻🇳 越南','1.01亿','28%','Shopee/TikTok','3C·服装·家居'),
    ('🇵🇭 菲律宾','1.17亿','22%','Shopee/Lazada','美妆·时尚·配件'),
    ('🇲🇾 马来西亚','3460万','50%','Shopee','穆斯林·3C·美妆'),
    ('🇸🇬 新加坡','600万','72%','Shopee/Amazon','健康·高端美妆'),
]:
    for i, val in enumerate(c):
        d.text((col_x[i], sy), val, fill=TEXT2 if i>0 else TEXT, font=f(13))
    sy+=26
sy+=16
d.text((sx+20,sy), '数据：Momentum Works / e-Conomy SEA 2025', fill=TEXT3, font=f(11))

# Bottom quote
d.rectangle([60,H-110,W-60,H-50], fill='#F5F2EB', outline=ACCENT)
d.text((cx,H-90), '"跨境电商的下一代增长不在欧美，在东南亚。先看懂规则的人先赚钱。"', fill=TEXT, font=f(18), anchor='ma')
d.text((cx,H-60), '出海早班车 · 东南亚特刊', fill=ACCENT, font=f(14), anchor='ma')
img.save(f'{OUT}/sea_04_platforms.png')
print("✓ Image 4: Platforms & Data")

print(f"\n✅ All 4 images saved to {OUT}/")
for fn in sorted(os.listdir(OUT)):
    if fn.endswith('.png'):
        sz = os.path.getsize(f'{OUT}/{fn}') // 1024
        print(f"  {fn} — {sz}KB")
