#!/usr/bin/env python3
"""Mapture 앱 아이콘 생성 (외부 라이브러리 없이 표준 라이브러리만 사용).

얼굴 구체(고리·반짝임 없음)를 흰 배경 위에 그려
icons/icon-192.png, icons/icon-512.png, icons/icon.svg 를 만든다.
구체는 maskable 안전 영역(가운데 지름 80%) 안에 들어가도록 지름 70%로 그린다.

사용: 프로젝트 루트에서  python3 tools/make-icons.py
"""
import math
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")

ACCENT = (0x0F, 0x7B, 0x6C)
WHITE = (255, 255, 255)

# 마스코트 좌표계(viewBox 0 0 120 120)의 얼굴 구체: 중심 (60,60), 반지름 38
FACE_R = 38
FILL_RATIO = 0.70  # 아이콘 한 변 대비 구체 지름


def quad_points(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


# 웃는 입: M47 71 q13 11 26 0  → (47,71) 제어점 (60,82) 끝 (73,71), 굵기 4.5
SMILE = quad_points((47, 71), (60, 82), (73, 71))
SMILE_HALF_W = 4.5 / 2


def blend(dst, src, a):
    return tuple(d + (s - d) * a for d, s in zip(dst, src))


def cov(d, px):
    """부호 있는 거리(d<0 안쪽) → 픽셀 커버리지(안티에일리어싱)"""
    return max(0.0, min(1.0, 0.5 - d / px))


def render(size):
    scale = size * FILL_RATIO / (2 * FACE_R)  # 마스코트 단위 → 픽셀
    px = 1 / scale  # 1픽셀이 마스코트 단위로 몇인지
    off = size / 2 - 60 * scale

    rows = []
    for j in range(size):
        row = bytearray()
        for i in range(size):
            x = (i + 0.5 - off) / scale
            y = (j + 0.5 - off) / scale
            c = WHITE
            c = blend(c, ACCENT, cov(math.hypot(x - 60, y - 60) - 38, px))
            c = blend(c, WHITE, 0.22 * cov(math.hypot(x - 46, y - 44) - 8, px))
            c = blend(c, WHITE, cov(math.hypot(x - 48, y - 58) - 5, px))
            c = blend(c, WHITE, cov(math.hypot(x - 72, y - 58) - 5, px))
            if 44 < x < 76 and 67 < y < 80:
                d = min(seg_dist(x, y, SMILE[k], SMILE[k + 1]) for k in range(len(SMILE) - 1))
                c = blend(c, WHITE, cov(d - SMILE_HALF_W, px))
            row += bytes(int(round(v)) for v in c)
        rows.append(bytes(row))
    return rows


def write_png(path, size, rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="{o} {o} {s} {s}">
<rect x="{o}" y="{o}" width="{s}" height="{s}" fill="#FFFFFF"/>
<circle cx="60" cy="60" r="38" fill="#0F7B6C"/>
<circle cx="46" cy="44" r="8" fill="#FFFFFF" fill-opacity="0.22"/>
<circle cx="48" cy="58" r="5" fill="#FFFFFF"/>
<circle cx="72" cy="58" r="5" fill="#FFFFFF"/>
<path d="M47 71q13 11 26 0" fill="none" stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round"/>
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for size in (192, 512):
        path = os.path.join(OUT, f"icon-{size}.png")
        write_png(path, size, render(size))
        print("wrote", path)
    s = 2 * FACE_R / FILL_RATIO
    o = 60 - s / 2
    with open(os.path.join(OUT, "icon.svg"), "w") as f:
        f.write(SVG.format(o=round(o, 3), s=round(s, 3)))
    print("wrote", os.path.join(OUT, "icon.svg"))


if __name__ == "__main__":
    main()
