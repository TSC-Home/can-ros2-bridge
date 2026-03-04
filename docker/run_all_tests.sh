#!/bin/bash
# Run all tests inside the ROS2 Docker container.
# Usage: docker/run_all_tests.sh <dbc_file> <xml_config> [--interface vcan0]
set -e

DBC="${1:?Usage: run_all_tests.sh <dbc_file> <xml_config>}"
XML="${2:?Usage: run_all_tests.sh <dbc_file> <xml_config>}"
IFACE="${3:-vcan0}"
cd /ws

echo "  DBC: $DBC"
echo "  XML: $XML"
echo ""

echo "========================================"
echo "  1/4  Rust unit tests"
echo "========================================"
cd node && cargo test && cd ..

echo ""
echo "========================================"
echo "  2/4  Python unit tests"
echo "========================================"
cd tools && python3 -m pytest test_parser.py test_xml_export.py -v && cd ..

echo ""
echo "========================================"
echo "  3/4  Integration test (filter check)"
echo "========================================"
ip link show "$IFACE" &>/dev/null || {
    modprobe vcan 2>/dev/null || true
    ip link add dev "$IFACE" type vcan
    ip link set up "$IFACE"
}
python3 test-pipeline/run_integration.py \
    "$DBC" "$XML" --interface "$IFACE"

echo ""
echo "========================================"
echo "  4/4  ROS2 end-to-end test"
echo "========================================"
source /opt/ros/humble/setup.bash
python3 test-pipeline/run_ros2_test.py \
    "$DBC" "$XML" --interface "$IFACE"

echo ""
echo "========================================"
echo "  ALL TESTS PASSED"
echo "========================================"
