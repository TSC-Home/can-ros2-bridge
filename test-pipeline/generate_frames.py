"""Generate virtual CAN frames from a DBC file for testing."""

import cantools

# Erkennbare Testwerte pro Signal (nicht 0, nicht Mitte)
KNOWN_VALUES = {
    "VelXPoi": 123.46,
    "VelYPoi": -42.0,
    "VelAPoi": 88.88,
    "AngSPoi": 12.345,
    "AccXHor": 9.82,
    "AccYHor": -3.14,
    "AccZHor": 1.5,
    "Standstill": 1,
    "TempSensor": 25.5,
    "SampleTime": 1234.567,
}


def _pick_value(sig) -> float:
    """Pick a recognizable test value for a signal."""
    if sig.name in KNOWN_VALUES:
        return KNOWN_VALUES[sig.name]
    # Fallback: 1/3 der Range (nie 0, nie Mitte)
    lo = sig.minimum if sig.minimum is not None else 0
    hi = sig.maximum if sig.maximum is not None else 100
    return lo + (hi - lo) / 3


def generate_test_vectors(db: cantools.database.Database) -> list[dict]:
    """Generate test vectors for all messages in the DBC with known values."""
    vectors = []
    for msg in db.messages:
        test_values = {sig.name: _pick_value(sig) for sig in msg.signals}
        data = msg.encode(test_values)
        vectors.append({
            "message": msg.name,
            "can_id": msg.frame_id,
            "data": data,
            "expected_values": test_values,
        })
    return vectors


def format_can_frame(can_id: int, data: bytes) -> str:
    """Format as cansend compatible string: can_id#hex_data."""
    hex_data = "".join(f"{b:02X}" for b in data)
    return f"{can_id:03X}#{hex_data}"
