from __future__ import annotations
from typing import Optional, Tuple
from pathlib import Path

try:
    import pytesseract  # type: ignore
    from PIL import Image
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore
    Image = None  # type: ignore

from .utils import extract_pair_and_price


class OCRUnavailableError(RuntimeError):
    pass


def ocr_image_to_text(image_path: str) -> str:
    if pytesseract is None or Image is None:
        raise OCRUnavailableError(
            "pytesseract/Pillow not available. Install dependencies and Tesseract OCR binary."
        )
    img = Image.open(Path(image_path))
    # OEM 3: default; PSM 6: assume a uniform block of text
    text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")
    return text or ""


def parse_pair_and_price_from_image(image_path: str) -> Tuple[Optional[str], Optional[float], str]:
    text = ocr_image_to_text(image_path)
    pair, price = extract_pair_and_price(text)
    return pair, price, text
