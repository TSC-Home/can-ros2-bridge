"""Generate virtual CAN frames from a DBC file for testing."""

import struct
import cantools


def encode_message(db: cantools.database.Database, msg_name: str, values: dict) -> tuple[int, bytes]:
    """Encode a CAN message using DBC definitions. Returns (can_id, data_bytes)."""
    msg = db.get_message_by_name(msg_name)
    data = msg.encode(values)
    return msg.frame_id, data


def generate_test_vectors(db: cantools.database.Database) -> list[dict]:
    """Generate test vectors for all messages in the DBC with known values."""
    vectors = []
    for msg in db.messages:
        test_values = {}
        for sig in msg.signals:
            mid = (sig.minimum + sig.maximum) / 2 if sig.minimum is not None else 0
            test_values[sig.name] = mid

        can_id, data = encode_message(db, msg.name, test_values)
        vectors.append({
            "message": msg.name,
            "can_id": can_id,
            "data": data,
            "expected_values": test_values,
        })
    return vectors


def format_can_frame(can_id: int, data: bytes) -> str:
    """Format as cansend compatible string: can_id#hex_data."""
    hex_data = "".join(f"{b:02X}" for b in data)
    return f"{can_id:03X}#{hex_data}"
