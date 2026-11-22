# Визуал и чертёж модели 1 (T1-Q60). Размеры в мм.
W, D, H = 590, 425, 710        # корпус
FT = 19                        # фасад
FW, GAP_S = 586, 2
LEG = 120
SINK_W, SINK_D, SINK_H = 600, 447, 30
F0, F1, F2, MID = 100, 302, 302, 3
HANDLE_L, HANDLE_C, HANDLE_T = 192, 160, 14   # длина ручки — ориентировочно (ВіЯр не указывает)
HANDLE_FROM_TOP = 38
import sys
URBAN = 'urban' in sys.argv
if URBAN: HANDLE_FROM_TOP = 60

# ---------------------------------------------------------------- визуал (кабинетная проекция)
s = 0.62
kx, ky = 0.42 * s, 0.26 * s     # смещение глубины
ox, oy = 105, 150                 # верхний левый угол «пола» сдвигаем ниже

def P(x, y, z):
    """x вправо, y вверх от пола, z — глубина от передней плоскости фасадов назад."""
    X = ox + x * s + z * kx
    Y = oy + (860 - y) * s - z * ky
    return f"{X:.1f},{Y:.1f}"

def poly(pts, fill, stroke="none", sw=0, extra=""):
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

v = []
zf = 0             # передняя плоскость фасадов
zc = FT            # передний край корпуса
zb = FT + D        # задний край
x0 = 0
# тень на полу
v.append(f'<ellipse cx="{ox + 300*s + 230*kx:.1f}" cy="{oy + 860*s - 230*ky + 6:.1f}" rx="{330*s:.1f}" ry="{70*s:.1f}" fill="url(#shadow)"/>')
# ножки (задние сначала)
def leg(x, z):
    out = []
    top_w, bot_w = 34, 22
    cx = x
    for (dx, col) in ((0, "#151515"),):
        pts_front = [P(cx - top_w/2, LEG, z), P(cx + top_w/2, LEG, z), P(cx + bot_w/2 + 6, 0, z), P(cx - bot_w/2 + 6, 0, z)]
        pts_side = [P(cx + top_w/2, LEG, z), P(cx + top_w/2, LEG, z + top_w), P(cx + bot_w/2 + 6, 0, z + bot_w), P(cx + bot_w/2 + 6, 0, z)]
        out.append(poly(pts_side, "#0b0b0b"))
        out.append(poly(pts_front, "url(#legGrad)"))
    return out
for (x, z) in ((40, zb - 70), (W - 40, zb - 70)):
    v += leg(x, z)
for (x, z) in ((40, zc + 30), (W - 40, zc + 30)):
    v += leg(x, z)

# корпус: правая боковина и верх (верх закрыт умывальником)
v.append(poly([P(W, LEG, zc), P(W, LEG, zb), P(W, LEG + H, zb), P(W, LEG + H, zc)], "url(#sideGrad)", "#d9d6cf", 0.6))
# торцы фасадов справа (толщина 19)
y = LEG + H
fronts = [("F0", F0), ("F1", F1), ("F2", F2)]
cur = LEG + H
for name, h in fronts:
    top, bot = cur, cur - h
    xr = W - GAP_S
    v.append(poly([P(xr, bot, zf), P(xr, bot, zc), P(xr, top, zc), P(xr, top, zf)], "#e7e4dd", "#d4d0c8", 0.5))
    cur = bot - MID
# фасады
cur = LEG + H
for i, (name, h) in enumerate(fronts):
    top, bot = cur, cur - h
    xl, xr = GAP_S, W - GAP_S
    v.append(poly([P(xl, bot, zf), P(xr, bot, zf), P(xr, top, zf), P(xl, top, zf)], "url(#frontGrad)", "#d8d4cc", 0.6))
    if name != "F0" or URBAN:
        # фрезеровка: Коррадо (рамка ~55 мм со скосом) или Урбан (~27 мм, скос 77°)
        b = 27 if URBAN else 55
        bev = 8 if URBAN else 14
        outer = [P(xl + b - bev, bot + b - bev, zf), P(xr - b + bev, bot + b - bev, zf), P(xr - b + bev, top - b + bev, zf), P(xl + b - bev, top - b + bev, zf)]
        inner = [P(xl + b, bot + b, zf), P(xr - b, bot + b, zf), P(xr - b, top - b, zf), P(xl + b, top - b, zf)]
        # скос: верх и лево — тень, низ и право — свет
        v.append(poly([outer[3], outer[2], inner[2], inner[3]], "#d9d5cd"))   # верхний скос (тень)
        v.append(poly([outer[0], outer[3], inner[3], inner[0]], "#dedad3"))   # левый скос
        v.append(poly([outer[1], outer[0], inner[0], inner[1]], "#fbfaf7"))   # нижний скос (свет)
        v.append(poly([outer[2], outer[1], inner[1], inner[2]], "#f6f4ef"))   # правый
        v.append(poly(inner, "url(#panelGrad)"))
    if name != "F0":
        # ручка
        hx = W / 2
        hy = top - HANDLE_FROM_TOP + 14
        a, b2 = P(hx - HANDLE_L/2, hy, zf - 22), P(hx + HANDLE_L/2, hy, zf - 22)
        (ax, ay), (bx, by) = [tuple(map(float, q.split(","))) for q in (a, b2)]
        # тень ручки на фасаде
        sa, sb = P(hx - HANDLE_L/2 + 4, hy - 10, zf), P(hx + HANDLE_L/2 + 4, hy - 10, zf)
        (sax, say), (sbx, sby) = [tuple(map(float, q.split(","))) for q in (sa, sb)]
        v.append(f'<line x1="{sax}" y1="{say}" x2="{sbx}" y2="{sby}" stroke="rgba(0,0,0,.18)" stroke-width="{HANDLE_T*s:.1f}" stroke-linecap="round" filter="url(#blur)"/>')
        # стойки
        for cxh in (hx - HANDLE_C/2, hx + HANDLE_C/2):
            p1, p2 = P(cxh, hy, zf), P(cxh, hy, zf - 22)
            (x1, y1), (x2, y2) = [tuple(map(float, q.split(","))) for q in (p1, p2)]
            v.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1d1d1d" stroke-width="{8*s:.1f}"/>')
        v.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="#141414" stroke-width="{HANDLE_T*s:.1f}" stroke-linecap="round"/>')
        v.append(f'<line x1="{ax}" y1="{ay-2}" x2="{bx}" y2="{by-2}" stroke="rgba(255,255,255,.28)" stroke-width="1.6" stroke-linecap="round"/>')
    cur = bot - MID

# умывальник: плита 600×447×30, свес
sx0 = (W - SINK_W) / 2
sz0, sz1 = zf + (FT + D - SINK_D) , FT + D          # задний край умывальника = задний край корпуса
sz0 = zb - SINK_D
yb_, yt_ = LEG + H, LEG + H + SINK_H
v.append(poly([P(sx0, yb_, sz0), P(sx0 + SINK_W, yb_, sz0), P(sx0 + SINK_W, yt_, sz0), P(sx0, yt_, sz0)], "url(#sinkFront)", "#cfcfcf", 0.6))
v.append(poly([P(sx0 + SINK_W, yb_, sz0), P(sx0 + SINK_W, yb_, sz1), P(sx0 + SINK_W, yt_, sz1), P(sx0 + SINK_W, yt_, sz0)], "#e9e9e9", "#cfcfcf", 0.6))
v.append(poly([P(sx0, yt_, sz0), P(sx0 + SINK_W, yt_, sz0), P(sx0 + SINK_W, yt_, sz1), P(sx0, yt_, sz1)], "#fdfdfd", "#d5d5d5", 0.6))
# чаша
bx0, bx1, bz0, bz1 = sx0 + 70, sx0 + SINK_W - 70, sz0 + 55, sz1 - 110
v.append(poly([P(bx0, yt_, bz0), P(bx1, yt_, bz0), P(bx1, yt_, bz1), P(bx0, yt_, bz1)], "url(#bowl)", "#d8d8d8", 0.6, 'rx="8"'))
# смеситель
fxp = P(W/2, yt_, sz1 - 55)
fx, fy = map(float, fxp.split(","))
v.append(f'<rect x="{fx-6}" y="{fy-62}" width="12" height="62" rx="5" fill="url(#chrome)"/>')
v.append(f'<path d="M{fx-2} {fy-50} q -4 -10 -30 -2" stroke="url(#chrome)" stroke-width="9" fill="none" stroke-linecap="round"/>')
v.append(f'<rect x="{fx-3}" y="{fy-68}" width="24" height="6" rx="3.5" fill="#9aa0a6"/>')

viz = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 760" font-family="Inter,Arial,sans-serif">
<defs>
 <linearGradient id="frontGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#efece6"/></linearGradient>
 <linearGradient id="panelGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbfaf7"/><stop offset="1" stop-color="#eeebe4"/></linearGradient>
 <linearGradient id="sideGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e6e3dc"/><stop offset="1" stop-color="#d6d2ca"/></linearGradient>
 <linearGradient id="legGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a2a2a"/><stop offset=".5" stop-color="#121212"/><stop offset="1" stop-color="#050505"/></linearGradient>
 <linearGradient id="handleGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a4a"/><stop offset=".45" stop-color="#1a1a1a"/><stop offset="1" stop-color="#050505"/></linearGradient>
 <linearGradient id="sinkFront" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ececec"/></linearGradient>
 <radialGradient id="bowl" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#e2e2e2"/><stop offset="1" stop-color="#ffffff"/></radialGradient>
 <linearGradient id="chrome" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8d9399"/><stop offset=".5" stop-color="#f1f3f5"/><stop offset="1" stop-color="#7c8288"/></linearGradient>
 <radialGradient id="shadow"><stop offset="0" stop-color="rgba(0,0,0,.28)"/><stop offset="1" stop-color="rgba(0,0,0,0)"/></radialGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f1ec"/><stop offset="1" stop-color="#e9e4dc"/></linearGradient>
 <filter id="blur"><feGaussianBlur stdDeviation="1.6"/></filter>
</defs>
<rect width="700" height="760" fill="#f7f5f1"/>
<rect y="{oy + 860*s - 60:.0f}" width="700" height="{760 - (oy + 860*s - 60):.0f}" fill="url(#floor)"/>
{chr(10).join(v)}
</svg>'''
open("/home/claude/viz/vizual-urban.svg" if URBAN else "/home/claude/viz/vizual.svg", "w").write(viz)
if URBAN: raise SystemExit

# ---------------------------------------------------------------- чертёж
k = 0.5
FX, FY = 150, 70       # вид спереди: левый верх (верх умывальника, y=860)
SX = FX + 600*k + 190  # вид сбоку
def fy(y): return FY + (860 - y) * k
d = []
def line(x1, y1, x2, y2, w=1, col="#222", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    d.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{da}/>')
def rect(x, y, w, h, fill="none", col="#222", sw=1.2, extra=""):
    d.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}" {extra}/>')
def text(x, y, t, size=11, anchor="middle", col="#222", w="normal", rot=None):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    d.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{col}" font-weight="{w}"{tr}>{t}</text>')
def vdim(x, y1, y2, label, side="l", col="#c0392b"):
    line(x, y1, x, y2, 0.8, col)
    for yy in (y1, y2):
        line(x - 4, yy, x + 4, yy, 0.8, col)
    text(x - 6 if side == "l" else x + 6, (y1 + y2) / 2 + 4, label, 10.5, "end" if side == "l" else "start", col)
def hdim(y, x1, x2, label, col="#c0392b", below=True):
    line(x1, y, x2, y, 0.8, col)
    for xx in (x1, x2):
        line(xx, y - 4, xx, y + 4, 0.8, col)
    text((x1 + x2) / 2, y + (13 if below else -5), label, 10.5, "middle", col)

text(FX, 40, "Вид спереди", 14, "start", "#111", "bold")
cx0 = FX + 5*k                       # корпус (590) внутри ширины умывальника 600
# умывальник
rect(FX, fy(860), 600*k, 30*k, "#eef6ff", "#2c7be5", 1)
text(FX + 300*k, fy(845) + 4, "умывальник 600 × 447 × 30", 9, col="#2c7be5")
# корпус
rect(cx0, fy(830), 590*k, 710*k, "#fafafa", "#999", 0.8)
# фасады
cur = 830
for name, h in fronts:
    rect(cx0 + 2*k, fy(cur), 586*k, h*k, "#ffffff", "#222", 1.2)
    if name != "F0":
        rect(cx0 + 2*k + 55*k, fy(cur) + 55*k, (586 - 110)*k, (h - 110)*k, "none", "#888", 0.7, 'stroke-dasharray="3 2"')
        hy = fy(cur) + HANDLE_FROM_TOP*k
        hx = cx0 + 2*k + 293*k
        d.append(f'<rect x="{hx - HANDLE_L/2*k:.1f}" y="{hy - 3.5:.1f}" width="{HANDLE_L*k:.1f}" height="7" rx="3.5" fill="#111"/>')
        for c_ in (-HANDLE_C/2, HANDLE_C/2):
            d.append(f'<circle cx="{hx + c_*k:.1f}" cy="{hy:.1f}" r="1.8" fill="#fff"/>')
        text(cx0 + 2*k + 293*k, fy(cur) + h*k/2 + 8, f"{'F1' if name=='F1' else 'F2'} 586 × {h}", 10, col="#555")
    else:
        text(cx0 + 2*k + 293*k, fy(cur) + h*k/2 + 4, "F0 царга 586 × 100 (гладкая)", 10, col="#555")
    cur -= h + MID
# ножки спереди
for lx in (40, 550):
    xl = cx0 + lx*k
    d.append(f'<polygon points="{xl-17*k:.1f},{fy(120):.1f} {xl+17*k:.1f},{fy(120):.1f} {xl+11*k+3:.1f},{fy(0):.1f} {xl-11*k+3:.1f},{fy(0):.1f}" fill="#111"/>')
line(FX - 30, fy(0), FX + 600*k + 30, fy(0), 1, "#666")
d.append(f'<path d="M{FX-30} {fy(0)} l 0 0" />')
# размеры по высоте слева
vdim(FX - 12, fy(120), fy(0), "120", "l", "#555")
vdim(FX - 50, fy(830), fy(0), "830", "l")
vdim(FX - 92, fy(860), fy(0), "860", "l")
# справа — разбивка фасадов
xr = FX + 600*k + 16
cur = 830
for name, h in fronts:
    vdim(xr, fy(cur), fy(cur - h), str(h), "r", "#1e6b3a")
    cur -= h
    if name != "F2":
        text(xr + 6, fy(cur) + 6, "3", 8.5, "start", "#1e6b3a")
        cur -= MID
vdim(xr + 44, fy(830), fy(120), "710", "r")
vdim(xr - 10 + 120, fy(830), fy(830 - HANDLE_FROM_TOP - 100 - MID), "", "r", "#fff")  # пусто (выравнивание)
# ширины
hdim(fy(0) + 18, FX, FX + 600*k, "600 (умывальник)")
hdim(fy(0) + 40, cx0, cx0 + 590*k, "590 (корпус), фасады 586")
# ручка
hy1 = fy(830 - F0 - MID)
hdim(hy1 + HANDLE_FROM_TOP*k - 14, cx0 + 2*k + 293*k - HANDLE_C/2*k, cx0 + 2*k + 293*k + HANDLE_C/2*k, "160", "#1e6b3a", below=False)

# ---------- вид сбоку
text(SX, 40, "Вид сбоку", 14, "start", "#111", "bold")
# умывальник 447, задний край = задний край корпуса
sb = SX + 447*k             # задний край
rect(SX, fy(860), 447*k, 30*k, "#eef6ff", "#2c7be5", 1)
# фасад 19 + корпус 425
rect(sb - 425*k, fy(830), 425*k, 710*k, "#fafafa", "#222", 1.2)
cur = 830
for name, h in fronts:
    rect(sb - 425*k - 19*k, fy(cur), 19*k, h*k, "#fff", "#222", 1)
    cur -= h + MID
# ручки сбоку
cur = 830 - F0 - MID
for h in (F1, F2):
    hy = fy(cur) + HANDLE_FROM_TOP*k
    xf = sb - 444*k
    d.append(f'<rect x="{xf - 26*k:.1f}" y="{hy-3.5:.1f}" width="{26*k:.1f}" height="7" rx="3" fill="#111"/>')
    cur -= h + MID
# ножки сбоку
for lz in (50, 375):
    xl = sb - 425*k + lz*k
    d.append(f'<polygon points="{xl-17*k:.1f},{fy(120):.1f} {xl+17*k:.1f},{fy(120):.1f} {xl+11*k:.1f},{fy(0):.1f} {xl-11*k:.1f},{fy(0):.1f}" fill="#111"/>')
line(SX - 30, fy(0), SX + 447*k + 30, fy(0), 1, "#666")
hdim(fy(0) + 18, sb - 444*k, sb, "444 (425 + фасад 19)")
hdim(fy(0) + 40, SX, sb, "447 (умывальник)")
vdim(sb + 16, fy(860), fy(830), "30", "r", "#2c7be5")

# пояснения
notes = [
 "Модель 1 (T1-Q60) — по типу Mirater «Естель» 60. Корпус МДФ 16, белый; фасады МДФ 19, белые.",
 "F0 — неподвижная царга 100 мм, крепится к царге корпуса K3 изнутри; F1, F2 — ящики, Häfele Matrix Runner.",
 "Ручки Ferro Fiori M 0734.160 чёрный браш (ВіЯр 191333), межосевое 160, по центру, ось 38 мм от верха фасада.",
 "Ножки Ferro Fiori PL 737 h=120, чёрные (ВіЯр 218885), 4 шт., центр ~40 мм от боковин.",
 "Пунктир на F1/F2 — рамка фрезеровки Коррадо (ширина ориентировочно, по листу ViyarFronts).",
]
for i, n in enumerate(notes):
    text(40, fy(0) + 82 + i * 17, n, 11, "start", "#333")
chert = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 {fy(0) + 82 + len(notes)*17 + 10:.0f}" font-family="Inter,Arial,sans-serif">
<rect width="100%" height="100%" fill="#ffffff"/>
{chr(10).join(d)}
</svg>'''
open("/home/claude/viz/chertezh.svg", "w").write(chert)
