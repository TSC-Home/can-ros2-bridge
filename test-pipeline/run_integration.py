#!/usr/bin/env python3
"""
Integration test: verifies the bridge only outputs signals from the XML config.
Sends ALL DBC messages, then checks that only XML-configured signals appear.

Usage: python run_integration.py <dbc_file> <xml_config> [--interface vcan0]
"""

import argparse
import os
import signal
import subprocess
import sys
import time

import cantools

from can_send import send_frame
from generate_frames import generate_test_vectors, format_can_frame
from xml_parser import parse_allowed
from validate import validate


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dbc_file")
    p.add_argument("xml_config")
    p.add_argument("--interface", default="vcan0")
    args = p.parse_args()

    root = os.path.join(os.path.dirname(__file__), "..")
    allowed = parse_allowed(args.xml_config)
    print(f"XML config: {len(allowed)} messages, "
          f"{sum(len(s) for s in allowed.values())} signals allowed")

    # Build
    print("\n=== Building bridge ===")
    r = subprocess.run(["cargo", "build", "--release"], cwd=os.path.join(root, "node"))
    if r.returncode != 0:
        sys.exit("Build failed")

    # Setup vcan
    print("\n=== Setting up vcan ===")
    subprocess.run(["bash", os.path.join(os.path.dirname(__file__), "vcan_setup.sh"),
                     args.interface], check=True)

    # Start bridge
    print("\n=== Starting bridge ===")
    bin_path = os.path.join(root, "node", "target", "release", "can-ros2-bridge")
    bridge = subprocess.Popen(
        [bin_path, "--config", args.xml_config, "-i", args.interface],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    time.sleep(0.5)

    # Send ALL DBC messages (including ones NOT in XML)
    print("\n=== Sending ALL DBC frames ===")
    db = cantools.database.load_file(args.dbc_file)
    vectors = generate_test_vectors(db)
    for v in vectors:
        in_xml = "ALLOWED" if v["can_id"] in allowed else "BLOCKED"
        print(f"  [{in_xml}] {v['message']} (0x{v['can_id']:X})")
        send_frame(args.interface, v["can_id"], v["data"])
        time.sleep(0.1)

    # Send completely unknown CAN ID
    print("  [BLOCKED] Unknown (0x999)")
    send_frame(args.interface, 0x999, b"\xDE\xAD\xBE\xEF")
    time.sleep(0.5)

    # Stop bridge, collect output
    bridge.send_signal(signal.SIGTERM)
    stdout, _ = bridge.communicate(timeout=5)
    print("\n=== Bridge output ===")
    print(stdout if stdout.strip() else "(empty)")

    # Validate
    validate(stdout, vectors, allowed, db)


if __name__ == "__main__":
    main()
