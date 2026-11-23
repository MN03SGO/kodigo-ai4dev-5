"""Carga y comprueba la configuración de las reglas de negocio."""
import json
from pathlib import Path


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        config = json.load(file)
    if not isinstance(config, dict):
        raise ValueError("La configuración debe ser un objeto JSON")
    for key, kind in (("status_mapping", dict), ("date_formats", dict),
                      ("supported_currencies", list)):
        if not isinstance(config.get(key), kind) or not config[key]:
            raise ValueError(f"Configuración inválida o ausente: {key}")
    if not all(isinstance(k, str) and isinstance(v, str) for key in ("status_mapping", "date_formats") for k, v in config[key].items()):
        raise ValueError("Los mapeos y formatos deben contener cadenas")
    if not all(isinstance(c, str) and c for c in config["supported_currencies"]):
        raise ValueError("Las monedas deben ser cadenas no vacías")
    for source in ("format_A", "format_B", "format_C"):
        if not config["date_formats"].get(source):
            raise ValueError(f"Formato de fecha ausente: {source}")
    return config
