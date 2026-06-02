"""
Тесты генерации QR-кодов для квитанций голосования.
"""
import pytest
from src.utils.qr import generate_receipt_qr, save_qr_to_file


class TestQRGeneration:
    def test_generates_bytes(self):
        qr = generate_receipt_qr(
            tx_hash="0x" + "a" * 64,
            voter_address="0x" + "1" * 40,
            candidate_address="0x" + "2" * 40,
            block_number=42,
            session_id="test-session-id",
        )
        assert qr is not None
        assert isinstance(qr, bytes)
        assert len(qr) > 100  # PNG should be substantial

    def test_png_header(self):
        """Сгенерированные байты должны быть валидным PNG (начинаются с PNG-сигнатуры)."""
        qr = generate_receipt_qr(
            tx_hash="0xdeadbeef",
            voter_address="0x" + "0" * 40,
            candidate_address="0x" + "1" * 40,
            block_number=1,
            session_id="s1",
        )
        assert qr is not None
        # Магические байты PNG: \x89PNG\r\n\x1a\n
        assert qr[:4] == b'\x89PNG'

    def test_different_inputs_different_qr(self):
        qr1 = generate_receipt_qr(
            tx_hash="0x" + "a" * 64,
            voter_address="0x" + "1" * 40,
            candidate_address="0x" + "2" * 40,
            block_number=1,
            session_id="s1",
        )
        qr2 = generate_receipt_qr(
            tx_hash="0x" + "b" * 64,
            voter_address="0x" + "3" * 40,
            candidate_address="0x" + "4" * 40,
            block_number=2,
            session_id="s2",
        )
        assert qr1 != qr2

    def test_save_qr_to_file(self, tmp_path):
        qr = generate_receipt_qr(
            tx_hash="0x" + "c" * 64,
            voter_address="0x" + "5" * 40,
            candidate_address="0x" + "6" * 40,
            block_number=10,
            session_id="save-test",
        )
        assert qr is not None
        output = tmp_path / "test_receipt.png"
        result = save_qr_to_file(qr, output)
        assert result is True
        assert output.exists()
        assert output.stat().st_size > 0
        # Проверяем что сохранённое содержимое совпадает
        assert output.read_bytes() == qr

    def test_save_qr_creates_parent_dirs(self, tmp_path):
        qr = generate_receipt_qr(
            tx_hash="0x" + "d" * 64,
            voter_address="0x" + "7" * 40,
            candidate_address="0x" + "8" * 40,
            block_number=5,
            session_id="dir-test",
        )
        deep_path = tmp_path / "a" / "b" / "c" / "receipt.png"
        result = save_qr_to_file(qr, deep_path)
        assert result is True
        assert deep_path.exists()