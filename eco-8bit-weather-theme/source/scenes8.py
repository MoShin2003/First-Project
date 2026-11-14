"""Two 8-bit backdrops at phone size: the Eco fleet, and an original gothic night city."""
import random
from PIL import Image, ImageDraw

import pixel as px
from pixel import hx

LW, LH, S = 130, 282, 3          # logical grid and pixel scale
SIZE = (390, 844)

RAMP = ["#D4EC6A", "#A6D22B", "#84BD00", "#4FAE3A", "#1E7F55", "#0B4D7A", "#0065A1", "#0088CC", "#009FDF", "#5CC8F0"]


def ramp_logo(width, ramp=RAMP, shadow="#000E1C"):
    """Pixel logo recoloured as clean stepped bands top-to-bottom, like an arcade title."""
    base = px.pixel_logo(width, shadow=None)
    out = Image.new("RGBA", (base.width + 1, base.height + 1), (0, 0, 0, 0))
    ys = [y for y in range(base.height) for x in range(base.width) if base.getpixel((x, y))[3]]
    top, bot = min(ys), max(ys)
    for y in range(base.height):
        for x in range(base.width):
            r, g, b, a = base.getpixel((x, y))
            if not a:
                continue
            white = min(r, g, b) > 185
            if white:
                c = hx("#FFFFFF")
            else:
                t = (y - top) / max(1, bot - top)
                c = hx(ramp[min(len(ramp) - 1, int(t * len(ramp)))])
            out.putpixel((x, y), c)
    if shadow:
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        for y in range(base.height):
            for x in range(base.width):
                if out.getpixel((x, y))[3]:
                    sh.putpixel((x + 1, y + 1), hx(shadow))
        sh.alpha_composite(out)
        out = sh
    return out


def house(d, img, x, base_y, w, h, rnd, wall="#0A2238", roof="#071A2C", lit="#FFD866"):
    d.rectangle([(x, base_y - h), (x + w - 1, base_y)], fill=hx(wall))
    peak = w // 2
    d.polygon([(x - 1, base_y - h), (x + peak, base_y - h - peak + 1), (x + w, base_y - h)], fill=hx(roof))
    if rnd.random() < .6:
        d.rectangle([(x + w - 4, base_y - h - peak + 2), (x + w - 3, base_y - h - 1)], fill=hx(roof))
    for wx in range(x + 2, x + w - 3, 5):
        for wy in range(base_y - h + 2, base_y - 3, 5):
            if rnd.random() < .55:
                d.rectangle([(wx, wy), (wx + 1, wy + 1)], fill=hx(lit))


def tree(img, cx, base_y, c="#0B3A2E", c2="#0E4A39"):
    d = ImageDraw.Draw(img)
    d.rectangle([(cx, base_y - 3), (cx, base_y)], fill=hx("#06121C"))
    d.ellipse([(cx - 4, base_y - 11), (cx + 4, base_y - 3)], fill=hx(c))
    d.point([(cx - 2, base_y - 9), (cx - 1, base_y - 10), (cx + 1, base_y - 8)], fill=hx(c2))


# ======================================================================= Eco 8-bit
def eco_scene():
    rnd = random.Random(7)
    img = Image.new("RGBA", (LW, LH), hx("#001426"))
    px.bands(img, 0, 200, ["#001426", "#001A31", "#00213B", "#032946", "#073253", "#0B3C61", "#104871", "#165682", "#1D6593"])
    # stars
    for _ in range(70):
        x, y = rnd.randrange(LW), rnd.randrange(4, 120)
        if (12 < x < 118 and 84 < y < 150) or (92 < x < 116 and 34 < y < 58):
            continue
        px.star(img, x, y, rnd.choice(["#FFFFFF", "#BFE9FB", "#D4EC6A"]), big=rnd.random() < .12)
    # moon
    d = ImageDraw.Draw(img)
    sky = img.getpixel((100, 44))
    d.ellipse([(98, 40), (112, 54)], fill=hx("#E9F3F8"))
    d.ellipse([(94, 37), (106, 51)], fill=sky)              # crescent bite, in the sky's own colour
    # pixel clouds
    for cx, cy, w in [(18, 62, 22), (92, 74, 26), (40, 166, 30), (104, 172, 22)]:
        d.rectangle([(cx, cy), (cx + w, cy + 3)], fill=hx("#1C4C75"))
        d.rectangle([(cx + 4, cy - 2), (cx + w - 6, cy)], fill=hx("#1C4C75"))
        d.rectangle([(cx + 8, cy - 4), (cx + w - 12, cy - 2)], fill=hx("#245A85"))

    # logo + tagline, centred
    logo = ramp_logo(98)
    lx = (LW - logo.width) // 2
    ly = 96
    img.alpha_composite(logo, (lx, ly))
    t1, t2 = "PLUMBERS · ELECTRICIANS", "HVAC TECHNICIANS"
    ty = ly + logo.height + 3
    px.draw_text(img, (LW - px.text_width(t1)) // 2, ty, t1, "#FFFFFF")
    w2 = px.text_width(t2)
    x2 = (LW - w2) // 2
    px.draw_text(img, x2, ty + 7, t2, "#FFFFFF")
    d.line([(x2 - 9, ty + 9), (x2 - 3, ty + 9)], fill=hx("#84BD00"))
    d.line([(x2 + w2 + 3, ty + 9), (x2 + w2 + 9, ty + 9)], fill=hx("#84BD00"))

    # neighbourhood
    ground = 203
    x = -4
    while x < LW:
        w = rnd.choice([13, 15, 17, 19])
        h = rnd.choice([9, 11, 13])
        house(d, img, x, ground, w, h, rnd)
        x += w + rnd.choice([3, 6, 9])
        if rnd.random() < .5 and x < LW - 4:
            tree(img, x - 2, ground)
    # road
    d.rectangle([(0, 204), (LW, 206)], fill=hx("#3A4B5A"))
    d.line([(0, 204), (LW, 204)], fill=hx("#5A6D7C"))
    d.rectangle([(0, 207), (LW, 240)], fill=hx("#18222C"))
    for x in range(0, LW, 10):
        d.rectangle([(x, 236), (x + 5, 237)], fill=hx("#F8B82A"))
    d.rectangle([(0, 241), (LW, LH)], fill=hx("#0E3B22"))

    # the convoy, heading right
    lane = 233
    box = px.box_truck(ramp_logo(30, shadow=None))
    vn = px.van(ramp_logo(19, shadow=None))
    pk = px.pickup(ramp_logo(13, shadow=None))
    for spr, x in [(pk, -8), (box, 40), (vn, 100)]:
        img.alpha_composite(spr, (x, lane - spr.height))
        px.puff(img, x - 3, lane - 5)
        for i, yy in enumerate((lane - spr.height + 5, lane - spr.height + 10)):
            d.line([(x - 9 - 2 * i, yy), (x - 4, yy)], fill=hx("#5A7A93"))
    return px.upscale(img, S, SIZE)


# ======================================================================= Night city (not Eco)
def city_scene():
    rnd = random.Random(11)
    img = Image.new("RGBA", (LW, LH), hx("#05060B"))
    px.bands(img, 0, 230, ["#05060B", "#07080F", "#0A0C15", "#0D101C", "#111524", "#151A2D", "#1A2036", "#1F2640", "#252D4A"])
    img = img.convert("RGB")          # so translucent fills blend instead of punching holes
    d = ImageDraw.Draw(img, "RGBA")
    # stars, sparse
    for _ in range(26):
        px.star(img, rnd.randrange(LW), rnd.randrange(2, 60), "#C9CEDC")
    # big moon, upper right, with a dithered halo
    mx, my, r = 92, 50, 17
    for y in range(my - r - 6, my + r + 7):
        for x in range(mx - r - 6, mx + r + 7):
            dd = (x - mx) ** 2 + (y - my) ** 2
            if r * r < dd <= (r + 5) ** 2 and (x + y) % 2 == 0 and 0 <= x < LW:
                px.blend(img, x, y, "#2A3150")
    d.ellipse([(mx - r, my - r), (mx + r, my + r)], fill=hx("#ECE6CC"))
    for cx, cy, cr in [(86, 44, 3), (98, 56, 4), (95, 41, 2), (84, 58, 2)]:
        d.ellipse([(cx - cr, cy - cr), (cx + cr, cy + cr)], fill=hx("#CFC7A6"))
    # low clouds across the moon
    for cx, cy, w in [(60, 62, 46), (76, 70, 40), (-6, 40, 40), (8, 88, 34)]:
        d.rectangle([(cx, cy), (cx + w, cy + 3)], fill=hx("#1B2033"))
        d.rectangle([(cx + 5, cy - 2), (cx + w - 7, cy)], fill=hx("#1B2033"))
        d.line([(cx + 5, cy - 3), (cx + w - 9, cy - 3)], fill=hx("#2A3150"))
    # two searchlights crossing (plain beams)
    for (bx, by), (tx, ty) in [((26, 168), (62, 40)), ((104, 176), (38, 46))]:
        d.polygon([(bx - 1, by), (bx + 1, by), (tx + 7, ty), (tx - 7, ty)], fill=(245, 233, 168, 34))
        d.polygon([(bx, by), (bx + 1, by), (tx + 2, ty), (tx - 2, ty)], fill=(245, 233, 168, 30))
        d.ellipse([(tx - 9, ty - 3), (tx + 9, ty + 3)], fill=(245, 233, 168, 70))

    # bats crossing the moon
    BAT = ["#.....#", "##.#.##", ".#####.", "..#.#.."]
    for bx, by in [(78, 36), (101, 60), (66, 52)]:
        for ry, row in enumerate(BAT):
            for rx, ch in enumerate(row):
                if ch == "#":
                    px.blend(img, bx + rx, by + ry, "#07080D")

    # far skyline
    x = -2
    while x < LW:
        w = rnd.choice([8, 10, 12])
        h = rnd.randrange(55, 95)
        top = 232 - h
        d.rectangle([(x, top), (x + w, 232)], fill=hx("#121626"))
        if rnd.random() < .4:
            d.rectangle([(x + w // 2 - 1, top - 6), (x + w // 2, top)], fill=hx("#121626"))
        for wx in range(x + 2, x + w - 1, 3):
            for wy in range(top + 3, 230, 4):
                if rnd.random() < .16:
                    px.blend(img, wx, wy, "#8A7A3E")
        x += w + 1

    # near gothic towers: spires, setbacks, arches
    def tower(x, w, h, spire):
        top = 236 - h
        c = "#06070B"
        d.rectangle([(x, top), (x + w, 236)], fill=hx(c))
        d.rectangle([(x + 2, top - 6), (x + w - 2, top)], fill=hx(c))           # setback
        d.rectangle([(x + 4, top - 12), (x + w - 4, top - 6)], fill=hx(c))      # setback
        cx = x + w // 2
        d.polygon([(cx - 2, top - 12), (cx, top - 12 - spire), (cx + 2, top - 12)], fill=hx(c))
        d.point([(x + 1, top - 1), (x + w - 1, top - 1)], fill=hx(c))
        # corner pinnacles
        for px_ in (x, x + w):
            d.line([(px_, top - 4), (px_, top)], fill=hx(c))
        # red beacon
        px.blend(img, cx, top - 12 - spire - 1, "#E5484D")
        # gothic arched windows
        for wx in range(x + 2, x + w - 2, 4):
            for wy in range(top + 4, 228, 7):
                if rnd.random() < .42:
                    d.rectangle([(wx, wy + 1), (wx + 1, wy + 3)], fill=hx("#F2C14E"))
                    d.point([(wx, wy), (wx + 1, wy)], fill=(242, 193, 78, 140))
        # arched entrance
        d.rectangle([(cx - 2, 229), (cx + 2, 236)], fill=hx("#1B1408"))

    tower(4, 22, 92, 16)
    tower(36, 16, 70, 10)
    tower(60, 26, 118, 22)
    tower(96, 18, 80, 12)
    tower(118, 16, 104, 14)
    # gargoyle on the big tower's ledge
    GAR = ["..##.", ".####", "####.", ".###.", ".#.#."]
    for ry, row in enumerate(GAR):
        for rx, ch in enumerate(row):
            if ch == "#":
                px.blend(img, 84 + rx, 236 - 118 - 5 + ry, "#06070B")

    # wet street
    d.rectangle([(0, 237), (LW, LH)], fill=hx("#0B0D14"))
    d.line([(0, 237), (LW, 237)], fill=hx("#2A3150"))
    for x in range(0, LW, 9):
        if rnd.random() < .7:
            d.line([(x, 240 + rnd.randrange(3)), (x + 2, 240 + rnd.randrange(3))], fill=(242, 193, 78, 90))

    # rain
    for _ in range(170):
        x, y = rnd.randrange(-10, LW), rnd.randrange(0, LH)
        a = rnd.choice([40, 60, 85])
        d.line([(x, y), (x + 1, y + 2)], fill=(150, 170, 210, a))
    return px.upscale(img, S, SIZE)


if __name__ == "__main__":
    eco_scene().save(px.HERE / "assets/bd-eco-8bit.png")
    city_scene().save(px.HERE / "assets/bd-night-city.png")
    print("ok")
