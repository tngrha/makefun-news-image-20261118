"""Draw a 1024x1024 newspaper front page summing up the world news of
Wednesday 18 November 2026, and write it to <MAKEFUN_OUTPUT_DIR>/entry.png.

PIL only, no network, no randomness: the output is byte-identical on
repeat runs. All facts are the verified brief for 18 November 2026.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Palette: newsprint paper, navy ink, Nvidia green accent, red alert.
PAPER = (247, 243, 232)
NAVY = (15, 42, 68)
NAVY2 = (23, 58, 90)
INK = (24, 28, 34)
GREEN = (98, 158, 31)
GREEN_D = (72, 120, 20)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
TEAL = (18, 110, 110)
GREY = (110, 116, 122)
TILE_BG = (255, 255, 255)
RULE = (200, 192, 172)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text to at most max_lines lines, ellipsising the last line."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textlength(last + "\u2026", font=fnt) > max_w:
        last = last[:-1].rstrip()
        if " " in last:
            last = last[: last.rfind(" ")].rstrip()
    lines[-1] = (last + "\u2026") if last else "\u2026"
    return lines


def spaced(draw, xy, text, fnt, fill, tracking=3):
    """Draw text with extra letter spacing."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def draw_chip(draw, x, y, s):
    """Flat microchip with pins and circuit traces."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=10, fill=NAVY2,
                           outline=GOLD, width=4)
    inner = s // 4
    draw.rounded_rectangle([x + inner, y + inner, x + s - inner, y + s - inner],
                           radius=6, fill=GREEN)
    draw.text((x + s // 2, y + s // 2 - 14), "NVDA", font=font(BOLD, 22),
              fill=(255, 255, 255), anchor="mm")
    pin = s // 6
    for i in range(3):
        off = s // 4 + i * s // 4
        draw.line([(x + off, y - 14), (x + off, y)], fill=GOLD, width=5)
        draw.line([(x + off, y + s), (x + off, y + s + 14)], fill=GOLD,
                  width=5)
        draw.line([(x - 14, y + off), (x, y + off)], fill=GOLD, width=5)
        draw.line([(x + s, y + off), (x + s + 14, y + off)], fill=GOLD,
                  width=5)
    # circuit traces
    draw.line([(x + s + 14, y + s // 4), (x + s + 44, y + s // 4),
               (x + s + 44, y - 10)], fill=GOLD, width=3)
    draw.ellipse([x + s + 38, y - 16, x + s + 50, y - 4], fill=GOLD)


def draw_chart(draw, x, y, w, h):
    """Steeply rising stock chart with arrow, on a panel."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(255, 255, 255))
    draw.line([(x + 14, y + h - 14), (x + w - 14, y + h - 14)], fill=GREY, width=2)
    pts = [(x + 18, y + h - 34), (x + 52, y + h - 40), (x + 86, y + h - 52),
           (x + 120, y + h - 58), (x + 154, y + h - 92), (x + 188, y + h - 118),
           (x + w - 22, y + 26)]
    draw.line(pts, fill=GREEN, width=6, joint="curve")
    hx, hy = pts[-1]
    draw.polygon([(hx + 10, hy - 12), (hx + 12, hy + 6), (hx - 8, hy - 2)],
                 fill=GREEN)
    draw.text((x + 16, y + 8), "+100% YoY", font=font(BOLD, 20), fill=GREEN_D)


def icon(draw, kind, x, y, s, bg):
    """Small flat pictogram inside a coloured square."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=10, fill=bg)
    cx, cy = x + s // 2, y + s // 2
    white = (255, 255, 255)
    if kind == "globe":  # ASEAN / Manila summit
        draw.ellipse([x + 10, y + 10, x + s - 10, y + s - 10], outline=white,
                     width=4)
        draw.ellipse([x + 20, y + 10, x + s - 20, y + s - 10], outline=white,
                     width=3)
        draw.line([(x + 10, cy), (x + s - 10, cy)], fill=white, width=3)
        draw.line([(x + 10, cy - 9), (x + s - 10, cy - 9)], fill=white, width=2)
        draw.line([(x + 10, cy + 9), (x + s - 10, cy + 9)], fill=white, width=2)
    elif kind == "bridge":
        draw.line([(x + 8, y + s - 12), (x + s - 8, y + s - 12)], fill=white,
                  width=4)
        draw.arc([x + 8, y + 12, x + s - 8, y + s - 6], 180, 360, fill=white,
                 width=4)
        for px in (x + 16, x + s // 2, x + s - 16):
            draw.line([(px, y + 22), (px, y + s - 12)], fill=white, width=4)
    elif kind == "radar":  # drone / radar
        for r in (10, 18, 26):
            draw.arc([cx - r, cy - r, cx + r, cy + r], 270, 30, fill=white,
                     width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
        draw.line([(cx, cy), (cx + 20, cy - 20)], fill=white, width=3)
    elif kind == "trade":  # two-way trade arrows
        draw.line([(x + 10, cy - 10), (x + s - 16, cy - 10)], fill=white,
                  width=5)
        draw.polygon([(x + s - 10, cy - 18), (x + s - 10, cy - 2),
                      (x + s - 2, cy - 10)], fill=white)
        draw.line([(x + s - 10, cy + 10), (x + 16, cy + 10)], fill=white,
                  width=5)
        draw.polygon([(x + 10, cy + 2), (x + 10, cy + 18), (x + 2, cy + 10)],
                     fill=white)
    elif kind == "scales":  # sanctions / law
        draw.line([(cx, y + 10), (cx, y + s - 12)], fill=white, width=4)
        draw.line([(x + 12, y + 16), (x + s - 12, y + 16)], fill=white, width=4)
        for sx in (x + 14, x + s - 14):
            draw.line([(sx, y + 16), (sx, y + 30)], fill=white, width=3)
            draw.polygon([(sx - 9, y + 30), (sx + 9, y + 30), (sx, y + 42)],
                         fill=white)
        draw.line([(x + 14, y + s - 12), (x + s - 14, y + s - 12)], fill=white,
                  width=4)
    elif kind == "warn":  # UN casualty toll
        draw.polygon([(cx, y + 8), (x + s - 8, y + s - 10), (x + 8, y + s - 10)],
                     fill=white)
        draw.text((cx, cy + 2), "!", font=font(BOLD, 30), fill=RED,
                  anchor="mm")
    elif kind == "cricket":
        draw.line([(x + 14, y + s - 12), (x + s - 22, y + 16)], fill=white,
                  width=7)
        draw.ellipse([x + s - 26, y + 8, x + s - 8, y + 26], fill=RED)
        draw.line([(x + 12, y + 12), (x + 26, y + 26)], fill=white, width=3)
        draw.line([(x + 12, y + 26), (x + 26, y + 12)], fill=white, width=3)
    elif kind == "bank":
        draw.polygon([(x + 6, y + 22), (cx, y + 8), (x + s - 6, y + 22)],
                     fill=white)
        for px in (x + 13, x + 24, x + 35):
            draw.line([(px, y + 26), (px, y + s - 14)], fill=white, width=4)
        draw.line([(x + 8, y + s - 12), (x + s - 8, y + s - 12)], fill=white,
                  width=4)


TILES = [
    ("globe", "ASIA", NAVY2,
     "TRUMP IN MANILA FOR ASEAN TALKS",
     "Modi at ASEAN\u2013India summit; defence ties grow."),
    ("bridge", "EUROPE", RED,
     "UKRAINE HITS CRIMEAN BRIDGE AGAIN",
     "Second day of strikes; Russia hits Kyiv bridges."),
    ("radar", "MIDDLE EAST", (122, 44, 44),
     "IRAN DRONES HIT US BASE IN BAHRAIN",
     "Intercepted; tanker hit in Hormuz, 21 of 24 saved."),
    ("trade", "WORLD", TEAL,
     "CANADA, CHINA EXTEND TRADE DEALS",
     "Xi meets Carney ahead of APEC; trade ties widen."),
    ("scales", "MIDDLE EAST", (90, 60, 20),
     "UK SANCTIONS 8 SETTLEMENT FIRMS",
     "Ceasefire may collapse; a hot meal every 2 days."),
    ("warn", "WORLD", (60, 60, 60),
     "372 CIVILIANS KILLED IN UKRAINE",
     "UN toll for October; 2,230+ deaths in Sudan."),
    ("cricket", "SPORT", GREEN_D,
     "DHONI RETIRES, SHAH RE-ELECTED",
     "Dhoni becomes CSK mentor; India win SAFF 2\u20131."),
    ("bank", "MARKETS", (70, 70, 110),
     "DEUTSCHE BANK IGNORED WARNINGS",
     "Leaked files: compliance alerts on risky clients."),
]

BRIEF = [
    "Cyclone Akvan intensifies in the Bay of Bengal; Chennai\u2013Yangon flights cancelled.",
    "SpaceX catches a falling Starship; Grammy 2027 nominations announced.",
    "Judge extends Trump\u2019s deposition deadline in his $10bn BBC lawsuit to 22 January.",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 104], fill=NAVY)
    d.rectangle([0, 104, W, 108], fill=GOLD)
    spaced(d, (28, 14), "THE WORLD IN ONE PAGE", font(BOLD, 20),
           (255, 255, 255), tracking=4)
    d.text((28, 40), "WEDNESDAY 18 NOVEMBER 2026", font=font(BOLD, 44),
           fill=(255, 255, 255))
    d.text((W - 28, 22), "ONE DAY \u00b7 ONE PAGE", font=font(BOLD, 16),
           fill=GOLD, anchor="ra")

    # ---- Hero: Nvidia ---------------------------------------------------
    hx, hy, hw, hh = 24, 118, 976, 302
    d.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=12, fill=NAVY2)
    d.text((hx + 24, hy + 16), "TOP STORY \u00b7 MARKETS",
           font=font(BOLD, 16), fill=GOLD)
    headline = "NVIDIA REVENUE DOUBLES TO $115.8BN \u2014 BUT HUANG STAYS OUT"
    lines = fit_lines(d, headline, font(BOLD, 34), 560, 3)
    y = hy + 44
    for ln in lines:
        d.text((hx + 24, y), ln, font=font(BOLD, 34), fill=(255, 255, 255))
        y += 40
    summary = ("Revenue $115.84bn, twice a year earlier, in the first report "
               "since Jensen Huang\u2019s ouster. The board says it will not "
               "reinstate him; Trump backs calls to bring him back.")
    slines = fit_lines(d, summary, font(REG, 18), 560, 3)
    y += 6
    for ln in slines:
        d.text((hx + 24, y), ln, font=font(REG, 18), fill=(214, 224, 234))
        y += 24
    # Hero scene: chip + rising chart
    d.rounded_rectangle([hx + 620, hy + 16, hx + hw - 24, hy + hh - 16],
                        radius=12, fill=(13, 38, 60))
    draw_chip(d, hx + 648, hy + 52, 96)
    draw_chart(d, hx + 762, hy + 52, 190, 150)
    d.text((hx + 648, hy + 232), "FIRST REPORT SINCE THE OUSTER",
           font=font(BOLD, 15), fill=GOLD)
    d.text((hx + 648, hy + 256), "Board: no return for Huang",
           font=font(REG, 16), fill=(214, 224, 234))

    # ---- Story grid: 2 cols x 4 rows ------------------------------------
    gx, gy = 24, 432
    tw, th, gap = 482, 110, 12
    tag_f = font(BOLD, 13)
    head_f = font(BOLD, 26)
    sum_f = font(REG, 15)
    for i, (kind, tag, color, head, summ) in enumerate(TILES):
        x = gx + (i % 2) * (tw + gap)
        y = gy + (i // 2) * (th + gap)
        d.rounded_rectangle([x, y, x + tw, y + th], radius=10, fill=TILE_BG,
                            outline=RULE, width=1)
        icon(d, kind, x + 12, y + 12, 52, color)
        tx = x + 76
        d.text((tx, y + 10), tag, font=tag_f, fill=color)
        hlines = fit_lines(d, head, head_f, tw - 88, 2)
        hy2 = y + 28
        for ln in hlines:
            d.text((tx, hy2), ln, font=head_f, fill=INK)
            hy2 += 29
        max_sum_lines = 2 if len(hlines) == 1 else 1
        slines = fit_lines(d, summ, sum_f, tw - 88, max_sum_lines)
        sy = hy2 + 1
        for ln in slines:
            d.text((tx, sy), ln, font=sum_f, fill=(74, 80, 88))
            sy += 19

    # ---- Footer: also in brief ------------------------------------------
    fx, fy, fw, fh = 24, 916, 976, 92
    d.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=10, fill=NAVY)
    d.text((fx + 20, fy + 12), "ALSO IN BRIEF", font=font(BOLD, 17),
           fill=GOLD)
    by = fy + 34
    for item in BRIEF:
        d.text((fx + 20, by), "\u2022  " + item, font=font(REG, 15),
               fill=(255, 255, 255))
        by += 18
    d.text((W - 28, fy + 12), "18 NOV 2026", font=font(BOLD, 15), fill=GOLD,
           anchor="ra")

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
