#!/usr/bin/env python3
"""THE DAILY GLOBE -- a newspaper front page for Thursday 26 November 2026.

Renders one 1024x1024 PNG of a newspaper front page summing up the day's
world news in a single image.  Pure standard library: the PNG is encoded by
hand (zlib + struct), and all text uses a hand-built 5x7 bitmap font defined
below.  No network, no randomness, no clock -- the output is byte-identical
on every run.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py        # writes out/entry.png
    python3 main.py --self-test                   # determinism + size check
"""

import binascii
import hashlib
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1024 * 1024  # 1 MiB

# ---------------------------------------------------------------------------
# Palette (fixed, so output is deterministic)
# ---------------------------------------------------------------------------
INK = (0, 0, 0)
PAPER = (255, 255, 255)
RED = (198, 32, 32)
BLUE = (28, 84, 160)
SKY = (198, 220, 240)
SEA = (36, 110, 180)
YELLOW = (238, 196, 48)
ORANGE = (232, 120, 32)
GREY = (150, 150, 150)
DARKGREY = (90, 90, 90)
LIGHTGREY = (215, 215, 215)
NAVY = (16, 24, 64)
GREEN = (40, 140, 70)
BROWN = (120, 80, 40)
CREAM = (245, 240, 220)

# ---------------------------------------------------------------------------
# 5x7 bitmap font, designed for this page.  Each glyph is 7 rows of 5 cells,
# '#' = ink, '.' = empty.  Text is rendered in capitals only.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    ":": (".....", "..#..", ".....", ".....", "..#..", ".....", "....."),
    ";": (".....", "..#..", ".....", ".....", "..#..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

GLYPH_W = 5
GLYPH_H = 7


def text_width(text, scale):
    """Pixel width of text at the given scale (no trailing spacing)."""
    return len(text) * (GLYPH_W + 1) * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB image with simple drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, bg=PAPER):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def hline(self, x0, x1, y, color):
        if x1 < x0:
            x0, x1 = x1, x0
        self.fill_rect(x0, y, x1 - x0 + 1, 1, color)

    def vline(self, x, y0, y1, color):
        if y1 < y0:
            y0, y1 = y1, y0
        self.fill_rect(x, y0, 1, y1 - y0 + 1, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, color, thick=3):
        half = thick // 2
        for k in range(-half, half + 1):
            self.line(x0 + k, y0, x1 + k, y1, color)

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.set(cx - dx, cy + dy, color)
            self.set(cx + dx, cy + dy, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        ys = sorted((y0, y1, y2))
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for ax, ay, bx, by in ((x0, y0, x1, y1),
                                   (x1, y1, x2, y2),
                                   (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= y <= max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                self.hline(int(min(xs)), int(max(xs)), y, color)

    # -- text ---------------------------------------------------------------
    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, cell in enumerate(row):
                    if cell == "#":
                        self.fill_rect(cx + col_i * scale,
                                       y + row_i * scale,
                                       scale, scale, color)
            cx += (GLYPH_W + 1) * scale

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - text_width(s.upper(), scale) // 2, y, s, scale, color)

    def text_right(self, x, y, s, scale, color):
        self.text(x - text_width(s.upper(), scale), y, s, scale, color)

    def draw_lines(self, x, y, lines, scale, color, leading):
        for i, line_text in enumerate(lines):
            self.text(x, y + i * leading, line_text, scale, color)


# ---------------------------------------------------------------------------
# Scenes: small drawn illustrations, one per story.  Each takes the scene
# box (x, y, w, h) and draws inside it.
# ---------------------------------------------------------------------------
def scene_ship(cv, x, y, w, h):
    """Container ship at dawn under a dock crane, red TARIFF 25% stamp."""
    cv.fill_rect(x, y, w, 80, SKY)
    cv.filled_circle(x + 330, y + 24, 14, YELLOW)
    cv.fill_rect(x + 430, y + 14, 80, 9, PAPER)
    cv.fill_rect(x + 450, y + 25, 55, 8, PAPER)
    cv.fill_rect(x, y + 80, w, h - 80, SEA)
    for wx in range(x + 12, x + w - 12, 46):
        cv.hline(wx, wx + 22, y + 88, PAPER)
    for wx in range(x + 34, x + w - 12, 52):
        cv.hline(wx, wx + 20, y + 130, PAPER)
    # stacked containers
    cols = (RED, BLUE, GREEN, ORANGE)
    for row in range(2):
        for i in range(4):
            cv.fill_rect(x + 200 + i * 52, y + 54 + row * 19, 48, 18,
                         cols[(i + row) % 4])
    # bridge tower with windows
    cv.fill_rect(x + 412, y + 50, 34, 42, PAPER)
    cv.rect(x + 412, y + 50, 34, 42, INK, 1)
    for i in range(3):
        cv.fill_rect(x + 418 + i * 10, y + 56, 6, 6, INK)
    # hull and bow
    cv.fill_rect(x + 190, y + 92, 300, 26, INK)
    cv.fill_triangle(x + 490, y + 92, x + 490, y + 118, x + 536, y + 118, INK)
    # dock crane
    cv.fill_rect(x + 560, y + 6, 4, 112, INK)
    cv.fill_rect(x + 516, y + 10, 104, 5, INK)
    cv.fill_rect(x + 592, y + 15, 2, 36, INK)
    cv.fill_rect(x + 584, y + 51, 18, 12, DARKGREY)
    # red stamp, top left
    cv.fill_rect(x + 10, y + 10, 180, 36, PAPER)
    cv.rect(x + 10, y + 10, 180, 36, RED, 3)
    cv.text_centered(x + 100, y + 21, "TARIFF 25%", 2, RED)


def scene_court(cv, x, y, w, h):
    """A courthouse: pediment, columns, steps."""
    cv.fill_rect(x, y, w, h, CREAM)
    cv.fill_triangle(x + 30, y + 22, x + w - 30, y + 22, x + w // 2, y + 4,
                     GREY)
    cv.fill_rect(x + 40, y + 22, w - 80, 34, LIGHTGREY)
    cv.rect(x + 40, y + 22, w - 80, 34, INK, 1)
    for cx in (x + 70, x + 120, x + 170, x + 220):
        cv.fill_rect(cx, y + 24, 10, 30, PAPER)
        cv.rect(cx, y + 24, 10, 30, INK, 1)
    cv.fill_rect(x + w // 2 - 12, y + 38, 24, 18, INK)
    cv.fill_rect(x + 30, y + 56, w - 60, 4, INK)
    cv.fill_rect(x + 20, y + 60, w - 40, 4, INK)


def scene_tanker(cv, x, y, w, h):
    """A fuel tanker held off by a red no-entry ring."""
    cv.fill_rect(x, y, w, 30, SKY)
    cv.fill_rect(x, y + 30, w, h - 30, SEA)
    cv.hline(x + 12, x + 60, y + 56, PAPER)
    cv.hline(x + 200, x + 250, y + 58, PAPER)
    # tanker hull, tanks and funnel
    cv.fill_rect(x + 20, y + 38, 180, 14, INK)
    cv.fill_triangle(x + 200, y + 38, x + 200, y + 52, x + 226, y + 52, INK)
    for cx in (x + 60, x + 105, x + 150):
        cv.filled_circle(cx, y + 32, 9, PAPER)
        cv.circle(cx, y + 32, 9, INK)
    cv.fill_rect(x + 180, y + 24, 14, 14, RED)
    # red no-entry ring
    cx, cy = x + 268, y + 32
    cv.filled_circle(cx, cy, 20, RED)
    cv.filled_circle(cx, cy, 14, PAPER)
    cv.thick_line(cx - 13, cy + 13, cx + 13, cy - 13, RED, 5)


def scene_bomber(cv, x, y, w, h):
    """A bomber jet over a coastline."""
    cv.fill_rect(x, y, w, 40, SKY)
    cv.fill_rect(x, y + 40, w, h - 40, SEA)
    cv.fill_triangle(x, y + 64, x + 170, y + 64, x, y + 42, GREEN)
    cv.hline(x + 180, x + 300, y + 52, PAPER)
    # fuselage, nose, tail, swept wings
    cv.fill_rect(x + 120, y + 16, 110, 8, DARKGREY)
    cv.fill_triangle(x + 230, y + 16, x + 230, y + 24, x + 252, y + 20,
                     DARKGREY)
    cv.fill_triangle(x + 118, y + 16, x + 118, y + 4, x + 132, y + 16,
                     DARKGREY)
    cv.fill_triangle(x + 150, y + 16, x + 172, y + 16, x + 158, y + 34,
                     DARKGREY)
    cv.fill_triangle(x + 182, y + 16, x + 204, y + 16, x + 192, y + 34,
                     DARKGREY)
    cv.fill_rect(x + 216, y + 18, 8, 4, INK)


def scene_gate(cv, x, y, w, h):
    """A shut diplomatic gate with a CLOSED sign."""
    cv.fill_rect(x, y, w, h, CREAM)
    for bx in range(x + 8, x + w - 8, 14):
        cv.fill_rect(bx, y + 6, 2, 48, INK)
    cv.fill_rect(x + 6, y + 12, w - 12, 3, INK)
    cv.fill_rect(x + 6, y + 48, w - 12, 3, INK)
    cv.fill_rect(x + 6, y + 2, 8, 58, INK)
    cv.fill_rect(x + w - 14, y + 2, 8, 58, INK)
    cx = x + w // 2
    cv.fill_rect(cx - 48, y + 18, 96, 28, PAPER)
    cv.rect(cx - 48, y + 18, 96, 28, INK, 2)
    cv.text_centered(cx, y + 25, "CLOSED", 2, INK)
    cv.fill_rect(x, y + 58, w, 6, GREY)


def scene_boats(cv, x, y, w, h):
    """Small crowded boats at sea."""
    cv.fill_rect(x, y, w, h, SEA)
    cv.hline(x + 10, x + 90, y + 12, PAPER)
    cv.hline(x + 200, x + 290, y + 20, PAPER)
    cv.hline(x + 120, x + 200, y + 56, PAPER)
    # first boat
    cv.fill_rect(x + 30, y + 34, 90, 10, BROWN)
    cv.vline(x + 75, y + 12, y + 34, INK)
    for px in (x + 45, x + 60, x + 75, x + 90, x + 105):
        cv.filled_circle(px, y + 30, 3, INK)
    # second boat
    cv.fill_rect(x + 180, y + 42, 80, 9, BROWN)
    cv.vline(x + 220, y + 24, y + 42, INK)
    for px in (x + 195, x + 210, x + 225, x + 240):
        cv.filled_circle(px, y + 38, 3, INK)


def scene_rocket(cv, x, y, w, h):
    """A rocket climbing at night."""
    cv.fill_rect(x, y, w, h, NAVY)
    for sx, sy in ((20, 8), (60, 20), (100, 6), (150, 16), (200, 8),
                   (250, 22), (290, 10), (40, 40), (230, 44), (280, 38),
                   (90, 48), (180, 52)):
        cv.fill_rect(x + sx, y + sy, 2, 2, PAPER)
    cv.filled_circle(x + 270, y + 14, 10, (240, 240, 220))
    # flame, fins, body, nose
    cv.fill_triangle(x + 143, y + 44, x + 155, y + 44, x + 149, y + 60,
                     ORANGE)
    cv.fill_triangle(x + 145, y + 44, x + 153, y + 44, x + 149, y + 56,
                     YELLOW)
    cv.fill_triangle(x + 140, y + 38, x + 128, y + 50, x + 140, y + 44, RED)
    cv.fill_triangle(x + 158, y + 38, x + 170, y + 50, x + 158, y + 44, RED)
    cv.fill_rect(x + 140, y + 14, 18, 30, PAPER)
    cv.rect(x + 140, y + 14, 18, 30, INK, 1)
    cv.fill_triangle(x + 140, y + 14, x + 158, y + 14, x + 149, y + 2, RED)
    cv.filled_circle(x + 149, y + 24, 3, BLUE)


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
def build_page():
    cv = Canvas(WIDTH, HEIGHT)
    # page border
    cv.rect(12, 12, 1000, 1000, INK, 2)

    # ---- masthead ---------------------------------------------------------
    cv.text_centered(512, 18, "THE WORLD IN ONE PAGE", 2, INK)
    cv.text_centered(512, 36, "THE DAILY GLOBE", 8, INK)
    cv.fill_rect(24, 100, 976, 3, INK)
    cv.text(24, 108, "THURSDAY, 26 NOVEMBER 2026", 2, INK)
    cv.text_right(1000, 108, "ONE DAY - ONE PAGE", 2, INK)
    cv.fill_rect(24, 128, 976, 1, INK)

    # ---- lead story (left) + markets (right) ------------------------------
    lead_x, lead_y, lead_w = 24, 140, 624
    mk_x, mk_y, mk_w = 664, 140, 336
    cv.vline(656, 140, 428, INK)

    cv.text(lead_x, lead_y + 6, "LEAD STORY - TRADE WAR", 2, RED)
    cv.text(lead_x, lead_y + 28, "TRUMP'S NEW TARIFF WAVE", 4, INK)
    cv.text(lead_x, lead_y + 60, "HITS 14 NATIONS", 4, INK)
    deck = ("US PROPOSES UP TO 25% ON INDIA, 15% ON TAIWAN; "
            "MARKETS SINK AS THE AI ROUT SPREADS.")
    cv.draw_lines(lead_x, lead_y + 96, wrap_text(deck, lead_w, 2),
                  2, INK, 20)
    scene_ship(cv, lead_x, lead_y + 138, lead_w, 142)

    # markets column
    cv.text(mk_x, mk_y + 6, "MARKETS", 3, INK)
    cv.fill_rect(mk_x, mk_y + 32, mk_w, 2, INK)
    chart_x, chart_y, chart_w, chart_h = mk_x, mk_y + 40, mk_w, 124
    cv.rect(chart_x, chart_y, chart_w, chart_h, INK, 1)
    for gy in (chart_y + 31, chart_y + 62, chart_y + 93):
        cv.hline(chart_x + 1, chart_x + chart_w - 2, gy, LIGHTGREY)
    cv.text(chart_x + 12, chart_y + 6, "NASDAQ -4%", 2, RED)
    pts = [(8, 30), (50, 40), (92, 36), (134, 54), (176, 50),
           (218, 68), (260, 64), (302, 88), (326, 98)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.thick_line(chart_x + ax, chart_y + ay,
                      chart_x + bx, chart_y + by, RED, 3)
    figures = ("NASDAQ -4% ON AI ROUT",
               "TAIWAN -1,927 PTS",
               "NTD PAST 33 PER USD",
               "BEIGE BOOK: MODEST",
               "GROWTH, WAGE GAINS")
    cv.draw_lines(mk_x, mk_y + 172, list(figures), 2, INK, 22)

    cv.fill_rect(24, 436, 976, 1, INK)

    # ---- secondary stories: two rows of three -----------------------------
    stories = [
        ("SOUTH AFRICA", "COURT VOIDS IMPEACHMENT REPORT",
         "RAMAPHOSA REPORT RULED UNLAWFUL BY COURT.", scene_court),
        ("CUBA", "WHO: END CUBA FUEL BLOCKADE",
         "WHO CHIEF URGES END TO US FUEL BLOCKADE ON CUBA.", scene_tanker),
        ("PHILIPPINES", "CHINESE BOMBER NEARS COAST",
         "BOMBER FLIES WITHIN 45 NM OF COAST, 170 FROM MANILA.",
         scene_bomber),
        ("NORTH KOREA", "PYONGYANG SHUTS SWISS OFFICE",
         "SWISS DIPLOMATS GIVEN 48 HOURS TO LEAVE.", scene_gate),
        ("CANARY ISLANDS", "RECORD DAY AT CANARIES",
         "NEARLY 2,000 MIGRANTS ARRIVE IN ONE DAY.", scene_boats),
        ("SPACE", "FIRST FOREIGNER ON TIANGONG",
         "PAKISTAN'S ZEESHAN ALI FLIES ON SHENZHOU-24.", scene_rocket),
    ]
    col_w = 314
    col_xs = (24, 354, 684)
    for row_i in range(2):
        row_y = 448 + row_i * 176
        for col_i in range(3):
            kicker, headline, deck_text, scene = stories[row_i * 3 + col_i]
            cx = col_xs[col_i]
            cv.text(cx, row_y, kicker, 2, RED)
            scene(cv, cx, row_y + 18, col_w, 64)
            cv.draw_lines(cx, row_y + 88,
                          wrap_text(headline, col_w, 2), 2, INK, 20)
            cv.draw_lines(cx, row_y + 126,
                          wrap_text(deck_text, col_w, 1), 1, INK, 9)

    cv.fill_rect(24, 796, 976, 1, INK)

    # ---- sport strip -------------------------------------------------------
    cv.text(24, 806, "SPORT", 3, INK)
    sport = ("REAL MADRID 5-1 PSV - MBAPPE BRACE, BELLINGHAM STUNNER",
             "SOUTH AFRICA SWEEP BANGLADESH 2-0 IN 2ND TEST",
             "1,220 REGISTER FOR IPL 2027 AUCTION - GUKESH FACES SINDAROV")
    cv.draw_lines(24, 834, list(sport), 2, INK, 22)

    # ---- wire ticker -------------------------------------------------------
    ticker = ("SIX DEAD IN PLANE CRASH * NATO EYES EASTERN FLANK * "
              "UN: 5 WOMEN KILLED HOURLY")
    cv.fill_rect(24, 902, 976, 28, INK)
    cv.text_centered(512, 909, ticker, 2, PAPER)

    # ---- footer ------------------------------------------------------------
    footer = ("ALL EVENTS OF THURSDAY 26 NOVEMBER 2026 - DRAWN IN CODE - "
              "SOURCES: AP, REUTERS, NDTV, MANILA TIMES, QATAR TRIBUNE")
    cv.text_centered(512, 946, footer, 1, INK)

    return cv


# ---------------------------------------------------------------------------
# PNG encoding (filter 0, zlib level 9 -- deterministic)
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF))


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = (y * cv.w) * 3
        raw += cv.px[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


def render(path):
    """Render the page to path; return (sha256 hex, byte count)."""
    data = encode_png(build_page())
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return hashlib.sha256(data).hexdigest(), len(data)


def self_test():
    """Render twice into fresh temp dirs and compare bytes and size."""
    results = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp:
            digest, size = render(Path(tmp) / "entry.png")
            results.append((digest, size))
    (d1, s1), (d2, s2) = results
    print(f"run 1: sha256={d1} bytes={s1}")
    print(f"run 2: sha256={d2} bytes={s2}")
    deterministic = d1 == d2 and s1 == s2
    size_ok = s1 <= MAX_BYTES and s2 <= MAX_BYTES
    print(f"deterministic: {'YES' if deterministic else 'NO'}")
    print(f"size <= 1 MiB: {'YES' if size_ok else 'NO'} "
          f"({s1} bytes, limit {MAX_BYTES})")
    if deterministic and size_ok:
        print("SELF-TEST PASSED")
        return 0
    print("SELF-TEST FAILED")
    return 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    digest, size = render(Path(out_dir) / "entry.png")
    print(f"wrote {Path(out_dir) / 'entry.png'}")
    print(f"sha256={digest}")
    print(f"bytes={size}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
