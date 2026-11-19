"""Генератор тумбы для ViyarPro.

Запуск:  python generate.py
Результат в папке out/:
  tumba.project  - файл для ViyarPro (Конвертація -> GibLab)
  cutlist.csv    - таблица деталей
  spec.md        - спецификация, фурнитура, сборка
  drawing.svg    - чертёж
"""

import pathlib
import sys

from tumba.config import CONFIG
from tumba import model, giblab, outputs


def check(parts):
    """Проверка: отверстия внутри детали и не глубже детали."""
    errors = []
    for p in parts:
        for h in p.holes:
            if h.side == "face":
                r = h.d / 2
                if not (r <= h.x <= p.l - r and r <= h.y <= p.w - r):
                    errors.append(f"{p.code}: отверстие в пласти вне детали ({h.x}, {h.y})")
            else:
                pos, span, length = (h.x, p.l, p.w) if h.side == "bottom" else (h.y, p.w, p.l)
                if not (h.d / 2 <= pos <= span - h.d / 2):
                    errors.append(f"{p.code}: отверстие в торце {h.side} вне детали ({pos})")
                if h.depth >= length:
                    errors.append(f"{p.code}: отверстие в торце {h.side} глубже детали")
    return errors


def main():
    parts, facades, geo = model.build(CONFIG)
    errors = check(parts)
    if errors:
        print("ОШИБКИ:\n" + "\n".join(errors))
        sys.exit(1)

    out = pathlib.Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    bands = CONFIG["bands"]
    (out / "tumba.project").write_text(giblab.to_xml(CONFIG["name"], parts, CONFIG["sheets"], bands), encoding="utf-8")
    (out / "cutlist.csv").write_text(outputs.cutlist_csv(parts, bands), encoding="utf-8-sig")
    (out / "spec.md").write_text(outputs.spec_md(CONFIG, parts, facades, geo, bands), encoding="utf-8")
    (out / "drawing.svg").write_text(outputs.drawing_svg(CONFIG, parts, facades, geo), encoding="utf-8")

    area, band_len, holes, conf = outputs.totals(parts, bands)
    print(f"Деталей: {sum(p.count for p in parts)} ({len(parts)} позиций), площадь {area:.2f} м2, отверстий {holes}")
    print(f"Файлы записаны в {out}")


if __name__ == "__main__":
    main()
