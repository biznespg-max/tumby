"""Визуал подвесных тумб (модель 2 — Маура с фрезерованной проходной ручкой, модель 3 — Сансет 64 с ручками).
Размеры фасадов берутся из генератора. Запуск из корня:  python modeli/vizual_podves.py
Результат: modeli/m2/vizual.svg, modeli/m3/vizual.svg
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from generator import config, model  # noqa: E402

s = 0.62
kx, ky = 0.42 * s, 0.26 * s
ox, oy = 105, 120
SINK_W, SINK_D, SINK_H = 600, 447, 30


def handle(v, P, xy, hx, hy, zf=0):
    """Условная накладная ручка: чёрная планка ~192 мм, межосевое 160, вылет 24."""
    for cc in (hx - 80, hx + 80):
        (x1, y1), (x2, y2) = xy(P(cc, hy, zf)), xy(P(cc, hy, zf - 24))
        v.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1d1d1d" stroke-width="{8*s:.1f}"/>')
    (sax, say), (sbx, sby) = xy(P(hx - 96 + 4, hy - 10, zf)), xy(P(hx + 96 + 4, hy - 10, zf))
    v.append(f'<line x1="{sax}" y1="{say}" x2="{sbx}" y2="{sby}" stroke="rgba(0,0,0,.18)" stroke-width="{12*s:.1f}" stroke-linecap="round" filter="url(#blur)"/>')
    (ax, ay), (bx, by) = xy(P(hx - 96, hy, zf - 24)), xy(P(hx + 96, hy, zf - 24))
    v.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="#141414" stroke-width="{12*s:.1f}" stroke-linecap="round"/>')
    v.append(f'<line x1="{ax}" y1="{ay-2}" x2="{bx}" y2="{by-2}" stroke="rgba(255,255,255,.25)" stroke-width="1.4" stroke-linecap="round"/>')


LT22_DROP = 38   # верх профиля LT22 от верхнего края фасада (модель 2, под рамкой)


def handle_lt22(v, P, xy, poly, hx, top, zf=0, L=340, h=22, lip=8):
    """Профиль LT22 (ВіЯр 213758): чёрная накладка вдоль верхнего края фасада, отгиб вперёд-вниз."""
    x0, x1 = hx - L / 2, hx + L / 2
    v.append(poly([P(x0 + 4, top - h - 9, zf), P(x1 + 4, top - h - 9, zf), P(x1, top - h, zf), P(x0, top - h, zf)], "rgba(0,0,0,.16)", extra='filter="url(#blur)"'))
    v.append(poly([P(x0, top - h, zf - lip), P(x1, top - h, zf - lip), P(x1, top, zf - lip), P(x0, top, zf - lip)], "#1b1b1b"))
    v.append(poly([P(x1, top - h, zf - lip), P(x1, top - h, zf), P(x1, top, zf), P(x1, top, zf - lip)], "#0c0c0c"))
    v.append(poly([P(x0, top, zf - lip), P(x1, top, zf - lip), P(x1, top, zf), P(x0, top, zf)], "#3a3a3a"))
    (ax, ay), (bx, by) = xy(P(x0, top - h, zf - lip)), xy(P(x1, top - h, zf - lip))
    v.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="rgba(255,255,255,.22)" stroke-width="1.2"/>')


def render(mkey, style):
    c = config.product_config(mkey, "adamant-quanto", 60)
    parts, facades, g = model.build(c)
    W, H, D, FT = c["width"], c["height"], c["depth"], c["facade_t"]
    Y0 = 260                      # низ корпуса над «полом» картинки (подвесная)

    def P(x, y, z):
        X = ox + x * s + z * kx
        Yv = oy + (Y0 + H + SINK_H + 40 - y) * s - z * ky
        return f"{X:.1f},{Yv:.1f}"

    def xy(p):
        return tuple(map(float, p.split(",")))

    def poly(pts, fill, stroke="none", sw=0, extra=""):
        return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

    v = []
    zf, zc, zb = 0, FT, FT + D
    # тень на стене
    sx0, sy0 = xy(P(10, Y0 - 40, zb))
    v.append(f'<rect x="{sx0:.1f}" y="{sy0 - H*s:.1f}" width="{W*s:.1f}" height="{(H+60)*s:.1f}" rx="18" fill="rgba(0,0,0,.10)" filter="url(#soft)"/>')
    # правая боковина
    v.append(poly([P(W, Y0, zc), P(W, Y0, zb), P(W, Y0 + H, zb), P(W, Y0 + H, zc)], "url(#sideGrad)", "#d9d6cf", 0.6))
    # низ корпуса (виден снизу чуть-чуть нет — смотрим сверху) ; торцы фасадов справа
    for f in facades:
        top, bot = Y0 + f["top"], Y0 + f["top"] - f["h"]
        xr = f["x"] + f["w"]
        v.append(poly([P(xr, bot, zf), P(xr, bot, zc), P(xr, top, zc), P(xr, top, zf)], "#e7e4dd", "#d4d0c8", 0.5))
    for i, f in enumerate(facades):
        top, bot = Y0 + f["top"], Y0 + f["top"] - f["h"]
        xl, xr = f["x"], f["x"] + f["w"]
        v.append(poly([P(xl, bot, zf), P(xr, bot, zf), P(xr, top, zf), P(xl, top, zf)], "url(#frontGrad)", "#d8d4cc", 0.6))
        if style == "maura":
            b, bev = 23, 6            # рамка ~20 мм, центр фрезы 23 мм от торца
            o = [P(xl + b - bev, bot + b - bev, zf), P(xr - b + bev, bot + b - bev, zf), P(xr - b + bev, top - b + bev, zf), P(xl + b - bev, top - b + bev, zf)]
            n = [P(xl + b, bot + b, zf), P(xr - b, bot + b, zf), P(xr - b, top - b, zf), P(xl + b, top - b, zf)]
            v.append(poly([o[3], o[2], n[2], n[3]], "#d3cfc7"))
            v.append(poly([o[0], o[3], n[3], n[0]], "#dad6ce"))
            v.append(poly([o[1], o[0], n[0], n[1]], "#fbfaf7"))
            v.append(poly([o[2], o[1], n[1], n[2]], "#f3f1ec"))
            v.append(poly(n, "url(#panelGrad)"))
        if style == "sunset":
            # вертикальные волны, шаг 64 от центра фасада (CR), у торцов неполная волна
            cx = (xl + xr) / 2
            k0 = -int((cx - xl) // 64) - 1
            for kk in range(k0, -k0 + 1):
                a, b2 = cx + kk * 64 - 32, cx + kk * 64 + 32
                a, b2 = max(a, xl), min(b2, xr)
                if b2 - a < 2:
                    continue
                v.append(poly([P(a, bot, zf), P(b2, bot, zf), P(b2, top, zf), P(a, top, zf)], "url(#wave)"))
    for f in facades:   # ручки поверх фрезеровки
        if f["code"] in ("F1", "F2"):
            if style == "maura":
                # под рамкой Мауры: рамка ~20 мм + фреза (центр 23) -> верх профиля на 38 мм ниже края
                handle_lt22(v, P, xy, poly, f["x"] + f["w"] / 2, Y0 + f["top"] - LT22_DROP)
            else:
                handle(v, P, xy, f["x"] + f["w"] / 2, Y0 + f["top"] - 45)
    # умывальник
    sx = (W - SINK_W) / 2
    sz0, sz1 = zb - SINK_D, zb
    yb_, yt_ = Y0 + H, Y0 + H + SINK_H
    v.append(poly([P(sx, yb_, sz0), P(sx + SINK_W, yb_, sz0), P(sx + SINK_W, yt_, sz0), P(sx, yt_, sz0)], "url(#sinkFront)", "#cfcfcf", 0.6))
    v.append(poly([P(sx + SINK_W, yb_, sz0), P(sx + SINK_W, yb_, sz1), P(sx + SINK_W, yt_, sz1), P(sx + SINK_W, yt_, sz0)], "#e9e9e9", "#cfcfcf", 0.6))
    v.append(poly([P(sx, yt_, sz0), P(sx + SINK_W, yt_, sz0), P(sx + SINK_W, yt_, sz1), P(sx, yt_, sz1)], "#fdfdfd", "#d5d5d5", 0.6))
    v.append(poly([P(sx + 70, yt_, sz0 + 55), P(sx + SINK_W - 70, yt_, sz0 + 55), P(sx + SINK_W - 70, yt_, sz1 - 110), P(sx + 70, yt_, sz1 - 110)], "url(#bowl)", "#d8d8d8", 0.6))
    fx, fy = xy(P(W / 2, yt_, sz1 - 55))
    v.append(f'<rect x="{fx-6}" y="{fy-62}" width="12" height="62" rx="5" fill="url(#chrome)"/>')
    v.append(f'<path d="M{fx-2} {fy-50} q -4 -10 -30 -2" stroke="url(#chrome)" stroke-width="9" fill="none" stroke-linecap="round"/>')
    v.append(f'<rect x="{fx-3}" y="{fy-68}" width="24" height="6" rx="3" fill="#9aa0a6"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 640" font-family="Inter,Arial,sans-serif">
<defs>
 <linearGradient id="frontGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#efece6"/></linearGradient>
 <linearGradient id="panelGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbfaf7"/><stop offset="1" stop-color="#eeebe4"/></linearGradient>
 <linearGradient id="sideGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e6e3dc"/><stop offset="1" stop-color="#d6d2ca"/></linearGradient>
 <linearGradient id="wave" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fbfaf8"/><stop offset=".12" stop-color="#e2ded6"/><stop offset=".5" stop-color="#f3f0ea"/><stop offset=".88" stop-color="#ffffff"/><stop offset="1" stop-color="#f7f5f1"/></linearGradient>
 <linearGradient id="pullTop" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#6d6a64"/><stop offset=".35" stop-color="#bdb8af"/><stop offset="1" stop-color="#f4f2ed"/></linearGradient>
 <linearGradient id="pullBot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#57544f"/><stop offset=".4" stop-color="#b3aea5"/><stop offset="1" stop-color="#f4f2ed"/></linearGradient>
 <linearGradient id="sinkFront" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ececec"/></linearGradient>
 <radialGradient id="bowl" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#e2e2e2"/><stop offset="1" stop-color="#ffffff"/></radialGradient>
 <linearGradient id="chrome" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8d9399"/><stop offset=".5" stop-color="#f1f3f5"/><stop offset="1" stop-color="#7c8288"/></linearGradient>
 <filter id="blur"><feGaussianBlur stdDeviation="1.6"/></filter>
 <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<rect width="700" height="640" fill="#f3f0ea"/>
{chr(10).join(v)}
</svg>'''
    out = ROOT / "modeli" / mkey / "vizual.svg"
    out.write_text(svg, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(render("m2", "maura"))
    print(render("m3", "sunset"))
