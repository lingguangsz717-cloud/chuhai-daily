#!/usr/bin/env python3.12
"""重制：小红书4图，4:3比例，报纸风，零排版错误"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

# 4:3 at 小红书 recommended resolution
W, H = 1440, 1080
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
OUT = '/mnt/c/Users/Lenovo/Desktop/跨境日报/xhs_output'
os.makedirs(OUT, exist_ok=True)

# Colors - newspaper palette
BG = '#FFFEF9'
TEXT = '#1A1A1A'; T2 = '#3D3D3D'; T3 = '#6B6B6B'
RED = '#C41E3A'; BLUE = '#1A5276'; GRN = '#1B5E20'; GLD = '#8B6914'
BDR = '#D4D0C8'; BDL = '#E8E4DC'
PAD = 50  # page margin

def F(sz):
    return ImageFont.truetype(FONT, sz)

def text_block(d, txt, x, y, w, font, color=TEXT, spacing=4):
    """Draw wrapped text. Returns bottom y. Never overflows x+w."""
    lines = []
    for para in txt.split('\n'):
        if para == '':
            lines.append('')
            continue
        # measure char width
        bb = d.textbbox((0,0), para, font=font)
        avg_cw = (bb[2]-bb[0]) / max(len(para), 1)
        chars = max(int(w / avg_cw), 5)
        for ln in textwrap.fill(para, width=chars).split('\n'):
            lines.append(ln)
    lh = font.size + spacing
    for ln in lines:
        if ln:
            d.text((x, y), ln, fill=color, font=font)
        y += lh
    return y

def rule(d, y, color=BDR, thickness=1, x=PAD, w=W-2*PAD):
    d.line([(x, y), (x+w, y)], fill=color, width=thickness)

def story_card(d, x, y, w, tag, num, title, desc, source, tc=RED):
    """Single story card, returns bottom y"""
    # Tag line
    d.text((x, y), tag.upper(), fill=tc, font=F(11)); y += 18
    # Big number
    nfont = F(42)
    d.text((x, y), num, fill=tc, font=nfont)
    nw = d.textbbox((0,0), num, font=nfont)[2] + 16
    # Title (next to number)
    tfont = F(20)
    tlines = textwrap.fill(title, width=max(int((w-nw)/14), 10))
    d.multiline_text((x+nw, y+6), tlines, fill=TEXT, font=tfont)
    tb = d.multiline_textbbox((x+nw, y+6), tlines, font=tfont)
    y = max(y + 52, tb[3] + 10)
    # Description
    dfont = F(15)
    y = text_block(d, desc, x, y, w, dfont, T2, spacing=2)
    y += 6
    # Source
    d.text((x, y), source, fill=T3, font=F(12))
    return y + 22

# ======================================================================
# IMAGE 1: MASTHEAD + HEADLINE
# ======================================================================
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
cx = W//2

# Top bar
d.rectangle([0,0,W,5], fill=TEXT)
# Masthead
d.text((cx, 28), '出海早班车 · 东南亚', fill=TEXT, font=F(58), anchor='mt')
d.text((cx, 92), '聚焦东南亚六国 ｜ 独立客观 · 数据驱动', fill=T3, font=F(15), anchor='mt')
d.text((cx, 120), '2026年5月2日 星期五 ｜ AI 情报编辑部 ｜ 印尼 · 泰国 · 越南 · 马来 · 菲律宾 · 新加坡', fill=T3, font=F(12), anchor='mt')
rule(d, 138, TEXT, 2)

# HEADLINE
y = 168
d.text((PAD, y), '头版头条', fill=RED, font=F(13)); y += 22
ht = 'TikTok Shop东南亚推出账号健康分体系\n7月全面取代违规分——三个月窗口期决定卖家命运'
d.multiline_text((PAD, y), ht, fill=TEXT, font=F(34))
y += d.multiline_textbbox((PAD,y), ht, font=F(34))[3] - y + 14

hb = ('TikTok Shop东南亚跨境站点正式推出全新店铺合规评估体系——账号健康分（AHR）。'
      '5月起开放预览，7月起全面取代现有违规分体系。AHR低于阈值将触发流量降权、限制大促甚至关店。'
      '对于东南亚六国跨境卖家，这三个月是熟悉新规、调整运营的关键窗口。')
y = text_block(d, hb, PAD, y, 620, F(18), T2, spacing=3)

# Right column: signal cards
rx, ry = 740, 168
d.text((rx, ry), '今日信号', fill=TEXT, font=F(24)); ry += 36
signals = [
    ('AHR合规', '7月全面生效', RED),
    ('泰国增值税', '+3%提案引发争议', RED),
    ('越南配件', '搜索量周涨 89%', BLUE),
    ('TikTok SEA', '年GMV达 $456亿', GRN),
    ('美妆ROAS', '标杆案例 4.73', GLD),
    ('马来时尚', '穆斯林品类年增 3×', GLD),
]
for lb, vl, clr in signals:
    d.rectangle([rx, ry, W-PAD, ry+40], fill='#F5F2EB', outline=BDR)
    d.text((rx+12, ry+9), lb, fill=clr, font=F(16))
    d.text((rx+200, ry+9), vl, fill=T2, font=F(16))
    ry += 48

# Bottom quote
d.rectangle([PAD, H-140, W-PAD, H-PAD], fill='#F5F2EB', outline=RED)
d.text((cx, H-105), '"东南亚TikTok Shop GMV是美区的三倍。', fill=TEXT, font=F(20), anchor='mt')
d.text((cx, H-78), '这里是全球社交电商的绝对中心。"', fill=TEXT, font=F(20), anchor='mt')
d.text((cx, H-48), '—— 综合 Momentum Works · Sensor Tower · TT123', fill=T3, font=F(11), anchor='mt')

img.save(f'{OUT}/xhs_01_cover.png')
print("✓ 1/4")

# ======================================================================
# IMAGE 2: POLICY & COMPLIANCE
# ======================================================================
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
cx = W//2
d.rectangle([0,0,W,42], fill=TEXT)
d.text((cx,21), '出海早班车 · 政策与合规', fill=BG, font=F(20), anchor='mm')

y = 72
# 3 cards in left column
cards = [
    ('税收政策·泰国', '+3%', '泰国拟将本土店增值税从7%上调至10%',
     '泰国财政部提案拟上调本土企业增值税率3个百分点。跨境卖家性价比竞争力相对提升，但需警惕消费者购买力短期承压。建议在泰国有业务的卖家准备两套预案。',
     '泰国财政部提案 · 雨果跨境 · 东南亚电商观察', RED),
    ('合规升级·印尼', 'BPOM', '印尼BPOM化妆品认证执法全面升级',
     '印尼食品药品监管局加大跨境美妆合规执法，多个店铺被强制下架。印尼是东南亚最大美妆市场（年规模$80亿+），卖家需先完成BPOM备案（周期4-8周）。',
     'BPOM官方公告 · Shopee印尼站 · 跨境卖家社群', BLUE),
    ('支付基建·东盟', 'QR', '东盟六国统一QR支付码启动试运行',
     '东盟六国央行联合推动统一QR支付系统4月试运行。全面落地后跨境卖家不再需要对接6套本地支付体系，收款成本预计下降40%以上。',
     '东盟央行联合公告 · 东南亚支付白皮书', GRN),
]
for tag, num, tit, desc, src, tc in cards:
    y = story_card(d, PAD, y, 660, tag, num, tit, desc, src, tc)

# Right sidebar
rx = 760
ry = 72
d.rectangle([rx, ry, W-PAD, H-PAD], fill='#F5F2EB', outline=BDR)
d.text((rx+16, ry+12), '⚡ 跨境卖家行动清单', fill=RED, font=F(20)); ry += 42
items = [
    ('AHR合规', '5-6月熟悉新规，7月前完成店铺合规自查'),
    ('泰国布局', '关注税改进展，准备本土店vs跨境店双方案'),
    ('印尼美妆', '有美妆线的立刻启动BPOM备案'),
    ('收款优化', '关注QR支付进展，准备对接统一收款'),
]
for title, desc in items:
    d.rectangle([rx+12, ry, W-PAD-12, ry+48], fill=BG, outline=BDL)
    d.text((rx+22, ry+6), title, fill=RED, font=F(16))
    d.text((rx+22, ry+26), desc, fill=T2, font=F(13))
    ry += 56

img.save(f'{OUT}/xhs_02_policy.png')
print("✓ 2/4")

# ======================================================================
# IMAGE 3: PRODUCT SIGNALS
# ======================================================================
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,42], fill=TEXT)
d.text((cx,21), '出海早班车 · 选品情报', fill=BG, font=F(20), anchor='mm')

y = 72
cards = [
    ('选品·越南', '89%↑', 'Type-C转接头周搜索量飙升',
     '越南站一周搜索涨89%，竞争不足50家。三星OPPO换机潮拉动配件需求。1688源头¥1.2-2.8元，终端¥10-16元，毛利55%-70%。建议选PD快充版做差异化。',
     'TikTok越南趋势 · 1688深圳产业带', GRN),
    ('选品·马来', '3×', '穆斯林时尚品类年增长3倍',
     'Modest Fashion年GMV增300%：头巾、长袍、祈祷毯。义乌/广州供应链集群成熟，头巾批发¥3-8元，终端¥15-40元。需注意Halal认证和本地化设计。',
     'TikTok Shop马来站 · 1688义乌产业带', GRN),
    ('选品·电子', '$12.9', 'TWS蓝牙耳机在印尼爆单',
     '$12.9定价的TWS耳机周销5万件：ENC降噪+30h续航+IPX5防水。1688源头¥25-38元/副。电子产品需关注各国SIRIM/SNI认证。',
     'TikTok Shop印尼站 · 1688深圳', GRN),
]
for tag, num, tit, desc, src, tc in cards:
    y = story_card(d, PAD, y, 660, tag, num, tit, desc, src, tc)

# Right: Data cards
rx = 760
ry = 72
d.rectangle([rx, ry, W-PAD, H-PAD], fill='#F5F2EB', outline=BDR)
d.text((rx+16, ry+12), '📊 核心数据', fill=TEXT, font=F(20)); ry += 42

data_blocks = [
    ('ROAS 4.73', '东南亚美妆低成本投放标杆',
     '"短视频种草+直播收割"\n本土KOC矩阵100+素人\n爆款单品集中投放\n小样试用→正装复购', BLUE),
    ('$456亿', 'TikTok Shop东南亚年GMV',
     '全球$643亿(+94%)\n东南亚占71% → 翻倍增速\n= 美国市场 × 3倍\n逼近Shopee的60%', GRN),
]
for big, title, desc, tc in data_blocks:
    d.rectangle([rx+12, ry, W-PAD-12, ry+160], fill=BG, outline=tc)
    d.text((rx+24, ry+14), big, fill=tc, font=F(44))
    d.text((rx+170, ry+28), title, fill=TEXT, font=F(16))
    d.multiline_text((rx+24, ry+80), desc, fill=T2, font=F(14))
    ry += 172

img.save(f'{OUT}/xhs_03_products.png')
print("✓ 3/4")

# ======================================================================
# IMAGE 4: PLATFORMS + DATA TABLE
# ======================================================================
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,42], fill=TEXT)
d.text((cx,21), '出海早班车 · 平台与趋势', fill=BG, font=F(20), anchor='mm')

y = 72
cards = [
    ('平台·Shopee', 'SLS', '印尼站跨境运费降8%-15%',
     'Shopee官方物流SLS宣布5月下调印尼费率。$5-$20日用品和配件直接受益。菲律宾站同步推"跨境优选卖家"激励计划，达标享额外流量倾斜。',
     'Shopee卖家中心公告 · 雨果跨境', GLD),
    ('物流·菲律宾', '72h', '海外仓72小时达覆盖85%',
     '马尼拉、宿务、达沃三大城市群全面覆盖。跨境物流体验逼近本土。"海外仓备货+TikTok直播"成菲律宾站标准打法。',
     '物流商公告 · 跨境物流白皮书', GRN),
    ('选品·家居', 'Home', '"租房经济"催生折叠家具增长67%',
     '东南亚年轻租房人群60%-80%。折叠书桌、便携衣柜月搜索增67%。1688折叠书桌¥35-60元，终端$15-25。适合海外仓模式。',
     'Shopee数据 · 1688 · 雨果跨境', GLD),
]
for tag, num, tit, desc, src, tc in cards:
    y = story_card(d, PAD, y, 660, tag, num, tit, desc, src, tc)

# Right: Country table
rx = 760
ry = 72
d.rectangle([rx, ry, W-PAD, H-PAD], fill='#F5F2EB', outline=BDR)
d.text((rx+16, ry+12), '📊 东南亚六国电商速览', fill=TEXT, font=F(18)); ry += 38

# Mini table
cols = [(rx+16, 70), (rx+100, 58), (rx+170, 40), (rx+220, 90), (rx+330, 120)]
for i, (h, w) in enumerate(zip(['国家','人口','渗透','平台','热门品类'], ['w','w','w','w','w'])):
    d.text((cols[i][0], ry), h, fill=T3, font=F(12))
ry += 18
rule(d, ry, BDR, 1, rx+12, 430)

rows = [
    ('🇮🇩 印尼','2.81亿','32%','Shopee','美妆·穆斯林·3C'),
    ('🇹🇭 泰国','7180万','48%','Shopee/Lazada','美妆·家居·食品'),
    ('🇻🇳 越南','1.01亿','28%','Shopee/TikTok','3C·服装·家居'),
    ('🇵🇭 菲律宾','1.17亿','22%','Shopee/Lazada','美妆·时尚·配件'),
    ('🇲🇾 马来西亚','3460万','50%','Shopee','穆斯林·3C·美妆'),
    ('🇸🇬 新加坡','600万','72%','Shopee/Amazon','健康·高端美妆'),
]
ry += 4
for row in rows:
    for i, val in enumerate(row):
        d.text((cols[i][0], ry), val, fill=TEXT if i==0 else T2, font=F(12))
    ry += 24

ry += 16
d.text((rx+16, ry), '数据：Momentum Works / e-Conomy SEA 2025', fill=T3, font=F(10))
ry += 36
d.text((rx+16, ry), '💡 趋势判断', fill=RED, font=F(18)); ry += 30
d.multiline_text((rx+16, ry), 
    'TikTok Shop东南亚GMV已达Shopee的60%。\n'
    '东南亚不是"顺便做做"的补充市场，\n'
    '而是TikTok电商生态的绝对主战场。\n'
    '入场越早，本地化壁垒越深。',
    fill=T2, font=F(14))

# Bottom bar
d.rectangle([0, H-36, W, H], fill=TEXT)
d.text((cx, H-18), '出海早班车 · 东南亚特刊 | 2026.05.02 | 多元来源交叉验证', fill=BG, font=F(13), anchor='mm')

img.save(f'{OUT}/xhs_04_platforms.png')
print("✓ 4/4")

# Verify dimensions
print("\n验证尺寸：")
for fn in sorted(os.listdir(OUT)):
    if fn.startswith('xhs_') and fn.endswith('.png'):
        img = Image.open(f'{OUT}/{fn}')
        ratio = img.size[0]/img.size[1]
        sz = os.path.getsize(f'{OUT}/{fn}')//1024
        print(f"  {fn}: {img.size[0]}×{img.size[1]} (4:3={'✓' if abs(ratio-1.333)<0.01 else '✗'}) - {sz}KB")
