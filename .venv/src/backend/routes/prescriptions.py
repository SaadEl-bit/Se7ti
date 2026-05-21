from fastapi import APIRouter, File, Form, UploadFile

from ..models.prescription import PrescriptionManual, PrescriptionUploadResult, ParsedPrescription
from ..services.ocr_service import OCRService
from ..services.llm_parser import LLMParser
from ..services.matching_engine import MatchingEngine

router = APIRouter(prefix="/api", tags=["prescriptions"])

_ocr = OCRService()
_llm = LLMParser()
_matcher = MatchingEngine()


@router.post("/prescriptions/upload", response_model=PrescriptionUploadResult)
async def upload_prescription(
    user_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    """Upload a prescription image → OCR cascade → LLM parse → geo-medication matching."""
    contents = await file.read()

    ocr_result = await _ocr.extract_text(contents)

    parsed_raw = await _llm.parse_medications(ocr_result.text)
    parsed = ParsedPrescription(**parsed_raw) if isinstance(parsed_raw, dict) else ParsedPrescription()

    matching_users: list[dict] = []
    for med in parsed.medications:
        result = await _matcher.find_matches(
            medication=med.name,
            lat=34.686,
            lon=-1.911,
            radius_km=5.0,
        )
        for u in result.get("matching_users", []):
            if not any(m["id"] == u["id"] for m in matching_users):
                matching_users.append(u)

    med_count = len(parsed.medications)
    parse_confidence = min(0.95, 0.5 + med_count * 0.15) if med_count else 0.0

    return {
        "user_id": user_id,
        "ocr_raw": ocr_result.text,
        "ocr_model": ocr_result.model_used,
        "ocr_confidence": round(ocr_result.confidence, 3),
        "ocr_attempts": ocr_result.attempts,
        "parsed_data": parsed,
        "matching_users": matching_users,
        "confidence": round(parse_confidence, 2),
    }


@router.post("/prescriptions/manual")
async def manual_prescription(payload: PrescriptionManual) -> dict:
    """Accept manually entered prescription medication data."""
    return {"user_id": payload.user_id, "medications": payload.medications, "status": "saved"}
