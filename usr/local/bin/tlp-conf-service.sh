#!/usr/bin/env bash
set -e

BLACKLIST_CONF="/etc/tlp.d/99-blacklist.conf"

CURRENT_ENTRY=$(bootctl status | grep "Current Entry:" | awk '{print $3}')

if [[ "$CURRENT_ENTRY" == "arch-blacklist-nvidia.conf" ]]; then
  if [[ ! -f "$BLACKLIST_CONF" ]]; then
    cat <<EOF >"$BLACKLIST_CONF"
TLP_DEFAULT_MODE=BAT
TLP_PERSISTENT_DEFAULT=1
EOF
    sleep 0.5
    tlp start
  fi
elif [[ "$CURRENT_ENTRY" == "arch.conf" ]]; then
  if [[ -f "$BLACKLIST_CONF" ]]; then
    rm $BLACKLIST_CONF
    sleep 0.5
    tlp start
  fi
fi
