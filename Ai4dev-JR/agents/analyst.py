"""Orquestación explícita: el modelo nunca ejecuta herramientas."""
from collections import Counter
from skills.transactions import SKILLS

PROFILES = {
    "tecnico": {"style": "Explica brevemente los motivos técnicos de rechazo en español.",
                "skills": tuple(SKILLS), "show_sources": True},
    "ejecutivo": {"style": "Resume brevemente los motivos de rechazo en español para una persona ejecutiva.",
                  "skills": tuple(SKILLS), "show_sources": False},
}


class TransactionAgent:
    def __init__(self, config, profile="tecnico", provider=None):
        if profile not in PROFILES:
            raise ValueError(f"Perfil desconocido: {profile}")
        self.config, self.profile, self.provider = config, PROFILES[profile], provider

    def run_skill(self, name, *args):
        if name not in self.profile["skills"] or name not in SKILLS:
            raise ValueError(f"Skill no permitida: {name}")
        return SKILLS[name](*args)

    def analyze(self, records):
        normalized = self.run_skill("normalizar_transacciones", records, self.config)
        valid, invalid = self.run_skill("validar_transacciones", normalized, self.config)
        metrics = self.run_skill("calcular_metricas", valid, invalid)
        # Solo se envían categorías fijas y conteos; no se envían registros ni valores.
        categories = Counter()
        for item in invalid:
            for error in item["errors"]:
                category = error.split(":", 1)[0].split(" (", 1)[0]
                categories[category] += 1
        explanation = None
        provider_error = None
        if self.provider and categories:
            try:
                explanation = self.provider.explain(self.profile["style"], dict(categories))
                if not isinstance(explanation, str) or not explanation.strip():
                    raise ValueError("Respuesta vacía del proveedor")
            except Exception:
                provider_error = "No fue posible generar la explicación; se muestran los motivos calculados."
        result = {"metrics": metrics, "rejection_categories": dict(categories),
                  "explanation": explanation, "provider_error": provider_error}
        if self.profile["show_sources"]:
            result["rejections"] = [{"source": item["transaction"].source,
                                     "errors": item["errors"]} for item in invalid]
        return result
