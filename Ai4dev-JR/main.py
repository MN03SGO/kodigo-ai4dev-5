
import json
import sys
from pathlib import Path

from normalizer import Normalizer, Transaction
from validator import Validator
from configuration import load_config

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
DATA_PATH = BASE_DIR / "data.json"


def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: no se encontró el archivo {path.name}")
    except json.JSONDecodeError as e:
        sys.exit(f"Error: {path.name} no es un JSON válido ({e})")


def process(records, normalizer: Normalizer, validator: Validator):
    valid, invalid = [], []
    for raw, tx in normalizer.normalize_all(records):
        errors = validator.get_errors(tx)
        if errors:
            invalid.append({"transaction": tx, "raw": raw, "errors": errors})
        else:
            valid.append(tx)
    return valid, invalid



def print_transactions(txs: list[Transaction]) -> None:
    if not txs:
        print("  (sin resultados)")
        return
    header = f"  {'ID':<10} {'MONTO':>10} {'MONEDA':<7} {'FECHA':<20} {'ESTADO':<9} {'FUENTE':<9}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for tx in txs:
        print(
            f"  {tx.id:<10} {tx.amount:>10.2f} {tx.currency:<7} "
            f"{tx.timestamp:<20} {tx.status:<9} {tx.source:<9}"
        )


def print_metrics(metrics: dict) -> None:
    print("\n  ===== MÉTRICAS GENERALES =====")
    print(f"  Total procesadas : {metrics['total_processed']}")
    print(f"  Válidas          : {metrics['valid_count']}")
    print(f"  Inválidas        : {metrics['invalid_count']}")
    print("\n  Conteo por estado:")
    for status, count in metrics["status_count"].items() or [("(ninguno)", 0)]:
        print(f"    - {status:<10} {count}")
    print("\n  Suma total por moneda:")
    for currency, total in metrics["total_by_currency"].items() or [("(ninguna)", 0)]:
        print(f"    - {currency:<10} {total:,.2f}")


def print_invalid(invalid: list[dict]) -> None:
    if not invalid:
        print("  (no hay transacciones inválidas)")
        return
    for i, item in enumerate(invalid, 1):
        print(f"\n  [{i}] Fuente: {item['transaction'].source}")
        print("  Motivo(s):")
        for err in item["errors"]:
            print(f"    - {err}")
        print("  JSON original:")
        print("    " + json.dumps(item["raw"], ensure_ascii=False, indent=2).replace("\n", "\n    "))


# Menú 
MENU = """
-NORMALIZADOR DE TRANSACCIONES
  1. Ver todas las transacciones válidas
  2. Filtrar por Estado
  3. Filtrar por Moneda
  4. Ver Métricas Generales
  5. Ver Transacciones Inválidas
  6. Salir
==================================================="""


def main() -> None:
    try:
        config = load_config(CONFIG_PATH)
    except (OSError, ValueError) as exc:
        sys.exit(f"Error de configuración: {exc}")
    records = load_json(DATA_PATH)

    normalizer = Normalizer(status_mapping=config["status_mapping"], date_formats=config["date_formats"])
    validator = Validator(config.get("supported_currencies", []))
    valid, invalid = process(records, normalizer, validator)

    while True:
        print(MENU)
        try:
            option = input("Seleccione una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if option == "1":
            print("\n  --- Transacciones válidas ---")
            print_transactions(valid)

        elif option == "2":
            status = input("Estado (SUCCESS, FAILED, PENDING): ").strip().upper()
            print(f"\n  --- Transacciones con estado {status} ---")
            print_transactions([tx for tx in valid if tx.status == status])

        elif option == "3":
            currency = input("Moneda (USD, EUR): ").strip().upper()
            print(f"\n  --- Transacciones en {currency} ---")
            print_transactions([tx for tx in valid if tx.currency == currency])

        elif option == "4":
            invalid_txs = [item["transaction"] for item in invalid]
            print_metrics(validator.generate_metrics(valid, invalid_txs))

        elif option == "5":
            print("\n  --- Transacciones inválidas ---")
            print_invalid(invalid)

        elif option == "6":
            print("Saliendo...")
            break

        else:
            print("  Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
