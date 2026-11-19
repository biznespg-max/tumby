"""Собирает все изделия всех моделей в папку izdeliya/<артикул>/.

Запуск:  python build.py            # все изделия
         python build.py TL-Q80     # одно изделие

В папке изделия:
  <артикул>.project - файл для ViyarPro (Конвертація -> GibLab)
  spec.md           - спецификация, фасады, фурнитура, сборка
  cutlist.csv       - таблица деталей
  drawing.svg/.png  - чертёж
"""

import pathlib
import shutil
import subprocess
import sys

from generator import config, model, giblab, outputs

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "izdeliya"


def check(parts):
    """Отверстия внутри детали и не глубже детали."""
    errors = []
    for p in parts:
        for h in p.holes:
            if h.side in ("face", "back"):
                r = h.d / 2
                if not (r <= h.x <= p.l - r and r <= h.y <= p.w - r):
                    errors.append(f"{p.code}: отверстие в пласти вне детали ({h.x}, {h.y})")
            else:
                pos, span, length = (h.x, p.l, p.w) if h.side == "bottom" else (h.y, p.w, p.l)
                if not (h.d / 2 <= pos <= span - h.d / 2):
                    errors.append(f"{p.code}: отверстие в торце {h.side} вне детали ({pos})")
                if h.depth >= length:
                    errors.append(f"{p.code}: отверстие в торце {h.side} глубже детали")
    # отверстия в одной пласти не пересекаются
    for p in parts:
        for side in ("face", "back"):
            hs = [h for h in p.holes if h.side == side]
            for i, a in enumerate(hs):
                for b in hs[i + 1:]:
                    if ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5 < (a.d + b.d) / 2 + 2:
                        errors.append(f"{p.code}: отверстия ({a.x}, {a.y}) и ({b.x}, {b.y}) слишком близко")
    return errors


def build_one(model_key, sink_key, size, override=None):
    c = config.product_config(model_key, sink_key, size, override)
    parts, facades, geo = model.build(c)
    errors = check(parts)
    if errors:
        raise SystemExit(f"{c['article']}: ОШИБКИ\n" + "\n".join(errors))
    d = OUT / c["article"]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{c['article']}.project").write_text(giblab.to_xml(f"{c['article']} {c['name']}", parts, c["sheets"], c["bands"]), encoding="utf-8")
    (d / "spec.md").write_text(outputs.spec_md(c, parts, facades, geo, c["bands"]), encoding="utf-8")
    (d / "cutlist.csv").write_text(outputs.cutlist_csv(parts, c["bands"]), encoding="utf-8-sig")
    svg = d / "drawing.svg"
    svg.write_text(outputs.drawing_svg(c, parts, facades, geo), encoding="utf-8")
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-z", "1.5", str(svg), "-o", str(d / "drawing.png")], check=True)
    area, band_len, holes, conf = outputs.totals(parts, c["bands"])
    return c, parts, facades, area, holes


def main():
    only = set(sys.argv[1:])
    rows = []
    for prod in config.all_products():
        c, parts, facades, area, holes = build_one(*prod)
        if only and c["article"] not in only:
            continue
        fd = [f for f in facades if f["code"] != "F0"]
        fp = [f for f in facades if f["code"] == "F0"]
        ftxt = (f"{fp[0]['w']:g} × {fp[0]['h']:g} + " if fp else "") + f"{fd[0]['w']:g} × {fd[0]['h']:g} (2 шт)"
        rows.append(f"| [{c['article']}]({c['article']}/spec.md) | {c['name']} | "
                    f"{c['width']} × {c['height']} × {c['depth']} | {ftxt} | "
                    f"{sum(p.count for p in parts)} | {area:.2f} м² | {holes} |")
        print(f"{c['article']}: {sum(p.count for p in parts)} деталей, {area:.2f} м2, {holes} отверстий")
    if not only:
        (OUT / "README.md").write_text(
            "# Изделия\n\nСобрано командой `python build.py`. Не редактировать вручную.\n\n"
            "| Артикул | Изделие | Корпус Ш×В×Г, мм | Фасады, мм | Деталей | Площадь | Отверстий |\n"
            "|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
