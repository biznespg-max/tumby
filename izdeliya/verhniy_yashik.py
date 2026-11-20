"""Чертёж верхнего ящика (с вырезом под сифон) для одной тумбы: python izdeliya/verhniy_yashik.py TG-Q70"""
import pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from generator import config, model

art = sys.argv[1] if len(sys.argv) > 1 else "TG-Q70"
code, rest = art.split("-")
size = int(rest[1:])
mkey = {"TG": "gold", "TL": "line"}[code]
c = config.product_config(mkey, "adamant-quanto", size)
parts, facades, g = model.build(c)
t, L, H = c["t_box"], c["drawer_len"], c["drawer_top_box_h"]
wo, wi, ww, uw = g["drawer_outer_width"], g["drawer_inner_width"], g["wing_w"], g["u_width"]
drain = c["drain_from_front"] - g["front_offset"]         # центр слива от переда короба
S = 0.9
W_, H_ = 1500, 760
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}" font-family="DejaVu Sans, sans-serif">')
a(f'<rect width="{W_}" height="{H_}" fill="#fff"/>')
a(f'<text x="30" y="40" font-size="26" font-weight="700" fill="#222">Верхний ящик {art} — вырез под сифон на всю глубину</text>')
a(f'<text x="30" y="68" font-size="16" fill="#555">ДСП 18 мм. Короб {wo:g} × {L} × {H} мм (Ш × Г × В). Вырез {uw:g} мм. Все стыки на минификсах.</text>')

COL = {"V1": "#e9c46a", "V2": "#f4a261", "V3": "#2a9d8f", "V4": "#8ab17d", "V7": "#d9d4c7"}


def dim_h(x1, x2, y, label, col="#222", fs=15):
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="1.4"/>')
    for x in (x1, x2):
        a(f'<line x1="{x}" y1="{y-6}" x2="{x}" y2="{y+6}" stroke="{col}" stroke-width="1.4"/>')
    a(f'<text x="{(x1+x2)/2}" y="{y-6}" font-size="{fs}" text-anchor="middle" fill="{col}">{label}</text>')


def dim_v(x, y1, y2, label, col="#222", fs=15):
    a(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{col}" stroke-width="1.4"/>')
    for y in (y1, y2):
        a(f'<line x1="{x-6}" y1="{y}" x2="{x+6}" y2="{y}" stroke="{col}" stroke-width="1.4"/>')
    a(f'<text x="{x-8}" y="{(y1+y2)/2}" font-size="{fs}" text-anchor="middle" fill="{col}" transform="rotate(-90 {x-8} {(y1+y2)/2})">{label}</text>')


# ---------------- Вид сверху
ox, oy = 110, 150
a(f'<text x="{ox}" y="{oy-30}" font-size="19" font-weight="700">Вид сверху</text>')
a(f'<text x="{ox + wo*S + 14}" y="{oy+16}" font-size="14" fill="#777">← перед (фасад)</text>')
a(f'<text x="{ox + wo*S + 14}" y="{oy + L*S}" font-size="14" fill="#777">← зад (к стене)</text>')


def R(x, z, w, d, k, lab=None):
    a(f'<rect x="{ox + x*S}" y="{oy + z*S}" width="{w*S}" height="{d*S}" fill="{COL[k]}" stroke="#333" stroke-width="1.2"/>')
    if lab:
        cx, cy = ox + (x + w/2)*S, oy + (z + d/2)*S
        rot = f' transform="rotate(-90 {cx} {cy})"' if d > w * 2 else ""
        a(f'<text x="{cx}" y="{cy+5}" font-size="14" text-anchor="middle" font-weight="700"{rot}>{lab}</text>')


R(t, t, ww, L - 2*t, "V7", "V7 дно крыла")
R(t + wi - ww, t, ww, L - 2*t, "V7", "V7 дно крыла")
R(0, 0, t, L - t, "V1", "V1")
R(wo - t, 0, t, L - t, "V1", "V1")
R(t, 0, wi, t, "V2", "V2 передняя стенка")
R(t + ww, t, t, L - 2*t, "V4", "V4")
R(wi - ww, t, t, L - 2*t, "V4", "V4")
R(0, L - t, ww + 2*t, t, "V3", "V3")
R(wi - ww, L - t, ww + 2*t, t, "V3", "V3")
# вырез и сифон
ux = 2*t + ww
a(f'<rect x="{ox + ux*S}" y="{oy + t*S}" width="{uw*S}" height="{(L - t)*S + 30}" fill="#eaf4ff" stroke="#1E90FF" stroke-dasharray="6 4"/>')
a(f'<circle cx="{ox + wo/2*S}" cy="{oy + drain*S}" r="{35*S}" fill="#cfe5ff" stroke="#1E90FF" stroke-width="2"/>')
a(f'<text x="{ox + wo/2*S}" y="{oy + drain*S + 5}" font-size="13" text-anchor="middle" fill="#1E5FAA">сифон</text>')
a(f'<path d="M{ox + wo/2*S},{oy + (drain+40)*S} L{ox + wo/2*S},{oy + L*S + 26}" stroke="#1E90FF" stroke-width="3" marker-end="url(#ar)"/>')
a('<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1E90FF"/></marker></defs>')
a(f'<text x="{ox + wo/2*S}" y="{oy + L*S + 46}" font-size="14" text-anchor="middle" fill="#1E5FAA">труба от сифона уходит к стене; вырез открыт сзади — ящик выезжает вперёд мимо сифона</text>')
dim_h(ox, ox + wo*S, oy - 8, f"{wo:g}")
dim_h(ox + ux*S, ox + (ux + uw)*S, oy + L*S + 80, f"вырез {uw:g}", "#1E5FAA")
dim_h(ox + t*S, ox + (t + ww)*S, oy + L*S + 80, f"{ww:g}")
dim_v(ox - 24, oy, oy + L*S, f"{L}")
a(f'<text x="{ox + wo/2*S + 40}" y="{oy + drain*S - 30}" font-size="13" fill="#1E5FAA">слив {drain:g} от переда</text>')

# ---------------- Вид сзади
bx, by = 860, 160
a(f'<text x="{bx}" y="{by-40}" font-size="19" font-weight="700">Вид сзади (со стороны стены)</text>')


def RB(x, y, w, h, k, lab=None):
    a(f'<rect x="{bx + x*S}" y="{by + (H - y - h)*S}" width="{w*S}" height="{h*S}" fill="{COL[k]}" stroke="#333" stroke-width="1.2"/>')
    if lab:
        a(f'<text x="{bx + (x + w/2)*S}" y="{by + (H - y - h/2)*S + 5}" font-size="13" text-anchor="middle" font-weight="700">{lab}</text>')


RB(0, 0, ww + 2*t, H, "V3", "V3")
RB(wi - ww, 0, ww + 2*t, H, "V3", "V3")
RB(ux, 0, uw, H, "V2", "V2 (видна в вырезе)")
dim_h(bx, bx + wo*S, by - 10, f"{wo:g}")
dim_h(bx, bx + (ww + 2*t)*S, by + H*S + 26, f"{ww + 2*t:g}", "#1d6d63")
dim_v(bx - 20, by, by + H*S, f"{H}")
a(f'<text x="{bx}" y="{by + H*S + 60}" font-size="14" fill="#333">V3 перекрывает торцы боковины V1 и стенки выреза V4;</text>')
a(f'<text x="{bx}" y="{by + H*S + 80}" font-size="14" fill="#333">длина V3 ≥ 200 мм — ViyarPro её сверлит.</text>')

# ---------------- Список деталей
lx, ly = 860, 420
a(f'<text x="{lx}" y="{ly}" font-size="19" font-weight="700">Детали верхнего ящика</text>')
rows = [(p.code, p.name, f"{p.l:g} × {p.w:g}", p.count) for p in parts if p.code.startswith("V")]
for i, (k, n, d, q) in enumerate(rows):
    y = ly + 32 + i * 30
    a(f'<rect x="{lx}" y="{y-16}" width="18" height="18" fill="{COL[k[:2]]}" stroke="#333"/>')
    a(f'<text x="{lx+28}" y="{y}" font-size="15"><tspan font-weight="700">{k}</tspan>  {n} — {d} мм × {q}</text>')
y = ly + 32 + len(rows) * 30 + 20
for s in ["Было: передняя полоса дна V6 и стенка V5 закрывали вырез спереди,",
          "задняя стенка из двух половинок 184,5 мм — ViyarPro не сверлит &lt; 200 мм.",
          "Стало: вырез от передней стенки V2 до зада, V5 и V6 убраны,",
          "каждое «крыло» — коробочка V1 + V4 + V7, сзади закрыта V3."]:
    a(f'<text x="{lx}" y="{y}" font-size="14" fill="#555">{s}</text>')
    y += 22
a("</svg>")
out = pathlib.Path(__file__).parent / art / "verhniy_yashik.svg"
out.write_text("\n".join(o), encoding="utf-8")
subprocess.run(["rsvg-convert", str(out), "-o", str(out.with_suffix(".png"))], check=True)
print(out.with_suffix(".png"))
