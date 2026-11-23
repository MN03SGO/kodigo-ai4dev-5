
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

FORMAT_A = "format_A"
FORMAT_B = "format_B"
FORMAT_C = "format_C"
FORMAT_UNKNOWN = "unknown"

@dataclass
class Transaction:

    id: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    timestamp: Optional[str]  # ISO-8601
    status: Optional[str]
    source: str

    def to_dict(self) -> dict:
        return asdict(self)


class Normalizer:
    "Convierte registros crudos (formatos A, B y C) en objetos Transaction."

    def __init__(self, status_mapping: dict[str, str], date_formats: dict[str, str]):
        self.status_mapping = {k.lower(): v for k, v in status_mapping.items()}
        self.date_formats = date_formats

    # ---------- Detección ----------
    @staticmethod
    def detect_format(record: dict[str, Any]) -> str:
        if "transaction_id" in record:
            return FORMAT_B
        if "ref" in record:
            return FORMAT_C
        if "id" in record and "timestamp" in record:
            return FORMAT_A
        return FORMAT_UNKNOWN

    # Montos 
    @staticmethod
    def parse_amount(raw: Any, source: str) -> Optional[float]:
        try:
            if source == FORMAT_B:
                return float(raw) / 100
            if source == FORMAT_C:
                cleaned = str(raw).replace("€", "").replace(",", ".").strip()
                return float(cleaned)
            return float(raw)
        except (TypeError, ValueError):
            return None

    #Fechas
    def parse_date(self, raw: Any, source: str) -> Optional[str]:
        fmt = self.date_formats.get(source)
        if fmt is None:
            return None
        try:
            return datetime.strptime(str(raw), fmt).isoformat()
        except (TypeError, ValueError):
            return None

    #Moneda y estado
    @staticmethod
    def parse_currency(raw: Any) -> Optional[str]:
        if raw is None:
            return None
        try:
            value = str(raw).strip().upper()
            return value or None
        except (TypeError, ValueError):
            return None

    def map_status(self, raw: Any) -> Optional[str]:
        if raw is None:
            return None
        key = str(raw).strip().lower()
        return self.status_mapping.get(key, key.upper())

    #Normalización
    def normalize(self, record: dict[str, Any]) -> Transaction:
        source = self.detect_format(record)

        if source == FORMAT_A:
            raw_id = record.get("id")
            raw_amount = record.get("amount")
            raw_currency = record.get("currency")
            raw_date = record.get("timestamp")
            raw_status = record.get("status")
        elif source == FORMAT_B:
            raw_id = record.get("transaction_id")
            raw_amount = record.get("total")
            raw_currency = record.get("currency_code")
            raw_date = record.get("created_at")
            raw_status = record.get("state")
        elif source == FORMAT_C:
            raw_id = record.get("ref")
            raw_amount = record.get("amount")
            # La fuente C no trae campo de moneda: se infiere EUR a partir del símbolo "€".
            raw_currency = "EUR" if "€" in str(raw_amount) else None
            raw_date = record.get("date")
            raw_status = record.get("result")
        else:
            return Transaction(None, None, None, None, None, source)

        return Transaction(
            id=str(raw_id) if raw_id is not None else None,
            amount=self.parse_amount(raw_amount, source),
            currency=self.parse_currency(raw_currency),
            timestamp=self.parse_date(raw_date, source),
            status=self.map_status(raw_status),
            source=source,
        )

    def normalize_all(self, records: list[dict[str, Any]]) -> list[tuple[dict, Transaction]]:
        #devuelve pares (registro_original, transacción_normalizada).
        return [(record, self.normalize(record)) for record in records]
