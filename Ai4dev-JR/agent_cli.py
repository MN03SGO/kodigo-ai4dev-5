"""Ejecuta el agente con un proveedor opcional configurado por entorno."""
import argparse
import json
import os
from pathlib import Path
from agents.analyst import TransactionAgent, PROFILES
from agents.provider import ChatProvider
from configuration import load_config


def main():
    base = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Analiza un lote de transacciones")
    parser.add_argument("--data", type=Path, default=base / "data.json")
    parser.add_argument("--config", type=Path, default=base / "config.json")
    parser.add_argument("--perfil", choices=PROFILES, default="tecnico")
    parser.add_argument("--llm", action="store_true", help="Solicita explicación al proveedor configurado")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        with args.data.open(encoding="utf-8") as file:
            records = json.load(file)
        provider = None
        if args.llm:
            provider = ChatProvider(os.getenv("AGENT_LLM_ENDPOINT", ""), os.getenv("AGENT_LLM_API_KEY", ""), os.getenv("AGENT_LLM_MODEL", ""))
        print(json.dumps(TransactionAgent(config, args.perfil, provider).analyze(records), ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
