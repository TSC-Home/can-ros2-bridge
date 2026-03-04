#!/usr/bin/env python3
"""
Integration test: sends virtual CAN frames and verifies bridge output.

Usage: python run_test.py <dbc_file> <xml_config> [--interface vcan0]
"""

import argparse
import os
import signal
import subprocess
import sys
import time

import cantools

from generate_frames import generate_test_vectors, format_can_frame

BRIDGE_BIN = os.path.join(os.path.dirname(__file__), "..", "node", "target", "release", "can-ros2-bridge")


def parse_args():
    p = argparse.ArgumentParser(description="CAN-ROS2 Bridge integration test")
    p.add_argument("dbc_file", help="Path to DBC file")
    p.add_argument("xml_config", help="Path to bridge XML config")
    p.add_argument("--interface", default="vcan0", help="Virtual CAN interface")
    return p.parse_args()


def setup_vcan(interface: str) -> bool:
    script = os.path.join(os.path.dirname(__file__), "vcan_setup.sh")
    result = subprocess.run(["bash", script, interface], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"vcan setup failed: {result.stderr}")
        return False
    print(result.stdout.strip())
    return True


def send_frame(interface: str, can_id: int, data: bytes):
    frame_str = format_can_frame(can_id, data)
    subprocess.run(["cansend", interface, frame_str], check=True)


def run_bridge(xml_config: str, interface: str) -> subprocess.Popen:
    bin_path = BRIDGE_BIN
    if not os.path.exists(bin_path):
        bin_path = bin_path.replace("/release/", "/debug/")
    return subprocess.Popen(
        [bin_path, "--config", xml_config, "--can-interface", interface],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
