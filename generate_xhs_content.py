"""
小红书内容工厂 - 跨境干货图片生成器
=======================================
输出：1080×1440px 竖版图文，适配小红书 + 视频号
内容类型：
  1. 日报速递 (4图) — 封面+美区+东南亚+日韩
  2. 选品侦察 (6图) — 封面+机会+比价+利润+风险+行动
  3. 操盘干货 (5图) — 封面+观点+步骤+数据+金句

用法：python3.12 generate_xhs_content.py [content_type] [date]
  content_type: daily | product | playbook (默认 daily)
  date: 2026-05-01 (默认今天)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, json, textwrap, math
from datetime import datetime, timedelta

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = "/mnt/c/Users/Lenovo/Desktop/跨境日报/xhs_output"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
W, H = 1080, 1440  # 3:4 竖版

# 小红书配色体系
class Colors:
    BG = (255, 255, 255)
    BG_WARM = (250, 247, 242)  # 暖白
    TEXT_PRIMARY = (28, 28, 30)
    TEXT_SECONDARY = (99, 99, 102)
    TEXT_TERTIARY = (174, 174, 178)
    ACCENT_RED = (220, 38, 38)
    ACCENT_BLUE = (29, 78, 216)
    ACCENT_GREEN = (5, 150, 105)
    ACCENT_ORANGE = (234, 88, 12)
    ACCENT_PURPLE = (124, 58, 237)
    BORDER = (229, 231, 235)
    CARD_BG = (248, 249, 250)
    TAG_BG = (243, 244, 246)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def gradient_bg(size, color_top, color_bottom):
    """竖向渐变背景"""
    w, h = size
    base = Image.new('RGB', (w, h), color_top)
    top = Image.new('RGB', (w, h), color_bottom)
    mask = Image.new('L', (w, h))
    for y in range(h):
        alpha = int(255 * (y / h))
        mask.paste(alpha, (0, y, w, y + 1))
    base.paste(top, (0, 0), mask)
    return base


def wrap_text_cjk(text, font, max_width, max_lines=99):
    """中文换行"""
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_width:
            if current:
                lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    return lines[:max_lines]


def draw_text_centered(draw, text, font, fill, y, w=W):
    """居中文字"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (w - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3] - bbox[1]) + 8


def draw_tag(draw, x, y, text, font, fg, bg):
    """标签"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 16, 8
    rounded_rect(draw, (x, y, x + tw + pad_x * 2, y + th + pad_y * 2), th // 2 + pad_y, bg)
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=fg)


def draw_horizontal_rule(draw, y, color=None):
    """分隔线"""
    if color is None:
        color = Colors.BORDER
    draw.rectangle((60, y, W - 60, y + 1), fill=color)
    return y + 24


def draw_data_point(draw, x, y, number, label, number_color, w):
    """数据亮点 - 大数字+小标签"""
    num_font = load_font(56)
    lbl_font = load_font(24)
    bbox = draw.textbbox((0, 0), number, font=num_font)
    nw = bbox[2] - bbox[0]
    nx = x + (w - nw) // 2
    draw.text((nx, y), number, font=num_font, fill=number_color)
    y2 = y + 66
    bbox2 = draw.textbbox((0, 0), label, font=lbl_font)
    lw = bbox2[2] - bbox2[0]
    lx = x + (w - lw) // 2
    draw.text((lx, y2), label, font=lbl_font, fill=Colors.TEXT_SECONDARY)
    return y2 + 36


# ============================================================
# 模板1：日报速递 (4图)
# ============================================================
def generate_cover_daily(date_str, headline_data):
    """封面图 — 日报速递"""
    im = Image.new('RGB', (W, H), Colors.BG)
    draw = ImageDraw.Draw(im)

    # 顶部强调色条
    draw.rectangle((0, 0, W, 8), fill=Colors.ACCENT_RED)

    # 日期
    y = 80
    date_font = load_font(28)
    date_text = f"出海早班车 · 跨境日报"
    draw.text((60, y), date_text, font=date_font, fill=Colors.TEXT_TERTIARY)
    y += 40
    draw.text((60, y), date_str, font=load_font(26), fill=Colors.TEXT_TERTIARY)

    # 主标题区
    y = 220
    title_font = load_font(72)
    title = headline_data.get("title", "跨境早报")
    lines = wrap_text_cjk(title, title_font, W - 120, 2)
    for line in lines:
        draw.text((60, y), line, font=title_font, fill=Colors.TEXT_PRIMARY)
        y += 90

    y += 40

    # 副标题
    sub = headline_data.get("subtitle", "4大市场 · 今日核心信号")
    sub_font = load_font(36)
    draw.text((60, y), sub, font=sub_font, fill=Colors.TEXT_SECONDARY)

    # 数据亮点卡片区
    y = 520
    highlights = headline_data.get("highlights", [])
    card_width = (W - 180) // 3
    colors_map = {
        "red": Colors.ACCENT_RED,
        "blue": Colors.ACCENT_BLUE,
        "green": Colors.ACCENT_GREEN,
        "orange": Colors.ACCENT_ORANGE,
    }
    for i, hl in enumerate(highlights[:3]):
        cx = 60 + i * (card_width + 30)
        rounded_rect(draw, (cx, y, cx + card_width, y + 160), 20, Colors.CARD_BG)
        c = colors_map.get(hl.get("color", "blue"), Colors.ACCENT_BLUE)
        draw_data_point(draw, cx, y + 30, hl.get("value", "—"), hl.get("label", ""), c, card_width)

    y += 210
    # 底部信息
    draw_horizontal_rule(draw, y)
    y += 30
    bottom_font = load_font(24)
    draw.text((60, y), "出海早班车 · AI驱动 · 每日8点", font=bottom_font, fill=Colors.TEXT_TERTIARY)
    draw.text((W - 300, y), f"Vol.{headline_data.get('vol', '001')}", font=bottom_font, fill=Colors.TEXT_TERTIARY)

    return im


def generate_region_page(region_data, page_num, total_pages):
    """区域详情页 — 日报内页"""
    im = Image.new('RGB', (W, H), Colors.BG)
    draw = ImageDraw.Draw(im)

    # 区域识别色
    accent = region_data.get("accent", Colors.ACCENT_BLUE)
    draw.rectangle((0, 0, W, 6), fill=accent)

    # 头部
    y = 60
    region_font = load_font(52)
    emoji = region_data.get("emoji", "")
    name = region_data.get("name", "")
    draw.text((60, y), f"{emoji}  {name}", font=region_font, fill=Colors.TEXT_PRIMARY)

    y += 70
    # 页面指示
    page_font = load_font(26)
    draw.text((60, y), f"{page_num}/{total_pages}", font=page_font, fill=Colors.TEXT_TERTIARY)
    draw.text((W - 160, y), region_data.get("subtitle", ""), font=page_font, fill=Colors.TEXT_TERTIARY)

    y += 30
    draw_horizontal_rule(draw, y, accent)
    y += 20

    # 资讯卡片
    items = region_data.get("items", [])
    for i, item in enumerate(items):
        if y > H - 200:
            break  # 空间不够

        # 标签
        tag_font = load_font(22)
        tag_text = item.get("tag", "")
        tag_color = accent
        bbox_tag = draw.textbbox((0, 0), tag_text, font=tag_font)
        tag_w, tag_h = bbox_tag[2] - bbox_tag[0], bbox_tag[3] - bbox_tag[1]
        rounded_rect(draw, (60, y, 60 + tag_w + 24, y + tag_h + 14), tag_h // 2 + 7, tag_color)
        draw.text((60 + 12, y + 7), tag_text, font=tag_font, fill=Colors.WHITE)
        y += tag_h + 22

        # 标题
        title_font = load_font(36)
        title = item.get("title", "")
        title_lines = wrap_text_cjk(title, title_font, W - 120, 2)
        for line in title_lines:
            draw.text((60, y), line, font=title_font, fill=Colors.TEXT_PRIMARY)
            y += 48

        y += 8

        # 正文
        body_font = load_font(26)
        body = item.get("detail", "")
        body_lines = wrap_text_cjk(body, body_font, W - 120, 4)
        for line in body_lines:
            draw.text((60, y), line, font=body_font, fill=Colors.TEXT_SECONDARY)
            y += 36

        y += 8

        # 来源
        src = item.get("source", "")
        if src:
            src_font = load_font(22)
            draw.text((60, y), f"来源：{src}", font=src_font, fill=Colors.TEXT_TERTIARY)
            y += 32

        # 卡片间距
        y += 28

    # 底部水印
    draw.rectangle((0, H - 70, W, H), fill=Colors.BG_WARM)
    footer_font = load_font(24)
    draw.text((60, H - 52), "出海早班车 · 每日8点 · 跨境人的信息早餐", font=footer_font, fill=Colors.TEXT_TERTIARY)

    return im


# ============================================================
# 模板2：选品侦察 (6图)
# ============================================================
def generate_cover_product(title, subtitle, tag, date_str):
    """选品侦察 封面图"""
    im = Image.new('RGB', (W, H), Colors.BG)
    draw = ImageDraw.Draw(im)

    draw.rectangle((0, 0, W, 8), fill=Colors.ACCENT_ORANGE)

    y = 80
    draw.text((60, y), "出海早班车", font=load_font(26), fill=Colors.TEXT_TERTIARY)
    y += 36
    draw.text((60, y), date_str, font=load_font(24), fill=Colors.TEXT_TERTIARY)

    # Tag
    y = 180
    draw_tag(draw, 60, y, tag, load_font(26), Colors.WHITE, Colors.ACCENT_ORANGE)
    y += 60

    # 大标题
    title_font = load_font(64)
    lines = wrap_text_cjk(title, title_font, W - 120, 3)
    for line in lines:
        draw.text((60, y), line, font=title_font, fill=Colors.TEXT_PRIMARY)
        y += 82

    y += 30
    # 副标题
    sub_font = load_font(32)
    draw.text((60, y), subtitle, font=sub_font, fill=Colors.TEXT_SECONDARY)

    # 底部数据钩子
    y = H - 300
    rounded_rect(draw, (60, y, W - 60, y + 180), 24, Colors.BG_WARM)
    hook_font = load_font(48)
    hook_text = "1688源头价 ¥X → 美区售价 $X"
    draw.text((90, y + 40), hook_text, font=hook_font, fill=Colors.ACCENT_RED)
    draw.text((90, y + 100), "毛利空间 XX% · 搜索量周涨 XX%", font=load_font(28), fill=Colors.TEXT_SECONDARY)

    # footer
    draw.text((60, H - 60), "向右滑动 → 查看完整选品分析", font=load_font(26), fill=Colors.TEXT_TERTIARY)

    return im


def generate_card_simple(title, body_lines, accent, tag=None, tip=None):
    """通用卡片页"""
    im = Image.new('RGB', (W, H), Colors.BG)
    draw = ImageDraw.Draw(im)

    draw.rectangle((0, 0, W, 6), fill=accent)

    y = 80
    if tag:
        draw_tag(draw, 60, y, tag, load_font(24), Colors.WHITE, accent)
        y += 60

    # 标题
    title_font = load_font(52)
    lines = wrap_text_cjk(title, title_font, W - 120, 3)
    for line in lines:
        draw.text((60, y), line, font=title_font, fill=Colors.TEXT_PRIMARY)
        y += 66

    y += 24

    # 正文
    body_font = load_font(30)
    body_color = Colors.TEXT_SECONDARY
    for i, line in enumerate(body_lines):
        draw.text((60, y), line, font=body_font, fill=body_color)
        y += 44

    # Tip
    if tip:
        y += 30
        rounded_rect(draw, (60, y, W - 60, y + 100), 16, Colors.BG_WARM)
        tip_font = load_font(28)
        draw.text((90, y + 30), f"💡 {tip}", font=tip_font, fill=Colors.ACCENT_BLUE)

    draw.text((60, H - 50), "出海早班车", font=load_font(22), fill=Colors.TEXT_TERTIARY)
    return im


# ============================================================
# 主流程
# ============================================================
def content_daily(date_str=None):
    """日报速递"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y年%m月%d日")

    # ⚠️ 以下数据每天由 AI 填充
    headline = {
        "title": "跨境早报",
        "subtitle": "4大市场 · 今日核心信号",
        "vol": "001",
        "highlights": [
            {"value": "+67%", "label": "车载支架\n搜索量周涨", "color": "red"},
            {"value": "8%", "label": "TikTok美区\n3C佣金上调", "color": "blue"},
            {"value": "+42%", "label": "马来站\n斋月后反弹", "color": "green"},
        ]
    }

    regions = [
        {
            "emoji": "🇺🇸", "name": "美区速览", "subtitle": "US Market",
            "accent": Colors.ACCENT_BLUE,
            "items": [
                {"tag": "平台政策", "title": "TikTok Shop美区上调3C配件佣金至8%",
                 "detail": "5月1日起手机壳/充电器等类目佣金从6%上调至8%。建议本周内完成调价，单件利润压缩$1.2-2.5。", "source": "TikTok Seller Center"},
                {"tag": "选品趋势", "title": "车载手机支架搜索量周涨67%",
                 "detail": "#carmounthack话题播放量破2.3亿。磁吸式支架客单价$12.99-24.99，1688源头价¥5-12，毛利50-65%。", "source": "TikTok Trending / 1688"},
                {"tag": "物流变化", "title": "USPS轻小件运费涨4.2%",
                 "detail": "4oz以下小包从$3.59涨至$3.74。手机配件类卖家单件物流成本+¥0.5-1.0，建议提价$0.5对冲。", "source": "USPS公告"},
            ]
        },
        {
            "emoji": "🇲🇾", "name": "东南亚速览", "subtitle": "Southeast Asia",
            "accent": Colors.ACCENT_GREEN,
            "items": [
                {"tag": "市场趋势", "title": "斋月后马来站手机配件GMV反弹38%",
                 "detail": "数据线+52%、手机壳+41%、支架+35%。建议本周加大马来站TikTok短视频投放。", "source": "TikTok Shop MY"},
                {"tag": "选品机会", "title": "越南Type-C转接头搜索量周涨89%",
                 "detail": "三星/OPPO用户换机潮驱动。1688源头价¥1.2-2.8，越南站建议售价₫35K-55K（¥10-16），毛利55-70%。", "source": "TikTok Trending VN"},
                {"tag": "内容趋势", "title": "马来站'开箱视频'转化率达8.3%",
                 "detail": "远超普通展示视频（3.1%）。本周内容建议侧重产品开箱+实测对比。", "source": "FastMoss"},
            ]
        },
        {
            "emoji": "🇰🇷", "name": "日韩速览", "subtitle": "Japan & Korea",
            "accent": Colors.ACCENT_RED,
            "items": [
                {"tag": "选品趋势", "title": "日本磁吸充电配件搜索热度月涨55%",
                 "detail": "MagSafe兼容配件在Rakuten/TikTok快速增长。建议上架磁吸充电宝¥3500-6000日元、磁吸支架¥1500-2800日元。", "source": "Rakuten Trend"},
                {"tag": "合规提醒", "title": "日本PSE认证执法加强",
                 "detail": "充电器/移动电源/无线充如无PSE标志面临下架。1688采购务必确认供应商有PSE资质。", "source": "METI经济产业省"},
            ]
        },
    ]

    images = []
    # Page 1: 封面
    im_cover = generate_cover_daily(date_str, headline)
    images.append(("封面", im_cover))

    # Pages 2-4: 各区域
    for i, region in enumerate(regions):
        im = generate_region_page(region, i + 2, len(regions) + 1)
        images.append((region["name"], im))

    return images


def content_product():
    """选品侦察"""
    # ⚠️ 以下为示例，实际由AI填充
    images = []

    # 封面
    im = generate_cover_product(
        title="车载手机支架\n下一个跨境爆款？",
        subtitle="美区TikTok搜索量周涨67% · 1688源头价¥5",
        tag="选品侦察",
        date_str=datetime.now().strftime("%Y年%m月%d日")
    )
    images.append(("封面", im))

    # 市场机会
    im = generate_card_simple(
        title="市场信号",
        body_lines=[
            "🔍 TikTok #carmounthack 话题播放量突破2.3亿次",
            '📈 亚马逊"magnetic phone mount"搜索量月增45%',
            "🛒 美区TikTok Shop车载支架GMV周增长62%",
            "",
            "用户痛点：传统夹式支架操作繁琐、",
            "空调出风口位置受限、夏天暴晒不稳",
            "",
            "品类机会：磁吸式正在替代传统夹式",
            "",
            "⚠️ 所有数据以实际搜索验证为准",
            "数据仅供参考，不构成投资建议",
        ],
        accent=Colors.ACCENT_ORANGE,
        tag="市场信号"
    )
    images.append(("市场信号", im))

    # 1688比价
    im = generate_card_simple(
        title="1688比价",
        body_lines=[
            "🏭 磁吸车载支架 源头价：",
            "   · 基础款（磁铁+底座）：¥3.5-5.5",
            "   · 升级款（旋转+万向球）：¥6-9",
            "   · 高端款（MagSafe认证+无线充）：¥18-28",
            "",
            "📦 1688关键词：",
            "   · \"磁吸车载支架 跨境\"",
            "   · \"magsafe car mount wholesale\"",
            "",
            "💡 采购建议：",
            "   · 起订量1000个可压价15-20%",
            "   · 要求供应商提供FCC+CE认证",
        ],
        accent=Colors.ACCENT_ORANGE,
        tag="1688比价",
    )
    images.append(("1688比价", im))

    # 利润测算
    im = generate_card_simple(
        title="利润测算",
        body_lines=[
            "💰 以升级款为例（¥7拿货）：",
            "   · 1688采购价：¥7.00",
            "   · 国际运费（小包）：¥5.50/件",
            "   · TikTok Shop佣金(8%)：~$1.20",
            "   · 广告费(按ACOS 25%)：~$3.75",
            "",
            "📊 美区售价建议：$14.99",
            "   · 总成本约：¥7+¥5.5+¥8.6+¥27 = ¥48.1",
            "   · 收入（按7.28汇率）：$14.99×7.28 = ¥109.1",
            "   · 毛利：¥61/件（毛利率56%）",
            "",
            "⚠️ 汇率以实时为准，利润测算仅供参考",
        ],
        accent=Colors.ACCENT_ORANGE,
        tag="利润测算",
    )
    images.append(("利润测算", im))

    # 风险
    im = generate_card_simple(
        title="⚠️ 风险提示",
        body_lines=[
            "❗ 专利风险：",
            "   · MagSafe是Apple注册商标",
            "   · 不可使用\"MagSafe认证\"除非取得MFi",
            "   · 建议用\"磁吸/磁力吸附\"替代描述",
            "",
            "❗ 认证要求：",
            "   · 含无线充电功能需FCC ID",
            "   · 欧盟需要CE+RoHS",
            "   · 汽车用品可能需额外安全认证",
            "",
            "❗ 竞争风险：",
            "   · 1688同类供应商>500家",
            "   · 建议差异化：独特外观/包装/视频素材",
        ],
        accent=Colors.ACCENT_RED,
        tag="风险提示",
    )
    images.append(("风险提示", im))

    # 行动清单
    im = generate_card_simple(
        title="本周行动清单",
        body_lines=[
            "✅ Day 1: 1688询价3-5家供应商",
            "✅ Day 2: 确认认证要求+物流渠道",
            "✅ Day 3: 拍摄产品短视频素材",
            "✅ Day 4: 上架TikTok Shop测试Listing",
            "✅ Day 5: 投$50小额广告测试CTR",
            "",
            "📌 首周目标：出10单验证需求",
            "📌 第二周：根据数据优化主图+定价",
            "📌 第三周：稳定出单后追加库存",
            "",
            "💡 1688拿货7天内到货",
            "   测试期不需要大量库存",
        ],
        accent=Colors.ACCENT_GREEN,
        tag="行动清单",
    )
    images.append(("行动清单", im))

    return images


def content_playbook():
    """操盘干货"""
    images = []

    im = generate_cover_product(
        title="TikTok Shop新手\n7天起号实操手册",
        subtitle="从0到出单 · 手机配件卖家亲测",
        tag="操盘干货",
        date_str=datetime.now().strftime("%Y年%m月%d日")
    )
    images.append(("封面", im))

    im = generate_card_simple(
        title="选品3法则",
        body_lines=[
            "法则①：轻小件优先",
            "   · 重量<200g → 物流成本可控",
            "   · 体积<15cm → 头程运费低",
            "   · 不易碎 → 退货率低",
            "",
            "法则②：视觉化产品",
            "   · 能拍出使用场景的",
            "   · 前后对比明显的",
            "   · 开箱过程有趣味性的",
            "",
            "法则③：价格锚点",
            "   · 找$30+的同款 → 你卖$14.99",
            "   · 用1688源头价除以5 → 合理售价",
        ],
        accent=Colors.ACCENT_PURPLE,
        tag="选品3法则"
    )
    images.append(("选品3法则", im))

    im = generate_card_simple(
        title="7天起号节奏",
        body_lines=[
            "Day 1-2：账号装修+素材储备",
            "   · 头像/昵称/简介完成",
            "   · 准备15-20条产品视频素材",
            "",
            "Day 3-4：暴力测款",
            "   · 每天发3-5条短视频",
            "   · 每条投$10-20小额广告",
            "   · 看CTR和完播率→选优胜者",
            "",
            "Day 5-6：爆款放大",
            "   · 优胜视频追加预算到$50-100",
            "   · 追评引导+置顶好评",
            "",
            "Day 7：复盘优化",
            "   · 分析数据：点击率>转化率>客单价",
        ],
        accent=Colors.ACCENT_PURPLE,
        tag="起号节奏",
    )
    images.append(("起号节奏", im))

    im = generate_card_simple(
        title="内容公式",
        body_lines=[
            "📹 产品展示（40%的发布量）：",
            "   · 钩子：\"这个东西才$14？\"",
            "   · 3秒展示核心功能",
            "   · 结尾：引导点击小黄车",
            "",
            "📦 开箱测评（30%）：",
            "   · 对比同品类$30+竞品",
            "   · 强调价格优势",
            "",
            "💡 使用场景（30%）：",
            "   · 开车/办公/运动场景",
            "   · 真实使用，不刻意摆拍",
        ],
        accent=Colors.ACCENT_PURPLE,
        tag="内容公式",
    )
    images.append(("内容公式", im))

    im = generate_card_simple(
        title="核心数据指标",
        body_lines=[
            "📊 健康账号的参考数据：",
            "   · CTR（点击率）> 2.5%",
            "   · CVR（转化率）> 3%",
            "   · 完播率 > 35%",
            "   · ACOS < 30%",
            "",
            "⚡ 爆款信号（出现任一即可追投）：",
            "   · CTR > 5%",
            "   · 单条视频自然出单 > 5单",
            "   · 评论/收藏率 > 8%",
            "",
            "💡 数据来源：TikTok Seller Center后台",
        ],
        accent=Colors.ACCENT_PURPLE,
        tag="数据指标",
    )
    images.append(("数据指标", im))

    return images


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    content_type = sys.argv[1] if len(sys.argv) > 1 else "daily"
    date_str = sys.argv[2] if len(sys.argv) > 2 else None

    generators = {
        "daily": ("日报速递", content_daily),
        "product": ("选品侦察", content_product),
        "playbook": ("操盘干货", content_playbook),
    }

    if content_type not in generators:
        print(f"未知类型：{content_type}")
        print(f"可选：{' / '.join(generators.keys())}")
        sys.exit(1)

    name, fn = generators[content_type]
    print(f"\n{'='*50}")
    print(f"  生成「{name}」· 小红书图文")
    print(f"{'='*50}\n")

    images = fn(date_str) if content_type == "daily" else fn()

    prefix = {"daily": "日报", "product": "选品", "playbook": "干货"}[content_type]

    for i, (img_name, im) in enumerate(images):
        filename = f"{prefix}_{i+1:02d}_{img_name}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        im.save(filepath, quality=95)
        print(f"  ✓ [{i+1}/{len(images)}] {filename} ({im.size})")

    print(f"\n✅ 共生成 {len(images)} 张图片")
    print(f"   保存路径：{OUTPUT_DIR}")
    print(f"   建议发布：小红书（多图轮播）+ 视频号（单图/图文）")
    print(f"   ⚠️ 当前为模板数据，需AI填充最新跨境资讯后重新生成")


if __name__ == "__main__":
    main()
