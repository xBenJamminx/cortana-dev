#!/bin/bash
# Daily clean gateway restart to prevent stale socket buildup
systemctl restart openclaw-gateway
sleep 5
if systemctl is-active --quiet openclaw-gateway; then
    echo "[$(date)] Gateway restarted cleanly" >> /var/log/clawd/gateway-restart.log
else
    echo "[$(date)] WARNING: Gateway failed to restart" >> /var/log/clawd/gateway-restart.log
    systemctl start openclaw-gateway
fi
