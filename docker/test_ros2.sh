#!/bin/bash
# Build the ROS2 Docker container and run all tests inside it.
#
# Usage:
#   bash docker/test_ros2.sh <dbc_file> <xml_config>
#
# Example:
#   bash docker/test_ros2.sh \
#       dbc/SensoricSolutionsOMSRace.dbc \
#       config/config_SensoricSolutionsOMSRace_040326_1846.xml
set -e

if [ $# -lt 2 ]; then
    echo "Usage: bash docker/test_ros2.sh <dbc_file> <xml_config>"
    echo ""
    echo "Example:"
    echo "  bash docker/test_ros2.sh \\"
    echo "      dbc/SensoricSolutionsOMSRace.dbc \\"
    echo "      config/config_SensoricSolutionsOMSRace_040326_1846.xml"
    exit 1
fi

DBC="$1"
XML="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

[ -f "$DBC" ] || { echo "DBC file not found: $DBC"; exit 1; }
[ -f "$XML" ] || { echo "XML config not found: $XML"; exit 1; }

echo "========================================"
echo "  DBC: $DBC"
echo "  XML: $XML"
echo "========================================"

echo ""
echo "========================================"
echo "  1/4  Starting Docker daemon"
echo "========================================"
if ! docker info &>/dev/null; then
    echo "Docker not running, starting..."
    sudo systemctl start docker
    echo "Docker started"
else
    echo "Docker already running"
fi

echo ""
echo "========================================"
echo "  2/4  Creating vcan0 on host"
echo "========================================"
if ip link show vcan0 &>/dev/null; then
    echo "vcan0 already exists"
else
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
    echo "vcan0 created"
fi

echo ""
echo "========================================"
echo "  3/4  Building Docker image (ROS2 + Rust)"
echo "========================================"
docker build -t can-ros2-bridge -f docker/Dockerfile .

echo ""
echo "========================================"
echo "  4/4  Running tests in container"
echo "========================================"
docker run --rm --privileged --network host \
    -v "$ROOT":/ws \
    can-ros2-bridge \
    bash /ws/docker/run_all_tests.sh "$DBC" "$XML"
