"""
Генерация QR-кодов для квитанций голосования.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_receipt_qr(
    tx_hash: str,
    voter_address: str,
    candidate_address: str,
    block_number: int,
    session_id: str,
) -> Optional[bytes]:

    try:

        import qrcode

        payload = (
            f"MYCELIUM|"
            f"TX:{tx_hash}|"
            f"FROM:{voter_address}|"
            f"TO:{candidate_address}|"
            f"BLOCK:{block_number}"
        )

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )

        qr.add_data(payload)

        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()

        img.save(
            buffer,
            format="PNG",
        )

        return buffer.getvalue()

    except ImportError:

        logger.error(
            "qrcode package missing"
        )

        return None

    except Exception as exc:

        logger.error(
            "QR generation failed: %s",
            exc,
        )

        return None

def save_qr_to_file(qr_bytes: bytes, output_path: Path) -> bool:
    """Сохраняет PNG-байты QR-кода в файл."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(qr_bytes)
        logger.info("QR saved: %s", output_path)
        return True
    except OSError as exc:
        logger.error("Failed to save QR: %s", exc)
        return False