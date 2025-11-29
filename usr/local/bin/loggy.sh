#!/bin/bash

FLAGFILE="/tmp/mouse_connected.flag"
DBUS_PATH="/org/bluez/hci0/dev_D8_AD_27_39_6C_FB"
DEVICE_MAC="D8:AD:27:39:6C:FB"

restart_logid() {
    touch "$FLAGFILE"
    sleep 3
    sudo systemctl start logid.service
    sleep 5
    sudo systemctl restart logid.service
}

check_mx_master() {
    if bluetoothctl devices | grep -q "$DEVICE_MAC"; then
        return 0
    else
        return 1
    fi
}

monitor_mx_master() {
    echo "Monitoring MX Master connection..."
    gdbus monitor -y -d org.bluez -o "$DBUS_PATH" | while read -r line; do
        if [[ "$line" =~ "Connected: yes" ]] || [[ "$line" =~ "<true>" ]]; then
             restart_logid
        fi
    done
}

main() {
    if ! check_mx_master; then
        echo "MX Master not found. Monitoring."
        monitor_mx_master
    else
        restart_logid
    fi
}

main
