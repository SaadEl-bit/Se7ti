import pytest
import asyncio
from unittest.mock import patch, MagicMock

from backend.services.ocr_service import OCRService


def test_ocr_service_instantiation():
    service = OCRService()
    assert service._model is None
    assert service._processor is None


def test_ocr_extract_text_mock():
    service = OCRService()

    mock_processor = MagicMock()
    mock_model = MagicMock()

    mock_pixel_values = MagicMock()
    mock_processor.return_value.pixel_values = mock_pixel_values
    mock_model.generate.return_value = [[1, 2, 3]]
    mock_processor.batch_decode.return_value = ["Metformine 500mg 1cp/j"]

    service._processor = mock_processor
    service._model = mock_model

    from PIL import Image
    import io

    img = Image.new("RGB", (100, 32), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    result = asyncio.run(service.extract_text(image_bytes))
    assert isinstance(result, str)
