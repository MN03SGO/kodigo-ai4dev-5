"""Proveedor HTTP compatible con el formato de Chat Completions."""
import json
from urllib.request import Request, urlopen


class ChatProvider:
    def __init__(self, endpoint, api_key, model, timeout=20):
        if not endpoint.startswith("https://") or not api_key or not model:
            raise ValueError("Se requiere endpoint HTTPS, clave y modelo")
        self.endpoint, self.api_key, self.model, self.timeout = endpoint, api_key, model, timeout

    def explain(self, style, categories):
        body = {"model": self.model, "messages": [
            {"role": "system", "content": style + " No inventes causas ni cifras; usa solo los datos proporcionados."},
            {"role": "user", "content": json.dumps(categories, ensure_ascii=False)}]}
        request = Request(self.endpoint, data=json.dumps(body).encode(),
                          headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key})
        with urlopen(request, timeout=self.timeout) as response:
            result = json.load(response)
        return result["choices"][0]["message"]["content"]
