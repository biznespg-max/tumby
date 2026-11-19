"""Виртуальная сборка на минификсах: каждый шток в пласти попадает в отверстие в торце
соседней детали, у каждого торцевого отверстия есть эксцентрик, снаружи отверстий нет.

Запуск: python -m pytest tests  (или python tests/test_assembly.py)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest

from generator import config, model

PRODUCTS = config.all_products()

from generator.joints import add, mul, sub, dot, close, face_normal, hole_point, _box_center, _inst_center


def _cfg(prod):
    return config.product_config(*prod)


@pytest.mark.parametrize("prod", PRODUCTS, ids=lambda p: f"{p[0]}-{p[1]}-{p[2]}")
def test_minifix_assembly(prod):
    """Каждый шток попадает в отверстие в торце соседней детали, у каждого торцевого отверстия
    есть эксцентрик на 24 мм, все отверстия в пласти смотрят внутрь изделия, конфирматов нет."""
    c = _cfg(prod)
    parts, facades, geo = model.build(c)
    by_code = {p.code: p for p in parts}
    problems = []
    for uname, unit in geo["units"].items():
        center = _box_center(by_code, unit)
        edges = []
        for j, inst in enumerate(unit):
            p = by_code[inst[0]]
            for h in p.holes:
                if h.side in ("left", "right", "bottom"):
                    edges.append((j, h, hole_point(p, inst, h)))
        used = set()
        for i, inst in enumerate(unit):
            p = by_code[inst[0]]
            n = face_normal(inst[2], inst[3])
            for h in p.holes:
                if h.side not in ("face", "back"):
                    continue
                assert h.depth is not None and h.depth < p.t, f"{p.code}: сквозное отверстие ({h.x}, {h.y})"
                sign = 1 if h.side == "face" else -1
                if h.d == 15:
                    continue
                pt = hole_point(p, inst, h)
                hit = [k for k, (j, eh, ept) in enumerate(edges)
                       if j != i and close(ept, add(pt, mul(n, sign * p.t / 2)))]
                if not hit:
                    problems.append(f"[{uname}] {p.code}: шток ({h.x}, {h.y}, {h.side}) никуда не попадает")
                used.update(hit)
        for k, (j, eh, ept) in enumerate(edges):
            p = by_code[unit[j][0]]
            if k not in used:
                problems.append(f"[{uname}] {p.code}: отверстие в торце {eh.side} без штока")
            if eh.side == "left":
                want = (24, eh.y)
            elif eh.side == "right":
                want = (p.l - 24, eh.y)
            else:
                want = (eh.x, 24)
            if not any(h.d == 15 and abs(h.x - want[0]) < 0.1 and abs(h.y - want[1]) < 0.1 for h in p.holes):
                problems.append(f"[{uname}] {p.code}: нет эксцентрика у торцевого отверстия {eh.side}")
    # декор: на односторонних деталях корпуса снаружи (лицевая пласть) отверстий нет
    if c.get("one_sided"):
        for code in ("K1Л", "K1П"):
            assert not [h for h in by_code[code].holes if h.side == "face"], f"{code}: отверстия на декоре"
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("prod", PRODUCTS, ids=lambda p: f"{p[0]}-{p[1]}-{p[2]}")
def test_fits_sink_and_runners(prod):
    c = _cfg(prod)
    sk = c["sink"]
    parts, facades, geo = model.build(c)
    assert c["depth"] + (0 if c.get("facade_inset") else c["facade_t"]) <= sk["depth"], "тумба глубже умывальника"
    assert c["width"] <= sk["width"], "тумба шире умывальника"
    max_w = c["runner_max_width"] if not c.get("runner_two_l_rule", True) else min(c["runner_max_width"], 2 * c["runner_nl"])
    assert c["width"] <= max_w, "направляющие не для такой ширины"
    inner_depth = c["depth"] - c["t"] - geo["front_offset"]   # от фасада до задних царг
    assert all(p.t == c["sheets"][p.material]["thickness"] for p in parts), "толщина детали не совпадает с материалом"
    if not c.get("corpus_band"):
        assert not any(p.edges for p in parts if p.material == "corpus"), "МДФ под покраску не кромкуется"
    else:
        assert all(len(p.edges) == 4 for p in parts if p.material == "corpus"), "все торцы корпуса в кромке"
    assert inner_depth >= c["runner_nl"] + 3, "направляющая не помещается по глубине"
    # верх короба верхнего ящика ниже чаши (чаша опускается максимум на 140 мм)
    top_box_top = geo["top_drawer_box_bottom"] + c["drawer_top_box_h"]
    assert top_box_top <= c["height"] - sk["height"] + 10, f"короб упирается в чашу: {top_box_top}"
    # вырез под сифон уже коробки и крылья не вырождаются
    assert geo["wing_w"] >= 100, f"крылья верхнего ящика слишком узкие: {geo['wing_w']}"
    # вырез под сифон перекрывает слив
    assert geo["u_from"] <= c["drain_from_front"] - geo["front_offset"] - 35
    # верхний ящик проходит под передней царгой (она стоит на ребре у фасада)
    assert top_box_top + 5 <= c["height"] - c["front_rail_h"], "короб верхнего ящика упирается в переднюю царгу"
    # фальш-панель держится на царге K3 (перекрытие по высоте не меньше 40 мм)
    for f in facades:
        if f["code"] == "F0":
            assert min(f["top"], c["height"]) - max(f["top"] - f["h"], c["height"] - c["front_rail_h"]) >= 40
    # короб нижнего ящика не доходит до верхнего
    assert geo["bottom_drawer_box_bottom"] + c["drawer_bottom_box_h"] < geo["top_drawer_box_bottom"]


if __name__ == "__main__":
    for prod in PRODUCTS:
        test_minifix_assembly(prod)
        test_fits_sink_and_runners(prod)
        print(f"OK {_cfg(prod)['article']}: минификсы сходятся, габариты в норме")
