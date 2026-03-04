"""Validate ROS2 topics: allowed topics exist with correct values, blocked do not."""

import subprocess
import sys
import cantools

from generate_frames import KNOWN_VALUES


def validate_ros2(topic_list: list[str], expected_topics: dict[str, str],
                  allowed: dict[int, set[str]], db: cantools.database.Database) -> None:
    """Full ROS2 validation."""
    passed, failed = 0, 0

    # Test 1: Expected topics MUST exist
    print("\n=== Expected ROS2 topics (must exist) ===")
    for topic, sig_name in expected_topics.items():
        if topic in topic_list:
            passed += 1
            print(f"  PASS: {topic} ({sig_name}) exists")
        else:
            failed += 1
            print(f"  FAIL: {topic} ({sig_name}) missing!")

    # Test 2: Read value and compare to expected
    print("\n=== Reading values from ROS2 topics ===")
    for topic, sig_name in expected_topics.items():
        if topic not in topic_list:
            continue
        expected = KNOWN_VALUES.get(sig_name)
        try:
            result = subprocess.run(
                ["ros2", "topic", "echo", "--once", topic],
                capture_output=True, text=True, timeout=5,
            )
            if "data:" not in result.stdout:
                failed += 1
                print(f"  FAIL: {topic} no data received")
                continue
            raw = result.stdout.split("data:")[1].strip().split()[0]
            actual = float(raw)
            if expected is not None and abs(actual - expected) < 1.0:
                passed += 1
                print(f"  PASS: {topic} = {actual} (expected ~{expected})")
            elif expected is not None:
                failed += 1
                print(f"  FAIL: {topic} = {actual} (expected ~{expected})")
            else:
                passed += 1
                print(f"  PASS: {topic} = {actual} (value received)")
        except subprocess.TimeoutExpired:
            failed += 1
            print(f"  FAIL: {topic} timeout (no message within 5s)")

    # Test 3: Blocked message topics must NOT exist
    print("\n=== Blocked topics (must NOT exist) ===")
    blocked_names = {msg.name.lower() for msg in db.messages if msg.frame_id not in allowed}
    leaked = [t for t in topic_list if any(name in t.lower() for name in blocked_names)]
    if not leaked:
        passed += 1
        print("  PASS: No blocked message topics found")
    else:
        for t in leaked:
            failed += 1
            print(f"  FAIL: Blocked topic {t} exists!")

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
