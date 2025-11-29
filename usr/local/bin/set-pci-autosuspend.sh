#!/usr/bin/env bash
# Enable PCIe power autosuspend for all devices
for dev in /sys/bus/pci/devices/*/power/control; do
    echo 'auto' > "$dev"
done

