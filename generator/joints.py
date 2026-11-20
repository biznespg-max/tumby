"""Сборка в 3D и перевод соединений на минификсы.

model.build() сначала размечает стыки как под конфирмат: сквозное отверстие в пласти
«хозяина» + отверстие в торце присоединяемой детали. Здесь каждая деталь ставится на своё
место в изделии (placements), стыки находятся по совпадению отверстий, и каждый стык
переделывается под минификс:

  хозяин:        глухое отверстие под шток Ø5 × 11 — с той пласти, к которой примыкает деталь;
  присоединяемая: отверстие в торце Ø8 × 34 + отверстие под эксцентрик Ø15 в пласти
                 на 24 мм от торца — с внутренней стороны изделия.

Снаружи изделия отверстий не остаётся.

Сторона пласти: "face" — лицевая (так деталь видна в ViyarPro: x вправо, y вверх),
"back" — обратная (в GibLab — отдельная операция XNC side="false", те же x/y).
Если два экземпляра одной детали требуют разной присадки, деталь разворачивается
(если присадка симметрична) или делится на зеркальную пару «Л»/«П».
"""

from dataclasses import replace

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

BOLT_D, BOLT_DEPTH = 5.0, 11.0
EDGE_D, EDGE_DEPTH = 8.0, 34.0
CAM_D, CAM_B = 15.0, 24.0


def cam_depth(t):
    return 13.5 if t >= 18 else 12.5


def add(*vs):
    return tuple(sum(c) for c in zip(*vs))


def mul(v, k):
    return tuple(c * k for c in v)


def sub(a, b):
    return tuple(p - q for p, q in zip(a, b))


def dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def close(a, b, tol=0.6):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


def placements(c, geo):
    """{узел: [(код, начало, ось x, ось y, направление толщины), ...]}.

    Мир: X - вправо (вид спереди), Y - вверх, Z - от фасада к стене.
    Начало - угол детали; деталь занимает origin + ex*[0,l] + ey*[0,w] + en*[0,t].
    """
    t, W, H, D = c["t"], c["width"], c["height"], c["depth"]
    iw, wi, L = geo["inner_width"], geo["drawer_inner_width"], c["drawer_len"]
    f0 = geo["front_offset"]
    tb = c["t_box"]
    rec, ww, zf = c["drawer_bottom_recess"], geo["wing_w"], geo["u_from"]
    if c.get("one_sided"):
        sides = [("K1Л", (0, 0, D), mul(Z, -1), Y, X),   # левая: смотрим снаружи, перед справа
                 ("K1П", (W - t, 0, 0), Z, Y, X)]         # правая: смотрим снаружи, перед слева
    else:
        sides = [("K1", (0, 0, 0), Z, Y, X), ("K1", (W - t, 0, 0), Z, Y, X)]
    corpus = sides + [
        ("K2", (t, 0, f0), X, Z, Y),
        ("K3", (t, H - c["front_rail_h"], f0), X, Y, Z),
        ("K4", (t, H - c["rear_top_rail_h"], D - t), X, Y, Z),
        ("K5", (t, t + c.get("rear_bottom_rail_lift", 0), D - t), X, Y, Z),
    ]
    t = tb
    uf_w = geo.get("u_width", c["u_width"]) + 2 * t
    uf_x0 = (wi - uf_w) / 2
    wo = wi + 2 * t
    bottom_box = [
        ("N1", (0, 0, 0), Z, Y, X), ("N1", (wo - t, 0, 0), Z, Y, X),
        ("N2", (t, 0, 0), X, Y, Z), ("N3", (t, 0, L - t), X, Y, Z),
        ("N4", (t, rec, t), X, Z, Y),
    ]
    bw = geo["wing_w"]
    top_box = [
        ("V1", (0, 0, 0), Z, Y, X), ("V1", (wo - t, 0, 0), Z, Y, X),
        ("V2", (t, 0, 0), X, Y, Z),
        ("V3Л", (t, 0, L - t), X, Y, Z), ("V3П", (t + wi - bw, 0, L - t), X, Y, Z),
        ("V4", (t, rec, L - t), X, mul(Z, -1), Y),
    ]
    return {"Корпус": corpus, "Нижний ящик": bottom_box, "Верхний ящик": top_box}


def face_normal(ex, ey):
    """Нормаль лицевой пласти (к зрителю, который видит x вправо, y вверх)."""
    return cross(ey, ex)


def hole_point(part, inst, h):
    """Точка отверстия на средней плоскости детали."""
    code, o, ex, ey, en = inst
    mid = add(o, mul(en, part.t / 2))
    if h.side in ("face", "back"):
        return add(mid, mul(ex, h.x), mul(ey, h.y))
    if h.side == "left":
        return add(mid, mul(ey, h.y))
    if h.side == "right":
        return add(mid, mul(ex, part.l), mul(ey, h.y))
    if h.side == "bottom":
        return add(mid, mul(ex, h.x))
    raise ValueError(h.side)


def _box_center(parts_by_code, unit):
    pts = []
    for inst in unit:
        p = parts_by_code[inst[0]]
        _, o, ex, ey, en = inst
        for a in (0, p.l):
            for b in (0, p.w):
                for d in (0, p.t):
                    pts.append(add(o, mul(ex, a), mul(ey, b), mul(en, d)))
    return tuple((min(v) + max(v)) / 2 for v in zip(*pts))


def _inst_center(part, inst):
    _, o, ex, ey, en = inst
    return add(o, mul(ex, part.l / 2), mul(ey, part.w / 2), mul(en, part.t / 2))


def _key(holes):
    return sorted((h.side, round(h.x, 1), round(h.y, 1), h.d, h.depth) for h in holes)


def _mirror(part, holes):
    """Отверстия той же детали, развёрнутой на 180° вокруг вертикали (x -> l - x, лицо <-> изнанка)."""
    out = []
    for h in holes:
        if h.side in ("face", "back"):
            out.append(replace(h, side="back" if h.side == "face" else "face", x=part.l - h.x))
        elif h.side == "left":
            out.append(replace(h, side="right"))
        elif h.side == "right":
            out.append(replace(h, side="left"))
        else:
            out.append(replace(h, x=part.l - h.x))
    return out


def apply_minifix(c, parts, geo, fixed_face=()):
    """Переводит стыки на минификсы. Возвращает (новые детали, узлы с экземплярами).

    fixed_face - коды деталей, которые нельзя разворачивать лицом внутрь (односторонний декор).
    """
    by_code = {p.code: p for p in parts}
    units = placements(c, geo)
    new_holes = {}                       # (узел, № экземпляра) -> список отверстий в системе экземпляра

    for uname, unit in units.items():
        center = _box_center(by_code, unit)
        per_inst = {i: [] for i in range(len(unit))}
        edge_pts = []
        for i, inst in enumerate(unit):
            p = by_code[inst[0]]
            for h in p.holes:
                if h.side not in ("face", "back"):
                    edge_pts.append((i, h, hole_point(p, inst, h)))
        used = set()
        for i, inst in enumerate(unit):
            p = by_code[inst[0]]
            n = face_normal(inst[2], inst[3])
            for h in p.holes:
                if h.side not in ("face", "back"):
                    continue
                pt = hole_point(p, inst, h)
                hit = None
                for k, (j, eh, ept) in enumerate(edge_pts):
                    if j != i and any(close(ept, add(pt, mul(n, s * p.t / 2))) for s in (1, -1)):
                        hit = k
                        break
                if hit is None:
                    raise ValueError(f"{uname}: {p.code} отверстие ({h.x}, {h.y}) без пары в торце")
                used.add(hit)
                j, eh, ept = edge_pts[hit]
                side = "face" if dot(sub(ept, pt), n) > 0 else "back"
                per_inst[i].append(replace(h, side=side, d=BOLT_D, depth=BOLT_DEPTH))
        for k, (j, eh, ept) in enumerate(edge_pts):
            if k not in used:
                raise ValueError(f"{uname}: {unit[j][0]} отверстие в торце {eh.side} без пары в пласти")
            inst = unit[j]
            p = by_code[inst[0]]
            n = face_normal(inst[2], inst[3])
            cam_side = "face" if dot(sub(center, _inst_center(p, inst)), n) > 0 else "back"
            per_inst[j].append(replace(eh, d=EDGE_D, depth=EDGE_DEPTH))
            if eh.side == "left":
                cx, cy = CAM_B, eh.y
            elif eh.side == "right":
                cx, cy = p.l - CAM_B, eh.y
            else:
                cx, cy = eh.x, CAM_B
            per_inst[j].append(type(eh)(cam_side, cx, cy, CAM_D, cam_depth(p.t)))
        for i in per_inst:
            new_holes[(uname, i)] = per_inst[i]

    # согласование экземпляров одной детали
    out_parts, final_units = [], {u: list(v) for u, v in units.items()}
    done = set()
    for p in parts:
        insts = [(u, i) for u, unit in units.items() for i, inst in enumerate(unit) if inst[0] == p.code]
        if not insts:
            out_parts.append(p)                      # фасады и т.п. - без присадки
            continue
        if p.code in done:
            continue
        done.add(p.code)
        groups = []                                  # [(отверстия, [(u, i, развернуть?)])]
        for (u, i) in insts:
            hs = new_holes[(u, i)]
            for g in groups:
                if _key(g[0]) == _key(hs):
                    g[1].append((u, i, False))
                    break
                if p.code not in fixed_face and _key(g[0]) == _key(_mirror(p, hs)):
                    g[1].append((u, i, True))
                    break
            else:
                groups.append((hs, [(u, i, False)]))
        for (u, i, flip) in (m for g in groups for m in g[1]):
            if flip:
                code, o, ex, ey, en = final_units[u][i]
                final_units[u][i] = (code, add(o, mul(ex, p.l), mul(en, p.t)), mul(ex, -1), ey, mul(en, -1))
        if len(groups) == 1:
            out_parts.append(replace(p, holes=groups[0][0], count=len(insts)))
            continue
        # зеркальная пара: левая - экземпляр с меньшим X
        def xpos(m):
            u, i, _ = m
            return _inst_center(p, final_units[u][i])[0]
        groups.sort(key=lambda g: min(xpos(m) for m in g[1]))
        for g, suffix, side_name in zip(groups, ("Л", "П"), ("левая", "правая")):
            code = p.code + suffix
            out_parts.append(replace(p, code=code, name=f"{p.name} ({side_name})", holes=g[0], count=len(g[1])))
            for (u, i, _) in g[1]:
                final_units[u][i] = (code,) + final_units[u][i][1:]
        if len(groups) > 2:
            raise ValueError(f"{p.code}: больше двух вариантов присадки")
    return out_parts, final_units
