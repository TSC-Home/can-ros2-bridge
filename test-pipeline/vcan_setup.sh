#!/bin/bash
# Set up virtual CAN interface for testing
set -e

IFACE="${1:-vcan0}"

if ip link show "$IFACE" &>/dev/null; then
    echo "$IFACE already exists"
    exit 0
fi

sudo modprobe vcan
sudo ip link add dev "$IFACE" type vcan
sudo ip link set up "$IFACE"
echo "$IFACE is up"
