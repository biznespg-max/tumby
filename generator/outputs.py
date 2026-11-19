"""Спецификация, таблица деталей и чертёж (SVG)."""

import csv
import io

SIDE_RU = {"left": "левый", "right": "правый", "bottom": "нижний", "top": "верхний"}


def _n(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def cutlist_csv(parts, bands):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Код", "Деталь", "Узел", "Длина (x), мм", "Ширина (y), мм", "Толщина", "Кол-во",
                "Кромка низ", "Кромка верх", "Кромка лев", "Кромка прав", "Отверстий"])
    for p in parts:
        e = {s: (bands[k]["thickness"] if k else "") for s, k in
             ((s, p.edges.get(s)) for s in ("bottom", "top", "left", "right"))}
        w.writerow([p.code, p.name, p.group, _n(p.l), _n(p.w), _n(p.t), p.count,
                    e["bottom"], e["top"], e["left"], e["right"], len(p.holes) * p.count])
    return buf.getvalue()


def totals(parts, bands):
    area = sum(p.l * p.w * p.count for p in parts) / 1e6
    band_len = {k: 0.0 for k in bands}
    for p in parts:
        for side, k in p.edges.items():
            band_len[k] += (p.l if side in ("bottom", "top") else p.w) * p.count / 1000
    holes = sum(len(p.holes) * p.count for p in parts)
    confirmats = sum(sum(1 for h in p.holes if h.side == "face") * p.count for p in parts)
    return area, band_len, holes, confirmats


def spec_md(c, parts, facades, geo, bands):
    area, band_len, holes, confirmats = totals(parts, bands)
    L = []
    a = L.append
    a(f"# {c['name']}\n")
    a(f"Корпус {c['width']} × {c['height']} × {c['depth']} мм (Ш × В × Г), подвесной, 2 ящика.  ")
    sk = c["sink"]
    a(f"Артикул: **{c['article']}**. Умывальник: {sk['brand']} {sk['series']} {sk['size']} "
      f"({sk['width']} × {sk['depth']} × {sk['height']} мм, EAN {sk['ean']}).  ")
    if c.get("facade_inset"):
        a(f"Фасады вкладные (вровень с боковинами), глубина тумбы {c['depth']} мм (умывальник {sk['depth']} мм).\n")
    else:
        a(f"Глубина с фасадом: {c['depth'] + c['facade_t']} мм (умывальник {sk['depth']} мм).\n")

    a("## Детали (входят в файл для ViyarPro)\n")
    for key, sh in c["sheets"].items():
        mp = [p for p in parts if p.material == key]
        if not mp:
            continue
        m_area = sum(p.l * p.w * p.count for p in mp) / 1e6
        sh_area = sh["length"] * sh["width"] / 1e6
        title = sh.get("title") or ("Корпус — МДФ под покраску" if key == "corpus" else "Короба ящиков — ДСП")
        a(f"### {title}\n")
        a(f"Материал: {sh['name']}\n")
        used = [k for k in bands if any(k in p.edges.values() for p in mp)]
        if not used:
            used = [k for k in ("B2", "B08") if k in bands]
        heads = [f"Кромка {_n(bands[k]['thickness']).replace('.', ',')} мм" for k in used]
        a("| Код | Деталь | Узел | Размер, мм | Шт | " + " | ".join(heads) + " |")
        a("|---|---|---|---|---|" + "---|" * len(used))
        for p in mp:
            cols = []
            for k in used:
                sides = [SIDE_RU[s] for s, v in p.edges.items() if v == k]
                cols.append("все" if len(sides) == 4 else (", ".join(sides) or "—"))
            a(f"| {p.code} | {p.name} | {p.group} | {_n(p.l)} × {_n(p.w)} × {_n(p.t)} | {p.count} | " + " | ".join(cols) + " |")
        a("")
        a(f"Площадь: **{m_area:.2f} м²** из листа {sh_area:.2f} м² — хватает одного листа.\n")
    if c.get("corpus_notes"):
        for line in c["corpus_notes"]:
            a(f"{line}  ")
        a("")
    elif any(p.material == "corpus" for p in parts):
        a("Детали корпуса из МДФ идут **без кромки**: торцы красятся вместе с пластью. "
          "Покраска — со всех сторон, включая торцы и отверстия (влагозащита).\n")
    for k, b in bands.items():
        if band_len[k]:
            a(f"- {b['name']}: **{band_len[k]:.1f} м.п.** (без запаса)")
    a(f"- Отверстий всего: **{holes}**, из них под конфирматы в пласти: **{confirmats}**.\n")

    if c.get("facades_in_cut"):
        a("## Фасады (входят в файл порезки, тот же материал, что и корпус)\n")
        a(f"Толщина {c['facade_t']} мм, {c['facade_style']}.\n")
    else:
        a("## Фасады (МДФ, заказать отдельно)\n")
        a(f"Толщина {c['facade_t']} мм, {c['facade_style']}. Цвет: {c['facade_color']}.  ")
        a("Заказ: ViyarPro → фарбовані фасади. Спросить у менеджера про влагостойкую основу МДФ.\n")
    a("| Код | Фасад | Размер, мм | Шт |")
    a("|---|---|---|---|")
    for f in facades:
        a(f"| {f['code']} | {f['name']} | {_n(f['w'])} × {_n(f['h'])} | 1 |")
    a(f"\nЗазоры: по {c['facade_side_gap']} мм с боков, {c['facade_mid_gap']} мм между фасадами, "
      f"{c['facade_top_gap']} мм сверху, {c['facade_bottom_gap']} мм снизу.\n")

    a("## Фурнитура\n")
    a("| Позиция | Код ВіЯр | Кол-во |")
    a("|---|---|---|")
    a(f"| {c['runner_name']} | {c['runner_code']} | 2 компл. |")
    if c.get("runner_extra"):
        a(f"| {c['runner_extra']} | — | — |")
    a(f"| Конфирмат 7×50 + заглушки в цвет | — | {confirmats} + 10 запас |")
    a("| Саморез 4×16 (направляющие к боковинам) | — | ~24 |")
    a("| Саморез 4×25 (фасад к ящику изнутри) | — | 8 |")
    if any(f["code"] == "F0" for f in facades):
        a("| Саморез 4×30 (фальш-панель F0 к царге K3 изнутри) | — | 4–6 |")
    if c.get("handles", "Ручки (выбрать под фасад)"):
        a(f"| {c.get('handles', 'Ручки (выбрать под фасад)')} | — | 2 |")
    a("| Крепление к стене: 2 анкера/шурупа 8×80 через заднюю верхнюю царгу или 2 навеса для подвесных тумб | — | 1 компл. |")
    a("| Сифон компактный (плоский) | — | 1 |")
    a("")

    a("## Важные размеры\n")
    a(f"- Внутренняя ширина корпуса: {_n(geo['inner_width'])} мм.")
    a(f"- Короб ящика: наружная ширина {_n(geo['drawer_outer_width'])} мм, внутренняя {_n(geo['drawer_inner_width'])} мм, длина {c['drawer_len']} мм.")
    a(f"- Короба: нижний {c['drawer_bottom_box_h']} мм, верхний {c['drawer_top_box_h']} мм (ниже чаши умывальника).")
    a(f"- Вырез под сифон в верхнем ящике: {c['u_width']} мм шириной, от {_n(geo['u_from'])} мм от передней стенки до задней. "
      f"Центр слива принят в {c['drain_from_front']} мм от переднего края корпуса.")
    a(f"- Низ короба нижнего ящика ≈ {_n(geo['bottom_drawer_box_bottom'])} мм от низа корпуса, верхнего ≈ {_n(geo['top_drawer_box_bottom'])} мм "
      "(точно — по фасадам, дальше регулировка 3D).\n")

    a("## Что проверить перед заказом\n")
    a("1. **Слив умывальника.** Положите умывальник на корпус и измерьте расстояние от переднего края корпуса до центра слива. "
      f"Если оно не {c['drain_from_front']} мм — поменяйте `drain_from_back` в `umyvalniki/<умывальник>.yaml` (расстояние от заднего края) и пересоберите.")
    a(f"2. **Ширина короба под направляющие.** Принято: внутренняя ширина короба = ширина корпуса внутри − {c['drawer_inner_deduct']} мм. "
      "Сверьте со схемой в упаковке направляющих.")
    a("3. **Сифон и выход канализации.** Сифон должен помещаться в вырез верхнего ящика и заканчиваться выше короба нижнего ящика.")
    a("4. **Кромка и материал.** После импорта в ViyarPro замените материал и кромку на позиции из каталога ВіЯр (импорт GibLab их не сопоставляет).")
    if c.get("one_sided"):
        a("5. **Лицевая сторона.** Материал односторонний: в ViyarPro проверьте, что декор снаружи — "
          "у боковин K1Л/K1П снаружи, " + ("" if c.get("bottom_material") else "у дна K2 снизу, ") + "у фасадов спереди; присадка с нужной стороны.\n")
    else:
        a("5. **Покраска корпуса.** Уточните у менеджера ВіЯр, красят ли они детали корпуса из МДФ так же, как фасады "
          "(тот же цвет RAL/NCS, все стороны и торцы). Если нет — порезка и присадка в ВіЯр, покраска в покрасочном цехе.\n")

    a("## Сборка\n")
    a(c.get("assembly_step0", "0. Детали корпуса красятся до сборки. Под конфирматы на видимых боковинах — заглушки в цвет или подкраска шляпок."))
    a("1. Корпус: боковины K1" + ("Л и K1П" if c.get("one_sided") else "") + " + дно K2 + задняя нижняя царга K5 + передняя царга K3 + задняя верхняя царга K4 на конфирматах.")
    if c.get("facade_inset"):
        a(f"2. Направляющие к боковинам саморезами 4×16, передний край — с отступом {c['facade_t']} мм + 2 мм от переднего торца боковины "
          "(вкладной фасад встаёт вровень с корпусом), высота — по фасадам.")
    else:
        a("2. Направляющие к боковинам саморезами 4×16, передний край — по краю корпуса, высота — по фасадам.")
    a("3. Нижний ящик: боковины N1 + передняя N2 + задняя N3 + дно N4 (дно поднято на 13 мм).")
    a("4. Верхний ящик: боковины V1, передняя V2, половинки задней V3, стенки выреза V4 и V5, дно V6 + V7. "
      "Вырез под сифон получается без фрезеровки — только из прямоугольных деталей.")
    a("5. Отверстия под задние крючки направляющих в задних стенках — по шаблону из инструкции направляющих.")
    if any(f["code"] == "F0" for f in facades):
        a("6. Фальш-панель F0 — к царге K3 изнутри саморезами 4×30 (зазор 2 мм до умывальника, по краям вровень с фасадами ящиков). "
          "Фасады ящиков — к передним стенкам ящиков изнутри саморезами 4×25, отрегулировать 3D-регулировкой направляющих.")
    else:
        a("6. Фасады к передним стенкам ящиков изнутри саморезами 4×25, отрегулировать 3D-регулировкой направляющих.")
    a("7. Повесить корпус, установить умывальник на силикон (он лежит на боковинах и царгах).")
    return "\n".join(L) + "\n"


def drawing_svg(c, parts, facades, geo):
    W, H, D, t = c["width"], c["height"], c["depth"], c["t"]
    s = 0.5
    pad = 40
    fw, fh = geo["facade_w"], geo["facade_h"]
    out = []
    a = out.append
    total_w = pad * 3 + W * s + D * s + 40
    sk = c["sink"]
    top_off = sk["height"] * s + 30
    total_h = pad * 2 + top_off + H * s + 60 + 390 * s + 60
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
      f'viewBox="0 0 {total_w:.0f} {total_h:.0f}" font-family="Arial" font-size="11">')
    a('<rect width="100%" height="100%" fill="white"/>')

    # Вид спереди
    ox, oy = pad, pad + top_off
    a(f'<text x="{ox}" y="{pad}" font-size="13" font-weight="bold">Вид спереди</text>')
    a(f'<rect x="{ox}" y="{oy}" width="{W*s}" height="{H*s}" fill="#f4f4f4" stroke="#999"/>')
    for f in facades:
        fy = oy + (H - f["top"]) * s
        a(f'<rect x="{ox + f.get("x", c["facade_side_gap"])*s}" y="{fy}" width="{fw*s}" height="{f["h"]*s}" fill="#e8eef5" stroke="#333"/>')
        a(f'<text x="{ox + W*s/2}" y="{fy + f["h"]*s/2 + 4}" text-anchor="middle">{f["code"]} {_n(fw)}×{_n(f["h"])}</text>')
    over = (sk["width"] - W) / 2
    a(f'<rect x="{ox - over*s}" y="{oy - sk["height"]*s}" width="{sk["width"]*s}" height="{sk["height"]*s}" fill="none" stroke="#1E90FF" stroke-dasharray="4 3"/>')
    a(f'<text x="{ox + W*s/2}" y="{oy - sk["height"]*s/2 + 4}" text-anchor="middle" fill="#1E90FF">{sk["brand"]} {sk["series"]} {sk["size"]} ({sk["width"]}×{sk["depth"]}×{sk["height"]})</text>')
    a(f'<text x="{ox}" y="{pad + 18}" fill="#666">{c["article"]} — {c["name"]}</text>')
    a(f'<text x="{ox + W*s/2}" y="{oy + H*s + 16}" text-anchor="middle">{W}</text>')
    a(f'<text x="{ox - 6}" y="{oy + H*s/2}" text-anchor="end">{H}</text>')

    # Разрез сбоку
    sx = ox + W * s + pad + 20
    a(f'<text x="{sx}" y="{pad}" font-size="13" font-weight="bold">Разрез сбоку (перед слева)</text>')
    a(f'<rect x="{sx}" y="{oy}" width="{D*s}" height="{H*s}" fill="none" stroke="#333"/>')
    f0 = geo.get("front_offset", 0)
    a(f'<rect x="{sx + f0*s}" y="{oy + (H - t)*s}" width="{(D - f0)*s}" height="{t*s}" fill="#ccc"/>')
    a(f'<rect x="{sx + f0*s}" y="{oy}" width="{t*s}" height="{c["front_rail_h"]*s}" fill="#ccc"/>')
    a(f'<rect x="{sx + (D - t)*s}" y="{oy}" width="{t*s}" height="{c["rear_top_rail_h"]*s}" fill="#ccc"/>')
    a(f'<rect x="{sx + (D - t)*s}" y="{oy + (H - t - c["rear_bottom_rail_h"])*s}" width="{t*s}" height="{c["rear_bottom_rail_h"]*s}" fill="#ccc"/>')
    for yb, hb in ((geo["bottom_drawer_box_bottom"], c["drawer_bottom_box_h"]),
                   (geo["top_drawer_box_bottom"], c["drawer_top_box_h"])):
        a(f'<rect x="{sx + f0*s}" y="{oy + (H - yb - hb)*s}" width="{c["drawer_len"]*s}" height="{hb*s}" fill="#fff6e0" stroke="#b07a00"/>')
    if f0:
        for f in facades:
            a(f'<rect x="{sx}" y="{oy + (H - f["top"])*s}" width="{f0*s}" height="{f["h"]*s}" fill="#e8eef5" stroke="#333"/>')
    dz = c["drain_from_front"]
    a(f'<line x1="{sx + dz*s}" y1="{oy - 30}" x2="{sx + dz*s}" y2="{oy + 260*s}" stroke="#1E90FF" stroke-dasharray="4 3"/>')
    a(f'<text x="{sx + dz*s + 4}" y="{oy - 18}" fill="#1E90FF">слив {dz}</text>')
    a(f'<text x="{sx + D*s/2}" y="{oy + H*s + 16}" text-anchor="middle">{D}{"" if f0 else f" (+{c['facade_t']} фасад)"}</text>')

    # Верхний ящик в плане
    px, py = pad, oy + H * s + 60
    wo, wi, L = geo["drawer_outer_width"], geo["drawer_inner_width"], c["drawer_len"]
    uw, zf = c["u_width"], geo["u_from"]
    a(f'<text x="{px}" y="{py - 8}" font-size="13" font-weight="bold">Верхний ящик, вид сверху (вырез под сифон)</text>')
    a(f'<rect x="{px}" y="{py}" width="{wo*s}" height="{L*s}" fill="#fff6e0" stroke="#b07a00"/>')
    ux = px + (t + (wi - uw) / 2) * s
    a(f'<rect x="{ux}" y="{py + zf*s}" width="{uw*s}" height="{(L - zf)*s}" fill="white" stroke="#b07a00"/>')
    a(f'<circle cx="{px + wo*s/2}" cy="{py + c["drain_from_front"]*s}" r="{35*s}" fill="none" stroke="#1E90FF"/>')
    a(f'<text x="{px + wo*s/2}" y="{py + L*s - 10}" text-anchor="middle">вырез {uw}</text>')
    a(f'<text x="{px + wo*s + 6}" y="{py + 12}">← перед (фасад)</text>')
    a(f'<text x="{px + wo*s + 6}" y="{py + L*s}">← зад</text>')
    a(f'<text x="{px + wo*s/2}" y="{py + L*s + 16}" text-anchor="middle">{_n(wo)} × {L}</text>')
    a("</svg>")
    return "\n".join(out)
