from normalizer import Normalizer
from validator import Validator
from metrics import generate_metrics


def normalizar_transacciones(records, config):
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError("Los registros deben ser una lista de objetos JSON")
    normalizer = Normalizer(config["status_mapping"], config["date_formats"])
    return normalizer.normalize_all(records)


def validar_transacciones(normalized, config):
    validator = Validator(config["supported_currencies"])
    valid, invalid = [], []
    for raw, tx in normalized:
        errors = validator.get_errors(tx)
        if errors:
            invalid.append({"transaction": tx, "raw": raw, "errors": errors})
        else:
            valid.append(tx)
    return valid, invalid


def calcular_metricas(valid, invalid):
    return generate_metrics(valid, invalid)


SKILLS = {"normalizar_transacciones": normalizar_transacciones,
          "validar_transacciones": validar_transacciones,
          "calcular_metricas": calcular_metricas}
