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
    material: str = "box"


def _all_edges(band):
    return {s: band for s in ("left", "right", "bottom", "top")}


def build(c):
    t = c["t"]
    W, H, D = c["width"], c["height"], c["depth"]
    iw = W - 2 * t                     # внутренняя ширина корпуса
    max_w = c["runner_max_width"]
    if c.get("runner_two_l_rule", True):
        max_w = min(max_w, 2 * c["runner_nl"])
    if W > max_w:
        raise ValueError(f"Корпус {W} мм шире допустимого для направляющих L={c['runner_nl']} "
                         f"(макс. {max_w} мм). Нужны другие направляющие или другая конструкция.")
    fd, ed, edp = c["conf_face_d"], c["conf_edge_d"], c["conf_edge_depth"]

    def face(x, y):
        return Hole("face", x, y, fd, None)

    def edge(side, pos):
        if side == "bottom":
            return Hole("bottom", x=pos, d=ed, depth=edp)
        return Hole(side, y=pos, d=ed, depth=edp)

    parts = []
    half = t / 2
    cb = c.get("corpus_band")                  # кромка корпуса и фасадов (None - МДФ под покраску)
    ce = _all_edges(cb) if cb else {}

    # ------------------------------------------------------------------ корпус
    f0 = c["facade_t"] if c.get("facade_inset") else 0   # вкладные фасады: дно и царга K3 отступают на толщину фасада
    Db = D - f0                                # глубина дна
    bottom_conf = [f0 + 50, f0 + Db / 2, D - 50]   # по глубине боковины, от её переднего торца
    f0s = bool(c.get("f0_structural") and c.get("facade_panel_h"))   # царга-фасад F0 сама связывает боковины (как у Mirater «Естель»), K3 нет
    rail_f = c["front_rail_h"]
    rail_f_y0 = H - rail_f                     # низ передней верхней царги
    front_rail_conf = [20, rail_f - 20]
    rt_h = c["rear_top_rail_h"]
    rt_y0 = H - rt_h                           # низ задней верхней царги
    rt_conf = [30, rt_h - 30]
    rb_h = c["rear_bottom_rail_h"]
    rb_conf = [27, rb_h - 23]
    rb_lift = c.get("rear_bottom_rail_lift", 0)  # K5 поднята над дном: под ней проходят направляющие
    min_depth = c.get("runner_min_depth")
    if min_depth:
        free = D - f0 - (0 if rb_lift else t)
        if free < min_depth:
            raise ValueError(f"Глубина под направляющие {free} мм < {min_depth} мм (мин. по направляющим)")
    rear_x = D - half                          # ось задних царг на боковине
    rail_bottom_x = [100, iw / 2, iw - 100]    # конфирматы дно -> задняя нижняя царга

    ph0 = c.get("facade_panel_h", 0)
    f0_y0 = H - c["facade_top_gap"] - ph0                 # низ царги-фасада F0
    f0_conf = [25, ph0 - 25]
    side_holes = (
        [face(z, half) for z in bottom_conf]
        + ([] if f0s else [face(f0 + half, rail_f_y0 + y) for y in front_rail_conf])
        + [face(rear_x, rt_y0 + y) for y in rt_conf]
        + [face(rear_x, t + rb_lift + y) for y in rb_conf]
    )
    mr = c.get("mid_rail")          # средняя царга K3 лёжа между ящиками: {"y": низ, "depth": глубина}
    if mr:
        mr_conf = [30, mr["depth"] - 30]
        side_holes = side_holes + [face(f0 + z, mr["y"] + half) for z in mr_conf]
    if f0s:   # стык с F0: торец боковины (передний, x=0) -> пласть F0 (шток в F0)
        side_holes = side_holes + [edge("left", f0_y0 + y) for y in f0_conf]
    if c.get("one_sided"):
        # односторонний материал: лицевая сторона наружу, поэтому боковины зеркальные
        mirrored = [Hole(h.side, D - h.x, h.y, h.d, h.depth) for h in side_holes]
        parts.append(Part("K1Л", "Боковина левая", "Корпус", D, H, t, 1, dict(ce), mirrored,
                          "Лицом (декор) наружу. Смотрим снаружи: передний торец справа.", "corpus"))
        parts.append(Part("K1П", "Боковина правая", "Корпус", D, H, t, 1, dict(ce), side_holes,
                          "Лицом (декор) наружу. Смотрим снаружи: передний торец слева.", "corpus"))
    else:
        parts.append(Part("K1", "Боковина", "Корпус", D, H, t, 2,
                          dict(ce), side_holes,
                          "x - глубина от переднего торца, y - высота от низа. Левая и правая одинаковые.", "corpus"))

    bm = c.get("bottom_material", "corpus")
    be = _all_edges(c["bottom_band"]) if c.get("bottom_band") else dict(ce)
    parts.append(Part("K2", "Дно", "Корпус", iw, Db, t, 1, be,
                      [edge("left", z - f0) for z in bottom_conf]
                      + [edge("right", z - f0) for z in bottom_conf]
                      + ([] if rb_lift else [face(x, Db - half) for x in rail_bottom_x]),
                      "Нижний торец (y=0) - передний."
                      + (f" Отступает от переднего края боковин на {f0} мм (за фасадом)." if f0 else "")
                      + (" Лицом (декор) вниз." if c.get("one_sided") and bm == "corpus" else ""), bm))

    if mr:
        parts.append(Part("K3", "Царга средняя (лежит между ящиками)", "Корпус", iw, mr["depth"], t, 1, dict(ce),
                          [edge("left", z) for z in mr_conf] + [edge("right", z) for z in mr_conf],
                          f"Лежит горизонтально между ящиками, низ на {mr['y']} мм от низа корпуса, передний торец "
                          "заподлицо с передним краем боковин. Нижний торец (y=0) - передний. Связывает боковины посередине.", "corpus"))
    if not f0s and not mr:
        parts.append(Part("K3", "Царга передняя верхняя", "Корпус", iw, rail_f, t, 1, dict(ce),
                        [edge("left", y) for y in front_rail_conf]
                        + [edge("right", y) for y in front_rail_conf],
                        ("Стоит на ребре" + (f" с отступом {f0} мм от переднего края боковин (за вкладным фасадом)" if f0 else " заподлицо с передним краем")
                         + ", верхний торец - под умывальником. Закрыта фасадом."), "corpus"))

    parts.append(Part("K4", "Царга задняя верхняя", "Корпус", iw, rt_h, t, 1, dict(ce),
                      [edge("left", y) for y in rt_conf] + [edge("right", y) for y in rt_conf],
                      "Стоит вертикально заподлицо с задним краем. Через неё тумба крепится к стене.", "corpus"))

    parts.append(Part("K5", "Царга задняя нижняя", "Корпус", iw, rb_h, t, 1, dict(ce),
                      [edge("left", y) for y in rb_conf] + [edge("right", y) for y in rb_conf]
                      + ([] if rb_lift else [edge("bottom", x) for x in rail_bottom_x]),
                      (f"Стоит вертикально заподлицо с задним краем, поднята на {rb_lift} мм над дном "
                       "(под ней проходят задние концы направляющих)." if rb_lift
                       else "Стоит вертикально на дне, заподлицо с задним краем."), "corpus"))

    # ------------------------------------------------------------------ ящики
    t = c["t_box"]
    half = t / 2
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
                      "Отверстия под задние крючки направляющих - по шаблону из инструкции направляющих."))
    parts.append(Part("N4", "Дно ящика", "Нижний ящик", wi, bot_depth, t, 1, _all_edges("B08"),
                      [edge("left", x - t) for x in bot_xs] + [edge("right", x - t) for x in bot_xs]
                      + [edge("bottom", x) for x in front_bottom_conf],
                      "Нижний торец - передний. Поднято на 13 мм от низа боковин."))

    # --- верхний ящик: обычный короб + П-образный вырез с полукругом под ограничитель сифона
    # (Mesan W=160 L=245 H=86 R=80, ВіЯр 228527 белый). Вырез в дне V4 - от задней стенки вперёд,
    # фрезеруется в ViyarPro («Виріз за шаблоном»); в задней стенке - щель на всю высоту,
    # поэтому задняя стенка из двух половинок V3Л/V3П (каждая >= 200 мм - ViyarPro сверлит от 200).
    ht = c["drawer_top_box_h"]
    min_drill = c.get("min_drill_len", 200)
    lim_w, lim_l, lim_r = c.get("siphon_limiter_w", 160), c.get("siphon_cut_len", 250), c.get("siphon_limiter_w", 160) / 2
    slot = min(lim_w, wi - 2 * min_drill)                 # щель в задней стенке
    if slot < 90:
        raise ValueError(f"Щель под трубу сифона {slot} мм - слишком узкая (короб {wi} мм)")
    bw = (wi - slot) / 2                                  # половинка задней стенки
    wd = L - 2 * t                                        # дно между передней и задней стенками
    zs = [60, L / 2, L - 60]                              # стыки дна с боковинами (z от переда короба)
    ys, holes = box_side_holes(ht, zs)
    parts.append(Part("V1", "Боковина ящика", "Верхний ящик (под сифон)", L, ht, t, 2, edges_box, holes,
                      "x - от переднего торца короба."))
    parts.append(Part("V2", "Передняя стенка ящика", "Верхний ящик (под сифон)", wi, ht, t, 1, edges_box,
                      [edge("left", y) for y in ys] + [edge("right", y) for y in ys],
                      "К ней изнутри крепится фасад."))
    parts.append(Part("V3Л", "Задняя стенка (левая половинка)", "Верхний ящик (под сифон)", bw, ht, t, 1, edges_box,
                      [edge("left", y) for y in ys] + [face(bw / 2, yb)],
                      f"Между левой боковиной и щелью {slot:g} мм под трубу сифона. Отверстия под крючки направляющих - по шаблону."))
    parts.append(Part("V3П", "Задняя стенка (правая половинка)", "Верхний ящик (под сифон)", bw, ht, t, 1, edges_box,
                      [edge("right", y) for y in ys] + [face(bw / 2, yb)],
                      f"Между щелью {slot:g} мм и правой боковиной. Отверстия под крючки направляющих - по шаблону."))
    back = (L - t)                                        # z задней грани дна
    parts.append(Part("V4", "Дно ящика с вырезом под сифон", "Верхний ящик (под сифон)", wi, wd, t, 1, _all_edges("B08"),
                      [edge("left", back - z) for z in zs] + [edge("right", back - z) for z in zs]
                      + [edge("bottom", bw / 2), edge("bottom", wi - bw / 2)],
                      f"Нижний торец (y=0) - ЗАДНИЙ. ВЫРЕЗ (фрезеровать в ViyarPro): от заднего торца по центру, "
                      f"ширина {lim_w:g}, глубина {lim_l:g} мм, передний край - полукруг R{lim_r:g} "
                      f"(центр дуги {lim_l - lim_r:g} мм от заднего торца). Под ограничитель сифона Mesan W160 R80."))
    zf = back - lim_l                                     # передний край выреза от переда короба
    wing_w = bw
    uw = lim_w

    # ------------------------------------------------------------------ фасады (МДФ)
    inset = bool(c.get("facade_inset"))
    fw = (iw if inset else W) - 2 * c["facade_side_gap"]
    fx = (t if inset else 0) + c["facade_side_gap"]   # левый край фасада от левого края корпуса
    ph = c.get("facade_panel_h", 0)            # фальш-панель (0 - без неё)
    gaps = c["facade_top_gap"] + c["facade_bottom_gap"] + c["facade_mid_gap"] * (2 if ph else 1)
    usable = H - gaps - ph
    fh_bot = c.get("facade_bottom_h") or usable / 2   # нижний фасад (верхний - остаток)
    fh = usable - fh_bot                       # верхний фасад
    facades = []
    if ph:
        facades.append({"code": "F0", "name": "Фальш-панель (неподвижная, на царгу K3)", "w": fw, "h": ph})
    facades += [
        {"code": "F1", "name": "Фасад верхнего ящика", "w": fw, "h": fh},
        {"code": "F2", "name": "Фасад нижнего ящика", "w": fw, "h": fh_bot},
    ]
    y = H - c["facade_top_gap"]                # верх фасада, от низа корпуса
    for f in facades:
        f["top"] = y
        f["x"] = fx
        y -= f["h"] + c["facade_mid_gap"]
    if c.get("facades_in_cut"):                # фасады из того же листа - в файл порезки
        for f in facades:
            parts.append(Part(f["code"], f["name"], "Фасады", f["w"], f["h"], c["facade_t"], 1,
                              dict(ce), [], "Лицом (декор) наружу. Текстура вдоль длины.", "corpus"))

    if f0s:
        # F0 из ViyarFronts в файл порезки не идёт; деталь нужна только чтобы разметить стыки (шток Ø5 в изнанке F0)
        fx0 = (t if inset else 0) + c["facade_side_gap"]
        parts.append(Part("F0", "Царга-фасад", "Фасады", fw, ph, c["facade_t"], 1, {},
                          [face(c["t"] / 2 - fx0, y) for y in f0_conf] + [face(W - c["t"] / 2 - fx0, y) for y in f0_conf],
                          "", "facade"))
    geometry = {
        "inner_width": iw, "drawer_inner_width": wi, "drawer_outer_width": wi + 2 * t,
        "u_from": zf, "wing_w": wing_w, "u_width": uw, "facade_w": fw, "facade_h": fh, "front_offset": f0,
        "facade_bottom_h": fh_bot,
        "top_drawer_box_bottom": c["facade_bottom_gap"] + fh_bot + c["facade_mid_gap"] + c.get("top_box_lift", 20),
        "bottom_drawer_box_bottom": c["t"] + 3,
    }
    if f0s:
        geometry["f0_structural_pre"] = (fx0, f0_y0)
    if c.get("joint", "minifix") == "minifix":
        from . import joints
        fixed = {p.code for p in parts if p.material == "corpus"} if c.get("one_sided") else set()
        parts, geometry["units"] = joints.apply_minifix(c, parts, geometry, fixed)
    if f0s:
        f0p = next(p for p in parts if p.code == "F0")
        parts = [p for p in parts if p.code != "F0"]
        for f in facades:
            if f["code"] == "F0":
                f["name"] = "Царга-фасад (неподвижная, на минификсах к боковинам)"
                f["holes"] = f0p.holes
    geometry["f0_structural"] = f0s
    return parts, facades, geometry
