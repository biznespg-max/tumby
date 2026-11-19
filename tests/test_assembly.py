"""Виртуальная сборка: каждое отверстие под конфирмат в пласти должно
попадать в отверстие в торце соседней детали, и наоборот.

Запуск: python -m pytest tests  (или python tests/test_assembly.py)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tumba.config import CONFIG
from tumba import model

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def add(*vs):
    return tuple(sum(c) for c in zip(*vs))


def mul(v, k):
    return tuple(c * k for c in v)


def placements(c, geo):
    """(код детали, начало, ось x детали, ось y детали, нормаль) для каждого экземпляра."""
    t, W, H, D = c["t"], c["width"], c["height"], c["depth"]
    iw, wi, L = geo["inner_width"], geo["drawer_inner_width"], c["drawer_len"]
    rec, ww, zf = c["drawer_bottom_recess"], geo["wing_w"], geo["u_from"]
    uf_x0 = (wi - c["u_width"] - 2 * t) / 2
    wo = wi + 2 * t
    corpus = [
        ("K1", (0, 0, 0), Z, Y, X), ("K1", (W - t, 0, 0), Z, Y, X),
        ("K2", (t, 0, 0), X, Z, Y),
        ("K3", (t, H - t, 0), X, Z, Y),
        ("K4", (t, H - c["rear_top_rail_h"], D - t), X, Y, Z),
        ("K5", (t, t, D - t), X, Y, Z),
    ]
    bottom_box = [
        ("N1", (0, 0, 0), Z, Y, X), ("N1", (wo - t, 0, 0), Z, Y, X),
        ("N2", (t, 0, 0), X, Y, Z), ("N3", (t, 0, L - t), X, Y, Z),
        ("N4", (t, rec, t), X, Z, Y),
    ]
    top_box = [
        ("V1", (0, 0, 0), Z, Y, X), ("V1", (wo - t, 0, 0), Z, Y, X),
        ("V2", (t, 0, 0), X, Y, Z),
        ("V3", (t, 0, L - t), X, Y, Z), ("V3", (t + wi - ww, 0, L - t), X, Y, Z),
        ("V4", (t + ww, 0, zf), Z, Y, X), ("V4", (t + wi - ww - t, 0, zf), Z, Y, X),
        ("V5", (t + uf_x0, rec + t, zf - t), X, Y, Z),
        ("V6", (t, rec, t), X, Z, Y),
        ("V7", (t, rec, zf), X, Z, Y), ("V7", (t + wi - ww, rec, zf), X, Z, Y),
    ]
    return {"Корпус": corpus, "Нижний ящик": bottom_box, "Верхний ящик": top_box}


def holes_3d(part, origin, ex, ey, en):
    half = part.t / 2
    face, edge = [], []
    for h in part.holes:
        if h.side == "face":
            face.append(add(origin, mul(ex, h.x), mul(ey, h.y), mul(en, half)))
        elif h.side == "left":
            edge.append(add(origin, mul(ey, h.y), mul(en, half)))
        elif h.side == "right":
            edge.append(add(origin, mul(ex, part.l), mul(ey, h.y), mul(en, half)))
        elif h.side == "bottom":
            edge.append(add(origin, mul(ex, h.x), mul(en, half)))
    return face, edge


def close(a, b, tol=0.6):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


def check_unit(parts_by_code, unit, t):
    faces, edges = [], []
    for code, origin, ex, ey, en in unit:
        f, e = holes_3d(parts_by_code[code], origin, ex, ey, en)
        faces += [(code, p, en) for p in f]
        edges += [(code, p) for p in e]
    used = set()
    missing = []
    for code, p, en in faces:
        targets = [add(p, mul(en, t / 2)), add(p, mul(en, -t / 2))]
        hit = [i for i, (c2, e) in enumerate(edges) if c2 != code and any(close(e, q) for q in targets)]
        if not hit:
            missing.append(f"{code}: отверстие в пласти {p} никуда не попадает")
        used.update(hit)
    for i, (code, e) in enumerate(edges):
        if i not in used:
            missing.append(f"{code}: отверстие в торце {e} без ответного в пласти")
    return len(faces), missing


def test_assembly():
    parts, facades, geo = model.build(CONFIG)
    by_code = {p.code: p for p in parts}
    total = 0
    problems = []
    for name, unit in placements(CONFIG, geo).items():
        n, missing = check_unit(by_code, unit, CONFIG["t"])
        total += n
        problems += [f"[{name}] {m}" for m in missing]
    assert not problems, "\n".join(problems)
    return total


def test_fits_sink_and_runners():
    c = CONFIG
    parts, facades, geo = model.build(c)
    assert c["depth"] + c["facade_t"] <= 447, "тумба глубже умывальника"
    assert c["width"] <= 800, "тумба шире умывальника"
    inner_depth = c["depth"] - c["t"]          # до задних царг
    assert inner_depth >= c["runner_nl"] + 3, "направляющая не помещается по глубине"
    # верх короба верхнего ящика ниже чаши (чаша опускается максимум на 140 мм)
    top_box_top = geo["top_drawer_box_bottom"] + c["drawer_top_box_h"]
    assert top_box_top <= c["height"] - 140 + 10, f"короб упирается в чашу: {top_box_top}"
    # вырез под сифон перекрывает слив
    assert geo["u_from"] <= c["drain_from_front"] - 35
    # короб нижнего ящика не доходит до верхнего
    assert geo["bottom_drawer_box_bottom"] + c["drawer_bottom_box_h"] < geo["top_drawer_box_bottom"]


if __name__ == "__main__":
    n = test_assembly()
    test_fits_sink_and_runners()
    print(f"OK: {n} отверстий в пласти, все попадают в ответные отверстия в торцах; габариты в норме")
