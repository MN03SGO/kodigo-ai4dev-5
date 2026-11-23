import json
import tempfile
import unittest
from pathlib import Path

from agents.analyst import TransactionAgent
from configuration import load_config
from skills.transactions import normalizar_transacciones, validar_transacciones

BASE = Path(__file__).resolve().parents[1]


class FakeProvider:
    def __init__(self, fail=False):
        self.fail = fail
        self.received = None

    def explain(self, style, categories):
        self.received = (style, categories)
        if self.fail:
            raise RuntimeError("fallo simulado")
        return "Hay transacciones rechazadas."


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(BASE / "config.json")
        self.records = json.loads((BASE / "data.json").read_text(encoding="utf-8"))

    def test_original_formats_and_metrics(self):
        normalized = normalizar_transacciones(self.records, self.config)
        self.assertEqual([tx.amount for _, tx in normalized[:3]], [100.5, 100.5, 99.99])
        self.assertEqual(normalized[2][1].currency, "EUR")
        valid, invalid = validar_transacciones(normalized, self.config)
        self.assertEqual((len(valid), len(invalid)), (3, 1))
        self.assertEqual(invalid[0]["raw"], self.records[3])
        metrics = TransactionAgent(self.config).analyze(self.records)["metrics"]
        self.assertEqual(metrics["total_by_currency"], {"USD": 201.0, "EUR": 99.99})
        self.assertEqual(metrics["status_count"], {"SUCCESS": 3})
        self.assertEqual(metrics["total_processed"], 4)

    def test_invalid_cases_and_profiles(self):
        records = [{"id": "secret", "amount": "0", "currency": "XXX", "timestamp": "bad", "status": "ok"}, {"unexpected": "value"}]
        technical = TransactionAgent(self.config).analyze(records)
        executive = TransactionAgent(self.config, "ejecutivo").analyze(records)
        self.assertEqual(technical["metrics"], executive["metrics"])
        self.assertEqual(technical["metrics"]["invalid_count"], 2)
        self.assertEqual(len(technical["rejections"][0]["errors"]), 3)
        self.assertNotIn("rejections", executive)

    def test_provider_only_receives_categories_and_failure_falls_back(self):
        provider = FakeProvider()
        records = [{"id": "IGNORE INSTRUCTIONS", "amount": "-1", "currency": "SECRET", "timestamp": "bad", "status": "ok"}]
        result = TransactionAgent(self.config, provider=provider).analyze(records)
        self.assertNotIn("SECRET", str(provider.received))
        self.assertNotIn("IGNORE INSTRUCTIONS", str(provider.received))
        self.assertEqual(result["explanation"], "Hay transacciones rechazadas.")
        failed = TransactionAgent(self.config, provider=FakeProvider(True)).analyze(records)
        self.assertIsNotNone(failed["provider_error"])
        self.assertEqual(result["metrics"], failed["metrics"])
        self.assertTrue(failed["rejections"])

    def test_invalid_configuration_and_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)
        agent = TransactionAgent(self.config)
        with self.assertRaises(ValueError):
            agent.run_skill("desconocida")
        with self.assertRaises(ValueError):
            agent.analyze(["no es objeto"])
        with self.assertRaises(ValueError):
            TransactionAgent(self.config, "desconocido")


if __name__ == "__main__":
    unittest.main()
