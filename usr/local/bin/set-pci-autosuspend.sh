#!/usr/bin/env bash

# List of PCI device IDs or paths to ignore
# Use the PCI address (e.g., 0000:03:00.0) or part of it.
IGNORE_LIST=(
    "0000:03:00.0"   # r8169 NIC
    "0000:04:00.0"   # mt7921e WiFi
)

should_ignore() {
    local devpath="$1"
    for ignore in "${IGNORE_LIST[@]}"; do
        if [[ "$devpath" == *"$ignore"* ]]; then
            return 0  # yes, ignore
        fi
    done
    return 1  # no, apply change
}

# Enable PCIe power autosuspend for all devices except ignored ones
for control_file in /sys/bus/pci/devices/*/power/control; do
    devpath="${control_file%/power/control}"
    if should_ignore "$devpath"; then
        echo "Skipping $devpath"
        continue
    fi
    echo 'auto' > "$control_file"
    echo "Set auto for $devpath"
done


