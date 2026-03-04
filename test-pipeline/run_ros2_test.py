#!/usr/bin/env python3
"""
ROS2 end-to-end test: verifies signals arrive as real ROS2 topics.
Requires: ROS2 sourced, bridge built with --features ros2, vcan0 up.

Usage: python run_ros2_test.py <dbc_file> <xml_config> [--interface vcan0]
"""

import argparse
import os
import signal
import subprocess
import sys
import threading
import time

import cantools

from can_send import send_frame
from generate_frames import generate_test_vectors
from xml_parser import parse_allowed, parse_topics
from validate_ros2 import validate_ros2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dbc_file")
    p.add_argument("xml_config")
    p.add_argument("--interface", default="vcan0")
    args = p.parse_args()

    root = os.path.join(os.path.dirname(__file__), "..")
    allowed = parse_allowed(args.xml_config)
    expected_topics = parse_topics(args.xml_config)
    db = cantools.database.load_file(args.dbc_file)
    vectors = generate_test_vectors(db)

    # Check ROS2
    if subprocess.run(["ros2", "topic", "list"], capture_output=True).returncode != 0:
        sys.exit("ERROR: ros2 not found. Source your ROS2 setup first.")

    # Build with ros2 feature
    print("=== Building bridge (with ros2) ===")
    r = subprocess.run(["cargo", "build", "--release", "--features", "ros2"],
                       cwd=os.path.join(root, "node"))
    if r.returncode != 0:
        sys.exit("Build failed. Is ROS2 sourced?")

    # Start bridge
    print("\n=== Starting bridge ===")
    bin_path = os.path.join(root, "node", "target", "release", "can-ros2-bridge")
    bridge = subprocess.Popen(
        [bin_path, "--config", args.xml_config, "-i", args.interface],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    # Background sender: keeps publishing frames so ros2 topic echo can catch them
    stop_sender = threading.Event()
    def sender_loop():
        while not stop_sender.is_set():
            for v in vectors:
                send_frame(args.interface, v["can_id"], v["data"])
                time.sleep(0.02)
    sender = threading.Thread(target=sender_loop, daemon=True)
    sender.start()
    print("  Sender running in background")
    time.sleep(1.0)

    # Get topic list
    print("\n=== Checking ROS2 topics ===")
    topic_list = subprocess.run(
        ["ros2", "topic", "list"], capture_output=True, text=True
    ).stdout.strip().splitlines()

    # Validate
    validate_ros2(topic_list, expected_topics, allowed, db)

    # Cleanup
    stop_sender.set()
    sender.join(timeout=2)
    bridge.send_signal(signal.SIGTERM)
    bridge.wait(timeout=5)


if __name__ == "__main__":
    main()
