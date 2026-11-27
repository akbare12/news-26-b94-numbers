#!/usr/bin/env python3
"""Render news-image-20261126 entry.png (b94, layout V92) - build time only."""
import hashlib
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

BG = (251, 247, 236)
INK = (20, 20, 20)
MUTED = (70, 70, 70)
NAVY = (18, 53, 91)
RED = (180, 35, 24)
TEAL = (14, 107, 107)
GOLD = (146, 96, 0)
CARD_BG = (255, 255, 255)
LINE = (120, 110, 90)
OCEAN = (199, 220, 234)
LAND = (227, 217, 190)
TAG_C = (14, 107, 107)
TAG_R = (146, 96, 0)
TAG_CL = (180, 35, 24)

TEXTBOXES = []
ARTBOXES = []


def F(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def tw(text, font):
    return font.getlength(text)


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def reg_textbox(box):
    TEXTBOXES.append(box)


def wrap(text, font, maxw, prefix=""):
    """Wrap text to lines that fit maxw; first line reserves prefix width."""
    words = text.split()
    lines = []
    cur = ""
    first = True
    for word in words:
        trial = (cur + " " + word).strip() if cur else word
        avail = maxw - (tw(prefix, font) if first else 0)
        if tw(trial, font) <= avail or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            first = False
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, leading=None, prefix=None, prefix_font=None, prefix_fill=None):
    """Draw lines; optional tag prefix on first line. Returns bottom y."""
    lh = leading if leading is not None else int(font.size * 1.25)
    for i, line in enumerate(lines):
        yy = y + i * lh
        xx = x
        if i == 0 and prefix:
            d.text((xx, yy), prefix, font=prefix_font or font, fill=prefix_fill or fill)
            xx += tw(prefix, prefix_font or font)
        d.text((xx, yy), line, font=font, fill=fill)
        reg_textbox((x, yy, x + tw(prefix, font) + tw(line, font) if i == 0 and prefix else x + tw(line, font), yy + font.size))
    return y + len(lines) * lh


# ---------------------------------------------------------------- content
HEROES = [
    {
        "tag": "[C]", "kicker": "HERO 1 · NEW YORK",
        "title": "MACY'S 100TH PARADE POSTPONED",
        "deck": "Thanksgiving parade delayed by storm, the first weather postponement ever; gusts hit 60 mph.",
        "why": "America's most iconic parade, in its 100th year, bows to the weather.",
        "stat": "100TH  ·  RESCHEDULED SAT 28 NOV 08:30 ET",
    },
    {
        "tag": "[CL]", "kicker": "HERO 2 · STRAIT OF HORMUZ",
        "title": "HORMUZ: IRGC CLAIMS 2 TANKERS HIT BY MINES",
        "deck": "Supertanker carrying 2M barrels among vessels Iran says were mined near Khasab.",
        "why": "The claim widens the Iran war to the world's key oil chokepoint.",
        "stat": "2M BARRELS  ·  CLAIM UNVERIFIED",
    },
    {
        "tag": "[C]", "kicker": "HERO 3 · MARKETS",
        "title": "TARIFFS: MARKETS REBOUND AS SALVO LOOKS MILDER",
        "deck": "Stocks rally as new US tariffs on 14 partners will not stack on July duties; China faces 20%.",
        "why": "Relief after the tariff shock: investors judge the macro hit modest.",
        "stat": "STOXX +1.6%  ·  14 PARTNERS  ·  CHINA 20%",
    },
]

CARDS = [
    ("GAZA", "[C]", "Israeli strike kills Hamas education deputy Khaled Abu Nada and his wife in Deir al-Balah.", "9 KILLED OVERNIGHT"),
    ("KYIV", "[C]", "Russian ballistic missiles hit a Kyiv mall; 7 wounded as 113 drones attack overnight.", "7 WOUNDED · 113 DRONES"),
    ("BOGOR", "[C]", "Flooded illegal gold mine in Bogor leaves 13 dead and 13 missing, 100m underground.", "13 DEAD · 13 MISSING"),
    ("NETANYAHU", "[C]", "Judge urges prosecutors to drop the sole bribery charge, Case 4000, against Netanyahu.", "CASE 4000"),
    ("NORTH KOREA", "[C]", "Kim Jong Un tours a nuclear-material plant and urges wider use of tactical nukes.", "TACTICAL NUKES PUSH"),
    ("STARMIND", "[CL]", "FCC approves SpaceX plan for 1M orbital compute satellites; approved 25 Nov.", "1M SATELLITES · 25 NOV"),
    ("UK MIGRATION", "[C]", "Net migration falls to 77,000 in the year to June, lowest since 1997 outside Covid.", "77,000 · LOWEST SINCE 1997"),
    ("MOSCOW BUDGET", "[C]", "Russia approves a record post-Soviet military budget.", "RECORD MILITARY BUDGET"),
    ("BANGKOK DEPOT", "[C]", "Blast at a Bangkok oil depot injures 7; fire controlled in about 30 minutes.", "7 HURT · BANGKOK"),
    ("COLOGNE PLOT", "[C]", "Germany arrests 2 Iraqi suspects over a plot to attack a synagogue in Cologne.", "2 ARRESTED · COLOGNE"),
]

ALSO = [
    ("[R]", "Cargo ship near Odesa claimed hit"),
    ("[C]", "Russia claims Kyiv strikes hit drone sites"),
    ("[CL]", "UN rights chief Turk warns of atrocity risk in Gaza 25 Nov"),
    ("[CL]", "Nvidia Wed close -3.91% at $149.30 25 Nov"),
    ("[CL]", "S&P -0.25%, Nasdaq -0.62% Wed close 25 Nov"),
    ("[CL]", "Brent Wed $94.61 a barrel 25 Nov"),
    ("[CL]", "Dow Wed +0.33% 25 Nov"),
    ("[CL]", "Saudi downs 2 ballistic missiles for Riyadh 25 Nov"),
    ("[CL]", "Jazan port: minor damage 25 Nov"),
    ("[CL]", "Myanmar faces ICJ hearing 25 Nov"),
    ("[CL]", "Macy's balloons inflated then deflated 25 Nov"),
    ("[CL]", "Eurostar services disrupted 25 Nov"),
    ("[CL]", "Syria seizes Captagon haul 25 Nov"),
    ("[CL]", "Hamas official Mohammad Abuelouf killed 25 Nov"),
    ("[C]", "UKMTO 222-26: blast near tanker off Dubai"),
    ("[CL]", "UKMTO 223-26: projectile attack near Khasab 25 Nov"),
    ("[R]", "UK on drone alert at air bases"),
    ("[R]", "Nvidia halts AI server shipments to 4 nations"),
    ("[C]", "Belarus offers to fly Zelensky to Moscow; he declines"),
    ("[C]", "Kushner calls Putin 'historic figure'"),
    ("[C]", "Eisenkot seals first Israel coalition deal"),
    ("[C]", "Merz warns Russia's ambitions go beyond Ukraine"),
    ("[C]", "Norse Atlantic suspends all flights"),
    ("[C]", "Poundland enters administration; 11,000 jobs at risk"),
    ("[C]", "Malaysia sues Google for $146m over harmful content"),
    ("[C]", "Kenya court halts US-backed Ebola facility"),
    ("[C]", "Estonia decides to shut border"),
    ("[C]", "Copernicus confirms longest stretch above 2C warming"),
    ("[C]", "US Bitcoin funds hit record $4.94bn"),
    ("[C]", "Ukraine drones hit Savasleyka base; 5 jets damaged"),
    ("[C]", "Couple aged 37 and 38 killed in Kharkiv flat strike"),
    ("[C]", "18 wounded in Kryvyi Rih strike"),
    ("[C]", "Philadelphia parade also cancelled over weather"),
    ("[C]", "Gold $3,572/oz, down 0.2% Thu"),
    ("[C]", "OPEC+ meets 29 Nov on 2027 output"),
    ("[C]", "NBC airs 2025 parade Thu, live parade Sat"),
    ("[CL]", "Saudi downs 4 drones over Ras Tanura 25 Nov"),
]

PINS = [
    ("NEW YORK", -74.0, 40.7),
    ("KHASAB", 56.2, 26.5),
    ("JAZAN", 42.5, 16.9),
    ("COLOGNE", 6.96, 50.94),
    ("KYIV", 30.5, 50.45),
    ("GAZA", 34.5, 31.5),
    ("BOGOR", 106.8, -6.6),
    ("BEIJING", 116.4, 39.9),
]

TIMELINE = [
    ("10:00", "Wind warning NYC"),
    ("THU AM", "NBC airs 2025 parade"),
    ("THU", "IRGC mine claim"),
    ("THU", "Markets rebound"),
    ("SAT 28 NOV", "Parade 08:30 ET"),
    ("SUN 29 NOV", "OPEC+ meets"),
]

STOPWORDS = {
    "the", "and", "for", "with", "from", "near", "over", "also", "after",
    "into", "that", "this", "will", "says", "sued", "hits", "hit",
}


def distinctive(text):
    toks = re.findall(r"[a-z]+", text.lower())
    return {t for t in toks if len(t) >= 4 and t not in STOPWORDS}


def check_content():
    need(len(HEROES) == 3, "heroes must be 3")
    need(len(CARDS) == 10, "cards must be 10")
    need(len(ALSO) == 37, "also must be 37")
    full = " ".join(
        [h["title"] + " " + h["deck"] + " " + h["why"] + " " + h["stat"] for h in HEROES]
        + [c[0] + " " + c[2] + " " + c[3] for c in CARDS]
        + [a[1] for a in ALSO]
    )
    need("third senior official" not in full.lower(), "banned phrase present")
    need("significant figure" not in full.lower(), "banned Kushner wording")
    need("historic figure" in full.lower(), "Kushner exact phrase missing")
    need("4 drones downed, jazan" not in full.lower(), "wrong Jazan wording")
    need("brent $93.8" not in full.lower(), "hero Brent stat repeated in ALSO")
    need("stoxx +1.6%" in full.lower(), "hero stat missing")
    for tag, text in ALSO:
        if tag == "[CL]" and "25 nov" in text.lower():
            pass
    for tag, text in ALSO:
        if tag == "[CL]":
            need("25 nov" in text.lower(), "CL ALSO item lacks 25 Nov: %s" % text)
    for c in CARDS:
        if c[1] == "[CL]":
            need("25 nov" in (c[2] + c[3]).lower(), "CL card lacks 25 Nov: %s" % c[0])
    items = (
        [(h["title"] + " " + h["deck"] + " " + h["why"]) for h in HEROES]
        + [(c[0] + " " + c[2]) for c in CARDS]
        + [a[1] for a in ALSO]
    )
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            shared = distinctive(items[i]) & distinctive(items[j])
            need(len(shared) < 3, "dup-scan flag %r vs %r shared=%s" % (items[i][:40], items[j][:40], shared))
    print("content checks OK: 3 heroes + 10 cards + 37 also = 50")


TAG_FILL = {"[C]": TAG_C, "[R]": TAG_R, "[CL]": TAG_CL}


def tag_color(tag):
    return TAG_FILL[tag]


def draw_masthead(d):
    d.rectangle([0, 0, W, 70], fill=NAVY)
    d.rectangle([0, 70, W, 72], fill=RED)
    title = "WORLD NEWS  •  THURSDAY 26 NOVEMBER 2026"
    f = F(27, bold=True)
    need(tw(title, f) <= W - 32, "masthead title too wide")
    d.text((16, 10), title, font=f, fill=(255, 255, 255))
    reg_textbox((16, 10, 16 + tw(title, f), 10 + 27))
    sub = "50 STORIES  •  MACY'S 100TH  •  HORMUZ  •  TARIFFS"
    fs = F(12, bold=True)
    d.text((16, 44), sub, font=fs, fill=(255, 214, 130))
    reg_textbox((16, 44, 16 + tw(sub, fs), 44 + 12))
    right = "26 NOV 2026"
    fr = F(13, bold=True)
    d.text((W - 16 - tw(right, fr), 44), right, font=fr, fill=(255, 255, 255))
    reg_textbox((W - 16 - tw(right, fr), 44, W - 16, 44 + 13))


def draw_datecheck(d):
    d.rectangle([8, 74, 1016, 108], fill=(255, 243, 205), outline=RED, width=2)
    l1 = "[CL] ITEMS HAPPENED 25 NOV — ALL OTHERS 26 NOV"
    f1 = F(13, bold=True)
    need(tw(l1, f1) <= 1000, "datecheck line1 too wide")
    d.text((16, 77), l1, font=f1, fill=RED)
    reg_textbox((16, 77, 16 + tw(l1, f1), 77 + 13))
    l2 = "THURSDAY 26 NOVEMBER 2026  •  3 HEROES + 10 CARDS + 37 ALSO = 50 STORIES"
    f2 = F(11)
    need(tw(l2, f2) <= 1000, "datecheck line2 too wide")
    d.text((16, 93), l2, font=f2, fill=INK)
    reg_textbox((16, 93, 16 + tw(l2, f2), 93 + 11))


def draw_also(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    fh = F(13, bold=True)
    head = "ALSO TODAY — 37 MORE STORIES"
    need(tw(head, fh) <= w - 16, "also header too wide")
    d.text((x + 8, y + 5), head, font=fh, fill=NAVY)
    reg_textbox((x + 8, y + 5, x + 8 + tw(head, fh), y + 5 + 13))
    d.line([(x + 8, y + 24), (x + w - 8, y + 24)], fill=LINE, width=1)
    top = y + 30
    col_w = (w - 16 - 16) // 3
    cols = [ALSO[0:13], ALSO[13:25], ALSO[25:37]]
    f = F(10)
    fb = F(10, bold=True)
    for ci, col in enumerate(cols):
        cx = x + 8 + ci * (col_w + 8)
        cy = top
        for tag, text in col:
            lines = wrap(text, f, col_w, prefix=tag + " ")
            need(len(lines) <= 2, "ALSO item wraps to 3 lines: %s" % text)
            bottom = draw_lines(d, cx, cy, lines, f, INK, leading=13,
                                prefix=tag + " ", prefix_font=fb, prefix_fill=tag_color(tag))
            cy = bottom + 4
        need(cy <= y + h - 4, "ALSO column overflows")
    return y + h


def draw_cards(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=BG, outline=LINE, width=1)
    rows, cols = 5, 2
    cw = (w - 12) // cols
    ch = (h - 10) // rows
    for idx, (title, tag, deck, stat) in enumerate(CARDS):
        r, c = divmod(idx, cols)
        bx = x + 6 + c * cw
        by = y + 5 + r * ch
        bw, bh = cw - 6, ch - 4
        d.rectangle([bx, by, bx + bw, by + bh], fill=CARD_BG, outline=LINE, width=1)
        ft = F(11, bold=True)
        need(tw(title, ft) + tw(tag + " ", ft) + 8 <= bw, "card title too wide: %s" % title)
        d.text((bx + 6, by + 4), tag + " ", font=ft, fill=tag_color(tag))
        reg_textbox((bx + 6, by + 4, bx + 6 + tw(tag + " ", ft), by + 4 + 11))
        d.text((bx + 6 + tw(tag + " ", ft), by + 4), title, font=ft, fill=INK)
        reg_textbox((bx + 6 + tw(tag + " ", ft), by + 4, bx + 6 + tw(tag + " ", ft) + tw(title, ft), by + 4 + 11))
        fd = F(10)
        lines = wrap(deck, fd, bw - 12)
        need(len(lines) <= 2, "card deck wraps to 3 lines: %s" % title)
        draw_lines(d, bx + 6, by + 20, lines, fd, INK, leading=12)
        fs = F(9, bold=True)
        need(tw(stat, fs) <= bw - 12, "card stat too wide: %s" % stat)
        d.text((bx + 6, by + bh - 14), stat, font=fs, fill=TEAL)
        reg_textbox((bx + 6, by + bh - 14, bx + 6 + tw(stat, fs), by + bh - 14 + 9))
    return y + h


def draw_hero_macy(d, x, y, w, h):
    hero = HEROES[0]
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    ax, ay, aw, ah = x + 8, y + 8, w - 16, 140
    d.rectangle([ax, ay, ax + aw, ay + ah], fill=(135, 180, 210))
    d.rectangle([ax, ay + 96, ax + aw, ay + ah], fill=(90, 90, 95))
    for bx, bw, bh in [(0, 52, 58), (58, 44, 80), (108, 60, 48), (174, 46, 88),
                       (226, 58, 60), (290, 44, 76), (340, 52, 54), (398, 30, 70)]:
        d.rectangle([ax + bx, ay + 96 - bh, ax + bx + bw, ay + 96], fill=(52, 58, 74))
        for wy in range(ay + 96 - bh + 8, ay + 90, 14):
            for wx in range(ax + bx + 6, ax + bx + bw - 6, 12):
                d.rectangle([wx, wy, wx + 5, wy + 6], fill=(255, 220, 120))
    balloons = []
    for cx, cy, rx, ry, col in [(90, 62, 34, 22, RED), (210, 52, 40, 26, (255, 200, 40)),
                                (330, 64, 32, 20, TEAL)]:
        box = (ax + cx - rx, ay + cy - ry, ax + cx + rx, ay + cy + ry)
        need(box[0] >= ax and box[1] >= ay and box[2] <= ax + aw and box[3] <= ay + ah,
             "balloon outside art box")
        d.ellipse(box, fill=col, outline=(255, 255, 255), width=2)
        d.line([(ax + cx, ay + cy + ry), (ax + cx, ay + 96)], fill=(60, 60, 60), width=1)
        balloons.append(box)
        ARTBOXES.append(box)
    fl = F(16, bold=True)
    lab1, lab2 = "100TH", "60 MPH"
    need(tw(lab1, fl) + tw(lab2, fl) + 24 <= aw, "art labels too wide")
    d.text((ax + 8, ay + 8), lab1, font=fl, fill=(255, 255, 255))
    b1 = (ax + 8, ay + 8, ax + 8 + tw(lab1, fl), ay + 8 + 16)
    d.text((ax + aw - 8 - tw(lab2, fl), ay + 8), lab2, font=fl, fill=(255, 255, 255))
    b2 = (ax + aw - 8 - tw(lab2, fl), ay + 8, ax + aw - 8, ay + 8 + 16)
    reg_textbox(b1)
    reg_textbox(b2)
    for bb in balloons:
        for lb in (b1, b2):
            dx = max(lb[0] - bb[2], bb[0] - lb[2], 0)
            dy = max(lb[1] - bb[3], bb[1] - lb[3], 0)
            need((dx * dx + dy * dy) ** 0.5 >= 8, "balloon too close to art label")
    ty = ay + ah + 8
    fk = F(10, bold=True)
    d.text((x + 8, ty), hero["kicker"] + "  " + hero["tag"], font=fk, fill=RED)
    reg_textbox((x + 8, ty, x + 8 + tw(hero["kicker"] + "  " + hero["tag"], fk), ty + 10))
    ty += 16
    ft = F(15, bold=True)
    lines = wrap(hero["title"], ft, w - 16)
    need(len(lines) <= 2, "hero title wraps to 3 lines")
    ty = draw_lines(d, x + 8, ty, lines, ft, INK, leading=18)
    fd = F(11)
    lines = wrap(hero["deck"], fd, w - 16)
    need(len(lines) <= 2, "hero deck wraps to 3 lines")
    ty = draw_lines(d, x + 8, ty + 2, lines, fd, INK, leading=13)
    fw = F(10)
    fwb = F(10, bold=True)
    lines = wrap(hero["why"], fw, w - 16, prefix="WHY IT MATTERS: ")
    need(len(lines) <= 2, "hero why wraps to 3 lines")
    ty = draw_lines(d, x + 8, ty + 2, lines, fw, MUTED, leading=12,
                    prefix="WHY IT MATTERS: ", prefix_font=fwb, prefix_fill=NAVY)
    fs = F(11, bold=True)
    need(tw(hero["stat"], fs) <= w - 16, "hero stat too wide")
    sy = y + h - 24
    need(ty + 2 <= sy, "hero text collides with stat bar")
    d.rectangle([x + 1, sy, x + w - 1, y + h - 1], fill=NAVY)
    d.text((x + 8, sy + 5), hero["stat"], font=fs, fill=(255, 255, 255))
    reg_textbox((x + 8, sy + 5, x + 8 + tw(hero["stat"], fs), sy + 5 + 11))


def draw_hero_band(d, x, y, w, h, hero, art_fill):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    ax, ay, aw, ah = x + 8, y + 8, 96, h - 16
    d.rectangle([ax, ay, ax + aw, ay + ah], fill=art_fill)
    if hero["tag"] == "[CL]":
        d.polygon([(ax + 15, ay + ah - 18), (ax + 48, ay + 22), (ax + 81, ay + ah - 18)], fill=(60, 60, 60))
        d.rectangle([ax + 42, ay + 30, ax + 54, ay + ah - 18], fill=(40, 40, 40))
        d.ellipse([ax + 28, ay + 12, ax + 68, ay + 44], fill=(255, 120, 60))
    else:
        for i, v in enumerate([22, 34, 30, 48, 58, 72, 66, 84]):
            bx = ax + 6 + i * 10
            d.rectangle([bx, ay + ah - 10 - v, bx + 7, ay + ah - 10], fill=(255, 255, 255))
        d.line([(ax + 8, ay + ah - 34), (ax + aw - 8, ay + 14)], fill=RED, width=3)
    tx = ax + aw + 10
    twd = x + w - 8 - tx
    fk = F(10, bold=True)
    d.text((tx, y + 8), hero["kicker"] + "  " + hero["tag"], font=fk, fill=RED)
    reg_textbox((tx, y + 8, tx + tw(hero["kicker"] + "  " + hero["tag"], fk), y + 8 + 10))
    ft = F(13, bold=True)
    lines = wrap(hero["title"], ft, twd)
    need(len(lines) <= 2, "band title wraps to 3 lines: %s" % hero["title"])
    ty = draw_lines(d, tx, y + 24, lines, ft, INK, leading=15)
    fd = F(10)
    lines = wrap(hero["deck"], fd, twd)
    need(len(lines) <= 2, "band deck wraps to 3 lines")
    ty = draw_lines(d, tx, ty + 2, lines, fd, INK, leading=12)
    fw = F(10)
    fwb = F(10, bold=True)
    lines = wrap(hero["why"], fw, twd, prefix="WHY IT MATTERS: ")
    need(len(lines) <= 2, "band why wraps to 3 lines")
    ty = draw_lines(d, tx, ty + 2, lines, fw, MUTED, leading=12,
                    prefix="WHY IT MATTERS: ", prefix_font=fwb, prefix_fill=NAVY)
    fs = F(10, bold=True)
    need(tw(hero["stat"], fs) <= twd, "band stat too wide")
    need(ty + 2 <= y + h - 16, "band text collides with stat line")
    d.text((tx, y + h - 16), hero["stat"], font=fs, fill=TEAL)
    reg_textbox((tx, y + h - 16, tx + tw(hero["stat"], fs), y + h - 16 + 10))


LAND_POLYS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 52), (-75, 35), (-80, 25), (-97, 26), (-105, 20), (-115, 32), (-125, 40), (-125, 49), (-150, 60)],
    [(-80, 10), (-60, 5), (-35, -5), (-40, -20), (-55, -35), (-70, -50), (-73, -35), (-80, -15)],
    [(-10, 36), (-9, 43), (0, 48), (5, 58), (10, 57), (18, 56), (28, 60), (30, 70), (40, 68), (45, 60), (40, 50), (28, 45), (20, 40), (12, 44), (3, 43), (-2, 37)],
    [(-17, 15), (-10, 30), (10, 37), (30, 32), (35, 28), (43, 12), (51, 11), (48, 0), (40, -20), (35, -30), (20, -35), (12, -18), (9, 4), (-8, 5)],
    [(40, 70), (60, 70), (80, 73), (110, 76), (140, 72), (160, 66), (162, 60), (158, 52), (142, 45), (140, 38), (127, 40), (120, 32), (110, 20), (105, 8), (100, 7), (95, 15), (90, 22), (80, 8), (77, 8), (72, 20), (66, 25), (60, 25), (52, 26), (48, 29), (43, 29), (40, 35), (40, 50)],
    [(113, -22), (114, -32), (130, -32), (137, -35), (142, -38), (150, -37), (153, -27), (146, -19), (142, -11), (136, -12), (132, -11), (126, -14), (122, -17)],
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    d.rectangle([x + 1, y + 1, x + w - 1, y + 25], fill=NAVY)
    fh = F(12, bold=True)
    head = "MAP — EVERY PIN IS A STORY IN THIS IMAGE"
    need(tw(head, fh) <= w - 16, "map header too wide")
    d.text((x + 8, y + 6), head, font=fh, fill=(255, 255, 255))
    reg_textbox((x + 8, y + 6, x + 8 + tw(head, fh), y + 6 + 12))
    px, py, pw, ph = x + 1, y + 26, w - 2, h - 27
    d.rectangle([px, py, px + pw, py + ph], fill=OCEAN)

    def proj(lon, lat):
        return (px + (lon + 180.0) / 360.0 * pw, py + (85.0 - lat) / 145.0 * ph)

    for poly in LAND_POLYS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND, outline=(160, 145, 115))
    dots = []
    for name, lon, lat in PINS:
        cx, cy = proj(lon, lat)
        dots.append((name, cx, cy))
    for i in range(len(dots)):
        for j in range(i + 1, len(dots)):
            dist = ((dots[i][1] - dots[j][1]) ** 2 + (dots[i][2] - dots[j][2]) ** 2) ** 0.5
            need(dist >= 18, "map dots too close: %s vs %s (%.1f)" % (dots[i][0], dots[j][0], dist))
    fl = F(9, bold=True)
    placed = []
    for name, cx, cy in dots:
        lw = tw(name, fl) + 8
        lh = 14
        cands = [(10, -20), (10, 8), (-lw - 10, -20), (-lw - 10, 8),
                 (10, -34), (-lw - 10, -34), (10, 22), (-lw - 10, 22)]
        chosen = None
        for dx, dy in cands:
            box = (cx + dx, cy + dy, cx + dx + lw, cy + dy + lh)
            if box[0] < px + 2 or box[1] < py + 2 or box[2] > px + pw - 2 or box[3] > py + ph - 2:
                continue
            if any(not (box[2] + 2 <= b[0] or b[2] + 2 <= box[0] or box[3] + 2 <= b[1] or b[3] + 2 <= box[1]) for b in placed):
                continue
            ok = True
            for _, ox, oy in dots:
                ddx = max(box[0] - ox, 0, ox - box[2])
                ddy = max(box[1] - oy, 0, oy - box[3])
                if (ddx * ddx + ddy * ddy) ** 0.5 < 9:
                    ok = False
                    break
            if ok:
                chosen = box
                break
        need(chosen is not None, "no label placement for pin %s" % name)
        placed.append(chosen)
        d.rectangle(chosen, fill=(255, 255, 255), outline=INK, width=1)
        d.text((chosen[0] + 4, chosen[1] + 2), name, font=fl, fill=INK)
        reg_textbox((chosen[0], chosen[1], chosen[2], chosen[3]))
    for name, cx, cy in dots:
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED, outline=(255, 255, 255), width=2)


def draw_timeline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE, width=1)
    fh = F(12, bold=True)
    head = "TIMELINE — THURSDAY 26 NOVEMBER 2026"
    d.text((x + 8, y + 6), head, font=fh, fill=NAVY)
    reg_textbox((x + 8, y + 6, x + 8 + tw(head, fh), y + 6 + 12))
    mid = y + 40
    d.line([(x + 20, mid), (x + w - 20, mid)], fill=NAVY, width=3)
    slot = (w - 40) / len(TIMELINE)
    ft = F(10, bold=True)
    fl = F(9)
    for i, (t, label) in enumerate(TIMELINE):
        cx = x + 20 + slot * (i + 0.5)
        need(tw(t, ft) <= slot - 8, "timeline time too wide: %s" % t)
        d.text((cx - tw(t, ft) / 2, y + 24), t, font=ft, fill=RED)
        reg_textbox((cx - tw(t, ft) / 2, y + 24, cx + tw(t, ft) / 2, y + 24 + 10))
        d.ellipse([cx - 5, mid - 5, cx + 5, mid + 5], fill=RED, outline=(255, 255, 255), width=2)
        lines = wrap(label, fl, slot - 8)
        need(len(lines) <= 2, "timeline label wraps to 3 lines: %s" % label)
        ly = mid + 10
        for ln in lines:
            d.text((cx - tw(ln, fl) / 2, ly), ln, font=fl, fill=INK)
            reg_textbox((cx - tw(ln, fl) / 2, ly, cx + tw(ln, fl) / 2, ly + 9))
            ly += 11
        need(ly <= y + h - 4, "timeline label overflows")


def draw_footer(d, x, y, w, h):
    fl = F(11, bold=True)
    leg = "[C] CONFIRMED  ·  [R] REPORTED  ·  [CL] CLAIM / 25 NOV EVENT"
    need(tw(leg, fl) <= w, "legend too wide")
    d.text((x, y + 4), leg, font=fl, fill=INK)
    reg_textbox((x, y + 4, x + tw(leg, fl), y + 4 + 11))
    fo = F(10)
    leftout = ("LEFT OUT ON PURPOSE: COP31 (22 Nov) · Shenzhou-24 (25 Nov) · Cairo tanker (25 Nov) · "
               "Cartagena hostages (25 Nov) · Australia-Solomon pact (25 Nov) · UK energy prices (25 Nov) · Huawei verdict (24 Nov)")
    lines = wrap(leftout, fo, w)
    need(len(lines) <= 2, "left-out wraps to 3 lines")
    ly = draw_lines(d, x, y + 22, lines, fo, MUTED, leading=12)
    fs = F(9)
    src = "50 STORIES  •  THURSDAY 26 NOVEMBER 2026  •  Sources: Reuters · AP · BBC · CNN · UKMTO · ONS · KCNA · FCC"
    need(tw(src, fs) <= w, "footer source line too wide")
    d.text((x, ly + 4), src, font=fs, fill=MUTED)
    reg_textbox((x, ly + 4, x + tw(src, fs), ly + 4 + 9))
    need(ly + 4 + 9 <= y + h, "footer overflows")


def main():
    check_content()
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_datecheck(d)
    draw_also(d, 8, 110, 556, 420)
    draw_cards(d, 8, 538, 556, 330)
    draw_hero_macy(d, 572, 110, 444, 270)
    draw_hero_band(d, 572, 386, 444, 126, HEROES[1], (70, 70, 78))
    draw_hero_band(d, 572, 518, 444, 126, HEROES[2], (18, 53, 91))
    draw_map(d, 572, 650, 444, 218)
    draw_timeline(d, 8, 874, 1008, 80)
    draw_footer(d, 8, 958, 1008, 66)
    for box in TEXTBOXES:
        need(0 <= box[0] and box[1] >= 0 and box[2] <= W and box[3] <= H,
             "textbox outside canvas: %r" % (box,))
        need(not (box[1] < 72 < box[3] and box[0] < W), "textbox crosses masthead divider: %r" % (box,))
    for box in ARTBOXES:
        need(580 <= box[0] and box[2] <= 1008 and 118 <= box[1] and box[3] <= 258,
             "art element outside Macy art box: %r" % (box,))
    img.save(OUT, "PNG", optimize=True)
    data = open(OUT, "rb").read()
    need(len(data) <= 1024 * 1024, "entry.png over 1 MiB: %d" % len(data))
    print("entry.png %d bytes sha256=%s" % (len(data), hashlib.sha256(data).hexdigest()))
    print("size %dx%d" % img.size)


if __name__ == "__main__":
    main()
