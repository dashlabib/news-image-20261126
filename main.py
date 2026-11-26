#!/usr/bin/env python3
"""THE DAILY GLOBE -- front page for Thursday 26 November 2026.

Stdlib only. Hand-rolled PNG encoder (zlib + struct) and a hand-made
5x7 bitmap font defined in this file. No network, no time, no randomness,
no file reads: the same run always produces the same bytes.

Run:
    python3 main.py                 -> ./out/entry.png
    MAKEFUN_OUTPUT_DIR=/tmp/x python3 main.py  -> /tmp/x/entry.png
    python3 main.py --self-test    -> render twice, compare bytes, check size
"""
import hashlib
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

W = 1024
H = 1024
MAX_BYTES = 1048576

PAPER = (248, 244, 230)
INK = (22, 22, 22)
RED = (155, 27, 27)
GREY = (105, 100, 88)
LIGHT = (232, 226, 205)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 strings of 5 chars, '#' = ink, '.' = blank.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale if text else 0


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines (upper-cased)."""
    text = text.upper()
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER[0] for _ in range(W * H))
        # Build as RGB bytearray filled with paper colour.
        self.buf = bytearray(W * H * 3)
        for i in range(W * H):
            self.buf[i * 3] = PAPER[0]
            self.buf[i * 3 + 1] = PAPER[1]
            self.buf[i * 3 + 2] = PAPER[2]

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = color[0]
                self.buf[i + 1] = color[1]
                self.buf[i + 2] = color[2]

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.set(cx + dx, cy + dy, color)

    def triangle(self, x, y, size, color, up=True):
        for row in range(size):
            wrow = row + 1 if up else size - row
            for dx in range(-wrow, wrow + 1):
                yy = y + row if up else y + row
                self.set(x + dx, yy, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = GLYPHS.get(ch, GLYPHS['?'])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale, scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, scale, color)
            cx += char_width(scale)
        return cx

    def draw_centred(self, y, text, scale, color):
        w = text_width(text.upper(), scale)
        self.draw_text((W - w) // 2, y, text, scale, color)

    def draw_wrapped(self, x, y, text, scale, color, max_w, line_h=None, max_lines=None):
        lines = wrap_text(text, scale, max_w)
        if max_lines is not None:
            lines = lines[:max_lines]
        lh = line_h if line_h is not None else 7 * scale + 3
        for i, line in enumerate(lines):
            self.draw_text(x, y + i * lh, line, scale, color)
        return y + len(lines) * lh


# ---------------------------------------------------------------- icons
def draw_icon(cv, x, y, kind):
    """Tiny geometric icon, 30x30 box at (x, y)."""
    if kind == "chart":
        # falling bars
        for i, h in enumerate((26, 18, 12)):
            cv.rect(x + i * 10, y + 28 - h, 7, h, RED)
    elif kind == "blast":
        cv.circle(x + 15, y + 15, 11, RED)
        for dx, dy in ((-14, -10), (14, -12), (-15, 12), (15, 10), (0, -15)):
            cv.rect(x + 15 + dx - 2, y + 15 + dy - 2, 4, 4, RED)
    elif kind == "rocket":
        cv.triangle(x + 15, y + 2, 12, INK, up=True)
        cv.rect(x + 11, y + 14, 8, 12, INK)
        cv.triangle(x + 15, y + 26, 5, RED, up=False)
    elif kind == "ballot":
        cv.rect(x + 4, y + 10, 22, 16, INK)
        cv.rect(x + 7, y + 13, 16, 10, PAPER)
        cv.rect(x + 9, y + 4, 12, 5, RED)
    elif kind == "globe":
        cv.circle(x + 15, y + 15, 13, INK)
        cv.circle(x + 15, y + 15, 9, PAPER)
        cv.rect(x + 2, y + 13, 26, 3, INK)
    elif kind == "plane":
        cv.triangle(x + 15, y + 2, 10, INK, up=True)
        cv.rect(x + 13, y + 12, 4, 14, INK)
        cv.rect(x + 4, y + 14, 22, 4, RED)
    elif kind == "balloon":
        cv.circle(x + 15, y + 12, 10, RED)
        cv.rect(x + 14, y + 22, 2, 7, INK)
    elif kind == "ball":
        cv.circle(x + 15, y + 15, 12, INK)
        cv.circle(x + 15, y + 15, 8, PAPER)
        cv.circle(x + 15, y + 15, 3, RED)
    else:  # "star" default
        cv.rect(x + 13, y + 2, 4, 26, RED)
        cv.rect(x + 2, y + 13, 26, 4, RED)


# ---------------------------------------------------------------- layout
def story_box(cv, x, y, w, h, kicker, headline, deck, icon):
    cv.rect(x, y, w, 1, INK)
    cv.draw_text(x, y + 8, kicker, 2, RED)
    draw_icon(cv, x + w - 34, y + 4, icon)
    # headline, scale 3, up to 2 lines (21px tall + 1px gap)
    cv.draw_wrapped(x, y + 28, headline, 3, INK, w - 40, line_h=22, max_lines=2)
    cv.draw_wrapped(x, y + 72, deck, 2, INK, w - 8, line_h=16, max_lines=2)


def render():
    cv = Canvas()
    mx = 36  # margin
    # --- masthead
    cv.draw_centred(20, "THE DAILY GLOBE", 8, INK)
    cv.rect(mx, 92, W - 2 * mx, 5, RED)
    cv.rect(mx, 101, W - 2 * mx, 1, INK)
    cv.draw_centred(112, "THURSDAY 26 NOVEMBER 2026", 2, INK)
    cv.draw_centred(134, "TRADE FEARS SHAKE MARKETS AS THE WORLD MARKS THANKSGIVING", 2, GREY)
    cv.rect(mx, 156, W - 2 * mx, 2, INK)

    # --- LEAD: trade war
    ly = 166
    cv.draw_text(mx, ly, "LEAD  -  TRADE WAR", 2, RED)
    cv.draw_wrapped(mx, ly + 22, "US PROPOSES NEW TARIFFS ON 14 PARTNERS", 4, INK,
                    620, line_h=32, max_lines=2)
    # One short deck paragraph, wrapped to at most 3 lines.
    dy = ly + 90
    cv.draw_wrapped(mx, dy, "CHINA 20%, TO 40% IF TRUCE LAPSES 10 JANUARY. "
                    "INDIA 17% WITH DEAL, 25% WITHOUT. CAP 15%: EU, JAPAN, "
                    "KOREA, TAIWAN. HEARING FIRST; EFFECT JANUARY.",
                    2, INK, 620, line_h=17, max_lines=3)
    # bar visual, right side
    bx, by = 700, ly + 18
    cv.draw_text(bx, by, "PROPOSED RATES", 2, RED)
    bars = [("CHINA", 40, "40%"), ("VIETNAM", 35, "35%"), ("INDIA", 25, "25%"), ("CAP", 15, "15%")]
    for i, (label, val, txt) in enumerate(bars):
        yy = by + 24 + i * 30
        cv.draw_text(bx, yy, label, 2, INK)
        cv.rect(bx + 110, yy + 2, int(val * 4.2), 12, RED)
        cv.draw_text(bx + 110 + int(val * 4.2) + 8, yy, txt, 2, INK)
    cv.rect(mx, 352, W - 2 * mx, 2, INK)

    # --- MARKETS strip (one line)
    my = 362
    cv.draw_text(mx, my, "MARKETS", 2, RED)
    cv.draw_wrapped(mx + 110, my, "NASDAQ -4%  |  TAIWAN -1,927  |  NT$ PAST 33  |  RAM PRICES TRIPLE", 2, INK, W - 2 * mx - 110, line_h=17, max_lines=1)
    cv.rect(mx, 388, W - 2 * mx, 1, INK)

    # --- grid: 2 columns x 4 rows, row_h 108 so headline (2 lines)
    # plus deck (2 lines) fits without spilling into the next row.
    gx, gy = mx, 398
    col_w = (W - 2 * mx - 16) // 2
    row_h = 108
    stories = [
        ("MARKETS", "SHARES SLIDE AS TARIFF FEARS HIT", "NASDAQ DOWN ABOUT 4%. FED SEES MODEST GROWTH, PRICE PRESSURE.", "chart"),
        ("GAZA", "NINE KILLED IN GAZA OVERNIGHT", "STRIKES HIT DEIR AL-BALAH DESPITE A YEAR-OLD CEASEFIRE.", "blast"),
        ("UKRAINE", "MISSILES HIT KYIV, SEVEN HURT", "SHOPPING CENTRE STRUCK. UKRAINE HITS OIL HUB IN BASHKORTOSTAN.", "blast"),
        ("NORTH KOREA", "KIM VOWS TO EXPAND NUCLEAR ARSENAL", "CALLS STATUS IRREVERSIBLE. KYIV SAYS AID TO RUSSIA HALTED.", "rocket"),
        ("EUROPE", "EU LEADERS SPLIT OVER BUDGET", "FRANCE: NO TALKS PAST DECEMBER. 45BN EURO UKRAINE LOAN PROPOSED.", "ballot"),
        ("BRITAIN", "UK MIGRATION FALLS TO 77,000", "DOWN FROM 204,000. LOWEST SINCE 1997 OUTSIDE THE PANDEMIC.", "globe"),
        ("SPACE", "MUSK PLEDGES SHARES FOR US CHILDREN", "TWO SHARES EACH, ABOUT $18BN. SPACEX WINS 1M SATELLITE NOD.", "rocket"),
        ("THANKSGIVING", "100TH MACY PARADE MARCHES", "RECORD 100 INFLATABLES IN NEW YORK. FIVE-GAME NFL SLATE.", "balloon"),
    ]
    for idx, (kicker, head, deck, icon) in enumerate(stories):
        r, c = divmod(idx, 2)
        x = gx + c * (col_w + 16)
        y = gy + r * row_h
        story_box(cv, x, y, col_w, row_h, kicker, head, deck, icon)
        if c == 0:
            cv.vline(x + col_w + 8, y + 4, row_h - 12, LIGHT, thick=1)

    # --- IN BRIEF (each line kept under 79 chars at scale 2 so it stays on one line)
    iy = 840
    cv.rect(mx, iy, W - 2 * mx, 2, INK)
    cv.draw_text(mx, iy + 10, "IN BRIEF", 2, RED)
    cy = iy + 34
    for line in (
        "PAKISTAN ASTRONAUT FIRST FOREIGNER ON TIANGONG STATION.",
        "NEARLY 2,000 MIGRANTS REACH CANARY ISLANDS IN ONE DAY.",
        "RAMAPHOSA REPORT RULED UNLAWFUL. WHO CHIEF URGES END TO CUBA FUEL BLOCKADE.",
        "ANDY TAYLOR DIES AT 65. CONGO EBOLA PASSES 12,000 CASES. 5.4 QUAKE JOLTS NEPAL.",
    ):
        cy = cv.draw_wrapped(mx, cy, line, 2, INK, W - 2 * mx, line_h=17, max_lines=1)

    # --- SPORT strip: label on its own line, then the results wrapped below.
    sy = 946
    cv.rect(mx, sy, W - 2 * mx, 2, RED)
    cv.draw_text(mx, sy + 8, "SPORT", 2, RED)
    cv.draw_wrapped(mx, sy + 28, "REAL MADRID BEAT PSV 5-1, MBAPPE SCORES TWICE. "
                    "SOUTH AFRICA SWEEP BANGLADESH 2-0. ITALY BEAT SOUTH KOREA, "
                    "DAVIS CUP SEMIS. 1,220 FOR IPL AUCTION.",
                    2, INK, W - 2 * mx, line_h=17, max_lines=2)
    return cv.buf


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(rgb):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    data = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", data)
    png += _chunk(b"IEND", b"")
    return png


def render_png_bytes():
    return encode_png(render())


def write_output(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = render_png_bytes()
    path = out_dir / "entry.png"
    path.write_bytes(data)
    return path, data


def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        p1, b1 = write_output(Path(d1))
        p2, b2 = write_output(Path(d2))
        if b1 != b2:
            print("FAIL: renders differ")
            ok = False
        if len(b1) > MAX_BYTES:
            print(f"FAIL: size {len(b1)} > {MAX_BYTES}")
            ok = False
        if p1.read_bytes() != p2.read_bytes():
            print("FAIL: files on disk differ")
            ok = False
    if ok:
        print(f"SELF-TEST OK: deterministic, 1024x1024, "
              f"{len(render_png_bytes())} bytes, "
              f"sha256={hashlib.sha256(render_png_bytes()).hexdigest()}")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    path, data = write_output(out_dir)
    print(f"Wrote {path} ({len(data)} bytes, 1024x1024)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
