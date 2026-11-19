"""Запись деталей в GibLab XML (*.project) для импорта в ViyarPro.

ViyarPro принимает этот формат на странице «Конвертація» -> GibLab.
Соответствие тегов взято из открытого проекта agav/ocl-viyar
(проверено автором на импорте ViyarPro в октябре 2026):

  кромка:   elb - нижний торец, elt - верхний, ell - левый, elr - правый
  отверстия в торцах: bt - нижний (коорд. x), bl - левый (y), br - правый (y)
  отверстия в пласти: bf (x, y), операция XNC side="true" (лицевая) / side="false" (обратная, те же x/y)
  mirVert="true" (начало - левый нижний угол), bySizeDetail="true" (чистовой размер)
  размеры: dl/dw - чистовые, l/w/cl/cw/jl/jw - чистовые минус толщина кромки
"""

import time
import uuid
from xml.sax.saxutils import quoteattr

VERSION = "21052101"
THROUGH_EXTRA = 2.0
BAND_ATTR = {"bottom": "elb", "top": "elt", "left": "ell", "right": "elr"}
EDGE_HOLE = {"bottom": ("bt", "x"), "left": ("bl", "y"), "right": ("br", "y")}
BAND_COLORS = ["#000000", "#D2691E", "#1E90FF", "#228B22"]


def _fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        r = round(v, 2)
        return str(int(r)) if r == int(r) else f"{r:.2f}".rstrip("0")
    return str(v)


def _tag(name, attrs, close=True):
    a = "".join(f" {k}={quoteattr(_fmt(v))}" for k, v in attrs.items())
    return f"<{name}{a}{'/' if close else ''}>"


class Ids:
    def __init__(self):
        self.n = {"good": 0, "part": 0, "op": 0}

    def next(self, kind):
        self.n[kind] += 1
        return self.n[kind]


def to_xml(project_name, parts, sheets, bands):
    """sheets: {ключ материала: {name, length, width, thickness}}; part.material - ключ."""
    ids = Ids()
    now = int(time.time() * 1000)

    product_good = ids.next("good")
    saw_good = ids.next("good")
    used_bands = {k for p in parts for k in p.edges.values()}
    band_info = {}
    for i, (key, b) in enumerate((k, b) for k, b in bands.items() if k in used_bands):
        band_info[key] = {"band": b, "tool": ids.next("good"), "good": ids.next("good"),
                          "op": ids.next("op"), "index": i, "parts": []}
    sheet_info = {}
    for key, sh in sheets.items():
        if any(p.material == key for p in parts):
            sheet_info[key] = {"sheet": sh, "good": ids.next("good"), "stock": ids.next("part"),
                               "op": ids.next("op"), "parts": []}

    part_ids = [ids.next("part") for _ in parts]

    product_xml = []
    xnc_xml = []
    for p, pid in zip(parts, part_ids):
        sheet_info[p.material]["parts"].append(pid)
        for key in set(p.edges.values()):
            band_info[key]["parts"].append(pid)
        product_xml.append(_product_part(p, pid, band_info))
        xnc = _xnc(p, pid, ids)
        if xnc:
            xnc_xml.append(xnc)

    x = ['<?xml version="1.0" encoding="UTF-8"?>']
    x.append(_tag("project", {"project.uuid": str(uuid.uuid4()), "version": VERSION, "costOperation": 0,
                              "costMaterial": 0, "cost": 0, "date": now, "orderDate": now}, False))

    x.append(_tag("good", {"typeId": "product", "count": 1, "id": product_good, "name": project_name,
                           "costMaterial": 0, "costOperation": 0, "cost": 0}, False))
    x.extend(product_xml)
    x.append("</good>")

    x.append(_tag("good", {"typeId": "tool.cutting", "swSawthick": 4.4, "swSawthickDiv": -1, "swPackageHeight": 40,
                           "swMaxturns": 6, "swComplexBand": True, "swTrimIncludeSaw": False, "swSort": 0,
                           "swSortInBand": 3, "swMinSizeBand": 0, "swMaxSizeBand": 0, "swMinPruning": 0,
                           "swMaxLengthBand": 0, "id": saw_good}))
    for b in band_info.values():
        x.append(_tag("good", {"typeId": "tool.edgeline", "elRestSide": 0, "elMinSize": 0, "elWidthPreJoint": 0,
                               "elCost": 0, "id": b["tool"]}))

    for s in sheet_info.values():
        sh = s["sheet"]
        x.append(_tag("good", {"typeId": "sheet", "w": sh["width"], "l": sh["length"], "t": sh["thickness"],
                               "count": 0, "cost": 0, "name": sh["name"], "id": s["good"]}, False))
        x.append(_tag("part", {"l": sh["length"], "w": sh["width"], "count": 1000, "usedCount": 0, "id": s["stock"]}))
        x.append("</good>")

    for b in band_info.values():
        x.append(_tag("good", {"typeId": "band", "w": b["band"]["width"], "t": float(b["band"]["thickness"]),
                               "count": 0, "cost": 0, "name": b["band"]["name"], "id": b["good"]}))

    for s in sheet_info.values():
        sh = s["sheet"]
        x.append(_tag("operation", {
            "l": sh["length"], "w": sh["width"], "t": sh["thickness"], "tool1": saw_good,
            "cFillRep": 0.9, "cCPF": 0.9, "cCostCut": 0, "cCostType": 0, "cSizeMode": 1, "cTrimL": 10, "cTrimW": 10,
            "cMinDimRegWaste1": 400, "cMinDimRegWaste2": 100, "cBusinessWaste": 10, "cTrimWaste": True,
            "cSaveDrawCut": False, "cMinDimDetail": 0, "cMaxPartsOnPattern": 0, "cCostByItem": False,
            "cCostByItemRound": 11, "cPrefLargePacket": False, "cCombiningParts": False, "cGroupParts": 0,
            "cAllowanceWorkpiece": 0, "typeId": "CS", "costMaterial": 0, "costOperation": 0, "costTotal": 0,
            "printable": True, "startNewPage": True, "id": s["op"], "csDirectCut": 0, "csTexture": True}, False))
        x.append(_tag("material", {"id": s["good"], "count": 0}))
        for pid in s["parts"]:
            x.append(_tag("part", {"id": pid}))
        x.append(_tag("part", {"id": s["stock"]}))
        x.append("</operation>")

    for b in band_info.values():
        x.append(_tag("operation", {
            "elWastePRC": 0, "elCalcMat": True, "elLength": 0, "tool1": b["tool"],
            "elSymbol": chr(ord("A") + b["index"]), "elColor": BAND_COLORS[b["index"] % len(BAND_COLORS)],
            "elLineMark": 0, "elRoundMat": 20, "elRoundLength": 20, "elMinDimDetail": 0, "typeId": "EL",
            "costMaterial": 0, "costOperation": 0, "costTotal": 0, "printable": True, "startNewPage": True,
            "id": b["op"]}, False))
        x.append(_tag("material", {"id": b["good"], "count": 0}))
        for pid in b["parts"]:
            x.append(_tag("part", {"id": pid}))
        x.append("</operation>")

    x.extend(xnc_xml)
    x.append("</project>")
    return "".join(x)


def _product_part(p, pid, band_info):
    bt = {s: float(band_info[k]["band"]["thickness"]) for s, k in p.edges.items()}
    cl = p.l - bt.get("left", 0) - bt.get("right", 0)
    cw = p.w - bt.get("bottom", 0) - bt.get("top", 0)
    attrs = {"l": float(cl), "w": float(cw), "dl": float(p.l), "dw": float(p.w), "jl": float(cl), "jw": float(cw),
             "cl": float(cl), "cw": float(cw), "minusCount": 0, "count": p.count, "usedCount": 0, "txt": True,
             "id": pid, "name": f"{p.code} {p.name}"}
    for side, attr in BAND_ATTR.items():
        key = p.edges.get(side)
        if key:
            attrs[attr] = f"@operation#{band_info[key]['op']}"
            attrs[attr + "Mat"] = band_info[key]["band"]["name"]
    return _tag("part", attrs)


def _xnc(p, pid, ids):
    """Одна операция XNC на сторону: лицевая (side="true", вместе с торцевыми) и обратная (side="false")."""
    front = [h for h in p.holes if h.side != "back"]
    back = [h for h in p.holes if h.side == "back"]
    out = ""
    for holes, side in ((front, True), (back, False)):
        if not holes:
            continue
        prog = [_tag("program", {"dx": float(p.l), "dy": float(p.w), "dz": float(p.t)}, False)]
        for d in dict.fromkeys(h.d for h in holes):
            prog.append(_tag("tool", {"name": f"D{_fmt(float(d))}", "d": float(d)}))
        for h in holes:
            depth = p.t + THROUGH_EXTRA if h.depth is None else h.depth
            name = f"D{_fmt(float(h.d))}"
            if h.side in ("face", "back"):
                prog.append(_tag("bf", {"x": float(h.x), "y": float(h.y), "dp": float(depth), "ac": 1, "av": False, "name": name}))
            else:
                tag, coord = EDGE_HOLE[h.side]
                prog.append(_tag(tag, {"ver": 2, coord: float(getattr(h, coord)), "dp": float(depth), "ac": 1, "m": True, "name": name}))
        prog.append("</program>")
        program = '<?xml version="1.0" encoding="UTF-8"?>' + "".join(prog)
        attrs = {"program": program, "count": 1, "side": side, "turn": 0, "mirHor": False, "mirVert": True,
                 "bySizeDetail": True, "priceBore": 0, "countBore": len(holes), "costBore": 0, "priceMill": 0,
                 "countMill": 0, "costMill": 0, "priceCut": 0, "countCut": 0, "costCut": 0, "price": 0, "cost": 0,
                 "typeId": "XNC", "costMaterial": 0, "costOperation": 0, "costTotal": 0, "printable": True,
                 "startNewPage": True, "id": ids.next("op")}
        out += _tag("operation", attrs, False) + _tag("part", {"id": pid}) + "</operation>"
    return out
