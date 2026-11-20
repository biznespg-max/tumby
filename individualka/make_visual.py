"""Візуал індивідуальної тумби 120 (виправлений): python make_visual.py -> vizual.svg / vizual.png"""
import subprocess, pathlib

W, H = 1536, 1024
S = 0.47                 # px на мм (фронтальний вигляд)
X0, FLOOR = 60, 950      # лівий край стіни, рівень підлоги
GOLD, INK, DIM = "#b8893a", "#2b2622", "#5a4a3a"

def X(mm): return X0 + mm * S
def Y(mm): return FLOOR - mm * S

o = []
a = o.append

def dim_h(x1, x2, y, label, sub=None, size=22, color=INK):
    a(f'<g stroke="{color}" stroke-width="2" fill="{color}">'
      f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>'
      f'<path d="M{x1},{y} l10,-5 v10 z M{x2},{y} l-10,-5 v10 z" stroke="none"/></g>')
    a(f'<text x="{(x1+x2)/2}" y="{y-9}" font-size="{size}" font-weight="700" text-anchor="middle" fill="{color}">{label}</text>')
    if sub:
        a(f'<text x="{(x1+x2)/2}" y="{y+22}" font-size="15" text-anchor="middle" fill="{color}">{sub}</text>')

def dim_v(x, y1, y2, label, size=20, color=INK, side=-1):
    a(f'<g stroke="{color}" stroke-width="2" fill="{color}">'
      f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>'
      f'<path d="M{x},{y1} l-5,10 h10 z M{x},{y2} l-5,-10 h10 z" stroke="none"/></g>')
    tx = x + side * 14
    a(f'<text x="{tx}" y="{(y1+y2)/2}" font-size="{size}" font-weight="700" text-anchor="middle" fill="{color}" '
      f'transform="rotate(-90 {tx} {(y1+y2)/2})" dy="7">{label}</text>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="DejaVu Sans, sans-serif">')
a('''<defs>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfae9c"/><stop offset="1" stop-color="#d4c6b6"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8cfc3"/><stop offset="1" stop-color="#e6ded3"/></linearGradient>
<linearGradient id="front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2d5c3"/><stop offset="1" stop-color="#d3c3ae"/></linearGradient>
<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf9f6"/><stop offset="1" stop-color="#ebe6df"/></linearGradient>
<linearGradient id="brass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8f6a2c"/><stop offset=".5" stop-color="#e2be72"/><stop offset="1" stop-color="#9b7431"/></linearGradient>
<radialGradient id="drum" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="#d9dadb"/><stop offset=".6" stop-color="#8e9092"/><stop offset="1" stop-color="#3b3d3f"/></radialGradient>
<filter id="glow" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur stdDeviation="18"/></filter>
<filter id="sh" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000" flood-opacity=".18"/></filter>
</defs>''')

# ---------- ЛІВА ЧАСТИНА: кімната ----------
a(f'<rect width="1040" height="{H}" fill="url(#wall)"/>')
a(f'<rect x="0" y="{FLOOR}" width="1040" height="{H-FLOOR}" fill="url(#floor)"/>')
a(f'<rect x="{X(2000)}" y="0" width="{1040-X(2000)}" height="{H}" fill="#b3a08c"/>')  # правий кут/стіна

# Ширина стіни
dim_h(X(0), X(2000), 50, "200 см", "(загальна ширина стіни)", size=30)

# Дзеркало по осі чаші (800 мм)
mx1, mx2, my1, my2 = X(150), X(1450), 110, 400
a(f'<rect x="{mx1}" y="{my1}" width="{mx2-mx1}" height="{my2-my1}" rx="4" fill="#ffd98a" opacity=".85" filter="url(#glow)"/>')
a(f'<rect x="{mx1}" y="{my1}" width="{mx2-mx1}" height="{my2-my1}" rx="3" fill="#9f9184" stroke="#efe2c9" stroke-width="3"/>')
a(f'<rect x="{mx1+40}" y="{my1+30}" width="{mx2-mx1-80}" height="{my2-my1-30}" fill="#a99a8b"/>')
a(f'<rect x="{X(650)}" y="{my1+55}" width="{X(950)-X(650)}" height="{my2-my1-55}" fill="#c1b3a3" stroke="#d8ccbd" stroke-width="6"/>')

# Тумба: ніжки 100, корпус 730, стільниця 20
leg, body, top = 100, 730, 20
for xm in (30, 1170):
    a(f'<rect x="{X(xm)-4}" y="{Y(leg)}" width="9" height="{leg*S}" fill="url(#brass)"/>')
a(f'<rect x="{X(0)}" y="{Y(leg+body)}" width="{1200*S}" height="{body*S}" fill="#cbb9a2" filter="url(#sh)"/>')
g = 3  # зазор, мм
def front(x1, x2, y1, y2):
    a(f'<rect x="{X(x1)}" y="{Y(y2)}" width="{(x2-x1)*S}" height="{(y2-y1)*S}" fill="url(#front)" stroke="#bda98f" stroke-width="1.5"/>')
fb, ft = leg + 2, leg + body - 2
# фасади вкладні між боковинами (18 мм), як у spec.md
fb, ft = leg + 1, leg + 727
front(20, 417, fb, ft)                             # кошик 397 x 726
front(420, 1180, fb, fb + 423)                     # нижня шухляда 760 x 423
front(420, 1180, fb + 426, ft)                     # верхня шухляда 760 x 300
for (h1, h2) in ((20, 417), (420, 1180)):          # фрезерована ручка 45° по верхньому торцю
    a(f'<rect x="{X(h1)}" y="{Y(ft)}" width="{(h2-h1)*S}" height="5" fill="#a8957c"/>')
a(f'<rect x="{X(420)}" y="{Y(fb+426)}" width="{760*S}" height="5" fill="#a8957c"/>')
# стільниця
a(f'<rect x="{X(-5)}" y="{Y(leg+body+top)}" width="{1210*S}" height="{top*S+1}" fill="url(#top)" stroke="#d8d1c7"/>')
# чаша (прихована, пунктир) та вісь
cx = X(800)
a(f'<path d="M{X(550)},{Y(leg+body)} v{20} q0,{38} 30,{40} h{(X(1050)-X(550))-60} q30,-2 30,-40 v-20" fill="none" stroke="#7d6a55" stroke-width="2" stroke-dasharray="7 5"/>')
a(f'<line x1="{cx}" y1="{Y(leg+body+top)-80}" x2="{cx}" y2="{Y(leg)-6}" stroke="#c0392b" stroke-width="1.8" stroke-dasharray="10 6"/>')
# змішувач
a(f'<rect x="{cx-8}" y="{Y(leg+body+top)-62}" width="16" height="62" rx="3" fill="url(#brass)"/>')
a(f'<rect x="{cx-8}" y="{Y(leg+body+top)-62}" width="30" height="11" rx="3" fill="url(#brass)"/>')
a(f'<ellipse cx="{cx}" cy="{Y(leg+body+top)}" rx="18" ry="4" fill="#9b7431"/>')
# декор
a(f'<path d="M{X(110)},{Y(leg+body+top)} c-8,-30 -8,-60 5,-80 h36 c13,20 13,50 5,80 z" fill="#efe9e1" stroke="#cfc6ba"/>')
for i, (dx, dy) in enumerate([(-40, -150), (-10, -175), (25, -160), (55, -130), (-60, -115)]):
    a(f'<path d="M{X(130)},{Y(leg+body+top)-78} q{dx/2},{dy/2} {dx},{dy}" stroke="#6b7a4a" stroke-width="3" fill="none"/>')
    a(f'<ellipse cx="{X(130)+dx}" cy="{Y(leg+body+top)-78+dy}" rx="11" ry="5" fill="#7d8c56" transform="rotate({-40+i*20} {X(130)+dx} {Y(leg+body+top)-78+dy})"/>')

# Пральна машина 600 (Ш) × 850 (В)
wx1, wx2 = X(1210), X(1800)
wy1 = Y(850)
a(f'<rect x="{wx1}" y="{wy1}" width="{wx2-wx1}" height="{850*S}" rx="6" fill="#f5f5f3" stroke="#d9d9d6" stroke-width="2" filter="url(#sh)"/>')
a(f'<line x1="{wx1}" y1="{wy1+62}" x2="{wx2}" y2="{wy1+62}" stroke="#dcdcd8" stroke-width="2"/>')
a(f'<rect x="{wx1+20}" y="{wy1+15}" width="70" height="30" rx="3" fill="#e2e2df"/>')
a(f'<circle cx="{wx1+150}" cy="{wy1+31}" r="17" fill="#e8e8e5" stroke="#bdbdba" stroke-width="2"/>')
a(f'<rect x="{wx1+195}" y="{wy1+15}" width="80" height="32" rx="3" fill="#2c2c2c"/>')
dcx, dcy = (wx1+wx2)/2, wy1 + 62 + (850*S-62)/2 + 5
a(f'<circle cx="{dcx}" cy="{dcy}" r="112" fill="#e9e9e6" stroke="#cfcfcb" stroke-width="3"/>')
a(f'<circle cx="{dcx}" cy="{dcy}" r="92" fill="#2a2a2a"/>')
a(f'<circle cx="{dcx}" cy="{dcy}" r="76" fill="url(#drum)"/>')

# Зона комунікацій 120 мм
a(f'<rect x="{X(1880)}" y="{Y(850)}" width="{120*S}" height="{850*S}" fill="#a8977f" opacity=".55"/>')
for k in range(0, 850, 40):
    a(f'<line x1="{X(1880)}" y1="{Y(k)}" x2="{X(2000)}" y2="{Y(k+60)}" stroke="#8d7c66" stroke-width="1"/>')

# Розміри фронтального вигляду
ytop = Y(leg+body+top)
dim_h(X(0), X(1200), ytop - 105, "120 см", "(стільниця з тумбою)", size=24)
dim_h(X(400), X(800), ytop - 45, "40 см", size=18, color="#c0392b")
dim_h(X(800), X(1200), ytop - 45, "40 см", size=18, color="#c0392b")
a(f'<rect x="{cx-150}" y="{ytop-170}" width="300" height="28" rx="14" fill="#fff" opacity=".9"/>')
a(f'<text x="{cx}" y="{ytop-150}" font-size="17" font-weight="700" text-anchor="middle" fill="#c0392b">вісь чаші — центр шухляд</text>')
dim_h(X(1210), X(1800), wy1 - 30, "60 см", "(пральна машина)", size=22)
dim_h(X(1800), X(1880), wy1 - 30, "8", size=15)
a(f'<text x="{X(1840)}" y="{wy1-62}" font-size="13" text-anchor="middle" fill="{INK}">запас</text>')
dim_h(X(1880), X(2000), wy1 - 125, "12 см", "(комунікації)", size=20)
# підписи секцій на фасадах
yb = Y(leg + 380)
dim_h(X(15), X(385), yb, "40 см", "(кошик)", size=26)
dim_h(X(415), X(1185), Y(leg+230), "80 см", "(2 шухляди)", size=26)
# висоти
dim_v(X(0) - 28, Y(leg+body+top), Y(0), "85 см", size=22)
dim_v(X(0) - 5 + 30, Y(leg), Y(0), "", size=1)
a(f'<text x="{X(0)+42}" y="{Y(40)}" font-size="20" font-weight="700" fill="{INK}">10 см</text>')

# ---------- ПРАВА ПАНЕЛЬ ----------
PX = 1060
a(f'<rect x="1040" y="0" width="{W-1040}" height="{H}" fill="#f6f1ea"/>')
a(f'<text x="{PX+238}" y="40" font-size="23" font-weight="700" text-anchor="middle" fill="{INK}">Стільниця з чашею Boat 500 <tspan font-weight="400" font-size="18">(зверху)</tspan></text>')
# стільниця вид зверху 1200 × 530
s2 = 0.35
tx0, ty0 = PX + 30, 105
def TX(mm): return tx0 + mm * s2
def TY(mm): return ty0 + mm * s2      # від задньої крайки
a(f'<rect x="{TX(0)}" y="{TY(0)}" width="{1200*s2}" height="{530*s2}" fill="#fbf9f6" stroke="{INK}" stroke-width="2"/>')
a(f'<rect x="{TX(540)}" y="{TY(110)}" width="{520*s2}" height="{365*s2}" fill="#eef2ef" stroke="#2f5a46" stroke-width="2" stroke-dasharray="6 4"/>')
a(f'<rect x="{TX(550)}" y="{TY(120)}" width="{500*s2}" height="{345*s2}" rx="8" fill="#e3ebe6" stroke="#2f5a46" stroke-width="2"/>')
a(f'<circle cx="{TX(800)}" cy="{TY(120+345/2)}" r="7" fill="none" stroke="#2f5a46" stroke-width="2"/>')
a(f'<rect x="{TX(800)-4}" y="{TY(35)}" width="8" height="22" rx="2" fill="url(#brass)"/>')
a(f'<line x1="{TX(800)}" y1="{TY(-20)}" x2="{TX(800)}" y2="{TY(560)}" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="8 5"/>')
dim_h(TX(0), TX(1200), ty0 - 22, "1200", size=15)
dim_h(TX(0), TX(540), TY(530) + 26, "540", size=15, color="#c0392b")
dim_h(TX(540), TX(1060), TY(530) + 26, "виріз 520", size=15, color="#c0392b")
dim_h(TX(1060), TX(1200), TY(530) + 26, "140", size=15, color="#c0392b")
dim_h(TX(0), TX(800), TY(530) + 62, "вісь зливу 800 (було 880)", size=15, color="#c0392b")
for (d1, d2, lab) in ((0, 110, "110"), (110, 475, "365"), (475, 530, "55")):
    dim_v(TX(0) - 10, TY(d1), TY(d2), "", size=1)
    a(f'<text x="{TX(0)-17}" y="{(TY(d1)+TY(d2))/2+5}" font-size="13" font-weight="700" text-anchor="end" fill="{INK}">{lab}</text>')

# Розподіл модулів
my = 395
a(f'<text x="{PX+238}" y="{my}" font-size="21" font-weight="700" text-anchor="middle" fill="{INK}">Розподіл модулів <tspan font-weight="400" font-size="17">(фронтальний вигляд)</tspan></text>')
mx0, ms = PX + 12, 0.375
def MX(mm): return mx0 + mm * ms
bt, bb = my + 45, my + 160
a(f'<rect x="{MX(-3)}" y="{bt-7}" width="{1206*ms}" height="7" fill="#fbf9f6" stroke="{INK}" stroke-width="1.5"/>')
a(f'<rect x="{MX(0)}" y="{bt}" width="{400*ms}" height="{bb-bt}" fill="#e2d5c3" stroke="{INK}" stroke-width="1.5"/>')
a(f'<rect x="{MX(400)}" y="{bt}" width="{800*ms}" height="{(bb-bt)*0.36}" fill="#e2d5c3" stroke="{INK}" stroke-width="1.5"/>')
a(f'<rect x="{MX(400)}" y="{bt+(bb-bt)*0.36}" width="{800*ms}" height="{(bb-bt)*0.64}" fill="#e2d5c3" stroke="{INK}" stroke-width="1.5"/>')
a(f'<path d="M{MX(700)},{bt} v14 q0,10 10,10 h{200*ms-20} q10,0 10,-10 v-14" fill="none" stroke="#7d6a55" stroke-width="1.5" stroke-dasharray="5 4"/>')
a(f'<line x1="{MX(800)}" y1="{bt-30}" x2="{MX(800)}" y2="{bb+8}" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="7 5"/>')
a(f'<rect x="{MX(800)-3}" y="{bt-26}" width="6" height="19" rx="2" fill="url(#brass)"/>')
dim_h(MX(0), MX(400), bb + 28, "40 см", size=16)
dim_h(MX(400), MX(1200), bb + 28, "80 см", size=16)
dim_h(MX(400), MX(800), bt + 30, "40", size=13, color="#c0392b")
dim_h(MX(800), MX(1200), bt + 30, "40", size=13, color="#c0392b")
dim_h(MX(0), MX(1200), bb + 62, "120 см", size=17)

# Параметри
py = 655
a(f'<rect x="{PX}" y="{py}" width="460" height="355" rx="16" fill="#eadfd1"/>')
a(f'<text x="{PX+22}" y="{py+38}" font-size="23" font-weight="700" fill="{INK}">Параметри проєкту</text>')
rows = [("Загальна ширина стіни", "200 см"), ("Стільниця з тумбою", "120 см"),
        ("Пральна машина", "60 см"), ("Комунікації", "12 см"),
        ("Чаша Boat 500", "по центру шухляд"), ("Вісь чаші від лівого краю", "80 см"),
        ("Кошик для білизни", "40 см"), ("Шухляди (2 шт)", "80 см"),
        ("Стільниця (своя)", "120 × 53 × 2 см"), ("Висота тумби", "85 см (ніжки 10)")]
for i, (k, v) in enumerate(rows):
    y = py + 74 + i * 28
    hl = i in (4, 5)
    a(f'<text x="{PX+22}" y="{y}" font-size="16" fill="{"#c0392b" if hl else INK}" font-weight="{700 if hl else 400}">{k}</text>')
    wv = 10 + len(v) * 9.2
    a(f'<rect x="{PX+440-wv}" y="{y-17}" width="{wv}" height="23" rx="11" fill="{"#c0392b" if hl else "#7a5a3a"}"/>')
    a(f'<text x="{PX+440-wv/2}" y="{y}" font-size="14" font-weight="700" text-anchor="middle" fill="#fff">{v}</text>')

a(f'<text x="20" y="{H-14}" font-size="13" fill="#5f5040">Viterra · індивідуальне замовлення · тумба 120 з Boat 500 · ескіз, не в масштабі деталей</text>')
a('</svg>')

here = pathlib.Path(__file__).parent
(here / "vizual.svg").write_text("\n".join(o), encoding="utf-8")
subprocess.run(["rsvg-convert", "-o", str(here / "vizual.png"), str(here / "vizual.svg")], check=True)
print("ok")
