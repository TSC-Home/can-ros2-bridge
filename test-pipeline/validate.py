"""Validate bridge output: allowed signals must appear, blocked must not."""

import sys
import cantools


def validate(stdout: str, vectors: list[dict], allowed: dict[int, set[str]],
             db: cantools.database.Database) -> None:
    """Check bridge output against XML allow-list."""
    passed, failed = 0, 0
    lines = stdout.strip().splitlines()

    # Test 1: Allowed signals MUST appear in output
    print("\n=== Allowed signals (must appear) ===")
    for can_id, signal_names in allowed.items():
        for sig_name in signal_names:
            if any(sig_name in line for line in lines):
                passed += 1
                print(f"  PASS: {sig_name} found in output")
            else:
                failed += 1
                print(f"  FAIL: {sig_name} NOT found (should be there)")

    # Test 2: Blocked messages must NOT appear
    print("\n=== Blocked messages (must NOT appear) ===")
    for msg in db.messages:
        if msg.frame_id in allowed:
            continue
        if any(msg.name in line for line in lines):
            failed += 1
            print(f"  FAIL: {msg.name} (0x{msg.frame_id:X}) leaked through!")
        else:
            passed += 1
            print(f"  PASS: {msg.name} (0x{msg.frame_id:X}) correctly filtered")

    # Test 3: Signals from allowed messages but NOT in XML must not appear
    print("\n=== Blocked signals within allowed messages ===")
    for msg in db.messages:
        if msg.frame_id not in allowed:
            continue
        allowed_sigs = allowed[msg.frame_id]
        for sig in msg.signals:
            if sig.name in allowed_sigs:
                continue
            if any(sig.name in line for line in lines):
                failed += 1
                print(f"  FAIL: {msg.name}.{sig.name} leaked (not in XML)")
            else:
                passed += 1
                print(f"  PASS: {msg.name}.{sig.name} correctly filtered")

    # Test 4: Unknown CAN ID must not appear
    print("\n=== Unknown CAN IDs ===")
    if not any("0x999" in line or "2457" in line for line in lines):
        passed += 1
        print("  PASS: Unknown ID 0x999 correctly filtered")
    else:
        failed += 1
        print("  FAIL: Unknown ID 0x999 leaked through")

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
