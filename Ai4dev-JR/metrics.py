"""Métricas calculadas exclusivamente a partir de transacciones válidas."""
from collections import Counter, defaultdict


def generate_metrics(valid_txs, invalid_txs):
    totals = defaultdict(float)
    for tx in valid_txs:
        totals[tx.currency] += tx.amount
    return {"total_processed": len(valid_txs) + len(invalid_txs),
            "valid_count": len(valid_txs), "invalid_count": len(invalid_txs),
            "status_count": dict(Counter(tx.status for tx in valid_txs)),
            "total_by_currency": {currency: round(total, 2) for currency, total in totals.items()}}
