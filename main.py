"""Draw a 1024x1024 newspaper front page summing up the world news of
Wednesday 18 November 2026, and write it to <MAKEFUN_OUTPUT_DIR>/entry.png.

PURE Python 3.13 standard library only (struct, zlib, binascii, os):
the sandbox runs plain python:3.13-slim, which has no Pillow and no
DejaVu fonts, so this file embeds its own 5x7 bitmap font and its own
PNG writer. No network, no randomness, no timestamps in the image:
the output is byte-identical on repeat runs. All facts are the
verified brief for 18 November 2026. All text is rendered UPPERCASE
(newspaper style).
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# Palette: newsprint paper, navy ink, Nvidia green accent, red alert.
PAPER = (247, 243, 232)
NAVY = (15, 42, 68)
NAVY2 = (23, 58, 90)
PANEL = (13, 38, 60)
INK = (24, 28, 34)
GREEN = (98, 158, 31)
GREEN_D = (72, 120, 20)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
TEAL = (18, 110, 110)
GREY = (110, 116, 122)
WHITE = (255, 255, 255)
TILE_BG = (255, 255, 255)
RULE = (200, 192, 172)
LIGHT = (214, 224, 234)
MUTED = (74, 80, 88)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs: 7 rows of 5 characters, '#' = ink, '.' = blank.
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "–": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "—": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "•": (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
    "×": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
}

BLANK = FONT[" "]

# ---------------------------------------------------------------- framebuffer
fb = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i], fb[i + 1], fb[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0 = x if x > 0 else 0
    y0 = y if y > 0 else 0
    x1 = x + w
    if x1 > W:
        x1 = W
    y1 = y + h
    if y1 > H:
        y1 = H
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    n = (x1 - x0) * 3
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        fb[i:i + n] = row


def draw_line(x0, y0, x1, y1, c):
    """Bresenham line, 1px."""
    dx = x1 - x0
    dy = y1 - y0
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    dx = dx if dx >= 0 else -dx
    dy = dy if dy >= 0 else -dy
    if dx >= dy:
        err = 2 * dy - dx
        y = y0
        for k in range(dx + 1):
            set_px(x0 + k * sx, y, c)
            if err >= 0:
                y += sy
                err -= 2 * dx
            err += 2 * dy
    else:
        err = 2 * dx - dy
        x = x0
        for k in range(dy + 1):
            set_px(x, y0 + k * sy, c)
            if err >= 0:
                x += sx
                err -= 2 * dy
            err += 2 * dx


def draw_line_thick(x0, y0, x1, y1, w, c):
    """Thick line: parallel thin lines offset perpendicular-ish."""
    dx = x1 - x0
    dy = y1 - y0
    half = w // 2
    if (dx if dx >= 0 else -dx) >= (dy if dy >= 0 else -dy):
        for k in range(-half, half + 1):
            draw_line(x0, y0 + k, x1, y1 + k, c)
    else:
        for k in range(-half, half + 1):
            draw_line(x0 + k, y0, x1 + k, y1, c)


def fill_circle(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def draw_circle(cx, cy, r, c, quad=None):
    """Midpoint circle outline. quad='ne' plots only the NE quadrant."""
    x, y, d = 0, r, 1 - r
    while x <= y:
        pts = ((x, y), (y, x), (-x, y), (y, -x),
               (x, -y), (-y, x), (-x, -y), (-y, -x))
        for px, py in pts:
            if quad == "ne" and not (px >= 0 and py <= 0):
                continue
            set_px(cx + px, cy + py, c)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1


def fill_polygon(pts, c):
    """Scanline fill (even-odd), deterministic: intersections sorted."""
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(xs[i])
            xb = int(xs[i + 1])
            fill_rect(xa, y, xb - xa + 1, 1, c)


def rounded_rect(x, y, w, h, r, c):
    fill_rect(x + r, y, w - 2 * r, h, c)
    fill_rect(x, y + r, w, h - 2 * r, c)
    for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                   (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
        fill_circle(cx, cy, r, c)


def rounded_rect_outline(x, y, w, h, r, width, border, fill):
    rounded_rect(x, y, w, h, r, border)
    rounded_rect(x + width, y + width, w - 2 * width, h - 2 * width,
                 r - width if r > width else 0, fill)


# ---------------------------------------------------------------- text
def norm(text):
    """Uppercase newspaper text; fold lookalike punctuation to glyphs."""
    return (text.upper()
            .replace("’", "'").replace("‘", "'")
            .replace("·", "•"))


def text_width(text, scale, tracking=0):
    n = len(text)
    if n == 0:
        return 0
    return n * 5 * scale + (n - 1) * (scale + tracking)


def draw_text(x, y, text, scale, c, tracking=0):
    """Draw text at integer scale; glyph advance is 6*scale + tracking."""
    adv = 6 * scale + tracking
    cx = x
    for ch in text:
        rows = FONT.get(ch, BLANK)
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == "#":
                    fill_rect(cx + rx * scale, y + ry * scale,
                              scale, scale, c)
        cx += adv
    return cx


def wrap(text, scale, max_w, tracking=0):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, tracking) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, scale, max_w, max_lines, tracking=0):
    """Wrap text to at most max_lines lines, ellipsising the last line."""
    lines = wrap(text, scale, max_w, tracking)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and text_width(last + "...", scale, tracking) > max_w:
        last = last[:-1].rstrip()
        if " " in last:
            last = last[:last.rfind(" ")].rstrip()
    lines[-1] = (last + "...") if last else "..."
    return lines


# ---------------------------------------------------------------- pictograms
def draw_chip(x, y, s):
    """Flat microchip with pins and circuit traces."""
    rounded_rect_outline(x, y, s, s, 10, 4, GOLD, NAVY2)
    inner = s // 4
    rounded_rect(x + inner, y + inner, s - 2 * inner, s - 2 * inner, 6, GREEN)
    label = "NVDA"
    draw_text(x + s // 2 - text_width(label, 2) // 2, y + s // 2 - 7,
              label, 2, WHITE)
    for i in range(3):
        off = s // 4 + i * s // 4
        fill_rect(x + off - 2, y - 14, 5, 14, GOLD)
        fill_rect(x + off - 2, y + s, 5, 14, GOLD)
        fill_rect(x - 14, y + off - 2, 14, 5, GOLD)
        fill_rect(x + s, y + off - 2, 14, 5, GOLD)
    # circuit traces (partly covered by the chart panel drawn after)
    draw_line_thick(x + s + 14, y + s // 4, x + s + 44, y + s // 4, 3, GOLD)
    draw_line_thick(x + s + 44, y + s // 4, x + s + 44, y - 10, 3, GOLD)
    fill_circle(x + s + 44, y - 10, 6, GOLD)


def draw_chart(x, y, w, h):
    """Steeply rising stock chart with arrow, on a panel."""
    rounded_rect(x, y, w, h, 10, WHITE)
    draw_text(x + 16, y + 8, "+100% YOY", 2, GREEN_D)
    fill_rect(x + 14, y + h - 14, w - 28, 2, GREY)
    pts = [(x + 18, y + h - 34), (x + 52, y + h - 40), (x + 86, y + h - 52),
           (x + 120, y + h - 58), (x + 154, y + h - 92), (x + 188, y + h - 118),
           (x + w - 22, y + 26)]
    for i in range(len(pts) - 1):
        draw_line_thick(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                        6, GREEN)
    hx, hy = pts[-1]
    fill_polygon([(hx + 10, hy - 12), (hx + 12, hy + 6), (hx - 8, hy - 2)],
                 GREEN)


def icon(kind, x, y, s, bg):
    """Small flat pictogram inside a coloured square."""
    rounded_rect(x, y, s, s, 10, bg)
    cx, cy = x + s // 2, y + s // 2
    if kind == "globe":  # ASEAN / Manila summit
        draw_circle(cx, cy, 16, WHITE)
        for yy in range(cy - 16, cy + 17):
            t = (yy - cy) / 16.0
            dx = int(8 * (1 - t * t) ** 0.5)
            set_px(cx - dx, yy, WHITE)
            set_px(cx + dx, yy, WHITE)
        fill_rect(x + 10, cy - 1, 33, 3, WHITE)
        fill_rect(cx - 13, cy - 10, 27, 2, WHITE)
        fill_rect(cx - 13, cy + 8, 27, 2, WHITE)
    elif kind == "bridge":
        fill_rect(x + 8, y + s - 12, s - 15, 3, WHITE)
        for px in range(cx - 18, cx + 19):
            t = (px - cx) / 18.0
            py = (y + s - 12) - int(14 * (1 - t * t) ** 0.5)
            set_px(px, py, WHITE)
            set_px(px, py + 1, WHITE)
        for px in (x + 16, cx - 1, x + s - 17):
            fill_rect(px, y + 30, 3, 11, WHITE)
    elif kind == "radar":  # drone / radar
        for r in (10, 18, 26):
            draw_circle(cx, cy, r, WHITE, quad="ne")
        fill_circle(cx, cy, 4, RED)
        draw_line_thick(cx, cy, cx + 20, cy - 20, 3, WHITE)
    elif kind == "trade":  # two-way trade arrows
        fill_rect(x + 10, cy - 12, 27, 5, WHITE)
        fill_polygon([(x + s - 10, cy - 18), (x + s - 10, cy - 2),
                      (x + s - 2, cy - 10)], WHITE)
        fill_rect(x + 15, cy + 8, 27, 5, WHITE)
        fill_polygon([(x + 10, cy + 2), (x + 10, cy + 18),
                      (x + 2, cy + 10)], WHITE)
    elif kind == "scales":  # sanctions / law
        fill_rect(cx - 2, y + 10, 4, 30, WHITE)
        fill_rect(x + 12, y + 14, s - 23, 4, WHITE)
        for sx in (x + 14, x + s - 14):
            fill_rect(sx - 1, y + 18, 3, 12, WHITE)
            fill_polygon([(sx - 9, y + 30), (sx + 9, y + 30),
                          (sx, y + 42)], WHITE)
        fill_rect(x + 14, y + s - 12, s - 27, 4, WHITE)
    elif kind == "warn":  # UN casualty toll
        fill_polygon([(cx, y + 8), (x + s - 8, y + s - 10),
                      (x + 8, y + s - 10)], WHITE)
        draw_text(cx - 7, cy - 4, "!", 3, RED)
    elif kind == "cricket":
        draw_line_thick(x + 14, y + s - 12, x + s - 22, y + 16, 7, WHITE)
        fill_circle(x + s - 17, y + 17, 9, RED)
        draw_line_thick(x + 12, y + 12, x + 26, y + 26, 3, WHITE)
        draw_line_thick(x + 12, y + 26, x + 26, y + 12, 3, WHITE)
    elif kind == "bank":
        fill_polygon([(x + 6, y + 22), (cx, y + 8), (x + s - 6, y + 22)],
                     WHITE)
        for px in (x + 13, x + 24, x + 35):
            fill_rect(px, y + 26, 4, 12, WHITE)
        fill_rect(x + 8, y + s - 12, s - 15, 4, WHITE)


# ---------------------------------------------------------------- content
TILES = [
    ("globe", "ASIA", NAVY2,
     "Trump in Manila for ASEAN talks",
     "Modi at ASEAN–India summit; defence ties grow."),
    ("bridge", "EUROPE", RED,
     "Ukraine hits Crimean bridge again",
     "Second day of strikes; Russia hits Kyiv bridges."),
    ("radar", "MIDDLE EAST", (122, 44, 44),
     "Iran drones hit US base in Bahrain",
     "Intercepted; tanker hit in Hormuz, 21 of 24 saved."),
    ("trade", "WORLD", TEAL,
     "Canada, China extend trade deals",
     "Xi meets Carney ahead of APEC; trade ties widen."),
    ("scales", "MIDDLE EAST", (90, 60, 20),
     "UK sanctions 8 settlement firms",
     "Ceasefire may collapse; a hot meal every 2 days."),
    ("warn", "WORLD", (60, 60, 60),
     "372 civilians killed in Ukraine",
     "UN toll for October; 2,230+ deaths in Sudan."),
    ("cricket", "SPORT", GREEN_D,
     "Dhoni retires, Shah re-elected",
     "Dhoni becomes CSK mentor; India win SAFF 2–1."),
    ("bank", "MARKETS", (70, 70, 110),
     "Deutsche Bank ignored warnings",
     "Leaked files: compliance alerts on risky clients."),
]

BRIEF = [
    "Cyclone Akvan intensifies in the Bay of Bengal; flights cancelled.",
    "SpaceX catches a falling Starship; Grammy 2027 nominations announced.",
    "Judge extends Trump deposition deadline in $10bn BBC lawsuit to 22 January.",
]


# ---------------------------------------------------------------- PNG writer
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += fb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- page
def main():
    fb[:] = bytes(PAPER) * (W * H)

    # ---- Masthead -------------------------------------------------------
    fill_rect(0, 0, W, 104, NAVY)
    fill_rect(0, 104, W, 4, GOLD)
    draw_text(28, 14, norm("The World in One Page"), 3, WHITE, tracking=2)
    draw_text(28, 42, norm("Wednesday 18 November 2026"), 6, WHITE)
    right = norm("One day • One page")
    draw_text(W - 28 - text_width(right, 2), 22, right, 2, GOLD)

    # ---- Hero: Nvidia ---------------------------------------------------
    hx, hy, hw, hh = 24, 118, 976, 302
    rounded_rect(hx, hy, hw, hh, 12, NAVY2)
    draw_text(hx + 24, hy + 16, norm("Top story • Markets"), 2, GOLD)
    headline = norm("NVIDIA revenue doubles to $115.8bn — "
                    "but Huang stays out")
    y = hy + 42
    for ln in fit_lines(headline, 4, 580, 3):
        draw_text(hx + 24, y, ln, 4, WHITE)
        y += 34
    summary = norm("Revenue $115.84bn, twice a year earlier, in the first "
                   "report since Jensen Huang’s ouster. The board says it "
                   "will not reinstate him; Trump backs calls to bring "
                   "him back.")
    y = hy + 148
    for ln in fit_lines(summary, 3, 580, 6):
        draw_text(hx + 24, y, ln, 3, LIGHT)
        y += 25
    # Hero scene: chip + rising chart
    rounded_rect(hx + 620, hy + 16, hw - 644, hh - 32, 12, PANEL)
    draw_chip(hx + 648, hy + 52, 96)
    draw_chart(hx + 762, hy + 52, 190, 150)
    draw_text(hx + 648, hy + 232, norm("First report since ouster"), 2, GOLD)
    draw_text(hx + 648, hy + 254, norm("Board says no return"), 2, LIGHT)

    # ---- Story grid: 2 cols x 4 rows ------------------------------------
    gx, gy = 24, 432
    tw, th, gap = 482, 110, 12
    for i, (kind, tag, color, head, summ) in enumerate(TILES):
        x = gx + (i % 2) * (tw + gap)
        y = gy + (i // 2) * (th + gap)
        rounded_rect_outline(x, y, tw, th, 10, 1, RULE, TILE_BG)
        icon(kind, x + 12, y + 12, 52, color)
        tx = x + 76
        draw_text(tx, y + 8, norm(tag), 2, color)
        hlines = fit_lines(norm(head), 3, tw - 88, 2)
        hy2 = y + 26
        for ln in hlines:
            draw_text(tx, hy2, ln, 3, INK)
            hy2 += 24
        slines = fit_lines(norm(summ), 2, tw - 88, 2)
        sy = hy2 + 4
        for ln in slines:
            draw_text(tx, sy, ln, 2, MUTED)
            sy += 15

    # ---- Footer: also in brief ------------------------------------------
    fx, fy, fw, fh = 24, 916, 976, 92
    rounded_rect(fx, fy, fw, fh, 10, NAVY)
    draw_text(fx + 20, fy + 12, norm("Also in brief"), 2, GOLD)
    date = norm("18 Nov 2026")
    draw_text(W - 28 - text_width(date, 2), fy + 12, date, 2, GOLD)
    by = fy + 34
    for item in BRIEF:
        draw_text(fx + 20, by, norm("•  " + item), 2, WHITE)
        by += 18

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
