
from collections import Counter, defaultdict

from normalizer import FORMAT_UNKNOWN, Transaction


class Validator:
    def __init__(self, supported_currencies: list[str]):
        self.supported_currencies = {c.upper() for c in supported_currencies}

    def get_errors(self, transaction: Transaction) -> list[str]:
        """Devuelve la lista de motivos por los que la transacción es inválida."""
        errors = []
        if transaction.source == FORMAT_UNKNOWN:
            errors.append("Formato de origen no reconocido")
        if transaction.amount is None:
            errors.append("Monto no se pudo interpretar")
        elif transaction.amount <= 0:
            errors.append(f"Monto debe ser mayor a 0 (recibido: {transaction.amount})")
        if transaction.currency not in self.supported_currencies:
            errors.append(f"Moneda no soportada: {transaction.currency}")
        if transaction.timestamp is None:
            errors.append("Fecha no se pudo interpretar")
        return errors

    def is_valid(self, transaction: Transaction) -> bool:
        return not self.get_errors(transaction)

    @staticmethod
    def generate_metrics(valid_txs: list[Transaction], invalid_txs: list[Transaction]) -> dict:
        """Conteo por estado y suma por moneda se calculan sobre las transacciones válidas."""
        status_count = Counter(tx.status for tx in valid_txs)

        totals = defaultdict(float)
        for tx in valid_txs:
            totals[tx.currency] += tx.amount

        return {
            "total_processed": len(valid_txs) + len(invalid_txs),
            "valid_count": len(valid_txs),
            "invalid_count": len(invalid_txs),
            "status_count": dict(status_count),
            "total_by_currency": {cur: round(total, 2) for cur, total in totals.items()},
        }
