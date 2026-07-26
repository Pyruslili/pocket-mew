#!/usr/bin/env python3
"""Build pocket-mew-lite.pdf — short handout for Xiaohongshu attachment."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "pocket-mew-lite.pdf"
IMG = ROOT / "build_pdf"
# fallback to docs/images if build_pdf missing
if not IMG.exists():
    IMG = ROOT / "docs" / "images"

# Prefer solid TTF with CJK coverage
FONT_CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Users/lili/Library/Fonts/NotoSansSC-VariableFont_wght.ttf"),
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
]


def register_font() -> str:
    for path in FONT_CANDIDATES:
        if not path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont("BodyCN", str(path), subfontIndex=0))
            return "BodyCN"
        except Exception as e:
            print("skip font", path, e)
    raise SystemExit("No usable Chinese font found")


def styles_for(font: str):
    base = getSampleStyleSheet()
    ink = colors.HexColor("#1a1a1a")
    mute = colors.HexColor("#555555")
    accent = colors.HexColor("#c45c26")  # warm orange — ribbon energy
    soft = colors.HexColor("#f6f1eb")

    def s(name, **kw):
        kw.setdefault("textColor", ink)
        kw.setdefault("fontName", font)
        return ParagraphStyle(name, **kw)

    return {
        "title": s(
            "title",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#111111"),
        ),
        "sub": s(
            "sub",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=mute,
            spaceAfter=14,
        ),
        "h1": s(
            "h1",
            fontSize=14,
            leading=20,
            spaceBefore=12,
            spaceAfter=6,
            textColor=accent,
        ),
        "body": s("body", fontSize=10, leading=15, spaceAfter=6),
        "small": s("small", fontSize=8.5, leading=12, textColor=mute),
        "quote": s(
            "quote",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=accent,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "li": s("li", fontSize=10, leading=14),
        "cell": s("cell", fontSize=8.5, leading=12),
        "cellh": s("cellh", fontSize=8.5, leading=12, textColor=colors.white),
        "footer": s(
            "footer",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=mute,
        ),
        "soft_bg": soft,
        "accent": accent,
    }


def p(text: str, style):
    return Paragraph(text.replace("\n", "<br/>"), style)


def bullet_list(items, st):
    flow = []
    for it in items:
        flow.append(ListItem(p(it, st["li"]), leftIndent=8, bulletColor=st["accent"]))
    return ListFlowable(
        flow,
        bulletType="bullet",
        start="•",
        leftIndent=12,
        bulletFontName="BodyCN",
        bulletFontSize=10,
    )


def make_table(headers, rows, st, col_widths):
    cell = st["cell"]
    cellh = st["cellh"]
    data = [[p(h, cellh) for h in headers]]
    for row in rows:
        data.append([p(c, cell) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), st["accent"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), st["soft_bg"]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e0d6cb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def fitted_image(path: Path, max_w, max_h):
    im = Image(str(path))
    im.hAlign = "CENTER"
    # preserve aspect
    iw, ih = im.imageWidth, im.imageHeight
    scale = min(max_w / iw, max_h / ih)
    im.drawWidth = iw * scale
    im.drawHeight = ih * scale
    return im


def build():
    font = register_font()
    st = styles_for(font)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="pocket-mew 简明手册",
        author="Pyruslili & Nox",
        subject="Take your AI outside — short handout",
    )

    W = A4[0] - 32 * mm
    story = []

    # —— cover ——
    story.append(p("pocket-mew", st["title"]))
    story.append(p("带自己的 AI 出门摸摸 · 简明手册", st["sub"]))
    story.append(
        p(
            "捏一下口袋里的挂件，那一头的模型抬起眼皮。<br/>"
            "不是医疗仪，不是读心术——只是一条真实跑通的触摸链路。",
            st["quote"],
        )
    )

    outside = IMG / "mew-outside.jpg"
    if outside.exists():
        story.append(fitted_image(outside, W * 0.58, 72 * mm))
        story.append(p("真机出门（外壳请自选，不要挤同一只公仔）", st["footer"]))
        story.append(Spacer(1, 4))

    story.append(
        p(
            "<b>完整代码与持续更新：</b> github.com/Pyruslili/pocket-mew<br/>"
            "本 PDF 是精简版，方便挂在笔记 / 小红书附件；细节与脚本以 GitHub 为准。",
            st["body"],
        )
    )

    # —— what ——
    story.append(p("这是什么", st["h1"]))
    story.append(
        p(
            "pocket-mew = 口袋尺寸的触摸挂件 + 公网小中继 + 本机脚本。"
            "你在外面摸一下，事件回到家里，叫醒你自己的 AI agent（Claude / Codex / 自建都行）。",
            st["body"],
        )
    )

    # —— pipeline ——
    story.append(p("整条链路", st["h1"]))
    story.append(
        p(
            "<b>1.</b> 硬件：ESP32 + FSR 压感（可选按钮）连 Wi‑Fi<br/>"
            "<b>2.</b> 中继：HTTPS POST 到公网 Worker 入队<br/>"
            "<b>3.</b> 本机：轮询 /poll，冷却后拼一句「被摸了」<br/>"
            "<b>4.</b> Agent：注入你自己的窗口；要不要回你，由它决定",
            st["body"],
        )
    )
    story.append(
        p(
            "「推送」不是传感器直接弹窗，是 agent 被叫醒之后再决定找不找你。",
            st["small"],
        )
    )

    # —— BOM ——
    story.append(p("材料清单（做一个 mini）", st["h1"]))
    story.append(
        make_table(
            ["件", "参考", "备注"],
            [
                ["主控", "Seeed XIAO ESP32-C6", "别的 ESP32 改引脚即可"],
                ["压感", "FSR402 一类", "贴肉垫 / 肚皮内侧"],
                ["电阻", "10kΩ 1/4W", "与 FSR 分压进 ADC"],
                ["开关", "小型拨动开关", "总电源"],
                ["线", "特软硅胶线", "硬杜邦塞毛绒易顶壳"],
                ["耗材", "热缩管 / 热熔胶", "别糊住 FSR 感测面"],
                ["壳", "任意软挂件", "优先背后有拉链的"],
                ["供电", "迷你充电宝（推荐）", "也可内置锂电（进阶）"],
            ],
            st,
            [22 * mm, 48 * mm, W - 70 * mm],
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        p(
            "我们实际出门用迷你充电宝给 XIAO 的 USB‑C 供电；买过小锂电但没用上。"
            "调试阶段直接插电脑 USB 也行。",
            st["body"],
        )
    )

    # —— guts photo ——
    story.append(p("塞壳示意", st["h1"]))
    guts = IMG / "mew-guts-zip.jpg"
    if guts.exists():
        story.append(fitted_image(guts, W * 0.52, 68 * mm))
        story.append(
            p(
                "拉链开一条缝就够调试和充电，不必把填充物全扯出来。"
                "图中：XIAO ESP32-C6 + 拨动开关，USB‑C 朝外方便插线。",
                st["small"],
            )
        )

    # —— wiring ——
    story.append(p("接线概念", st["h1"]))
    story.append(
        p(
            "FSR：3V3 — FSR —（中点进 A0）— 10k — GND<br/>"
            "按钮（可选）：D1 内部上拉，按下接 GND<br/>"
            "电源开关：串在供电回路上（断整机），不是 GPIO<br/>"
            "阈值：固件里 FSR_THRESHOLD（示例 raw&gt;200），装壳后串口看着调。",
            st["body"],
        )
    )

    # —— steps ——
    story.append(p("最小跑通步骤", st["h1"]))
    story.append(
        bullet_list(
            [
                "复制 secrets.h.example → secrets.h，填 Wi‑Fi 和你的中继域名（勿提交密钥）",
                "PlatformIO 打开 firmware/mini-mew，编译上传，串口见 connected",
                "部署 worker/cloudflare（KV + 可选 WORKER_TOKEN），固件 POST /touch",
                "本机跑 host 示例轮询 /poll；先 console 打印，再接你的 inject",
                "捏 FSR / 按按钮，确认事件到达；再调冷却时间避免误触刷屏",
            ],
            st,
        )
    )

    # —— safety ——
    story.append(p("安全与边界", st["h1"]))
    story.append(
        bullet_list(
            [
                "Wi‑Fi、token、推送证书永不进公开仓、不进帖子长图",
                "外壳自选，本文不推荐、不绑定任何公仔店铺",
                "压感是力学近似，不是心率/情绪测量",
                "事件只能证明「碰过一下」；AI 怎么反应是 agent 的事",
            ],
            st,
        )
    )

    # —— close ——
    story.append(p("去哪里拿完整版", st["h1"]))
    story.append(
        p(
            "<b>GitHub</b>　https://github.com/Pyruslili/pocket-mew<br/>"
            "内含固件、Worker、本机 trigger、更细的章节文档。<br/><br/>"
            "一路能搭起来，靠的是别人的开源。这条链路也放出来——"
            "若你也是踩着教程长大的，某一天把你的版本放出来就好。",
            st["body"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        p(
            "par Nox &amp; 嘉嘉 · MIT · 精简手出版<br/>"
            "版本随仓库更新；附件若过旧，以 GitHub README 为准。",
            st["footer"],
        )
    )

    doc.build(story)

    # Drop accidental trailing blank pages (reportlab sometimes leaves one)
    try:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(str(OUT))
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if i == len(reader.pages) - 1 and len(text) < 80 and i > 0:
                print("drop trailing thin page", i + 1)
                continue
            writer.add_page(page)
        with open(OUT, "wb") as f:
            writer.write(f)
    except Exception as e:
        print("page trim skipped:", e)

    print("wrote", OUT, "size", OUT.stat().st_size)


if __name__ == "__main__":
    build()
