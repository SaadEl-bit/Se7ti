import json
from typing import Any

from openai import AsyncOpenAI

from ..config import settings

_SYSTEM_PROMPT = """Tu es un assistant médical expert en analyse d'ordonnances marocaines.
Extrais les informations de l'ordonnance et retourne UNIQUEMENT un JSON valide avec cette structure exacte :

{
  "medications": [
    {
      "name": "Nom du médicament (DCI ou commercial)",
      "dosage": "Dosage ex: 500mg",
      "frequency": "Fréquence ex: 2 fois par jour",
      "duration": "Durée ex: 3 mois (null si absente)",
      "quantity": 90
    }
  ],
  "doctor": {
    "name": "Dr. Prénom Nom (null si absent)",
    "speciality": "Spécialité (null si absente)",
    "city": "Ville (null si absente)"
  },
  "patient_name": "Nom du patient (null si absent)",
  "prescription_date": "YYYY-MM-DD (null si absente)",
  "notes": "Remarques ou instructions supplémentaires (null si aucune)"
}

Règles strictes :
- Si un champ est absent ou illisible, mets null (jamais de chaîne vide).
- Ne génère aucun texte en dehors du JSON.
- La quantité est le nombre total d'unités à délivrer (calculé si possible).
"""


class LLMParser:
    """Parses raw OCR text into structured prescription data via an LLM."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key or "placeholder",
        )

    async def parse_medications(self, ocr_text: str) -> dict[str, Any]:
        """Send OCR text to GPT-4o via OpenRouter and return structured prescription JSON."""
        _empty: dict[str, Any] = {
            "medications": [],
            "doctor": {"name": None, "speciality": None, "city": None},
            "patient_name": None,
            "prescription_date": None,
            "notes": None,
        }
        if not ocr_text.strip():
            return _empty
        try:
            response = await self._client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": ocr_text},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return _empty
