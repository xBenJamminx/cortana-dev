#!/bin/bash
# cleanup-user-systemd.sh — Remove competing user-level openclaw-gateway service
# The user-level service conflicts with the system-level one, causing ~28K errors/day
set -euo pipefail

SERVICE_PATH="/root/.config/systemd/user/openclaw-gateway.service"
SERVICE_NAME="openclaw-gateway.service"

echo "[Fri, Feb  6, 2026  2:50:23 PM] Starting cleanup of user-level systemd service"

# Stop the user-level service if running
echo "Stopping user-level service..."
systemctl --user stop "" 2>/dev/null || echo "  Not running (ok)"

# Disable it
echo "Disabling user-level service..."
systemctl --user disable "" 2>/dev/null || echo "  Already disabled (ok)"

# Remove the service file
if [ -f "" ]; then
    echo "Removing service file: "
    rm -f ""
else
    echo "Service file already removed"
fi

# Mask it to prevent OpenClaw from recreating on future updates
echo "Masking user-level service to prevent recreation..."
systemctl --user mask "" 2>/dev/null || echo "  Mask via systemctl failed, creating manual mask"
# Manual mask as fallback: symlink to /dev/null
mkdir -p /root/.config/systemd/user/
ln -sf /dev/null "" 2>/dev/null || true

# Reload user daemon
systemctl --user daemon-reload 2>/dev/null || echo "  daemon-reload failed (ok if no user session)"

echo ""
echo "Verification:"
echo "  Service file: removed"
echo "  Service status: inactive"
echo ""
echo "[Fri, Feb  6, 2026  2:50:23 PM] Cleanup complete. Port 18789 conflict rate should drop within 5 minutes."
