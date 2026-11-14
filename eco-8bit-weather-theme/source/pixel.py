"""8-bit pixel art: the Eco logo, a small pixel font, and the fleet sprites.

Everything is drawn at logical resolution (1 px = one 'fat' pixel) and scaled
up with nearest-neighbour at the end.
"""
import random
from PIL import Image, ImageDraw

HERE = __import__("pathlib").Path(__file__).parent


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


# ---------------------------------------------------------------- logo
LOGO_PAL = [hx(c) for c in (
    "#FFFFFF", "#BFE9FB", "#5CC8F0", "#009FDF", "#0072B5", "#0065A1", "#003F6E", "#003057", "#001E36",
    "#D4EC6A", "#A6D22B", "#84BD00", "#4FAE3A", "#25A64E", "#00843D", "#0B5E3A",
)]


def nearest(rgb, pal):
    return min(pal, key=lambda p: (p[0] - rgb[0]) ** 2 * 3 + (p[1] - rgb[1]) ** 2 * 4 + (p[2] - rgb[2]) ** 2 * 2)


def pixel_logo(width, shadow="#000E1C"):
    """The eco wordmark from the brand PNG (white-outline version), pixelated."""
    src = Image.open(HERE / "assets/logo-white.png").convert("RGBA").crop((0, 0, 1355, 487))
    h = round(width * src.height / src.width)
    small = src.resize((width, h), Image.BOX)
    out = Image.new("RGBA", (width + 1, h + 1), (0, 0, 0, 0))
    px = small.load()
    for y in range(h):
        for x in range(width):
            r, g, b, a = px[x, y]
            if a > 110:
                # un-premultiply edge pixels toward white (the outline colour)
                out.putpixel((x, y), nearest((r, g, b), LOGO_PAL))
    if shadow:
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        for y in range(h):
            for x in range(width):
                if out.getpixel((x, y))[3]:
                    sh.putpixel((x + 1, y + 1), hx(shadow))
        sh.alpha_composite(out)
        out = sh
    return out


# ---------------------------------------------------------------- font (variable width, 5 tall)
GLYPHS = {
    "A": ".#.|#.#|###|#.#|#.#", "B": "##.|#.#|##.|#.#|##.", "C": ".##|#..|#..|#..|.##",
    "D": "##.|#.#|#.#|#.#|##.", "E": "###|#..|##.|#..|###", "F": "###|#..|##.|#..|#..",
    "G": ".##|#..|#.#|#.#|.##", "H": "#.#|#.#|###|#.#|#.#", "I": "###|.#.|.#.|.#.|###",
    "K": "#.#|#.#|##.|#.#|#.#", "L": "#..|#..|#..|#..|###", "M": "#...#|##.##|#.#.#|#...#|#...#",
    "N": "#..#|##.#|#.##|#..#|#..#", "O": ".#.|#.#|#.#|#.#|.#.", "P": "##.|#.#|##.|#..|#..",
    "R": "##.|#.#|##.|#.#|#.#", "S": ".##|#..|.#.|..#|##.", "T": "###|.#.|.#.|.#.|.#.",
    "U": "#.#|#.#|#.#|#.#|###", "V": "#.#|#.#|#.#|#.#|.#.", "W": "#...#|#...#|#.#.#|##.##|#...#",
    "Y": "#.#|#.#|.#.|.#.|.#.", "·": ".|.|#|.|.", ".": ".|.|.|.|#", " ": "..|..|..|..|..",
}


def text_width(s):
    return sum(len(GLYPHS[c].split("|")[0]) + 1 for c in s) - 1


def draw_text(img, x, y, s, color, italic=True):
    col = hx(color)
    for c in s:
        rows = GLYPHS[c].split("|")
        for ry, row in enumerate(rows):
            dx = 1 if (italic and ry < 2) else 0
            for rx, ch in enumerate(row):
                if ch == "#":
                    img.putpixel((x + rx + dx, y + ry), col)
        x += len(rows[0]) + 1


# ---------------------------------------------------------------- sprites
K = "#07111C"   # outline
WHEEL = ["..KKKK..", ".KDDDDK.", "KDDggDDK", "KDgwwgDK", "KDgwwgDK", "KDDggDDK", ".KDDDDK.", "..KKKK.."]
SPR = {"K": K, "D": "#26323D", "g": "#6E7F8C", "w": "#C9D6DF"}


def stamp(img, x, y, rows, pal):
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch in pal:
                img.putpixel((x + rx, y + ry), hx(pal[ch]))


def wheel(img, cx, by):
    stamp(img, cx - 4, by - 8, WHEEL, SPR)


def van(logo_small, headlight=True):
    """Transit-style high-roof van, facing right. 46 x 22."""
    im = Image.new("RGBA", (46, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = [(1, 1), (31, 1), (38, 9), (43, 10), (44, 12), (44, 17), (1, 17)]
    d.polygon(body, fill=hx("#84BD00"), outline=hx(K))
    # navy rear-lower panel with a white swoosh edge
    d.polygon([(2, 9), (14, 9), (27, 16), (2, 16)], fill=hx("#003057"))
    d.line([(14, 9), (27, 16)], fill=hx("#FFFFFF"))
    d.line([(15, 9), (28, 16)], fill=hx("#FFFFFF"))
    d.line([(3, 14), (17, 13)], fill=hx("#009FDF"))
    # roof highlight
    d.line([(2, 2), (30, 2)], fill=hx("#B5DC3C"))
    # windows
    d.polygon([(32, 3), (37, 9), (32, 9)], fill=hx("#1B4B6B"))
    d.line([(33, 4), (35, 7)], fill=hx("#7FC8EE"))
    d.rectangle([(26, 3), (30, 8)], fill=hx("#1B4B6B"))
    d.line([(27, 4), (27, 6)], fill=hx("#7FC8EE"))
    # logo on the side
    im.alpha_composite(logo_small, (4, 2))
    # lights, bumper, grille
    if headlight:
        d.rectangle([(42, 11), (43, 12)], fill=hx("#FFE27A"))
    d.rectangle([(1, 10), (1, 12)], fill=hx("#E5484D"))
    d.line([(36, 17), (44, 17)], fill=hx("#26323D"))
    d.line([(1, 17), (6, 17)], fill=hx("#26323D"))
    d.rectangle([(42, 14), (44, 16)], fill=hx("#26323D"))
    # wheel wells
    for cx in (9, 36):
        d.rectangle([(cx - 5, 14), (cx + 4, 17)], fill=hx(K))
        wheel(im, cx, 22)
    return im


def box_truck(logo_big):
    """Box truck, facing right. 56 x 26."""
    im = Image.new("RGBA", (56, 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # box
    d.rectangle([(1, 0), (38, 20)], fill=hx("#84BD00"), outline=hx(K))
    d.line([(2, 1), (37, 1)], fill=hx("#B5DC3C"))
    d.polygon([(2, 13), (20, 13), (30, 19), (2, 19)], fill=hx("#003057"))
    d.line([(20, 13), (30, 19)], fill=hx("#FFFFFF"))
    d.line([(21, 13), (31, 19)], fill=hx("#FFFFFF"))
    d.line([(3, 17), (22, 16)], fill=hx("#009FDF"))
    im.alpha_composite(logo_big, (4, 2))
    # cab
    cab = [(39, 6), (47, 6), (52, 12), (54, 13), (55, 15), (55, 21), (39, 21)]
    d.polygon(cab, fill=hx("#84BD00"), outline=hx(K))
    d.polygon([(40, 14), (46, 14), (52, 20), (40, 20)], fill=hx("#FFFFFF"))
    d.polygon([(47, 8), (51, 12), (47, 12)], fill=hx("#1B4B6B"))
    d.rectangle([(41, 8), (45, 12)], fill=hx("#1B4B6B"))
    d.line([(42, 9), (42, 11)], fill=hx("#7FC8EE"))
    d.rectangle([(53, 15), (54, 16)], fill=hx("#FFE27A"))
    d.rectangle([(1, 15), (1, 17)], fill=hx("#E5484D"))
    d.line([(1, 21), (55, 21)], fill=hx("#26323D"))
    for cx in (10, 46):
        d.rectangle([(cx - 5, 18), (cx + 4, 21)], fill=hx(K))
        wheel(im, cx, 26)
    return im


def pickup(logo_small):
    """Pickup, facing right. 44 x 18."""
    im = Image.new("RGBA", (44, 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = [(1, 6), (18, 6), (19, 1), (28, 1), (33, 6), (41, 7), (43, 9), (43, 14), (1, 14)]
    d.polygon(body, fill=hx("#FFFFFF"), outline=hx(K))
    d.polygon([(2, 7), (12, 7), (22, 13), (2, 13)], fill=hx("#003057"))
    d.line([(12, 7), (22, 13)], fill=hx("#009FDF"))
    d.polygon([(23, 7), (42, 8), (42, 13), (30, 13)], fill=hx("#84BD00"))
    d.polygon([(21, 2), (27, 2), (31, 6), (21, 6)], fill=hx("#1B4B6B"))
    d.line([(22, 3), (24, 5)], fill=hx("#7FC8EE"))
    d.line([(26, 2), (26, 6)], fill=hx(K))
    im.alpha_composite(logo_small, (24, 8))
    d.rectangle([(41, 9), (42, 10)], fill=hx("#FFE27A"))
    d.rectangle([(1, 7), (1, 9)], fill=hx("#E5484D"))
    d.line([(1, 14), (43, 14)], fill=hx("#26323D"))
    for cx in (9, 34):
        d.rectangle([(cx - 5, 11), (cx + 4, 14)], fill=hx(K))
        wheel(im, cx, 18)
    return im


def puff(img, x, y, c="#9FB2C2"):
    for dx, dy in [(0, 1), (1, 0), (1, 1), (2, 1), (1, 2), (-2, 2), (-3, 1), (-3, 2), (-6, 0)]:
        img.putpixel((x + dx, y + dy), hx(c))


def bands(img, top, bottom, colors, dither=True):
    """Stepped sky gradient with a checkerboard dither row between bands."""
    n = len(colors)
    span = (bottom - top) / n
    d = ImageDraw.Draw(img)
    for i, c in enumerate(colors):
        y0 = round(top + i * span)
        y1 = round(top + (i + 1) * span)
        d.rectangle([(0, y0), (img.width - 1, y1)], fill=hx(c))
        if dither and i > 0:
            prev = hx(colors[i - 1])
            for yy in (y0, y0 + 1):
                for x in range(img.width):
                    if (x + yy) % 2 == (0 if yy == y0 else 1) and yy == y0:
                        img.putpixel((x, yy), prev)
                    elif yy == y0 + 1 and (x + yy) % 4 == 0:
                        img.putpixel((x, yy), prev)


def blend(img, x, y, c, a=255):
    """Paint one pixel, mixing toward colour c by alpha a; ignores pixels off the canvas."""
    if not (0 <= x < img.width and 0 <= y < img.height):
        return
    r, g, b = hx(c)[:3] if isinstance(c, str) else c[:3]
    o = img.getpixel((x, y))
    k = a / 255
    v = (round(o[0] + (r - o[0]) * k), round(o[1] + (g - o[1]) * k), round(o[2] + (b - o[2]) * k))
    img.putpixel((x, y), v if img.mode == 'RGB' else v + (255,))


def star(img, x, y, c="#FFFFFF", big=False):
    blend(img, x, y, c)
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            blend(img, x + dx, y + dy, c, 140)


def upscale(img, s, size):
    img = img.convert("RGB")
    big = img.resize((img.width * s, img.height * s), Image.NEAREST)
    return big.crop((0, 0) + size)
