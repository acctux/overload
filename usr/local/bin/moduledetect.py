#!/usr/bin/env python3

import subprocess
import re

MKINITCPIO_PATH = "/etc/mkinitcpio.conf"


def parse_mkinitcpio_modules(path=MKINITCPIO_PATH):
    modules = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("MODULES=("):
                inner = line[len("MODULES=(") : -1].strip()
                modules.extend(mod.strip() for mod in inner.split())
                break

    return modules


def hwdetect_run():
    raw = subprocess.check_output(["hwdetect", "--show-modules"], text=True)
    modules = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            cat, mods = line.split(":", 1)
            modules[cat.strip()] = mods.strip().split()
    hw_modules = [m for modlist in modules.values() for m in modlist]
    return hw_modules


def write_modules_to_mkinitcpio(modules, path=MKINITCPIO_PATH):
    """Replace or append MODULES=(...) line in mkinitcpio.conf"""
    with open(path, "r") as f:
        content = f.read()

    new_line = f"MODULES=({' '.join(modules)})"

    if re.search(r"^MODULES=\(.*\)", content, flags=re.MULTILINE):
        content = re.sub(r"^MODULES=\(.*\)", new_line, content, flags=re.MULTILINE)
    else:
        content += "\n" + new_line + "\n"

    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    mk_modules = parse_mkinitcpio_modules()
    hw_modules = hwdetect_run()
    all_unique_modules = sorted(set(hw_modules + mk_modules))
    write_modules_to_mkinitcpio(all_unique_modules)
    print(f"Updated {MKINITCPIO_PATH} with {len(all_unique_modules)} modules.")
