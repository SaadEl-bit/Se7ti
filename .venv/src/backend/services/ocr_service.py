"""
OCR service — multi-model cascade strategy via OpenRouter.

Cascade order:
  1. Five best free vision models (tried in order).
     Stop early if confidence >= OCR_FREE_THRESHOLD.
  2. Claude Haiku Vision (mid-tier, paid).
     Stop if confidence >= OCR_HAIKU_THRESHOLD.
  3. Claude Sonnet (final, always accepted).

At every step the BEST result so far is kept.  The cascade falls through to
the next tier only when the current best confidence is still below threshold.

TrOCR local backend (OCR_BACKEND=trocr) bypasses the cascade entirely and is
kept for offline/CPU-only environments.
"""

import base64
import io
import json
import re
from dataclasses import dataclass, field
from typing import Any

# pyrefly: ignore [missing-import]
from ..config import settings

# ── Model lists ───────────────────────────────────────────────────────────────

# 5 best free vision/OCR models available on OpenRouter (ranked by OCR quality)
_FREE_MODELS: list[str] = [
    "recraft/recraft-v4.1-pro-vector",
    "recraft/recraft-v4.1",
    "recraft/recraft-v3",
    "recraft/recraft-v4.1-vector",
    "recraft/recraft-v4.1-pro",
]

_HAIKU_MODEL = "anthropic/claude-4-20251001-haiku"
_SONNET_MODEL = "anthropic/claude-sonnet-4-6"

# ── Prompts ───────────────────────────────────────────────────────────────────

_OCR_PROMPT = (
    "Extract ALL visible text from this medical prescription image exactly as written.\n"
    "Return ONLY a JSON object — no markdown, no extra text:\n"
    '{"text": "<complete extracted text>", "confidence": <0.0-1.0>}\n'
    "confidence = your accuracy estimate (1.0 = perfect, 0.0 = unreadable)."
)


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class OCRResult:
    text: str
    confidence: float
    model_used: str
    attempts: int
    attempt_log: list[dict[str, Any]] = field(default_factory=list)


# ── Confidence heuristic ──────────────────────────────────────────────────────

_MEDICAL_PATTERNS: list[str] = [
    r"\b\d+\s*mg\b",
    r"\b\d+\s*mcg\b",
    r"\b\d+\s*ml\b",
    r"\bdr\.?\s+\w+",
    r"\bdocteur\b",
    r"\bordonnance\b",
    r"\bprescription\b",
    r"\bcomprim[eé]s?\b",
    r"\bgélules?\b",
    r"\bposologie\b",
    r"\btraitement\b",
    r"\bpatient\b",
    r"\bsignature\b",
    r"\bdate\b",
    r"\b[12]x?\s*/?\s*(jour|day|j\b)",
]


def _score_text(text: str) -> float:
    """Heuristic confidence score for extracted prescription text."""
    if not text or len(text.strip()) < 10:
        return 0.05

    t = text.strip()
    score = 0.0

    # Length: a prescription is usually 60–2500 chars
    length = len(t)
    if 60 <= length <= 2500:
        score += 0.25
    elif length > 10:
        score += 0.10

    # Medical keywords / patterns
    hits = sum(
        1 for p in _MEDICAL_PATTERNS if re.search(p, t, re.IGNORECASE)
    )
    score += min(0.50, hits * 0.06)

    # Digit density (prescriptions have numbers for dosages)
    digit_ratio = sum(c.isdigit() for c in t) / len(t)
    if 0.02 <= digit_ratio <= 0.20:
        score += 0.10

    return round(min(0.95, score), 3)


def _parse_response(content: str) -> tuple[str, float]:
    """
    Extract (text, confidence) from a model response.
    Handles raw JSON, JSON in a markdown code block, or plain text fallback.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", content).strip()

    # Try to locate a JSON object in the response
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            text = str(data.get("text") or "").strip()
            confidence = float(data.get("confidence") or 0.0)
            if text:
                return text, min(1.0, max(0.0, confidence))
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: treat entire response as plain text
    plain = content.strip()
    return plain, _score_text(plain)


def _detect_mime(image_bytes: bytes) -> str:
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:2] == b"\xff\xd8":
        return "image/jpeg"
    if image_bytes[:4] == b"%PDF":
        return "application/pdf"
    return "image/jpeg"


# ── Service ───────────────────────────────────────────────────────────────────

class OCRService:
    """
    Extracts text from prescription images using a tiered model cascade.

    Default backend: OpenRouter multi-model cascade.
    Legacy backend: local TrOCR (set OCR_BACKEND=trocr in .env).
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._trocr_processor: Any = None
        self._trocr_model: Any = None

    def _get_client(self) -> Any:
        """Lazy-initialize a single AsyncOpenAI client for the OpenRouter cascade."""
        if self._client is None:
            from openai import AsyncOpenAI
            if not settings.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY manquant dans .env")
            self._client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.openrouter_api_key,
            )
        return self._client

    # ── Public API ────────────────────────────────────────────────────────────

    async def extract_text(self, image_bytes: bytes) -> OCRResult:
        """Extract text from a prescription image and return an OCRResult."""
        if settings.ocr_backend == "trocr":
            return await self._run_trocr(image_bytes)
        return await self._run_cascade(image_bytes)

    # ── Cascade ───────────────────────────────────────────────────────────────

    async def _run_cascade(self, image_bytes: bytes) -> OCRResult:
        mime = _detect_mime(image_bytes)
        if mime == "application/pdf":
            raise ValueError(
                "PDF non supporté par les modèles vision. Convertissez en JPEG/PNG."
            )

        b64 = base64.b64encode(image_bytes).decode()  # encode once, reuse across all models
        best = OCRResult(text="", confidence=0.0, model_used="none", attempts=0)
        log: list[dict[str, Any]] = []

        # ── Tier 1 : Free models ──────────────────────────────────────────────
        for model_id in _FREE_MODELS:
            best.attempts += 1
            entry: dict[str, Any] = {"model": model_id, "tier": "free"}
            try:
                text, confidence = await self._call_model(model_id, b64, mime)
                # Use max of self-reported confidence and heuristic
                confidence = max(confidence, _score_text(text))
                entry.update({"confidence": confidence, "status": "ok"})
                if text and confidence > best.confidence:
                    best.text, best.confidence, best.model_used = text, confidence, model_id
                if best.confidence >= settings.ocr_free_threshold:
                    log.append(entry)
                    break
            except Exception as exc:
                entry.update({"confidence": 0.0, "status": f"error: {exc}"})
            log.append(entry)

        if best.confidence >= settings.ocr_free_threshold:
            best.attempt_log = log
            return best

        # ── Tier 2 : Claude Haiku Vision ─────────────────────────────────────
        best.attempts += 1
        haiku_entry: dict[str, Any] = {"model": _HAIKU_MODEL, "tier": "haiku"}
        try:
            text, confidence = await self._call_model(_HAIKU_MODEL, b64, mime)
            confidence = max(confidence, _score_text(text))
            haiku_entry.update({"confidence": confidence, "status": "ok"})
            if text and confidence > best.confidence:
                best.text, best.confidence, best.model_used = text, confidence, _HAIKU_MODEL
        except Exception as exc:
            haiku_entry.update({"confidence": 0.0, "status": f"error: {exc}"})
        log.append(haiku_entry)

        if best.confidence >= settings.ocr_haiku_threshold:
            best.attempt_log = log
            return best

        # ── Tier 3 : Claude Sonnet — final, always accepted ──────────────────
        best.attempts += 1
        sonnet_entry: dict[str, Any] = {"model": _SONNET_MODEL, "tier": "final"}
        try:
            text, confidence = await self._call_model(_SONNET_MODEL, b64, mime)
            confidence = max(confidence, _score_text(text))
            sonnet_entry.update({"confidence": confidence, "status": "ok"})
            if text and confidence > best.confidence:
                best.text, best.confidence, best.model_used = text, confidence, _SONNET_MODEL
        except Exception as exc:
            sonnet_entry.update({"confidence": best.confidence, "status": f"error: {exc}"})
        log.append(sonnet_entry)

        best.attempt_log = log
        return best

    # ── Model call ────────────────────────────────────────────────────────────

    async def _call_model(
        self, model_id: str, b64: str, mime: str
    ) -> tuple[str, float]:
        """Send image to one model via OpenRouter, return (text, confidence)."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                        {"type": "text", "text": _OCR_PROMPT},
                    ],
                }
            ],
            max_tokens=2048,
            timeout=30.0,
        )
        content = response.choices[0].message.content or ""
        return _parse_response(content)

    # ── TrOCR local backend ───────────────────────────────────────────────────

    def _load_trocr(self) -> None:
        """Lazy-load TrOCR model from HuggingFace cache."""
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "transformers non installé. "
                "Exécutez : pip install transformers torch --index-url https://download.pytorch.org/whl/cpu"
            ) from exc

        model_id = "microsoft/trocr-base-printed"
        self._trocr_processor = TrOCRProcessor.from_pretrained(model_id)
        self._trocr_model = VisionEncoderDecoderModel.from_pretrained(model_id)

    async def _run_trocr(self, image_bytes: bytes) -> OCRResult:
        """Run local TrOCR inference and wrap result in OCRResult."""
        from PIL import Image

        if self._trocr_model is None:
            self._load_trocr()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixel_values = self._trocr_processor(image, return_tensors="pt").pixel_values
        generated_ids = self._trocr_model.generate(pixel_values)
        text = self._trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        confidence = _score_text(text)
        return OCRResult(
            text=text,
            confidence=confidence,
            model_used="microsoft/trocr-base-printed",
            attempts=1,
            attempt_log=[{"model": "trocr-base-printed", "tier": "local", "confidence": confidence, "status": "ok"}],
        )
