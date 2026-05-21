"""Test TrOCR CPU inference with a sample image or a generated blank image."""

import sys
import time


def test_trocr_printed(image_path: str | None = None) -> None:
    from PIL import Image
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    print("Loading TrOCR model (microsoft/trocr-base-printed) …")
    t0 = time.time()
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
    print(f"Model loaded in {time.time() - t0:.1f}s")

    if image_path:
        image = Image.open(image_path).convert("RGB")
    else:
        image = Image.new("RGB", (320, 64), color=(255, 255, 255))
        print("No image provided — using blank white image for smoke test.")

    print("Running inference …")
    t1 = time.time()
    pixel_values = processor(image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    elapsed = time.time() - t1

    print(f"Inference time : {elapsed:.2f}s")
    print(f"Extracted text : {repr(text)}")


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    test_trocr_printed(image_path)
