"""Чертёж внутреннего устройства модели 1 (T1-Q60): разрез спереди (без фасадов) и разрез сбоку.
Размеры берутся из генератора (generator/model.py), поэтому совпадают с деталями в файле для ViyarPro.
Запуск из корня репозитория:  python modeli/m1/vnutri.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from generator import config, model  # noqa: E402

c = config.product_config("m1", "adamant-quanto", 60)
parts, facades, g = model.build(c)
cers = config.product_config("m1", "adamant-cers", 60)["sink"]

W, H, D, t, tb = c["width"], c["height"], c["depth"], c["t"], c["t_box"]
LEG, SINK_T = 120, 30
FT = c["facade_t"]
iw, bw = g["inner_width"], g["drawer_outer_width"]
L = c["drawer_len"]
rf, rt, rb, rbl = c["front_rail_h"], c["rear_top_rail_h"], c["rear_bottom_rail_h"], c["rear_bottom_rail_lift"]
yb_bot, hb_bot = g["bottom_drawer_box_bottom"], c["drawer_bottom_box_h"]
yb_top, hb_top = g["top_drawer_box_bottom"], c["drawer_top_box_h"]
rec = c["drawer_bottom_recess"]
sink = c["sink"]
drain = c["drain_from_front"]
cut_len = c.get("siphon_cut_len", 250)

k = 0.55
TOP = 80                       # y экрана для отметки 900 мм от пола
def Y(y):                      # y — мм от пола
    return TOP + (900 - y) * k

out = []
def a(s): out.append(s)
def rect(x, y0, w, h, fill="none", col="#222", sw=1.1, extra=""):
    """x, w — экранные; y0, h — мм от пола (y0 = низ)."""
    a(f'<rect x="{x:.1f}" y="{Y(y0 + h):.1f}" width="{w:.1f}" height="{h * k:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}" {extra}/>')
def text(x, y, s, size=10.5, anchor="middle", col="#222", w="normal"):
    a(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{col}" font-weight="{w}">{s}</text>')
def line(x1, y1, x2, y2, col="#222", sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"{d}/>')
def vdim(x, y1, y2, label, side="r", col="#c0392b"):
    line(x, Y(y1), x, Y(y2), col, 0.8)
    for yy in (y1, y2):
        line(x - 4, Y(yy), x + 4, Y(yy), col, 0.8)
    text(x + (6 if side == "r" else -6), (Y(y1) + Y(y2)) / 2 + 4, label, 10, "start" if side == "r" else "end", col)
def hdim(yscr, x1, x2, label, col="#c0392b"):
    line(x1, yscr, x2, yscr, col, 0.8)
    for xx in (x1, x2):
        line(xx, yscr - 4, xx, yscr + 4, col, 0.8)
    text((x1 + x2) / 2, yscr + 13, label, 10, "middle", col)

C_CORP, C_RAIL, C_BOX, C_RUN = "#e9e4da", "#c9b48a", "#fbf3dc", "#5b6770"

# ===================================================================== разрез спереди (без фасадов)
X0 = 120
def FX(x): return X0 + x * k
text(X0, 40, "Вид спереди без фасадов", 14, "start", "#111", "bold")
# умывальник (Quanto)
sx = FX((W - sink["width"]) / 2)
rect(sx, LEG + H, sink["width"] * k, SINK_T, "#eef6ff", "#2c7be5", 1)
bwid = sink["bowl_width"] or 450
a(f'<path d="M{FX(W/2 - bwid/2):.1f} {Y(LEG+H):.1f} L{FX(W/2 - bwid/2 + 30):.1f} {Y(LEG+H+SINK_T-sink["height"]):.1f} '
  f'L{FX(W/2 + bwid/2 - 30):.1f} {Y(LEG+H+SINK_T-sink["height"]):.1f} L{FX(W/2 + bwid/2):.1f} {Y(LEG+H):.1f}" fill="none" stroke="#2c7be5" stroke-dasharray="4 3"/>')
text(FX(W/2), Y(LEG + H + SINK_T) - 6, f"чаша {sink['brand']} {sink['series']} (пунктир)", 9, col="#2c7be5")
# боковины и дно
rect(FX(0), LEG, t * k, H, C_CORP)
rect(FX(W - t), LEG, t * k, H, C_CORP)
rect(FX(t), LEG, iw * k, t, C_CORP)
F0S = g.get("f0_structural")
F0 = next(f for f in facades if f["code"] == "F0")
if F0S:   # внутренней K3 нет: спереди вверху связь — сама царга-фасад F0 (снята на этом виде)
    rect(FX(F0["x"]), LEG + F0["top"] - F0["h"], F0["w"] * k, F0["h"], "none", "#8a6d3b", 1, 'stroke-dasharray="5 3"')
    text(FX(W / 2), Y(LEG + H - rf / 2) + 4, "здесь царга-фасад F0 (снята) — внутренней царги нет", 9.5, col="#6b4f1d")
    for h in F0["holes"]:   # минификсы F0 -> боковины
        a(f'<circle cx="{FX(F0["x"] + h.x):.1f}" cy="{Y(LEG + F0["top"] - F0["h"] + h.y):.1f}" r="3.2" fill="#c0392b"/>')
else:
    rect(FX(t), LEG + H - rf, iw * k, rf, C_RAIL, "#8a6d3b")
    text(FX(W / 2), Y(LEG + H - rf / 2) + 4, f"K3 царга передняя {iw}×{rf}", 9.5)
# ящики
for (y0, h, lab) in ((yb_bot, hb_bot, f"нижний ящик (короб {bw}×{hb_bot})"), (yb_top, hb_top, f"верхний ящик (короб {bw}×{hb_top}) — под сифон")):
    xl = FX((W - bw) / 2)
    rect(xl, LEG + y0, bw * k, h, C_BOX, "#b8860b")
    rect(xl + tb * k, LEG + y0 + rec, (bw - 2 * tb) * k, tb, "#f3e2b3", "#b8860b", 0.6)   # дно короба
    text(FX(W / 2), Y(LEG + y0 + h / 2) + 4, lab, 9.5)
    # направляющие Matrix под коробом у боковин
    for xr in (FX(t), FX(W - t) - 22 * k):
        rect(xr, LEG + y0, 22 * k, rec, C_RUN, C_RUN, 0.5)
# ножки
for lx in (40, W - 40):
    a(f'<polygon points="{FX(lx-17):.1f},{Y(LEG):.1f} {FX(lx+17):.1f},{Y(LEG):.1f} {FX(lx+11):.1f},{Y(0):.1f} {FX(lx-11):.1f},{Y(0):.1f}" fill="#111"/>')
line(X0 - 20, Y(0), FX(W) + 20, Y(0), "#666")
# размеры справа
xd = FX(W) + 14
vdim(xd, LEG, LEG + t, f"дно {t}")
vdim(xd, LEG + yb_bot, LEG + yb_bot + hb_bot, f"{hb_bot}")
vdim(xd, LEG + yb_top, LEG + yb_top + hb_top, f"{hb_top}")
vdim(xd, LEG + H - rf, LEG + H, f"{rf}")
vdim(xd + 56, LEG, LEG + H, f"{H}")
# зазоры между коробами
text(xd + 6, Y(LEG + (yb_bot + hb_bot + yb_top) / 2) + 4, f"{yb_top - yb_bot - hb_bot}", 9, "start", "#888")
text(xd + 6, Y(LEG + (yb_top + hb_top + H - rf) / 2) + 4, f"{H - rf - yb_top - hb_top}", 9, "start", "#888")
hdim(Y(0) + 20, FX(0), FX(W), f"корпус {W}")
hdim(Y(0) + 42, FX(t), FX(W - t), f"внутри {iw}")
hdim(Y(0) + 64, FX((W - bw) / 2), FX((W + bw) / 2), f"короб {bw} (по {(iw - bw) / 2:g} на направляющие)")

# ===================================================================== разрез сбоку (по центру)
S0 = FX(W) + 190
zfront = S0 + FT * k                       # передний край корпуса (фасады перед ним)
def SZ(z): return zfront + z * k           # z — мм от переднего края корпуса назад
text(S0, 40, "Разрез сбоку (перед слева)", 14, "start", "#111", "bold")
# умывальник: задний край = задний край корпуса
rect(SZ(D - sink["depth"]), LEG + H, sink["depth"] * k, SINK_T, "#eef6ff", "#2c7be5", 1)
bd = sink["bowl_depth"]
bz0 = drain - bd / 2
bot_q = LEG + H + SINK_T - sink["height"]
bot_c = LEG + H + SINK_T - cers["height"]
a(f'<path d="M{SZ(bz0):.1f} {Y(LEG+H):.1f} Q{SZ(bz0):.1f} {Y(bot_q):.1f} {SZ(drain):.1f} {Y(bot_q):.1f} Q{SZ(bz0+bd):.1f} {Y(bot_q):.1f} {SZ(bz0+bd):.1f} {Y(LEG+H):.1f}" fill="none" stroke="#2c7be5" stroke-dasharray="4 3"/>')
line(SZ(drain - 60), Y(bot_c), SZ(drain + 60), Y(bot_c), "#8e44ad", 1, "2 2")
text(SZ(drain - 60), Y(bot_c) + 12, "низ чаши Cers", 8.5, "start", "#8e44ad")
# слив и сифон
line(SZ(drain), Y(bot_q), SZ(drain), Y(LEG + yb_top + rec + tb) , "#2c7be5", 1.2)
text(SZ(drain) + 4, Y(LEG + H + SINK_T) - 8, f"слив {drain} от края", 9, "start", "#2c7be5")
# боковина (контур), дно, царги
rect(SZ(0), LEG, D * k, H, "none", "#222", 1.2)
rect(SZ(0), LEG, D * k, t, C_CORP, "#222", 0.8)                                   # дно K2
if not F0S:
    rect(SZ(0), LEG + H - rf, t * k, rf, C_RAIL, "#8a6d3b")                       # K3
rect(SZ(D - t), LEG + H - rt, t * k, rt, C_RAIL, "#8a6d3b")                       # K4
rect(SZ(D - t), LEG + t + rbl, t * k, rb, C_RAIL, "#8a6d3b")                      # K5
if F0S:
    for h in F0["holes"][:2]:   # минификс: шток в F0, эксцентрик в боковине на 24 мм от торца
        yy = Y(LEG + F0["top"] - F0["h"] + h.y)
        line(S0 + FT * k / 2, yy, SZ(24), yy, "#c0392b", 1.6)
        a(f'<circle cx="{SZ(24):.1f}" cy="{yy:.1f}" r="4.2" fill="#fff" stroke="#c0392b" stroke-width="1.4"/>')
    text(SZ(32), Y(LEG + H - 50) + 4, "F0 на минификсах к боковинам", 9, "start", "#c0392b")
else:
    text(SZ(t) + 4, Y(LEG + H - rf / 2) + 4, "K3", 9.5, "start", "#6b4f1d", "bold")
text(SZ(D - t) - 4, Y(LEG + H - rt / 2) + 4, "K4", 9.5, "end", "#6b4f1d", "bold")
text(SZ(D - t) - 4, Y(LEG + t + rbl + rb / 2) + 4, "K5", 9.5, "end", "#6b4f1d", "bold")
# ящики
for (y0, h, name) in ((yb_bot, hb_bot, "нижний"), (yb_top, hb_top, "верхний")):
    rect(SZ(0), LEG + y0, L * k, h, C_BOX, "#b8860b")
    rect(SZ(tb), LEG + y0 + rec, (L - 2 * tb) * k, tb, "#f3e2b3", "#b8860b", 0.6)          # дно короба
    rect(SZ(0), LEG + y0, L * k, 6, C_RUN, C_RUN, 0.3)                                    # направляющая
    text(SZ(tb + 8), Y(LEG + y0 + h - 22) + 4, f"{name} ящик, короб {L}×{h}", 9.5, "start")
# вырез под сифон в верхнем ящике: от задней стенки вперёд
zc0 = L - tb - cut_len
rect(SZ(zc0), LEG + yb_top + rec, (cut_len + tb) * k, tb, "#ffffff", "#c0392b", 0.8, 'stroke-dasharray="3 2"')
rect(SZ(zc0 + 6), LEG + yb_top + rec + tb, (cut_len - 12) * k, 86, "rgba(255,255,255,.75)", "#7f8c8d", 0.8)
text(SZ(zc0 + cut_len / 2), Y(LEG + yb_top + rec + tb + 43) + 4, "ограничитель сифона", 8.5, "middle", "#555")
# фасады
cur = LEG + H
for f in facades:
    rect(S0, cur - f["h"], FT * k, f["h"], "#ffffff", "#222", 1)
    cur -= f["h"] + c["facade_mid_gap"]
# ножки
for lz in (50, D - 50):
    a(f'<polygon points="{SZ(lz-17):.1f},{Y(LEG):.1f} {SZ(lz+17):.1f},{Y(LEG):.1f} {SZ(lz+11):.1f},{Y(0):.1f} {SZ(lz-11):.1f},{Y(0):.1f}" fill="#111"/>')
line(S0 - 20, Y(0), SZ(D) + 20, Y(0), "#666")
# размеры сбоку
xr = SZ(D) + 14
vdim(xr, LEG + H - rt, LEG + H, f"K4 {rt}")
vdim(xr, LEG + t + rbl, LEG + t + rbl + rb, f"K5 {rb}")
vdim(xr, LEG + t, LEG + t + rbl, f"{rbl}")
vdim(SZ(drain + 95), LEG + yb_top + hb_top, bot_c, f"{bot_c - LEG - yb_top - hb_top:g}", "r", "#8e44ad")
hdim(Y(0) + 20, SZ(0), SZ(L), f"ящик {L} (NL {c['runner_nl']})")
hdim(Y(0) + 42, SZ(0), SZ(D), f"корпус {D}")
hdim(Y(0) + 64, S0, SZ(D), f"с фасадом {D + FT}")
yy = Y(LEG + yb_top + rec + tb + 86) - 10
line(SZ(zc0), yy, SZ(L - tb), yy, "#c0392b", 0.8)
for xx in (SZ(zc0), SZ(L - tb)):
    line(xx, yy - 4, xx, yy + 4, "#c0392b", 0.8)
text((SZ(zc0) + SZ(L - tb)) / 2, yy - 4, f"вырез {cut_len}", 9.5, "middle", "#c0392b")

# ===================================================================== легенда
notes = [
    ("#e9e4da", f"Корпус: боковины K1Л/K1П {D}×{H} и дно K2 {iw}×{D}, МДФ 16 мм, всё на минификсах (снаружи отверстий нет)."),
    ("#c9b48a", (f"Царги: спереди — сама царга-фасад F0 586×100 на 4 минификсах к торцам боковин (как у Естель); K4 задняя верхняя {iw}×{rt} (через неё — к стене),"
                 if g.get("f0_structural") else f"Царги: K3 передняя {iw}×{rf} (на неё крепится фасад-царга F0), K4 задняя верхняя {iw}×{rt} (через неё — к стене),")),
    (None, f"K5 задняя нижняя {iw}×{rb}, поднята на {rbl} мм над дном — под ней проходят задние концы направляющих."),
    ("#fbf3dc", f"Ящики: короба ДСП 18, ширина {bw}, длина {L}; дно короба поднято на {rec} мм — под ним направляющие Häfele Matrix Runner."),
    ("#ffffff", f"Верхний ящик: в дне вырез {g['u_width']}×{cut_len} от задней стенки с полукругом R80 + пластиковый ограничитель Mesan; задняя стенка из двух половинок."),
    (C_RUN, "Направляющие Matrix Runner UM (полное выдвижение, доводчик), NL 400, крепятся к боковинам."),
    ("#c0392b", "Красные точки — минификсы F0: штоки Ø5×11 в изнанке F0 (6 мм от торцов, на 25 и 75 мм от низа), эксцентрики в боковинах изнутри."),
]
ny = Y(0) + 100
for i, (col, n) in enumerate(notes):
    if col:
        a(f'<rect x="40" y="{ny + i*18 - 10:.1f}" width="12" height="12" fill="{col}" stroke="#888" stroke-width="0.6"/>')
    text(60, ny + i * 18, n, 11, "start", "#333")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SZ(D) + 200:.0f} {ny + len(notes)*18 + 10:.0f}" font-family="Inter,Arial,sans-serif">'
       '<rect width="100%" height="100%" fill="#fff"/>' + "\n".join(out) + "</svg>")
p = pathlib.Path(__file__).resolve().parent / "vnutri.svg"
p.write_text(svg, encoding="utf-8")
print(p)
