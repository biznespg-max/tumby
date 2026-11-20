"""Чертёж верхнего ящика (вырез под ограничитель сифона): python izdeliya/verhniy_yashik.py TG-Q70"""
import pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from generator import config, model

art = sys.argv[1] if len(sys.argv) > 1 else "TG-Q70"
code, rest = art.split("-")
mkey = {"TG": "gold", "TL": "line"}[code]
c = config.product_config(mkey, "adamant-quanto", int(rest[1:]))
parts, facades, g = model.build(c)
t, L, H = c["t_box"], c["drawer_len"], c["drawer_top_box_h"]
wo, wi, bw, uw, zf = g["drawer_outer_width"], g["drawer_inner_width"], g["wing_w"], g["u_width"], g["u_from"]
slot = wi - 2 * bw
r = uw / 2
drain = c["drain_from_front"] - g["front_offset"]
S = 0.9
W_, H_ = 1500, 760
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}" font-family="DejaVu Sans, sans-serif">')
a(f'<rect width="{W_}" height="{H_}" fill="#fff"/>')
a(f'<text x="30" y="40" font-size="26" font-weight="700" fill="#222">Верхний ящик {art} — вырез под ограничитель сифона</text>')
a(f'<text x="30" y="68" font-size="16" fill="#555">ДСП 18 мм. Короб {wo:g} × {L} × {H} мм. Ограничитель Mesan W160 L245 H86 R80, белый (ВіЯр 228527). Стыки — минификсы.</text>')
COL = {"V1": "#e9c46a", "V2": "#f4a261", "V3": "#2a9d8f", "V4": "#d9d4c7"}


def dim_h(x1, x2, y, label, col="#222"):
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="1.4"/>')
    for x in (x1, x2):
        a(f'<line x1="{x}" y1="{y-6}" x2="{x}" y2="{y+6}" stroke="{col}" stroke-width="1.4"/>')
    a(f'<text x="{(x1+x2)/2}" y="{y-6}" font-size="15" text-anchor="middle" fill="{col}">{label}</text>')


def dim_v(x, y1, y2, label, col="#222"):
    a(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{col}" stroke-width="1.4"/>')
    for y in (y1, y2):
        a(f'<line x1="{x-6}" y1="{y}" x2="{x+6}" y2="{y}" stroke="{col}" stroke-width="1.4"/>')
    a(f'<text x="{x-8}" y="{(y1+y2)/2}" font-size="15" text-anchor="middle" fill="{col}" transform="rotate(-90 {x-8} {(y1+y2)/2})">{label}</text>')


ox, oy = 110, 150
a(f'<text x="{ox}" y="{oy-30}" font-size="19" font-weight="700">Вид сверху</text>')
a(f'<text x="{ox + wo*S + 14}" y="{oy+16}" font-size="14" fill="#777">← перед (фасад)</text>')
a(f'<text x="{ox + wo*S + 14}" y="{oy + L*S}" font-size="14" fill="#777">← зад (к стене)</text>')
X = lambda v: ox + v * S
Y = lambda v: oy + v * S
cx = t + wi / 2
a(f'<path d="M{X(t)},{Y(t)} H{X(t+wi)} V{Y(L-t)} H{X(cx+r)} V{Y(zf+r)} A{r*S},{r*S} 0 0 0 {X(cx-r)},{Y(zf+r)} V{Y(L-t)} H{X(t)} Z" fill="{COL["V4"]}" stroke="#333"/>')
a(f'<text x="{X(t + bw/2)}" y="{Y(L/2)}" font-size="15" text-anchor="middle" font-weight="700">V4 дно</text>')
a(f'<path d="M{X(cx-r)},{Y(L-t)} V{Y(zf+r)} A{r*S},{r*S} 0 0 1 {X(cx+r)},{Y(zf+r)} V{Y(L-t)}" fill="none" stroke="#999" stroke-width="5"/>')
a(f'<text x="{X(cx)}" y="{Y(zf + r + 80)}" font-size="13" text-anchor="middle" fill="#555">ограничитель</text>')
a(f'<text x="{X(cx)}" y="{Y(zf + r + 98)}" font-size="13" text-anchor="middle" fill="#555">(пластик, H86)</text>')
for x0, w_, k, lab in ((0, t, "V1", ""), (wo - t, t, "V1", ""), (t, wi, "V2", "V2 передняя стенка"),
                       (t, bw, "V3", "V3Л"), (t + wi - bw, bw, "V3", "V3П")):
    z0, d = ((0, L) if k == "V1" else (0, t) if k == "V2" else (L - t, t))
    a(f'<rect x="{X(x0)}" y="{Y(z0)}" width="{w_*S}" height="{d*S}" fill="{COL[k]}" stroke="#333"/>')
    if lab:
        a(f'<text x="{X(x0 + w_/2)}" y="{Y(z0 + d/2) + 5}" font-size="13" text-anchor="middle" font-weight="700">{lab}</text>')
a(f'<circle cx="{X(cx)}" cy="{Y(drain)}" r="{20*S}" fill="#cfe5ff" stroke="#1E90FF" stroke-width="2"/>')
a(f'<text x="{X(cx) + 26}" y="{Y(drain) + 5}" font-size="13" fill="#1E5FAA">слив {drain:g}</text>')
dim_h(X(0), X(wo), oy - 8, f"{wo:g}")
dim_h(X(cx - r), X(cx + r), Y(L) + 30, f"вырез {uw:g}", "#1E5FAA")
dim_h(X(t), X(t + bw), Y(L) + 30, f"{bw:g}")
dim_v(X(wo) + 70, Y(zf), Y(L - t), f"{L - t - zf:g}", "#1E5FAA")
dim_v(ox - 24, oy, Y(L), f"{L}")
a(f'<text x="{ox}" y="{Y(L) + 66}" font-size="14" fill="#1E5FAA">Передняя часть дна ({zf - t:g} мм) остаётся целой. Вырез в дне фрезеруется в ViyarPro, полукруг R{r:g}.</text>')

bx, by = 880, 160
a(f'<text x="{bx}" y="{by-40}" font-size="19" font-weight="700">Вид сзади (со стороны стены)</text>')
BX = lambda v: bx + v * S
for x0, w_, k, lab in ((0, t, "V1", ""), (wo - t, t, "V1", ""), (t, bw, "V3", "V3Л"), (t + wi - bw, bw, "V3", "V3П")):
    a(f'<rect x="{BX(x0)}" y="{by}" width="{w_*S}" height="{H*S}" fill="{COL[k]}" stroke="#333"/>')
    if lab:
        a(f'<text x="{BX(x0 + w_/2)}" y="{by + H*S/2 + 5}" font-size="13" text-anchor="middle" font-weight="700">{lab}</text>')
a(f'<rect x="{BX(t + bw)}" y="{by}" width="{slot*S}" height="{H*S}" fill="#eaf4ff" stroke="#1E90FF" stroke-dasharray="5 4"/>')
a(f'<text x="{BX(t + bw + slot/2)}" y="{by + H*S/2 + 5}" font-size="12" text-anchor="middle" fill="#1E5FAA">щель</text>')
dim_h(BX(0), BX(wo), by - 10, f"{wo:g}")
dim_h(BX(t + bw), BX(t + bw + slot), by + H*S + 26, f"{slot:g}", "#1E5FAA")
dim_v(bx - 20, by, by + H*S, f"{H}")
a(f'<text x="{bx}" y="{by + H*S + 60}" font-size="14" fill="#333">Труба сифона проходит через щель, когда ящик выдвигается.</text>')
a(f'<text x="{bx}" y="{by + H*S + 80}" font-size="14" fill="#333">Каждая половинка задней стенки ≥ 200 мм — ViyarPro её сверлит.</text>')

lx, ly = 880, 420
a(f'<text x="{lx}" y="{ly}" font-size="19" font-weight="700">Детали верхнего ящика</text>')
rows = [(p.code, p.name, f"{p.l:g} × {p.w:g}", p.count) for p in parts if p.code.startswith("V")]
for i, (k, n, d, q) in enumerate(rows):
    y = ly + 32 + i * 30
    a(f'<rect x="{lx}" y="{y-16}" width="18" height="18" fill="{COL[k[:2]]}" stroke="#333"/>')
    a(f'<text x="{lx+28}" y="{y}" font-size="15"><tspan font-weight="700">{k}</tspan>  {n} — {d} мм × {q}</text>')
a("</svg>")
out = pathlib.Path(__file__).parent / art / "verhniy_yashik.svg"
out.write_text("\n".join(o), encoding="utf-8")
subprocess.run(["rsvg-convert", str(out), "-o", str(out.with_suffix(".png"))], check=True)
print(out.with_suffix(".png"))
