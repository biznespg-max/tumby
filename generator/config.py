"""Сборка параметров изделия: модель (modeli/<модель>/model.yaml) + умывальник
(umyvalniki/<умывальник>.yaml) + размер -> словарь параметров для model.build().
"""

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sink(key):
    return load_yaml(ROOT / "umyvalniki" / f"{key}.yaml")


def load_model(key):
    return load_yaml(ROOT / "modeli" / key / "model.yaml")


def _merge(base, extra):
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def product_config(model_key, sink_key, size, override=None):
    m = _merge(load_model(model_key), override)
    s = load_sink(sink_key)
    sz = s["sizes"][size]
    c = {k: v for k, v in m.items() if k not in ("izdeliya", "title", "code", "name")}
    c["article"] = f"{m['code']}-{s['code']}{size}"
    c["name"] = m["title"].format(size=size, brand=s["brand"], series=s["series"])
    c["model"] = model_key
    c["sink"] = {
        "key": sink_key, "brand": s["brand"], "series": s["series"], "size": size,
        "width": sz["width"], "depth": s["depth"], "height": s["height"],
        "bowl_width": sz.get("bowl_width"), "bowl_depth": s["bowl_depth"], "bowl_drop": s["bowl_drop"],
        "ean": sz.get("ean", ""),
    }
    c["width"] = sz["width"] + m["width_from_sink"]
    c["depth"] = s["depth"] - m["facade_t"] + m["depth_from_sink"]
    # центр слива от переднего края корпуса (задний край корпуса = задний край умывальника)
    c["drain_from_front"] = c["depth"] - s["drain_from_back"]
    return c


def all_products():
    """Все изделия всех моделей: список (model_key, sink_key, size, override)."""
    out = []
    for d in sorted((ROOT / "modeli").iterdir()):
        if not (d / "model.yaml").exists():
            continue
        m = load_model(d.name)
        for item in m.get("izdeliya", []):
            for size in item["sizes"]:
                out.append((d.name, item["umyvalnik"], size, item.get("override")))
    return out
