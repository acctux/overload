#!/usr/bin/env python3
import asyncio
import subprocess
import time
from pathlib import Path
from dbus_fast.aio import MessageBus
from dbus_fast import BusType, Message, Variant

FLAGFILE = Path("/tmp/mouse_connected.flag")
DEVICE_MAC = "D8:AD:27:39:6C:FC"
bool_state = {
    "resolved": False,
}


def run_cmd(command, check=False, capture_output=True):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )
    return result.stdout.strip() if capture_output else None


def logid_running():
    status = run_cmd(["systemctl", "is-active", "logid.service"])
    if status == "active":
        print("logid.service is running")
        return True
    print(f"logid.service is not running. Status: {status}")
    return False


def restart_logid():
    run_cmd(["sudo", "systemctl", "restart", "logid.service"], check=False)
    time.sleep(6)
    run_cmd(["sudo", "systemctl", "restart", "logid.service"], check=False)
    print("logid.service restarted")


def stop_logid():
    run_cmd(["sudo", "systemctl", "stop", "logid.service"], check=False)


def start_logid():
    run_cmd(["sudo", "systemctl", "start", "logid.service"], check=False)


def warn_in_logs(service_name="logid", check_str="[WARN] Failed"):
    logs = run_cmd(["journalctl", "-u", service_name])
    if logs:
        if check_str in logs:
            print(f"Warning: {check_str} found in {service_name} logs.")
            return True
        else:
            print(f"No {check_str} messages found in {service_name} logs.")
            return False


def logid_nuclear():
    FLAGFILE.touch()
    stop_logid()
    time.sleep(3)
    start_logid()
    time.sleep(5)
    if warn_in_logs():
        restart_logid()


def device_connected():
    output = run_cmd(["bluetoothctl", "devices"])
    if output:
        if DEVICE_MAC in output:
            return True
        else:
            return False


def handle_signal(msg):
    _, changed, *_ = msg.body
    updated = {
        k: (v.value if isinstance(v, Variant) else v) for k, v in changed.items()
    }
    if "ServicesResolved" in updated:
        bool_state["resolved"] = updated["ServicesResolved"]
        print("ServicesResolved:", bool_state["resolved"])
        if bool_state["resolved"]:
            print("Triggering logid")
            logid_nuclear()


async def add_match(bus, rule):
    msg = Message(
        destination="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="AddMatch",
        signature="s",
        body=[rule],
    )
    await bus.call(msg)


async def main():
    if device_connected():
        logid_nuclear()
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    bus.add_message_handler(handle_signal)
    logid_nuclear()
    await add_match(bus, "type='signal',interface='org.freedesktop.DBus.Properties'")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
