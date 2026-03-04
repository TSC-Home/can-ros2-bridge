"""DBC file parser using cantools."""

import cantools


def load_dbc(path: str) -> cantools.database.Database:
    """Load and return a DBC database."""
    return cantools.database.load_file(path)


def list_messages(db: cantools.database.Database) -> list[dict]:
    """Return summary of all messages in the DBC."""
    return [
        {
            "id": msg.frame_id,
            "name": msg.name,
            "signals": [
                {
                    "name": sig.name,
                    "start_bit": sig.start,
                    "length": sig.length,
                    "byte_order": sig.byte_order,
                    "signed": not sig.is_unsigned if hasattr(sig, "is_unsigned") else sig.length > 1,
                    "scale": sig.scale,
                    "offset": sig.offset,
                    "unit": sig.unit or "",
                    "minimum": sig.minimum,
                    "maximum": sig.maximum,
                }
                for sig in msg.signals
            ],
        }
        for msg in db.messages
    ]
