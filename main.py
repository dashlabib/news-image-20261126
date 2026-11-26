#!/usr/bin/env python3
"""news-image-20261126: one-day world news front page for 26 November 2026.

Draws a newspaper-style front page summing up Thursday 26 November 2026,
entirely in pure Python (standard library only, no network, no fonts, no PIL).

The day's stories (all verified from news reports of 26 November 2026,
as of about 00:40 UTC, when the news day had barely begun in UTC but was
well under way in Asia; an improvement round will follow later in the day):
  LEAD   Trade war: Washington proposes new tariffs on 14 trading
         partners -- up to 25% on Indian goods (17% if a trade deal is
         reached) and up to 15% on Taiwan in a Section 301 overcapacity
         probe; Nasdaq sinks about 4% on the AI rout and tariff fears
         (Mathrubhumi; SimpleLife; bdnews24).
  MARKETS Nasdaq down about 4%; Taiwan shares fall 1,926.92 points as
         the NT dollar weakens past 33 per dollar; Fed Beige Book shows
         modest growth, wage gains and persistent price pressure
         (bdnews24; SimpleLife).
  S.AFRICA A South African court rules the Ramaphosa impeachment report
         unlawful (Qatar Tribune).
  CUBA   The WHO chief urges an end to the US fuel blockade on Cuba
         (Qatar Tribune).
  PHILIPPINES A Chinese long-range bomber flies within 45 nautical miles
         of the Philippine coast, about 170 from Manila, in a show of
         force, the armed forces say (Manila Times).
  N.KOREA North Korea orders Switzerland to close its newly opened
         diplomatic office in Pyongyang; its senior diplomat must leave
         within 48 hours (Indian Express; Manila Times).
  CANARIES Nearly 2,000 migrants reach Spain's Canary Islands in a
         record single-day arrival (Manila Times).
  SPACE  China welcomes its first foreign astronaut aboard the Tiangong
         station: Pakistan's Muhammad Zeeshan Ali, aboard Shenzhou-24
         (Qatar Tribune; Indian Express).
  SPORT  Real Madrid thrash PSV 5-1 (Mbappe brace, Bellingham stunner);
         South Africa sweep Bangladesh 2-0 in the 2nd Test; 1,220 players
         register for the IPL 2027 auction; Gukesh faces Sindarov in the
         World Chess Championship (NDTV; Indian Express).
  WIRE   Six dead in a plane crash off the southern US coast (US Coast
         Guard); NATO boosts air surveillance on its eastern flank after
         missile crashes; UN: five women killed every hour globally by a
         partner or relative last year; Trump seeks faster federal
         executions; South Korea issues an evacuation warning after
         Russian aircraft approach; Puerto Rico's Jennifer Barreto wins
         Miss Universe 2026 at home; India announces a Rs 15,000 crore
         development package for Nepal; Bangladesh garment workers win a
         36% wage hike; Sheikh Hasina seeks return on Dec 16; Flipkart
         CEO Kalyan Krishnamurthy steps down in December; Shein agrees a
         $100m settlement with the US consumer watchdog; an unclassified
         CIA system was breached, reports say (Qatar Tribune; NDTV;
         Manila Times; Indian Express; Economic Times).

Output: a 1024x1024 PNG at $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
Deterministic: fixed palette, fixed geometry, no randomness, no clock.
"""

import hashlib
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 227)   # newsprint cream
INK = (26, 26, 26)        # near-black ink
RED = (176, 32, 32)       # headline red
TEAL = (14, 74, 90)       # deep sea teal
SEA = (20, 88, 110)       # lighter sea
SKY = (191, 217, 232)     # pale sky blue
DUSK = (38, 52, 84)       # night sky
BLUE = (31, 78, 121)      # steel blue
GREY = (107, 107, 107)    # smoke grey
LIGHTGREY = (214, 210, 196)
ORANGE = (232, 106, 28)   # flame orange
YELLOW = (242, 183, 5)    # flame yellow
FLAME_RED = (214, 48, 24)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GREEN = (28, 110, 58)     # small positive accents
DARKRED = (140, 20, 20)
CRATE = (196, 84, 32)     # shipping-container rust

# ------------------------------------------------------------- bitmap font --
# A hand-built 5x7 bitmap font (uppercase, digits, common punctuation).
# Each glyph is 7 rows of 5 bits; '1' is ink, '0' is blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

CHAR_W = 6   # advance per character, in font units (5 glyph + 1 gap)
CHAR_H = 7


def text_width(text, scale):
    """Pixel width of a line of text at the given scale."""
    return len(text) * CHAR_W * scale

# ------------------------------------------------------------------ canvas --
class Canvas:
    """A plain RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, background)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x1 - x0):
                i = base + xx * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, t, length, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line; width>1 draws a small disc at each step."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        rad = width // 2
        while True:
            if width <= 1:
                self.set(x0, y0, color)
            else:
                self.fill_circle(x0, y0, rad, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        if r <= 0:
            self.set(cx, cy, color)
            return
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            span = rx * (1.0 - (dy * dy) / float(ry * ry)) ** 0.5
            dx = int(span)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_poly(self, pts, color):
        """Scanline polygon fill for a list of (x, y) vertices."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x_a, y_a = pts[i]
                x_b, y_b = pts[(i + 1) % n]
                if y_a == y_b:
                    continue
                if (y_a <= y < y_b) or (y_b <= y < y_a):
                    t = (y + 0.5 - y_a) / float(y_b - y_a)
                    xs.append(x_a + t * (x_b - x_a))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[k]), int(xs[k + 1])
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, color)

    # ------------------------------------------------------------- text ----
    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            return
        for row in range(CHAR_H):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def draw_text(self, x, y, text, scale, color, align="left"):
        """Draw one line; align left/center/right around x."""
        text = text.upper()  # the bitmap font carries capitals only
        w = text_width(text, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        for ch in text:
            self.draw_char(x, y, ch, scale, color)
            x += CHAR_W * scale

    def wrap(self, text, scale, max_width):
        """Greedy word wrap; returns a list of lines fitting max_width."""
        max_chars = max(1, max_width // (CHAR_W * scale))
        lines, cur = [], ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # A single over-long word is hard-split.
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_block(self, x, y, text, scale, color, max_width, leading=None):
        """Draw wrapped text; returns the y just below the last line."""
        if leading is None:
            leading = CHAR_H * scale + 2
        for line in self.wrap(text, scale, max_width):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y

    def fit_line(self, text, scale, max_width):
        """Shorten a one-liner with '...' until it fits max_width."""
        while text and text_width(text, scale) > max_width:
            text = text[:-4] + "..." if len(text) > 4 else ""
        return text


def flame(cv, x, y, s, color_mid=ORANGE, color_tip=YELLOW, color_base=FLAME_RED):
    """A small stylised flame: layered triangles rising from (x, y)."""
    cv.fill_poly([(x - s, y), (x + s, y), (x, y - 2 * s)], color_base)
    cv.fill_poly([(x - s * 2 // 3, y), (x + s * 2 // 3, y),
                  (x, y - 3 * s // 2)], color_mid)
    cv.fill_poly([(x - s // 3, y), (x + s // 3, y), (x, y - s)], color_tip)


def smoke(cv, x, y, r, color=GREY):
    """A puff of smoke: three overlapping circles, darker at the base."""
    cv.fill_circle(x, y, r, color)
    cv.fill_circle(x - r // 2, y - r // 2, r * 3 // 4, color)
    cv.fill_circle(x + r // 2, y - r // 3, r * 2 // 3, color)


# --------------------------------------------------------------------- png --
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    """Encode the canvas as a deterministic PNG (filter 0, level 9)."""
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # no filter
        start = y * cv.w * 3
        raw += cv.buf[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return png

# -------------------------------------------------------------- page parts --
def draw_masthead(cv):
    """Nameplate, date line and rules at the top of the front page."""
    cv.hline(24, 16, 976, INK, 3)
    cv.draw_text(512, 28, "THE WORLD IN ONE PAGE", 2, INK, align="center")
    cv.draw_text(512, 52, "THE DAILY GLOBE", 7, INK, align="center")
    cv.hline(24, 106, 976, INK, 3)
    cv.draw_text(24, 116, "THURSDAY, 26 NOVEMBER 2026", 2, INK)
    cv.draw_text(1000, 116, "ONE DAY - ONE PAGE", 2, INK, align="right")
    cv.hline(24, 134, 976, INK, 2)


def draw_lead_scene(cv, x, y, w, h):
    """A container ship at dawn under a dock crane, tariff stamp overhead.

    The lead story is the new tariff wave: a laden ship, stacked
    containers, a gantry crane, and a red stamp reading 25%.
    """
    # Dawn sky in bands, low sun, a distant shore.
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h // 3, w, h // 3, (168, 196, 214))
    cv.fill_circle(x + 70, y + 30, 20, YELLOW)
    cv.fill_circle(x + 70, y + 30, 13, (250, 220, 120))
    cv.fill_poly([(x, y + h // 2), (x + 120, y + h // 4),
                  (x + 240, y + h // 2)], (90, 96, 110))
    # The sea, with wave strokes.
    sea_y = y + h // 2
    cv.fill_rect(x, sea_y, w, h - h // 2, SEA)
    for i, wy in enumerate(range(sea_y + 12, y + h - 8, 18)):
        cv.hline(x + 12 + (i % 3) * 40, wy, 90, (120, 180, 196), 2)
    # Gantry crane on the left, arm reaching over the ship.
    cv.fill_rect(x + 16, y + 6, 10, sea_y - y + 8, INK)
    cv.fill_rect(x + 16, y + 6, 190, 10, INK)
    cv.line(x + 26, y + 16, x + 190, y + 44, INK, 3)
    cv.fill_rect(x + 176, y + 44, 6, 26, INK)
    cv.fill_rect(x + 168, y + 70, 22, 12, DARKRED)
    # The container ship: hull, bridge, funnel, stacked containers.
    hull_y = sea_y + 34
    cv.fill_rect(x + 150, hull_y, 420, 26, (40, 40, 44))
    cv.fill_rect(x + 150, hull_y + 26, 420, 8, BLACK)
    cv.fill_rect(x + 510, hull_y - 22, 44, 22, WHITE)
    cv.fill_rect(x + 528, hull_y - 34, 26, 12, WHITE)
    cv.fill_rect(x + 150, hull_y - 30, 24, 30, (176, 32, 32))
    # Containers in two tiers, rust red, teal and ochre.
    crate_cols = [CRATE, TEAL, (214, 160, 40), CRATE, TEAL]
    for tier in range(2):
        cy = hull_y - 12 - tier * 16
        for i, col in enumerate(crate_cols):
            cv.fill_rect(x + 190 + i * 62, cy - 14, 58, 14, col)
            cv.fill_rect(x + 190 + i * 62, cy - 14, 58, 2, INK)
    # A red tariff stamp, tilted, over the right of the scene.
    sx, sy = x + w - 150, y + 18
    cv.rect(sx, sy, 118, 58, RED, 4)
    cv.draw_text(sx + 59, sy + 8, "TARIFF", 2, RED, align="center")
    cv.draw_text(sx + 59, sy + 28, "25%", 4, RED, align="center")
    cv.rect(x, y, w, h, INK, 2)


def draw_lead(cv):
    """Lead story: headline, deck and the tariff-ship scene (left, wide)."""
    x, y, w = 24, 142, 636
    cv.draw_text(x, y, "LEAD STORY - TRADE WAR", 2, RED)
    cv.draw_text(x, y + 22, "TRUMP'S NEW TARIFF", 4, INK)
    cv.draw_text(x, y + 54, "WAVE HITS 14 NATIONS", 4, INK)
    cv.draw_block(x, y + 92, "US proposes up to 25% on India, 15% on "
                  "Taiwan; markets sink as the AI rout spreads.",
                  2, INK, w)
    draw_lead_scene(cv, x, y + 138, w, 158)
    # Caption line under the scene.
    cv.draw_text(x, y + 304,
                 "A CONTAINER SHIP AT DAWN: THE TARIFF WAVE REACHES THE "
                 "DOCKS.", 1, GREY)


def draw_markets(cv):
    """Right column: the Nasdaq sell-off, chart and figures."""
    x, y, w = 684, 142, 316
    cv.draw_text(x, y, "MARKETS", 2, RED)
    cv.draw_text(x, y + 22, "NASDAQ SINKS", 3, INK)
    cv.draw_text(x, y + 44, "ABOUT 4%", 3, INK)
    # Chart box: axes, gridlines, a falling red line, down arrow.
    cx, cy, cw, ch = x, y + 76, w, 116
    cv.rect(cx, cy, cw, ch, INK, 2)
    cv.fill_rect(cx + 2, cy + 2, cw - 4, ch - 4, WHITE)
    for gy in range(cy + 24, cy + ch - 8, 24):
        cv.hline(cx + 4, gy, cw - 8, LIGHTGREY, 1)
    cv.line(cx + 14, cy + ch - 14, cx + cw - 14, cy + ch - 14, INK, 1)
    cv.line(cx + 14, cy + 12, cx + 14, cy + ch - 14, INK, 1)
    pts = [(cx + 20, cy + 22), (cx + 70, cy + 30), (cx + 120, cy + 28),
           (cx + 170, cy + 52), (cx + 220, cy + 64), (cx + 270, cy + 88),
           (cx + cw - 22, cy + ch - 22)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    for px, py in pts:
        cv.fill_circle(px, py, 4, RED)
    cv.fill_poly([(cx + cw - 34, cy + ch - 34), (cx + cw - 10, cy + ch - 34),
                  (cx + cw - 22, cy + ch - 12)], RED)
    # Figures under the chart.
    fy = y + 204
    cv.draw_text(x, fy, "TAIWAN -1,927 PTS", 2, RED)
    cv.draw_text(x, fy + 18, "NT DOLLAR PAST 33", 2, INK)
    cv.draw_text(x, fy + 36, "AI ROUT SPREADS", 2, INK)
    cv.draw_text(x, fy + 54, "FED: MODEST GROWTH,", 2, INK)
    cv.draw_text(x, fy + 72, "PRICES STILL HIGH", 2, INK)
    cv.draw_text(x, fy + 94, "TARIFFS WEIGH ON ASIA;", 1, GREY)
    cv.draw_text(x, fy + 106, "INDIA RATE MAY FALL TO 17%.", 1, GREY)

# ------------------------------------------------------------ story panels --
def draw_panel(cv, x, y, w, kicker, scene, headline, deck):
    """One pictured secondary story: kicker, scene, headline, deck."""
    cv.draw_text(x, y, kicker, 2, RED)
    scene(cv, x, y + 20, w, 80)
    hy = cv.draw_block(x, y + 108, headline, 2, INK, w)
    cv.draw_block(x, hy + 4, deck, 2, INK, w)


def scene_court(cv, x, y, w, h):
    """A courthouse front: pediment, columns and steps."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_poly([(x + 20, y + 22), (x + w - 20, y + 22),
                  (x + w // 2, y + 4)], BLUE)
    cv.fill_rect(x + 20, y + 22, w - 40, 8, BLUE)
    for i in range(5):
        col_x = x + 34 + i * 52
        cv.fill_rect(col_x, y + 30, 18, h - 44, WHITE)
        cv.fill_rect(col_x - 3, y + 30, 24, 5, WHITE)
    cv.fill_rect(x, y + h - 14, w, 6, LIGHTGREY)
    cv.fill_rect(x, y + h - 8, w, 8, GREY)
    cv.fill_circle(x + w - 34, y + 16, 8, YELLOW)
    cv.rect(x, y, w, h, INK, 2)


def scene_fuel(cv, x, y, w, h):
    """A fuel tanker held off by a blockade ring: no-entry sign at sea."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + 52, y + 22, 14, YELLOW)
    cv.fill_rect(x, y + h // 2, w, h - h // 2, SEA)
    for i, wy in enumerate(range(y + h // 2 + 12, y + h - 8, 16)):
        cv.hline(x + 12 + (i % 3) * 40, wy, 80, (120, 180, 196), 2)
    # Tanker hull and tanks, stopped short of the harbour.
    cv.fill_rect(x + 24, y + h - 34, 150, 20, (40, 40, 44))
    cv.fill_rect(x + 24, y + h - 14, 150, 6, BLACK)
    for i, tx in enumerate([40, 88, 136]):
        cv.fill_ellipse(x + tx, y + h - 40, 20, 10, (200, 200, 205))
        cv.fill_rect(x + tx - 20, y + h - 40, 40, 4, (120, 120, 126))
    cv.fill_rect(x + 150, y + h - 52, 20, 18, WHITE)
    # The blockade ring: a red circle with a bar across it.
    cx, cy, r = x + w - 52, y + 34, 24
    cv.fill_circle(cx, cy, r, WHITE)
    cv.fill_circle(cx, cy, r, RED)
    cv.fill_circle(cx, cy, r - 6, WHITE)
    cv.line(cx - r + 4, cy + r - 4, cx + r - 4, cy - r + 4, RED, 6)
    cv.rect(x, y, w, h, INK, 2)


def scene_jet(cv, x, y, w, h):
    """A long-range bomber crossing a pale sky above a green coast."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + w - 44, y + 18, 12, YELLOW)
    # Coastline and sea below.
    cv.fill_poly([(x, y + h), (x, y + h - 26), (x + 120, y + h - 34),
                  (x + w, y + h - 18), (x + w, y + h)], (60, 120, 70))
    cv.fill_rect(x, y + h - 18, w, 18, SEA)
    # The bomber: swept fuselage, wings, tail, twin engines.
    bx, by = x + 110, y + 26
    cv.fill_poly([(bx - 70, by + 6), (bx + 80, by - 2), (bx + 96, by + 4),
                  (bx + 80, by + 10), (bx - 60, by + 12)], (52, 56, 62))
    cv.fill_poly([(bx - 10, by + 2), (bx + 20, by - 22),
                  (bx + 34, by - 20), (bx + 12, by + 4)], (52, 56, 62))
    cv.fill_poly([(bx - 10, by + 10), (bx + 16, by + 30),
                  (bx + 28, by + 28), (bx + 10, by + 8)], (52, 56, 62))
    cv.fill_poly([(bx - 66, by + 4), (bx - 78, by - 8),
                  (bx - 70, by - 10), (bx - 58, by + 2)], (52, 56, 62))
    cv.fill_circle(bx + 46, by + 4, 5, (30, 30, 34))
    cv.fill_circle(bx + 62, by + 4, 5, (30, 30, 34))
    # Distance marker: 45 nautical miles.
    cv.draw_text(x + 12, y + h - 16, "45 NM OFF THE COAST", 1, WHITE)
    cv.rect(x, y, w, h, INK, 2)


def scene_gate(cv, x, y, w, h):
    """A diplomatic office gate, shut: fence, flag lowered, sign."""
    cv.fill_rect(x, y, w, h, (222, 214, 196))
    cv.fill_rect(x + 30, y + 20, w - 60, h - 38, (240, 236, 224))
    cv.fill_rect(x + 30, y + 20, w - 60, 16, BLUE)
    # Iron fence bars across the front.
    for i in range(9):
        bx = x + 44 + i * 28
        cv.fill_rect(bx, y + 36, 6, h - 54, INK)
    cv.fill_rect(x + 36, y + 44, w - 72, 4, INK)
    cv.fill_rect(x + 36, y + h - 22, w - 72, 4, INK)
    # A flag at half-mast and a small closed sign.
    cv.line(x + w - 34, y + 8, x + w - 34, y + 34, INK, 2)
    cv.fill_rect(x + w - 34, y + 14, 22, 10, RED)
    cv.fill_rect(x + w // 2 - 34, y + h - 16, 68, 10, WHITE)
    cv.draw_text(x + w // 2, y + h - 15, "CLOSED", 1, RED, align="center")
    cv.rect(x, y, w, h, INK, 2)


def scene_boats(cv, x, y, w, h):
    """Small crowded boats crossing a wide blue sea toward a far shore."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + 52, y + 20, 13, YELLOW)
    cv.fill_rect(x, y + h // 2, w, h - h // 2, SEA)
    for i, wy in enumerate(range(y + h // 2 + 10, y + h - 8, 14)):
        cv.hline(x + 12 + (i % 3) * 40, wy, 80, (120, 180, 196), 2)
    # Far shore with a lighthouse.
    cv.fill_rect(x + w - 60, y + h // 2 - 22, 60, 22, (120, 110, 90))
    cv.fill_rect(x + w - 30, y + h // 2 - 46, 8, 24, WHITE)
    cv.fill_circle(x + w - 26, y + h // 2 - 48, 5, YELLOW)
    # Three small boats, each crowded with dots.
    for bx, by, bw in [(30, 52, 64), (120, 62, 58), (200, 50, 66)]:
        cv.fill_poly([(x + bx, y + by), (x + bx + bw, y + by),
                      (x + bx + bw - 8, y + by + 10),
                      (x + bx + 8, y + by + 10)], (176, 84, 32))
        for k in range(4):
            cv.fill_circle(x + bx + 12 + k * 14, y + by - 5, 3, INK)
    cv.rect(x, y, w, h, INK, 2)


def scene_space(cv, x, y, w, h):
    """Night sky, stars and a rocket climbing from Jiuquan."""
    cv.fill_rect(x, y, w, h, DUSK)
    for sx, sy in [(20, 12), (70, 30), (130, 10), (200, 26), (260, 14),
                   (40, 55), (150, 48), (230, 60), (290, 40), (100, 62)]:
        cv.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    cv.fill_rect(x, y + h - 8, w, 8, (60, 60, 66))
    # Rocket: white body, red nose, fins, orange exhaust.
    rx = x + w // 2
    cv.fill_rect(rx - 8, y + 14, 16, 40, WHITE)
    cv.fill_poly([(rx - 8, y + 14), (rx + 8, y + 14), (rx, y + 2)], RED)
    cv.fill_poly([(rx - 8, y + 44), (rx - 18, y + 58), (rx - 8, y + 54)],
                 RED)
    cv.fill_poly([(rx + 8, y + 44), (rx + 18, y + 58), (rx + 8, y + 54)],
                 RED)
    flame(cv, rx, y + 58, 10)
    cv.fill_circle(rx - 30, y + 22, 10, (220, 225, 235))
    cv.fill_circle(rx - 30, y + 22, 6, (140, 160, 180))
    cv.rect(x, y, w, h, INK, 2)


def draw_rows(cv):
    """Two rows of three pictured secondary stories each."""
    panels = [
        ("SOUTH AFRICA", scene_court,
         "COURT BLOCKS RAMAPHOSA IMPEACHMENT BID",
         "Judges rule the impeachment report unlawful."),
        ("CUBA", scene_fuel,
         "WHO: END THE U.S. FUEL BLOCKADE ON CUBA",
         "Health chief warns the blockade strangles care."),
        ("PHILIPPINES", scene_jet,
         "CHINESE BOMBER BUZZES PHILIPPINE COAST",
         "Jet flies within 45 nautical miles of Luzon."),
        ("NORTH KOREA", scene_gate,
         "PYONGYANG EXPELS SWISS ENVOY",
         "North Korea orders the office shut in 48 hours."),
        ("CANARY ISLANDS", scene_boats,
         "RECORD DAY AT THE CANARIES",
         "Nearly 2,000 migrants land in a single day."),
        ("SPACE", scene_space,
         "FIRST FOREIGNER ABOARD TIANGONG",
         "Pakistan's Zeeshan Ali joins China's station crew."),
    ]
    xs = [24, 358, 692]
    for row, y in enumerate((476, 682)):
        for col, px in enumerate(xs):
            kicker, scene, head, deck = panels[row * 3 + col]
            draw_panel(cv, px, y, 308, kicker, scene, head, deck)


def draw_sport_and_wire(cv):
    """Sport strip, the wire ticker and the footer."""
    y = 888
    cv.draw_text(24, y, "SPORT", 2, RED)
    cv.draw_text(110, y, "REAL MADRID THRASH PSV 5-1: MBAPPE BRACE",
                 2, INK)
    cv.draw_text(110, y + 18,
                 "SOUTH AFRICA SWEEP BANGLADESH 2-0 * IPL: 1,220 REGISTER "
                 "* GUKESH v SINDAROV", 2, INK)
    # The wire: one black band with the rest of the day.
    cv.fill_rect(24, 940, 976, 38, BLACK)
    wire = ("SIX DEAD IN PLANE CRASH * NATO EYES EASTERN FLANK * "
            "UN: 5 WOMEN KILLED HOURLY")
    cv.draw_text(512, 952, cv.fit_line(wire, 2, 960), 2, WHITE,
                 align="center")
    cv.draw_text(512, 988,
                 "ALL EVENTS OF THURSDAY 26 NOVEMBER 2026 - DRAWN IN CODE "
                 "- SOURCES: AP, REUTERS, NDTV, MANILA TIMES, QATAR "
                 "TRIBUNE", 1, GREY, align="center")


# ------------------------------------------------------------------- build --
def build():
    """Assemble the whole front page and return the canvas."""
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    draw_markets(cv)
    cv.vline(672, 142, 318, INK, 2)
    cv.hline(24, 468, 976, INK, 3)
    draw_rows(cv)
    cv.hline(24, 674, 976, INK, 2)
    cv.hline(24, 880, 976, INK, 2)
    draw_sport_and_wire(cv)
    return cv


def render(out_dir):
    """Render once into out_dir/entry.png; return (path, sha256, bytes)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "entry.png"
    png = write_png(path, build())
    return path, hashlib.sha256(png).hexdigest(), len(png)


def self_test():
    """Render twice into fresh temp dirs and compare bytes exactly."""
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        p1, h1, n1 = render(Path(d1))
        p2, h2, n2 = render(Path(d2))
        ok_size = n1 <= 1048576 and n1 == n2
        ok_hash = h1 == h2
        print(f"run 1: {p1} sha256={h1} bytes={n1}")
        print(f"run 2: {p2} sha256={h2} bytes={n2}")
        print(f"dimensions: {WIDTH}x{HEIGHT}")
        print(f"deterministic: {'PASS' if ok_hash else 'FAIL'}")
        print(f"size <= 1 MiB: {'PASS' if ok_size else 'FAIL'}")
        return 0 if (ok_hash and ok_size) else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path, digest, nbytes = render(Path(out_dir))
    print(f"wrote {path} sha256={digest} bytes={nbytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
