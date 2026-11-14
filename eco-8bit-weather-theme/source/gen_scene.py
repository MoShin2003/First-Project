"""Builds the animated 8-bit Eco backdrop as one SVG: rain -> sun -> wind on a loop.

Layout, in CSS pixels with no root viewBox, so every screen gets the same 3 px
'fat pixel' and nothing stretches:
  sky        full screen, stepped bands that recolour with the weather
  weather    pinned top-centre: sun, clouds, birds, lightning
  ground     pinned bottom-centre: houses, trees, road, the fleet driving by
  logo       pinned centre, 42% down
  particles  full screen: rain, wind gusts, leaves, lightning flash
"""
import random
import sys
from PIL import Image

import pixel as px
from pixel import hx
from scenes8 import ramp_logo

CYCLE = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0   # seconds for rain -> sun -> wind
OUT = sys.argv[2] if len(sys.argv) > 2 else "scene.svg"
HALF = 440                                                   # ground half-width, logical px
rnd = random.Random(5)

# ------------------------------------------------------------------ weather palette: (rain, sun, wind)
SKY = list(zip(
    ["#36465A", "#3B4B5F", "#415165", "#47576A", "#4D5D70", "#536376", "#5A697C", "#617082", "#687788"],
    ["#1C78C8", "#2484D0", "#2C90D8", "#369CDF", "#42A8E5", "#50B3EA", "#5FBEEE", "#70C8F2", "#84D2F5"],
    ["#3A86BE", "#428FC4", "#4B98C9", "#55A1CE", "#60AAD3", "#6BB3D7", "#77BCDB", "#84C4DF", "#92CCE3"],
))
FILL = {
    "w0": ("#5E6B78", "#F2E6CF", "#E6DCC8"), "w1": ("#56697A", "#CFE3EE", "#C5DAE6"),
    "w2": ("#5D6E62", "#D8E8C8", "#CFE0C0"), "w3": ("#6C6263", "#EED9D0", "#E3CFC7"),
    "r0": ("#26303B", "#3B4B5C", "#3B4B5C"), "r1": ("#3F2E2B", "#8A4A3C", "#8A4A3C"), "r2": ("#25362C", "#2F5A40", "#2F5A40"),
    "wn": ("#FFD866", "#9ED8F5", "#B5E2F7"),
    "tk": ("#2E2118", "#5A3E2A", "#5A3E2A"),
    "c0": ("#2C5E3A", "#3E9B3A", "#4AA23F"), "c1": ("#3A7048", "#64C04A", "#70C552"),
    "ch": ("#4C5866", "#9AA6B0", "#9AA6B0"), "cf": ("#36414C", "#6E7B86", "#6E7B86"),
    "rd": ("#1D252E", "#3A4550", "#3C4752"),
    "gr": ("#22492C", "#3E8E3A", "#4A9A3E"), "gh": ("#2E5C38", "#5DB04A", "#64B44E"),
    "tg": ("#FFFFFF", "#003057", "#003057"),
}
for i, c in enumerate(SKY):
    FILL[f"k{i}"] = c
OPAC = {"oR": (1, 0, 0), "oS": (0, 1, 0), "oW": (0, 0, 1), "oSW": (0, 1, .85), "oRS": (1, 1, 0)}

T = "0%,30%{{{p}:{r}}}33.33%,63.33%{{{p}:{s}}}66.67%,96.67%{{{p}:{w}}}100%{{{p}:{r}}}"


def css_weather():
    out = []
    for name, (r, s, w) in FILL.items():
        out.append(f"@keyframes {name}{{{T.format(p='fill', r=r, s=s, w=w)}}}.{name}{{fill:{r};animation:{name} {CYCLE}s linear infinite}}")
    for name, (r, s, w) in OPAC.items():
        out.append(f"@keyframes {name}{{{T.format(p='opacity', r=r, s=s, w=w)}}}.{name}{{opacity:{r};animation:{name} {CYCLE}s linear infinite}}")
    return "".join(out)


# ------------------------------------------------------------------ helpers
def run(x, y, n, h=1):
    return f"M{x} {y}h{n}v{h}h-{n}z"


def img_runs(img, ox=0, oy=0):
    """{hex: path-d} for the opaque pixels of a pixel-art image."""
    by = {}
    w, h = img.size
    p = img.load()
    for y in range(h):
        x = 0
        while x < w:
            c = p[x, y]
            if c[3] < 128:
                x += 1
                continue
            x0 = x
            while x < w and p[x, y][:3] == c[:3] and p[x, y][3] >= 128:
                x += 1
            key = "#%02X%02X%02X" % c[:3]
            by.setdefault(key, []).append(run(ox + x0, oy + y, x - x0))
    return {k: "".join(v) for k, v in by.items()}


def paths(by, cls=None):
    return "".join(f'<path fill="{c}" d="{d}"/>' for c, d in by.items())


class Layer:
    """Collects run-paths per CSS class, so one <path> per colour role."""

    def __init__(self):
        self.d = {}

    def add(self, cls, d):
        self.d.setdefault(cls, []).append(d)

    def svg(self, order=None):
        keys = order or list(self.d)
        return "".join(f'<path class="{k}" d="{"".join(self.d[k])}"/>' for k in keys if k in self.d)


# ------------------------------------------------------------------ ground (bottom-anchored, y=0 is the screen's foot)
def ground():
    g = Layer()
    base = -79                          # houses stand here
    x = -HALF - 4
    trees = []
    while x < HALF:
        w = rnd.choice([13, 15, 17, 19])
        h = rnd.choice([9, 11, 13])
        wall, roof = f"w{rnd.randrange(4)}", f"r{rnd.randrange(3)}"
        g.add(wall, run(x, base - h, w, h + 1))
        peak = w // 2
        for i in range(peak):                       # stepped gable
            g.add(roof, run(x - 1 + i, base - h - 1 - i, w + 2 - 2 * i))
        if rnd.random() < .6:
            g.add(roof, run(x + w - 4, base - h - peak + 1, 2, peak - 2))
        for wx in range(x + 2, x + w - 3, 5):
            for wy in range(base - h + 2, base - 3, 5):
                if rnd.random() < .6:
                    g.add("wn", run(wx, wy, 2, 2))
        x += w + rnd.choice([3, 6, 9])
        if rnd.random() < .5:
            trees.append(x - 2)
    calm, sway = Layer(), Layer()
    for cx in trees:
        g.add("tk", run(cx, base - 3, 1, 4))
        for lay in (calm, sway):
            dx = 1 if lay is sway else 0
            for i, (ox, ww) in enumerate([(-2, 5), (-3, 7), (-4, 9), (-4, 9), (-4, 9), (-3, 7), (-2, 5)]):
                lay.add("c0", run(cx + ox + dx * (i < 4), base - 11 + i, ww))
            lay.add("c1", run(cx - 2 + dx, base - 10, 2) + run(cx - 1 + dx, base - 9, 1))
    # road
    g.add("ch", run(-HALF, -78, 2 * HALF))
    g.add("cf", run(-HALF, -77, 2 * HALF, 2))
    g.add("rd", run(-HALF, -75, 2 * HALF, 34))
    g.add("gh", run(-HALF, -41, 2 * HALF))
    g.add("gr", run(-HALF, -40, 2 * HALF, 40))
    dashes = "".join(run(x, -46, 5, 2) for x in range(-HALF, HALF, 10))
    # rain extras: puddles + splashes
    pud = "".join(run(x, -58 + rnd.randrange(10), rnd.choice([8, 12, 16]), 1) for x in range(-HALF + 7, HALF, 37))
    spl = []
    for i, x in enumerate(range(-HALF + 3, HALF, 13)):
        y = -70 + rnd.randrange(26)
        d = run(x, y, 1) + run(x + 2, y, 1) + run(x + 1, y + 1, 1)
        spl.append(f'<path class="sp" style="animation-delay:-{rnd.random() * .9:.2f}s" d="{d}"/>')
    order = [k for k in ["w0", "w1", "w2", "w3", "r0", "r1", "r2", "wn", "tk", "ch", "cf", "rd", "gh", "gr"]]
    return (g.svg(order)
            + f'<g class="oRS">{calm.svg(["c0", "c1"])}</g><g class="oW"><g class="sway">{sway.svg(["c0", "c1"])}</g></g>'
            + f'<path fill="#F8B82A" d="{dashes}"/>'
            + f'<g class="oR"><path fill="#33424F" d="{pud}"/>{"".join(spl)}</g>')


WHEEL_A = px.WHEEL
WHEEL_B = ["..KKKK..", ".KDDDDK.", "KDgDDgDK", "KDDwwDDK", "KDDwwDDK", "KDgDDgDK", ".KDDDDK.", "..KKKK.."]


def sprite_svg(make, lane_bottom=-49):
    px.WHEEL = WHEEL_A
    a = make()
    px.WHEEL = WHEEL_B
    b = make()
    px.WHEEL = WHEEL_A
    w, h = a.size
    base = Image.new("RGBA", a.size, (0, 0, 0, 0))
    ha = Image.new("RGBA", a.size, (0, 0, 0, 0))
    hb = Image.new("RGBA", a.size, (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            pa, pb = a.getpixel((x, y)), b.getpixel((x, y))
            if pa == pb:
                base.putpixel((x, y), pa)
            else:
                ha.putpixel((x, y), pa)
                hb.putpixel((x, y), pb)
    top = lane_bottom - h
    # headlight: find the yellow pixel on the front
    hy = next(y for y in range(h) for x in range(w - 1, 0, -1) if a.getpixel((x, y))[:3] == hx("#FFE27A")[:3])
    y0 = top + hy
    beam = ('<g class="oR">'
            + "".join(f'<path fill="#FFF1A8" fill-opacity="{o}" d="M{w + x} {y0 - g}h{n}v{2 + 2 * g}h-{n}z"/>'
                      for x, n, g, o in [(0, 4, 0, .55), (4, 5, 1, .38), (9, 6, 2, .24), (15, 7, 3, .12)])
            + "</g>")
    puff = f'<path class="pf" fill="#9FB2C2" d="{run(-3, lane_bottom - 5, 2)}{run(-6, lane_bottom - 6, 2)}{run(-5, lane_bottom - 4, 1)}"/>'
    return (beam + puff + paths(img_runs(base, 0, top))
            + f'<g class="hA">{paths(img_runs(ha, 0, top))}</g><g class="hB">{paths(img_runs(hb, 0, top))}</g>'), w


def fleet():
    box = lambda: px.box_truck(ramp_logo(30, shadow=None))
    van = lambda: px.van(ramp_logo(19, shadow=None))
    pk = lambda: px.pickup(ramp_logo(13, shadow=None))
    out = []
    for i, (mk, rest) in enumerate([(pk, -58), (box, -2), (van, 52)]):
        body, w = sprite_svg(mk)
        out.append(f'<g class="drv t{i}" style="--x:{rest}px">{body}</g>')
    return "".join(out)


# ------------------------------------------------------------------ logo (centred on 0,0)
def logo():
    lg = ramp_logo(98)
    t1, t2 = "PLUMBERS · ELECTRICIANS", "HVAC TECHNICIANS"
    tw1, tw2 = px.text_width(t1), px.text_width(t2)
    H = lg.height + 3 + 12
    ox, oy = -lg.width // 2, -H // 2
    out = paths(img_runs(lg, ox, oy))
    tag = Image.new("RGBA", (max(tw1, tw2) + 4, 12), (0, 0, 0, 0))
    px.draw_text(tag, (tag.width - tw1) // 2, 0, t1, "#FFFFFF")
    x2 = (tag.width - tw2) // 2
    px.draw_text(tag, x2, 7, t2, "#FFFFFF")
    tx, ty = -tag.width // 2, oy + lg.height + 3
    d = "".join(img_runs(tag, tx, ty).values())
    out += f'<path class="tg" d="{d}"/>'
    out += f'<path fill="#84BD00" d="{run(tx + x2 - 9, ty + 9, 6)}{run(tx + x2 + tw2 + 3, ty + 9, 6)}"/>'
    return out


# ------------------------------------------------------------------ sky weather (top-anchored, centred on x=0)
def cloud(x, y, w, body, top):
    return (f'<path fill="{body}" d="{run(x, y, w, 4)}{run(x + 4, y - 2, w - 9, 2)}{run(x + 8, y - 4, w - 17, 2)}"/>'
            f'<path fill="{top}" d="{run(x + 9, y - 4, w - 20, 1)}{run(x + 5, y - 2, 3, 1)}"/>')


def clouds(cls, n, body, top, ys, widths, dur):
    out = []
    for i in range(n):
        w = rnd.choice(widths)
        y = rnd.randrange(*ys)
        out.append(f'<g class="{cls}" style="animation-delay:-{dur * i / n:.1f}s">{cloud(-w // 2, y, w, body, top)}</g>')
    return "".join(out)


def sky_weather():
    out = []
    # sun (sun + wind), with two ray frames
    sx, sy = 40, 34
    disc = "".join(run(sx + ox, sy + i, w) for i, (ox, w) in enumerate(
        [(-3, 7), (-5, 11), (-6, 13), (-7, 15), (-7, 15), (-7, 15), (-7, 15), (-7, 15), (-7, 15), (-7, 15), (-6, 13), (-5, 11), (-3, 7)]))
    hi = run(sx - 4, sy + 2, 3) + run(sx - 5, sy + 3, 2)
    raysA = "".join(run(sx + dx, sy + 5 + dy, 2, 2) for dx, dy in [(-1, -11), (-1, 11), (-12, 0), (10, 0), (-10, -9), (8, -9), (-10, 9), (8, 9)])
    raysB = "".join(run(sx + dx, sy + 5 + dy, 2, 2) for dx, dy in [(-1, -13), (-1, 13), (-14, 0), (12, 0), (-11, -10), (9, -10), (-11, 10), (9, 10)])
    out.append(f'<g class="oSW"><path fill="#FFD54A" d="{disc}"/><path fill="#FFF0A0" d="{hi}"/>'
               f'<path class="rA" fill="#FFE27A" d="{raysA}"/><path class="rB" fill="#FFE27A" d="{raysB}"/></g>')
    out.append(f'<g class="oS">{clouds("cS", 5, "#FFFFFF", "#E3F1FA", (52, 78), [22, 26, 30], 60)}</g>')
    out.append(f'<g class="oW">{clouds("cW", 6, "#F2F8FC", "#FFFFFF", (48, 86), [18, 24, 30], 13)}</g>')
    out.append(f'<g class="oR">{clouds("cR", 7, "#26313F", "#33404F", (10, 70), [36, 44, 52], 90)}</g>')
    # birds (sun)
    bA = "M0 0h1v1h-1zM1 1h1v1h-1zM2 0h1v1h-1z"
    bB = "M0 1h1v1h-1zM1 1h1v1h-1zM2 1h1v1h-1zM1 0h1v1h-1z"
    birds = "".join(
        f'<g class="cB" style="animation-delay:-{i * 4}s"><g transform="translate({dx} {dy})">'
        f'<path class="fA" fill="#12324F" d="{bA}"/><path class="fB" fill="#12324F" d="{bB}"/></g></g>'
        for i, (dx, dy) in enumerate([(-10, 64), (-4, 60), (2, 66)]))
    out.append(f'<g class="oS">{birds}</g>')
    # lightning (rain)
    bolt = [(0, 0), (1, 1), (1, 2), (2, 3), (2, 4), (1, 5), (2, 5), (3, 6), (3, 7), (4, 8), (3, 9), (4, 9), (5, 10), (5, 11), (6, 12), (6, 13)]
    d = "".join(run(-38 + x, 40 + y * 2, 2, 2) for x, y in bolt)
    out.append(f'<path class="bolt" fill="#F4F8FF" d="{d}"/>')
    return "".join(out)


# ------------------------------------------------------------------ full-screen particle patterns (CSS px, 3 px per pixel)
def particles():
    r2 = random.Random(9)
    # rain: tile 48 x 96, falls (-48, 192) per loop
    drops = "".join(f"M{x} {y}h3v6h-3zM{x - 3} {y + 6}h3v3h-3z"
                    for x, y in [(r2.randrange(1, 16) * 3, r2.randrange(0, 32) * 3) for _ in range(5)])
    far = "".join(f"M{x} {y}h3v3h-3zM{x - 3} {y + 3}h3v3h-3z"
                  for x, y in [(r2.randrange(1, 16) * 3, r2.randrange(0, 32) * 3) for _ in range(4)])
    gust_pts = [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 2), (8, 1), (8, 0), (7, 0), (6, 1)]
    gust = lambda ox, oy: "".join(f"M{ox + x * 3} {oy + y * 3}h3v3h-3z" for x, y in gust_pts)
    gusts = gust(12, 30) + gust(150, 96) + gust(60, 150) + "".join(f"M{x} {y}h18v3h-18z" for x, y in [(210, 42), (24, 120), (180, 168)])
    leaves = [("#84BD00", 30, 24), ("#F08A24", 120, 60), ("#25A64E", 200, 18), ("#B5DC3C", 72, 120), ("#E9B23A", 168, 132)]
    leaf = "".join(f'<path fill="{c}" d="M{x} {y}h6v3h-6zM{x + 3} {y + 3}h3v3h-3z"/>' for c, x, y in leaves)
    defs = (f'<pattern id="rn" width="48" height="96" patternUnits="userSpaceOnUse"><path fill="#A9C2DA" fill-opacity=".75" d="{drops}"/></pattern>'
            f'<pattern id="rf" width="48" height="96" patternUnits="userSpaceOnUse"><path fill="#8EA6BE" fill-opacity=".45" d="{far}"/></pattern>'
            f'<pattern id="gs" width="270" height="180" patternUnits="userSpaceOnUse"><path fill="#FFFFFF" fill-opacity=".7" d="{gusts}"/></pattern>'
            f'<pattern id="lv" width="240" height="150" patternUnits="userSpaceOnUse">{leaf}</pattern>')
    layers = ('<g class="oR"><g class="fall2"><rect x="-48" y="-192" width="200%" height="140%" fill="url(#rf)"/></g>'
              '<g class="fall"><rect x="-48" y="-192" width="200%" height="140%" fill="url(#rn)"/></g></g>'
              '<g class="oW"><g class="blow"><rect x="-270" y="0" width="200%" height="100%" fill="url(#gs)"/></g>'
              '<g class="tumble"><rect x="-480" y="-150" width="300%" height="140%" fill="url(#lv)"/></g></g>'
              '<rect class="flash" width="100%" height="100%" fill="#DDE8FF"/>')
    return defs, layers


def build():
    pdefs, players = particles()
    c = CYCLE
    flash_at = [8.0, 8.5, 21.0]   # % of the cycle, all inside the rain window
    fk = "".join(f"{a:.2f}%{{opacity:0}}{a + .15:.2f}%{{opacity:1}}{a + .45:.2f}%{{opacity:0}}" for a in flash_at)
    css = (
        "svg{shape-rendering:crispEdges}"
        + css_weather()
        + f"@keyframes bolt{{0%{{opacity:0}}{fk}100%{{opacity:0}}}}.bolt{{opacity:0;animation:bolt {c}s linear infinite}}"
        + f"@keyframes flash{{0%{{opacity:0}}{fk.replace('opacity:1', 'opacity:.28')}100%{{opacity:0}}}}.flash{{opacity:0;animation:flash {c}s linear infinite}}"
        # fleet: phones by default, a longer road on wide screens
        + "@keyframes drv{from{transform:translateX(-132px)}to{transform:translateX(84px)}}"
        + "@keyframes drvL{from{transform:translateX(-500px)}to{transform:translateX(452px)}}"
        + ".drv{transform:translateX(var(--x));animation:drv 10.8s linear infinite}"
        + ".t1{animation-delay:-3.6s}.t2{animation-delay:-7.2s}"
        + "@keyframes hA{0%{opacity:1}50%{opacity:0}}@keyframes hB{0%{opacity:0}50%{opacity:1}}"
        + ".hA{animation:hA .24s steps(1) infinite}.hB{opacity:0;animation:hB .24s steps(1) infinite}"
        + "@keyframes pf{0%{opacity:.9;transform:translateX(0)}100%{opacity:0;transform:translateX(-4px)}}.pf{animation:pf .6s steps(3) infinite}"
        + "@keyframes sp{0%{opacity:0}40%{opacity:1}70%{opacity:0}}.sp{fill:#A9C2DA;animation:sp .9s steps(1) infinite}"
        # clouds and birds drift
        + "@keyframes dr{from{transform:translateX(-120px)}to{transform:translateX(120px)}}"
        + "@keyframes drL{from{transform:translateX(-480px)}to{transform:translateX(480px)}}"
        + ".cS{animation:dr 60s linear infinite}.cW{animation:dr 13s linear infinite}.cR{animation:dr 90s linear infinite}.cB{animation:dr 26s linear infinite}"
        + "@keyframes fl{0%{opacity:1}50%{opacity:0}}.fA{animation:fl .5s steps(1) infinite}.fB{opacity:0;animation:fl .5s steps(1) infinite reverse}"
        + ".rB{opacity:0;animation:fl 1.6s steps(1) infinite reverse}.rA{animation:fl 1.6s steps(1) infinite}"
        + "@keyframes sw{0%{transform:translateX(0)}50%{transform:translateX(1px)}}.sway{animation:sw .7s steps(1) infinite}"
        # particles
        + "@keyframes fall{to{transform:translate(-48px,192px)}}.fall{animation:fall .55s linear infinite}.fall2{animation:fall .95s linear infinite}"
        + "@keyframes blow{to{transform:translateX(270px)}}.blow{animation:blow 1.1s linear infinite}"
        + "@keyframes tumble{to{transform:translate(480px,150px)}}.tumble{animation:tumble 2.6s linear infinite}"
        + "@media (min-width:600px){.drv{animation-name:drvL;animation-duration:44s}.t1{animation-delay:-14.7s}.t2{animation-delay:-29.3s}"
          ".cS,.cW,.cR,.cB{animation-name:drL}.cS{animation-duration:160s}.cW{animation-duration:36s}.cR{animation-duration:240s}.cB{animation-duration:70s}}"
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    sky = "".join(f'<rect class="k{i}" y="{i * 100 / 9:.2f}%" width="100%" height="{100 / 9 + .2:.2f}%"/>' for i in range(9))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">'
        f"<style>{css}</style><defs>{pdefs}</defs>"
        f"{sky}"
        f'<svg x="50%" y="0" width="1" height="1" overflow="visible"><g transform="scale(3)">{sky_weather()}</g></svg>'
        f'<svg x="50%" y="100%" width="1" height="1" overflow="visible"><g transform="scale(3)">{ground()}{fleet()}</g></svg>'
        f'<svg x="50%" y="42%" width="1" height="1" overflow="visible"><g transform="scale(3)">{logo()}</g></svg>'
        f"{players}"
        "</svg>"
    )
    return svg


if __name__ == "__main__":
    s = build()
    open(OUT, "w").write(s)
    print(OUT, len(s), "chars")
