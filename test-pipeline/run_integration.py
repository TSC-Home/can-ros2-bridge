#!/usr/bin/env python3
"""
Full integration test runner.
Builds bridge, sets up vcan, sends frames, validates output.

Usage: python run_integration.py <dbc_file> <xml_config> [--interface vcan0]
"""

import os
import signal
import subprocess
import sys
import time

import cantools

from generate_frames import generate_test_vectors, format_can_frame


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("dbc_file")
    p.add_argument("xml_config")
    p.add_argument("--interface", default="vcan0")
    args = p.parse_args()

    project_root = os.path.join(os.path.dirname(__file__), "..")

    # Step 1: Build bridge
    print("=== Building bridge ===")
    r = subprocess.run(["cargo", "build", "--release"], cwd=os.path.join(project_root, "node"))
    if r.returncode != 0:
        sys.exit("Build failed")

    # Step 2: Setup vcan
    print("\n=== Setting up vcan ===")
    script = os.path.join(os.path.dirname(__file__), "vcan_setup.sh")
    subprocess.run(["bash", script, args.interface], check=True)

    # Step 3: Start bridge
    print("\n=== Starting bridge ===")
    bin_path = os.path.join(project_root, "node", "target", "release", "can-ros2-bridge")
    bridge = subprocess.Popen(
        [bin_path, "--config", args.xml_config, "-i", args.interface],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    time.sleep(0.5)

    # Step 4: Generate and send test frames
    print("\n=== Sending test frames ===")
    db = cantools.database.load_file(args.dbc_file)
    vectors = generate_test_vectors(db)
    for v in vectors:
        frame_str = format_can_frame(v["can_id"], v["data"])
        print(f"  Sending {v['message']}: {frame_str}")
        subprocess.run(["cansend", args.interface, frame_str], check=True)
        time.sleep(0.1)

    # Also send an unknown ID to test filtering
    print("  Sending unknown ID 0x999")
    subprocess.run(["cansend", args.interface, "999#DEADBEEF"], check=True)
    time.sleep(0.5)

    # Step 5: Check bridge output
    bridge.send_signal(signal.SIGTERM)
    stdout, stderr = bridge.communicate(timeout=5)
    print("\n=== Bridge output ===")
    print(stdout)

    # Step 6: Validate
    print("=== Validation ===")
    passed = 0
    failed = 0
    for v in vectors:
        for sig_name, expected in v["expected_values"].items():
            if sig_name in stdout:
                passed += 1
                print(f"  PASS: {v['message']}.{sig_name} found in output")
            else:
                failed += 1
                print(f"  FAIL: {v['message']}.{sig_name} NOT in output")

    if "0x999" not in stdout and "unknown" not in stdout.lower():
        passed += 1
        print("  PASS: Unknown CAN ID 0x999 correctly filtered")
    else:
        failed += 1
        print("  FAIL: Unknown CAN ID 0x999 leaked through")

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
