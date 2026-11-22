#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news front page (map-led edition).

Reads stories.json beside this file and writes entry.png (1024x1024).
Deterministic: no randomness, no network, fixed fonts.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 24
CW = W - 2 * MARGIN

PAPER = (250, 247, 240)
INK = (24, 24, 28)
FAINT = (90, 88, 84)
RULE = (40, 40, 44)
OCEAN = (168, 200, 224)
LAND = (238, 230, 200)
LAND_EDGE = (120, 110, 80)

REGION_COLORS = {
    "MIDDLE EAST & GULF": (178, 34, 34),
    "EUROPE": (30, 80, 160),
    "ASIA-PACIFIC": (0, 128, 96),
    "AMERICAS": (110, 50, 160),
    "AFRICA": (200, 110, 20),
    "CLIMATE & PLANET": (30, 130, 60),
    "BUSINESS · TECH · SPORT": (160, 30, 110),
}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w, max_lines=None):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while text_w(draw, last + "…", f) > max_w and len(last) > 3:
            last = last[:-1].rstrip()
        lines[-1] = last + "…"
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


# Simplified continent outlines as (lon, lat) polygons, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-78, 58), (-65, 50), (-55, 47), (-60, 45), (-70, 44),
     (-74, 40), (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-89, 30),
     (-94, 29), (-97, 26), (-97, 22), (-94, 18), (-90, 14), (-83, 9),
     (-79, 9), (-81, 13), (-87, 13), (-92, 15), (-97, 16), (-102, 18),
     (-105, 20), (-110, 23), (-114, 29), (-117, 33), (-122, 37), (-124, 46),
     (-128, 51), (-133, 56), (-150, 61), (-162, 61)],
    # Greenland
    [(-45, 60), (-30, 68), (-22, 70), (-25, 76), (-35, 80), (-50, 78),
     (-55, 70), (-53, 64)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-52, 5), (-44, -3), (-35, -8),
     (-39, -13), (-40, -22), (-48, -27), (-52, -33), (-57, -38), (-62, -39),
     (-65, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -50),
     (-73, -44), (-73, -37), (-71, -30), (-70, -20), (-70, -18), (-75, -15),
     (-77, -12), (-81, -5), (-81, 1)],
    # Africa
    [(-17, 15), (-10, 29), (-6, 35), (10, 37), (11, 34), (20, 32), (30, 31),
     (32, 31), (35, 28), (37, 22), (39, 15), (43, 12), (48, 11), (51, 12),
     (51, 10), (48, 5), (42, -2), (40, -10), (40, -16), (36, -22), (33, -26),
     (28, -33), (20, -35), (17, -32), (15, -27), (12, -18), (13, -12),
     (9, -1), (9, 4), (6, 4), (-7, 4), (-13, 8)],
    # Europe (mainland, simplified)
    [(-9, 37), (0, 38), (3, 42), (8, 44), (12, 44), (14, 46), (19, 42),
     (23, 36), (26, 38), (28, 41), (30, 46), (28, 50), (24, 58), (30, 60),
     (31, 70), (25, 71), (18, 69), (12, 64), (5, 60), (5, 58), (8, 57),
     (8, 54), (3, 52), (-2, 50), (-5, 48), (-2, 44), (-9, 43)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (0, 52), (1, 51)],
    # Asia
    [(28, 41), (36, 36), (44, 29), (48, 30), (50, 24), (56, 26), (61, 25),
     (66, 25), (72, 20), (76, 10), (77, 8), (80, 13), (86, 20), (88, 22),
     (92, 16), (98, 10), (100, 6), (103, 1), (104, 9), (106, 9), (109, 15),
     (110, 20), (114, 22), (118, 25), (122, 30), (120, 34), (122, 38),
     (126, 40), (130, 42), (135, 45), (140, 50), (142, 54), (150, 60),
     (160, 60), (170, 66), (178, 65), (178, 68), (170, 69), (160, 69),
     (150, 70), (140, 72), (130, 72), (120, 73), (110, 74), (100, 77),
     (90, 75), (80, 73), (70, 72), (60, 69), (50, 68), (40, 67), (33, 67),
     (30, 60), (28, 50)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 42), (139, 38), (135, 34), (131, 32)],
    # Indonesia (Borneo / Sumatra / Java / New Guinea blobs)
    [(95, 5), (100, 0), (104, -3), (106, -6), (102, -4), (97, 2)],
    [(109, 1), (113, 4), (117, 2), (119, -1), (114, -3), (110, -2)],
    [(105, -6), (110, -7), (114, -8), (114, -9), (106, -8)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (147, -9), (140, -8),
     (134, -4)],
    # Australia
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -36), (140, -38), (145, -38), (147, -38),
     (150, -37), (153, -30), (153, -27), (151, -24), (149, -20), (146, -19),
     (142, -11), (142, -14), (141, -17), (136, -15), (135, -12), (132, -11),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -46), (172, -41), (174, -37), (176, -38), (174, -41), (169, -46)],
]


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    px = x0 + (lon + 180) / 360.0 * (x1 - x0)
    py = y0 + (78 - lat) / 140.0 * (y1 - y0)
    return px, py


def draw_map(draw, box, markers):
    """markers: list of (lon, lat, number, color)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=OCEAN, outline=RULE, width=2)
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0, box)
        draw.line([(gx, y0), (gx, y1)], fill=(150, 185, 215), width=1)
    for lat in range(-45, 76, 15):
        _, gy = project(0, lat, box)
        draw.line([(x0, gy), (x1, gy)], fill=(150, 185, 215), width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    fnum = font(SANS_B, 11)
    for lon, lat, num, color in markers:
        px, py = project(lon, lat, box)
        r = 9
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color,
                     outline=(255, 255, 255), width=2)
        s = str(num)
        tw = text_w(draw, s, fnum)
        draw.text((px - tw / 2, py - 7), s, font=fnum, fill=(255, 255, 255))


# ---------- scene painters: bold, thumbnail-legible ----------

def _sky(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    steps = 24
    for i in range(steps):
        t = i / steps
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        draw.rectangle([x0, y0 + (y1 - y0) * i / steps,
                        x1, y0 + (y1 - y0) * (i + 1) / steps], fill=c)


def scene_conference(d, b):
    _sky(d, b, (30, 60, 110), (90, 140, 190))
    x0, y0, x1, y1 = b
    # globe
    cx, cy, r = (x0 + x1) / 2, y0 + (y1 - y0) * 0.52, (y1 - y0) * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 150, 90),
              outline=(240, 240, 230), width=2)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=(240, 240, 230), width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(240, 240, 230), width=2)
    # delegate desk row
    d.rectangle([x0 + 8, y1 - 12, x1 - 8, y1 - 4], fill=(240, 240, 230))
    for i in range(6):
        dx = x0 + 14 + i * ((x1 - x0 - 28) / 5)
        d.ellipse([dx - 3, y1 - 20, dx + 3, y1 - 14], fill=(240, 240, 230))


def scene_f1car(d, b):
    _sky(d, b, (10, 10, 40), (40, 20, 70))
    x0, y0, x1, y1 = b
    # neon signs
    for i, col in enumerate([(255, 60, 160), (60, 220, 255), (255, 200, 40)]):
        sx = x0 + 10 + i * (x1 - x0 - 20) / 3
        d.rectangle([sx, y0 + 6, sx + 26, y0 + 16], outline=col, width=2)
    # track
    d.rectangle([x0, y1 - 16, x1, y1], fill=(50, 50, 60))
    d.line([(x0, y1 - 8), (x1, y1 - 8)], fill=(255, 255, 255), width=2)
    # car body: nose, cockpit, rear wing, wheels
    cy = y1 - 24
    cx = (x0 + x1) / 2
    d.polygon([(cx - 54, cy - 2), (cx - 34, cy - 10), (cx - 6, cy - 12),
               (cx + 22, cy - 10), (cx + 52, cy - 4), (cx + 54, cy + 2),
               (cx - 52, cy + 2)], fill=(220, 30, 40))
    d.rectangle([cx + 40, cy - 24, cx + 54, cy - 2], fill=(220, 30, 40))
    d.rectangle([cx + 38, cy - 26, cx + 56, cy - 22], fill=(30, 30, 40))
    d.polygon([(cx - 10, cy - 12), (cx - 2, cy - 21), (cx + 10, cy - 12)],
              fill=(20, 20, 20))
    d.rectangle([cx - 58, cy + 2, cx - 44, cy + 6], fill=(30, 30, 40))
    for wx in (cx - 38, cx + 36):
        d.ellipse([wx - 10, cy - 1, wx + 10, cy + 17], fill=(15, 15, 15),
                  outline=(210, 210, 210), width=2)
        d.ellipse([wx - 3, cy + 5, wx + 3, cy + 11], fill=(210, 210, 210))


def scene_missiles(d, b):
    _sky(d, b, (70, 40, 60), (200, 110, 70))
    x0, y0, x1, y1 = b
    # skyline
    heights = [0.45, 0.62, 0.38, 0.55, 0.48, 0.66, 0.42]
    bw = (x1 - x0) / len(heights)
    for i, hf in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 2, y1 - (y1 - y0) * hf, bx + bw - 2, y1],
                    fill=(35, 30, 40))
    # missile arcs
    import math
    for k, (sx, ex) in enumerate([(x0 + 14, x0 + (x1 - x0) * 0.55),
                                  (x1 - 16, x0 + (x1 - x0) * 0.8)]):
        pts = []
        for t in range(21):
            u = t / 20
            px = sx + (ex - sx) * u
            py = y0 + 10 + (y1 - y0 - 24) * (u * u) * 0.9
            pts.append((px, py))
        d.line(pts, fill=(255, 220, 120), width=3)
        hx, hy = pts[-1]
        d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(255, 160, 40))
    # explosion star
    ex, ey = x0 + (x1 - x0) * 0.55, y1 - 14
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        d.line([(ex, ey), (ex + 13 * math.cos(rad), ey + 13 * math.sin(rad))],
               fill=(255, 200, 60), width=3)


def scene_shipfire(d, b):
    _sky(d, b, (90, 120, 160), (170, 200, 225))
    x0, y0, x1, y1 = b
    sea_y = y0 + (y1 - y0) * 0.66
    d.rectangle([x0, sea_y, x1, y1], fill=(40, 90, 140))
    for i in range(5):
        wy = sea_y + 5 + i * 6
        d.line([(x0 + 6 + (i % 2) * 10, wy), (x1 - 6, wy)],
               fill=(120, 180, 220), width=2)
    # hull
    cx = (x0 + x1) / 2
    d.polygon([(cx - 58, sea_y + 2), (cx + 58, sea_y + 2), (cx + 44, sea_y + 14),
               (cx - 44, sea_y + 14)], fill=(60, 40, 35))
    d.rectangle([cx - 40, sea_y - 14, cx + 18, sea_y + 2], fill=(90, 60, 50))
    d.rectangle([cx + 24, sea_y - 20, cx + 38, sea_y + 2], fill=(230, 230, 230))
    # flames
    import math
    for fx, fh in [(cx - 30, 26), (cx - 12, 34), (cx + 4, 24)]:
        d.polygon([(fx - 8, sea_y - 12), (fx, sea_y - 12 - fh),
                   (fx + 8, sea_y - 12)], fill=(255, 110, 20))
        d.polygon([(fx - 4, sea_y - 12), (fx, sea_y - 12 - fh * 0.6),
                   (fx + 4, sea_y - 12)], fill=(255, 200, 60))
    # smoke
    for sx, sy, sr in [(cx - 16, sea_y - 44, 9), (cx - 4, sea_y - 54, 12),
                       (cx + 10, sea_y - 62, 10)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(70, 70, 75))


def scene_quake(d, b):
    _sky(d, b, (150, 180, 210), (220, 230, 240))
    x0, y0, x1, y1 = b
    gy = y0 + (y1 - y0) * 0.62
    # mountains
    d.polygon([(x0, gy), (x0 + (x1 - x0) * 0.3, y0 + 12),
               (x0 + (x1 - x0) * 0.55, gy)], fill=(130, 120, 110))
    d.polygon([(x0 + (x1 - x0) * 0.45, gy), (x0 + (x1 - x0) * 0.72, y0 + 16),
               (x1, gy)], fill=(110, 100, 95))
    # snow caps
    d.polygon([(x0 + (x1 - x0) * 0.3 - 7, y0 + 20), (x0 + (x1 - x0) * 0.3, y0 + 12),
               (x0 + (x1 - x0) * 0.3 + 7, y0 + 20)], fill=(255, 255, 255))
    # ground + crack
    d.rectangle([x0, gy, x1, y1], fill=(150, 120, 90))
    cx = (x0 + x1) / 2
    crack = [(cx - 40, y1 - 2), (cx - 22, gy + 8), (cx - 6, y1 - 6),
             (cx + 8, gy + 10), (cx + 26, y1 - 3), (cx + 44, gy + 7)]
    d.line(crack, fill=(40, 30, 20), width=4)
    # tilted houses
    for hx, tilt in [(x0 + 16, -6), (x1 - 40, 6)]:
        d.polygon([(hx, gy + 2), (hx + 22, gy + 2 + tilt), (hx + 22, gy - 14 + tilt),
                   (hx, gy - 14)], fill=(240, 235, 220), outline=(60, 50, 40))
        d.polygon([(hx - 2, gy - 14), (hx + 11, gy - 24), (hx + 24, gy - 14)],
                  fill=(180, 60, 40))


def scene_crash(d, b):
    d.rectangle(b, fill=(18, 22, 34))
    x0, y0, x1, y1 = b
    # grid
    for i in range(1, 4):
        gy = y0 + (y1 - y0) * i / 4
        d.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(60, 70, 95), width=1)
    # falling line
    pts = [(x0 + 10, y0 + 14), (x0 + (x1 - x0) * 0.3, y0 + 22),
           (x0 + (x1 - x0) * 0.5, y0 + (y1 - y0) * 0.42),
           (x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.58),
           (x1 - 16, y1 - 16)]
    d.line(pts, fill=(255, 60, 60), width=4)
    # arrow head
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 14, ay - 3), (ax - 4, ay - 13)],
              fill=(255, 60, 60))
    # candlesticks
    for i, (oy, cy) in enumerate([(0.2, 0.34), (0.38, 0.55), (0.55, 0.78)]):
        bx = x0 + (x1 - x0) * (0.22 + i * 0.24)
        d.rectangle([bx - 5, y0 + (y1 - y0) * oy, bx + 5, y0 + (y1 - y0) * cy],
                    fill=(255, 90, 90))
    # down percent
    f = font(SANS_B, 20)
    d.text((x0 + 10, y0 + 6), "-5.3%", font=f, fill=(255, 90, 90))


def scene_bars(d, b):
    d.rectangle(b, fill=(45, 48, 60))
    x0, y0, x1, y1 = b
    # silhouette behind bars
    cx = (x0 + x1) / 2
    cy = y0 + (y1 - y0) * 0.42
    d.ellipse([cx - 13, cy - 16, cx + 13, cy + 10], fill=(15, 15, 18))
    d.polygon([(cx - 22, y1), (cx - 16, cy + 12), (cx + 16, cy + 12),
               (cx + 22, y1)], fill=(15, 15, 18))
    # bars
    n = 7
    for i in range(n):
        bx = x0 + 8 + i * ((x1 - x0 - 16) / (n - 1))
        d.rectangle([bx - 3, y0 + 4, bx + 3, y1 - 4], fill=(190, 195, 205))
    d.rectangle([x0 + 4, y0 + 4, x1 - 4, y0 + 10], fill=(190, 195, 205))
    d.rectangle([x0 + 4, y1 - 10, x1 - 4, y1 - 4], fill=(190, 195, 205))


def scene_fence(d, b):
    _sky(d, b, (140, 175, 215), (215, 232, 245))
    x0, y0, x1, y1 = b
    gy = y0 + (y1 - y0) * 0.72
    d.rectangle([x0, gy, x1, y1], fill=(120, 150, 90))
    # fence posts + wires
    n = 6
    for i in range(n):
        fx = x0 + 8 + i * ((x1 - x0 - 16) / (n - 1))
        d.rectangle([fx - 2, gy - 34, fx + 2, gy + 4], fill=(70, 60, 50))
    for wy in (gy - 32, gy - 20, gy - 8):
        d.line([(x0 + 4, wy), (x1 - 4, wy)], fill=(90, 90, 95), width=2)
    # warning sign
    sx, sy = (x0 + x1) / 2, gy - 30
    d.polygon([(sx, sy - 14), (sx - 13, sy + 10), (sx + 13, sy + 10)],
              fill=(255, 200, 30), outline=(30, 30, 30), width=2)
    d.rectangle([sx - 1.5, sy - 6, sx + 1.5, sy + 3], fill=(30, 30, 30))
    d.ellipse([sx - 1.5, sy + 5, sx + 1.5, sy + 8], fill=(30, 30, 30))


def scene_village(d, b):
    _sky(d, b, (170, 205, 235), (235, 242, 248))
    x0, y0, x1, y1 = b
    gy = y0 + (y1 - y0) * 0.68
    d.rectangle([x0, gy, x1, y1], fill=(130, 165, 95))
    # hills
    d.polygon([(x0, gy), (x0 + (x1 - x0) * 0.35, gy - 22),
               (x0 + (x1 - x0) * 0.6, gy)], fill=(105, 140, 85))
    # houses
    for hx, hw in [(x0 + 14, 34), ((x0 + x1) / 2 - 20, 40), (x1 - 52, 34)]:
        d.rectangle([hx, gy - 20, hx + hw, gy + 2], fill=(245, 240, 225),
                    outline=(90, 75, 60))
        d.polygon([(hx - 3, gy - 20), (hx + hw / 2, gy - 32), (hx + hw + 3, gy - 20)],
                  fill=(170, 70, 45))
        d.rectangle([hx + hw / 2 - 4, gy - 10, hx + hw / 2 + 4, gy + 2],
                    fill=(90, 65, 45))
    # red cross flag
    fx = (x0 + x1) / 2 + 26
    d.line([(fx, gy - 40), (fx, gy)], fill=(70, 60, 50), width=3)
    d.rectangle([fx, gy - 40, fx + 20, gy - 26], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.rectangle([fx + 8, gy - 38, fx + 12, gy - 28], fill=(220, 40, 40))
    d.rectangle([fx + 5, gy - 35, fx + 15, gy - 31], fill=(220, 40, 40))


def scene_desert(d, b):
    _sky(d, b, (250, 200, 130), (250, 230, 190))
    x0, y0, x1, y1 = b
    # sun
    d.ellipse([x1 - 34, y0 + 8, x1 - 10, y0 + 32], fill=(255, 170, 40))
    # dunes
    d.polygon([(x0, y1), (x0, y0 + (y1 - y0) * 0.55),
               (x0 + (x1 - x0) * 0.5, y0 + (y1 - y0) * 0.72), (x1, y1)],
              fill=(232, 190, 120))
    d.polygon([(x0, y1), (x0 + (x1 - x0) * 0.4, y0 + (y1 - y0) * 0.68),
               (x1, y0 + (y1 - y0) * 0.8), (x1, y1)], fill=(215, 165, 95))
    # huts
    gy = y0 + (y1 - y0) * 0.78
    for hx in (x0 + 18, (x0 + x1) / 2 - 14, x1 - 52):
        d.polygon([(hx, gy), (hx + 14, gy - 18), (hx + 28, gy)],
                  fill=(160, 115, 60), outline=(110, 80, 40))
        d.rectangle([hx + 11, gy - 8, hx + 17, gy], fill=(80, 55, 30))
    # acacia tree
    tx = x0 + (x1 - x0) * 0.72
    d.line([(tx, gy), (tx + 4, gy - 22)], fill=(90, 65, 40), width=3)
    d.ellipse([tx - 16, gy - 34, tx + 24, gy - 20], fill=(90, 140, 70))


def scene_vial(d, b):
    d.rectangle(b, fill=(225, 238, 248))
    x0, y0, x1, y1 = b
    cx = (x0 + x1) / 2
    # vial
    vw, vh = 34, (y1 - y0) * 0.58
    vy = y1 - vh - 8
    d.rounded_rectangle([cx - vw / 2, vy, cx + vw / 2, vy + vh], radius=6,
                        fill=(200, 230, 250), outline=(60, 90, 130), width=2)
    d.rectangle([cx - vw / 2 + 3, vy + vh * 0.45, cx + vw / 2 - 3, vy + vh - 3],
                fill=(80, 170, 230))
    d.rectangle([cx - 11, vy - 8, cx + 11, vy], fill=(60, 90, 130))
    # label cross
    d.rectangle([cx - 3, vy + 10, cx + 3, vy + 26], fill=(220, 40, 40))
    d.rectangle([cx - 8, vy + 15, cx + 8, vy + 21], fill=(220, 40, 40))
    # virus dots
    for vx, vy2 in [(x0 + 22, y0 + 20), (x1 - 26, y0 + 26), (x0 + 30, y1 - 24),
                    (x1 - 20, y1 - 30)]:
        d.ellipse([vx - 6, vy2 - 6, vx + 6, vy2 + 6], fill=(230, 90, 90))
        for ang in (0, 60, 120, 180, 240, 300):
            import math
            rad = math.radians(ang)
            d.line([(vx, vy2), (vx + 10 * math.cos(rad), vy2 + 10 * math.sin(rad))],
                   fill=(230, 90, 90), width=2)


def scene_plane(d, b):
    _sky(d, b, (120, 170, 220), (210, 232, 248))
    x0, y0, x1, y1 = b
    # clouds
    for cx, cy in [(x0 + 26, y0 + 16), (x1 - 30, y0 + 22), ((x0 + x1) / 2, y1 - 14)]:
        d.ellipse([cx - 18, cy - 7, cx + 18, cy + 7], fill=(255, 255, 255))
    # fuselage
    cy = y0 + (y1 - y0) * 0.52
    d.rounded_rectangle([x0 + 16, cy - 9, x1 - 26, cy + 9], radius=9,
                        fill=(240, 240, 245), outline=(80, 90, 110), width=2)
    d.polygon([(x1 - 26, cy - 9), (x1 - 10, cy), (x1 - 26, cy + 9)],
              fill=(240, 240, 245), outline=(80, 90, 110))
    # tail
    d.polygon([(x0 + 16, cy - 8), (x0 + 26, cy - 26), (x0 + 36, cy - 8)],
              fill=(200, 40, 40))
    # wing + engine with smoke
    wx = (x0 + x1) / 2
    d.polygon([(wx - 4, cy + 6), (wx + 16, cy + 22), (wx + 26, cy + 22),
               (wx + 12, cy + 6)], fill=(150, 160, 180))
    ex, ey = wx + 12, cy + 16
    d.ellipse([ex - 6, ey - 5, ex + 6, ey + 5], fill=(90, 90, 100))
    for i, (sx, sy, sr) in enumerate([(ex - 12, ey - 4, 5), (ex - 24, ey - 8, 7),
                                      (ex - 38, ey - 12, 9)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(100, 100, 105))
    # windows
    for i in range(7):
        wx2 = x0 + 44 + i * 13
        d.ellipse([wx2, cy - 4, wx2 + 5, cy + 1], fill=(60, 90, 130))


SCENES = {
    "conference": scene_conference,
    "f1car": scene_f1car,
    "missiles": scene_missiles,
    "shipfire": scene_shipfire,
    "quake": scene_quake,
    "crash": scene_crash,
    "bars": scene_bars,
    "fence": scene_fence,
    "village": scene_village,
    "desert": scene_desert,
    "vial": scene_vial,
    "plane": scene_plane,
}


# ---------- layout ----------

def chip(draw, x, y, text, bg, fg=(255, 255, 255), size=12):
    f = font(SANS_B, size)
    tw = text_w(draw, text, f)
    draw.rounded_rectangle([x, y, x + tw + 14, y + size + 8], radius=4, fill=bg)
    draw.text((x + 7, y + 4), text, font=f, fill=fg)
    return tw + 14


def badge(draw, cx, cy, num, color, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
                 outline=(255, 255, 255), width=2)
    f = font(SANS_B, 11)
    s = str(num)
    draw.text((cx - text_w(draw, s, f) / 2, cy - 7), s, font=f,
              fill=(255, 255, 255))


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ---
    f_title = font(SERIF_B, 46)
    title = data["masthead"]
    d.text(((W - text_w(d, title, f_title)) / 2, 12), title, font=f_title,
           fill=INK)
    f_date = font(SANS_B, 20)
    date = data["date"]
    d.text(((W - text_w(d, date, f_date)) / 2, 62), date, font=f_date,
           fill=(178, 34, 34))
    d.line([(MARGIN, 88), (W - MARGIN, 88)], fill=RULE, width=3)
    d.line([(MARGIN, 93), (W - MARGIN, 93)], fill=RULE, width=1)

    lead = data["lead"]
    cards = data["cards"]

    # --- lead block: map + text ---
    ly0, ly1 = 100, 318
    map_box = (MARGIN, ly0, MARGIN + 520, ly1)
    markers = [(lead["lon"], lead["lat"], 1, REGION_COLORS["MIDDLE EAST & GULF"])]
    for i, c in enumerate(cards):
        markers.append((c["lon"], c["lat"], i + 2, REGION_COLORS[c["region"]]))
    draw_map(d, map_box, markers)
    f_cap = font(SANS_R, 10.5)
    cap = "Numbers match the story cards below."
    d.text((MARGIN + 4, ly1 + 3), cap, font=f_cap, fill=FAINT)

    tx = MARGIN + 536
    tw_max = W - MARGIN - tx
    y = ly0
    chip(d, tx, y, lead["kicker"], REGION_COLORS["MIDDLE EAST & GULF"], size=13)
    badge(d, tx + tw_max - 12, y + 11, 1, REGION_COLORS["MIDDLE EAST & GULF"],
          r=11)
    y += 30
    f_lead_h = font(SANS_B, 25)
    y = draw_lines(d, wrap(d, lead["headline"], f_lead_h, tw_max, 3),
                   tx, y, f_lead_h, INK, 29)
    y += 4
    f_lead_s = font(SANS_R, 13.5)
    y = draw_lines(d, wrap(d, lead["summary"], f_lead_s, tw_max, 3),
                   tx, y, f_lead_s, (50, 50, 55), 17)
    y += 6
    f_bul = font(SANS_R, 12.5)
    for btxt in lead["bullets"]:
        d.polygon([(tx + 1, y + 3), (tx + 8, y + 7), (tx + 1, y + 11)],
                  fill=(178, 34, 34))
        y = draw_lines(d, wrap(d, btxt, f_bul, tw_max - 14, 2),
                       tx + 14, y, f_bul, INK, 15)
        y += 2

    # --- cards grid: 4 cols x 3 rows ---
    cy0 = 336
    cols, rows, gap = 4, 3, 8
    card_w = (CW - (cols - 1) * gap) / cols
    card_h = 126
    f_kick = font(SANS_B, 9.5)
    f_head = font(SANS_B, 15)
    f_sum = font(SANS_R, 11)
    for i, c in enumerate(cards):
        col, row = i % cols, i // cols
        x = MARGIN + col * (card_w + gap)
        y = cy0 + row * (card_h + gap)
        color = REGION_COLORS[c["region"]]
        d.rectangle([x, y, x + card_w, y + card_h], fill=(255, 255, 255),
                    outline=(170, 165, 155), width=1)
        SCENES[c["scene"]](d, (x + 1, y + 1, x + card_w - 1, y + 51))
        d.rectangle([x, y + 51, x + card_w, y + 54], fill=color)
        badge(d, x + 13, y + 62, i + 2, color, r=9)
        d.text((x + 27, y + 55), c["region"], font=f_kick, fill=color)
        hy = draw_lines(d, wrap(d, c["headline"], f_head, card_w - 12, 2),
                        x + 6, y + 72, f_head, INK, 16)
        draw_lines(d, wrap(d, c["summary"], f_sum, card_w - 12, 2),
                   x + 6, hy, f_sum, (70, 68, 64), 11.5)

    # --- text list: 2 columns ---
    ty = cy0 + rows * (card_h + gap) + 6
    f_sect = font(SANS_B, 13)
    d.text((MARGIN, ty), "ALSO TODAY — AROUND THE WORLD", font=f_sect, fill=INK)
    d.line([(MARGIN, ty + 18), (W - MARGIN, ty + 18)], fill=RULE, width=1)
    ty += 24
    f_th = font(SANS_B, 12.5)
    f_ts = font(SANS_R, 10.5)
    items = data["textlist"]
    half = (len(items) + 1) // 2
    col_w = (CW - 16) / 2
    for idx, it in enumerate(items):
        col = 0 if idx < half else 1
        row = idx if idx < half else idx - half
        x = MARGIN + col * (col_w + 16)
        y = ty + row * 26
        color = REGION_COLORS[it["region"]]
        d.rectangle([x, y + 2, x + 4, y + 22], fill=color)
        hl = wrap(d, it["headline"], f_th, col_w - 12, 1)
        d.text((x + 10, y), hl[0], font=f_th, fill=INK)
        sl = wrap(d, it["summary"], f_ts, col_w - 12, 1)
        d.text((x + 10, y + 13), sl[0], font=f_ts, fill=(80, 78, 74))

    # --- ticker ---
    tick_y = ty + half * 26 + 8
    d.rectangle([MARGIN, tick_y, W - MARGIN, tick_y + 34], fill=(24, 24, 28))
    f_tick = font(SANS_R, 11)
    tick = data["ticker"]
    for r in range(2):
        part = "   •   ".join(tick[r * 3:(r + 1) * 3])
        d.text((MARGIN + 10, tick_y + 4 + r * 15), part, font=f_tick,
               fill=(245, 242, 235))

    # --- footer ---
    f_foot = font(SANS_R, 11)
    foot = data["footer"]
    d.text(((W - text_w(d, foot, f_foot)) / 2, tick_y + 42), foot,
           font=f_foot, fill=FAINT)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
