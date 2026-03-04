"""Send CAN frames via Python socket (no can-utils dependency)."""

import socket
import struct

CAN_RAW = 1
CAN_FMT = "<IB3x8s"  # can_id, len, pad, data


def send_frame(interface: str, can_id: int, data: bytes) -> None:
    """Send a single CAN frame on the given interface."""
    sock = socket.socket(socket.AF_CAN, socket.SOCK_RAW, CAN_RAW)
    sock.bind((interface,))
    padded = data.ljust(8, b"\x00")[:8]
    frame = struct.pack(CAN_FMT, can_id, len(data), padded)
    sock.send(frame)
    sock.close()
