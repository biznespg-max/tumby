"""Деталировка подвесной тумбы с двумя ящиками под умывальник.

Система координат детали (как в ViyarPro / GibLab):
  смотрим на лицевую пласть; x - вдоль длины (l) от левого торца,
  y - вдоль ширины (w) от нижнего торца; начало - левый нижний угол.

Отверстия:
  side="face"   - в пласти (x, y), depth=None -> насквозь
  side="left"   - в левом торце (x=0), координата y
  side="right"  - в правом торце (x=l), координата y
  side="bottom" - в нижнем торце (y=0), координата x
Верхний торец для отверстий не используем (в формате GibLab он не проверен).

Кромка: edges = {"left"|"right"|"bottom"|"top": "B2"|"B08"}.
Размеры деталей - чистовые (с кромкой).
"""

from dataclasses import dataclass, field


@dataclass
class Hole:
    side: str
    x: float = 0.0
    y: float = 0.0
    d: float = 5.0
    depth: float | None = None  # None = насквозь


@dataclass
class Part:
    code: str
    name: str
    group: str
    l: float
    w: float
    t: float
    count: int = 1
    edges: dict = field(default_factory=dict)
    holes: list = field(default_factory=list)
    note: str = ""


def _all_edges(band):
    return {s: band for s in ("left", "right", "bottom", "top")}


def build(c):
    t = c["t"]
    W, H, D = c["width"], c["height"], c["depth"]
    iw = W - 2 * t                     # внутренняя ширина корпуса
    fd, ed, edp = c["conf_face_d"], c["conf_edge_d"], c["conf_edge_depth"]

    def face(x, y):
        return Hole("face", x, y, fd, None)

    def edge(side, pos):
        if side == "bottom":
            return Hole("bottom", x=pos, d=ed, depth=edp)
        return Hole(side, y=pos, d=ed, depth=edp)

    parts = []
    half = t / 2

    # ------------------------------------------------------------------ корпус
    bottom_conf = [50, D / 2, D - 50]          # по глубине, от переднего края
    rail_f = c["front_rail_depth"]
    front_rail_conf = [30, rail_f - 30]
    rt_h = c["rear_top_rail_h"]
    rt_y0 = H - rt_h                           # низ задней верхней царги
    rt_conf = [30, rt_h - 30]
    rb_h = c["rear_bottom_rail_h"]
    rb_conf = [27, rb_h - 23]
    rear_x = D - half                          # ось задних царг на боковине
    rail_bottom_x = [100, iw / 2, iw - 100]    # конфирматы дно -> задняя нижняя царга

    side_holes = (
        [face(z, half) for z in bottom_conf]
        + [face(z, H - half) for z in front_rail_conf]
        + [face(rear_x, rt_y0 + y) for y in rt_conf]
        + [face(rear_x, t + y) for y in rb_conf]
    )
    parts.append(Part("K1", "Боковина", "Корпус", D, H, t, 2,
                      {"left": "B2", "right": "B08", "bottom": "B08", "top": "B08"},
                      side_holes,
                      "x - глубина от переднего торца, y - высота от низа. Левая и правая одинаковые."))

    parts.append(Part("K2", "Дно", "Корпус", iw, D, t, 1,
                      {"bottom": "B2", "left": "B08", "right": "B08", "top": "B08"},
                      [edge("left", z) for z in bottom_conf]
                      + [edge("right", z) for z in bottom_conf]
                      + [face(x, D - half) for x in rail_bottom_x],
                      "Нижний торец (y=0) - передний."))

    parts.append(Part("K3", "Царга передняя верхняя", "Корпус", iw, rail_f, t, 1,
                      {"bottom": "B2", "left": "B08", "right": "B08", "top": "B08"},
                      [edge("left", y) for y in front_rail_conf]
                      + [edge("right", y) for y in front_rail_conf],
                      "Лежит плашмя под умывальником, нижний торец - передний."))

    parts.append(Part("K4", "Царга задняя верхняя", "Корпус", iw, rt_h, t, 1,
                      _all_edges("B08"),
                      [edge("left", y) for y in rt_conf] + [edge("right", y) for y in rt_conf],
                      "Стоит вертикально заподлицо с задним краем. Через неё тумба крепится к стене."))

    parts.append(Part("K5", "Царга задняя нижняя", "Корпус", iw, rb_h, t, 1,
                      _all_edges("B08"),
                      [edge("left", y) for y in rb_conf] + [edge("right", y) for y in rb_conf]
                      + [edge("bottom", x) for x in rail_bottom_x],
                      "Стоит вертикально на дне, заподлицо с задним краем."))

    # ------------------------------------------------------------------ ящики
    L = c["drawer_len"]
    wi = iw - c["drawer_inner_deduct"]         # внутренняя ширина короба
    rec = c["drawer_bottom_recess"]
    yb = rec + half                            # ось дна короба на боковине
    front_bottom_conf = [100, wi / 2, wi - 100]

    def box_side_holes(h, bottom_xs, back_x=L - half):
        ys = [30, h - 30] if h <= 150 else [35, h - 35]
        return ys, ([face(half, y) for y in ys] + [face(back_x, y) for y in ys]
                    + [face(x, yb) for x in bottom_xs])

    # --- нижний ящик: обычный короб
    hb = c["drawer_bottom_box_h"]
    bot_depth = L - 2 * t
    bot_xs = [60, L / 2, L - 60]
    ys, holes = box_side_holes(hb, bot_xs)
    edges_box = {"top": "B2", "left": "B08", "right": "B08", "bottom": "B08"}
    parts.append(Part("N1", "Боковина ящика", "Нижний ящик", L, hb, t, 2, edges_box, holes,
                      "x - от переднего торца короба."))
    parts.append(Part("N2", "Передняя стенка ящика", "Нижний ящик", wi, hb, t, 1, edges_box,
                      [edge("left", y) for y in ys] + [edge("right", y) for y in ys]
                      + [face(x, yb) for x in front_bottom_conf],
                      "К ней изнутри крепится фасад."))
    parts.append(Part("N3", "Задняя стенка ящика", "Нижний ящик", wi, hb, t, 1, edges_box,
                      [edge("left", y) for y in ys] + [edge("right", y) for y in ys],
                      "Отверстия под задние крючки направляющих - по шаблону Muller при сборке."))
    parts.append(Part("N4", "Дно ящика", "Нижний ящик", wi, bot_depth, t, 1, _all_edges("B08"),
                      [edge("left", x - t) for x in bot_xs] + [edge("right", x - t) for x in bot_xs]
                      + [edge("bottom", x) for x in front_bottom_conf],
                      "Нижний торец - передний. Поднято на 13 мм от низа боковин."))

    # --- верхний ящик: П-образный вырез под сифон
    ht = c["drawer_top_box_h"]
    uw = c["u_width"]
    zf = c["drain_from_front"] - c["siphon_clearance"]   # задняя грань передней стенки выреза
    wing_w = (wi - uw - 2 * t) / 2                        # ширина "крыла"
    lu = L - zf                                           # длина стенки выреза
    strip_d = zf - t                                      # глубина передней полосы дна
    wing_d = (L - t) - zf                                 # глубина дна крыла
    strip_x = (t + zf) / 2                                # конфирмат боковина -> передняя полоса
    wing_xs = [zf + 60, zf + wing_d - 52]                 # конфирматы в дно крыла
    uf_h = ht - (rec + t)                                 # передняя стенка выреза стоит на полосе дна
    uf_w = uw + 2 * t
    uf_ys = [25, uf_h - 24]
    uf_x0 = (wi - uf_w) / 2

    ys, holes = box_side_holes(ht, [strip_x] + wing_xs)
    parts.append(Part("V1", "Боковина ящика", "Верхний ящик (под сифон)", L, ht, t, 2, edges_box, holes,
                      "x - от переднего торца короба."))
    parts.append(Part("V2", "Передняя стенка ящика", "Верхний ящик (под сифон)", wi, ht, t, 1, edges_box,
                      [edge("left", y) for y in ys] + [edge("right", y) for y in ys]
                      + [face(x, yb) for x in front_bottom_conf],
                      "К ней изнутри крепится фасад."))
    parts.append(Part("V3", "Задняя стенка (половинка)", "Верхний ящик (под сифон)", wing_w, ht, t, 2, edges_box,
                      [edge("left", y) for y in ys] + [edge("right", y) for y in ys],
                      "Между боковиной и стенкой выреза. Отверстия под крючки направляющих - по шаблону."))
    parts.append(Part("V4", "Стенка выреза боковая", "Верхний ящик (под сифон)", lu, ht, t, 2, edges_box,
                      [face(lu - half, y) for y in ys]
                      + [face(x - zf, yb) for x in wing_xs]
                      + [edge("left", rec + t + y) for y in uf_ys],
                      "x - от переднего торца (у передней стенки выреза) к задней стенке."))
    parts.append(Part("V5", "Стенка выреза передняя", "Верхний ящик (под сифон)", uf_w, uf_h, t, 1,
                      {"top": "B2", "left": "B08", "right": "B08", "bottom": "B08"},
                      [face(half, y) for y in uf_ys] + [face(uf_w - half, y) for y in uf_ys]
                      + [edge("bottom", x) for x in (60, uf_w - 60)],
                      "Стоит на передней полосе дна, закрывает торцы боковых стенок выреза."))
    parts.append(Part("V6", "Дно - передняя полоса", "Верхний ящик (под сифон)", wi, strip_d, t, 1,
                      _all_edges("B08"),
                      [edge("left", strip_x - t), edge("right", strip_x - t)]
                      + [edge("bottom", x) for x in front_bottom_conf]
                      + [face(uf_x0 + x, strip_d - half) for x in (60, uf_w - 60)],
                      "Нижний торец - передний."))
    parts.append(Part("V7", "Дно крыла", "Верхний ящик (под сифон)", wing_w, wing_d, t, 2,
                      _all_edges("B08"),
                      [edge("left", x - zf) for x in wing_xs] + [edge("right", x - zf) for x in wing_xs],
                      "Нижний торец - передний (стык с передней полосой)."))

    # ------------------------------------------------------------------ фасады (МДФ)
    fw = W - 2 * c["facade_side_gap"]
    fh_total = H - c["facade_top_gap"] - c["facade_mid_gap"] - c["facade_bottom_gap"]
    fh = fh_total / 2
    facades = [
        {"code": "F1", "name": "Фасад верхнего ящика", "w": fw, "h": fh},
        {"code": "F2", "name": "Фасад нижнего ящика", "w": fw, "h": fh},
    ]

    geometry = {
        "inner_width": iw, "drawer_inner_width": wi, "drawer_outer_width": wi + 2 * t,
        "u_from": zf, "wing_w": wing_w, "facade_w": fw, "facade_h": fh,
        "top_drawer_box_bottom": c["facade_bottom_gap"] + fh + c["facade_mid_gap"] + 20,
        "bottom_drawer_box_bottom": t + 3,
    }
    return parts, facades, geometry
